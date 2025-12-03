import os
import secrets
import time
from datetime import datetime
from typing import Dict, List, Optional

import psycopg
from psycopg import errors
from psycopg_pool import ConnectionPool
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS

_pool: Optional[ConnectionPool] = None


def _generate_short_id(length: int = 6) -> str:
  """Generate a short id comprised of hex characters."""
  return secrets.token_hex(length // 2).upper()


def _init_pool() -> ConnectionPool:
  """Initialize (or reuse) the global PostgreSQL connection pool."""
  global _pool
  if _pool is not None:
    return _pool

  conninfo = os.getenv(
    "DATABASE_URL", "postgresql://linkshort:linkshort@localhost:5432/linkshort"
  )
  max_size = max(1, int(os.getenv("DB_POOL_MAX", "10")))
  retries = int(os.getenv("DB_CONNECT_RETRIES", "10"))
  wait = float(os.getenv("DB_CONNECT_RETRY_INTERVAL", "1.0"))
  last_error: Optional[Exception] = None

  for attempt in range(1, retries + 1):
    try:
      pool = ConnectionPool(conninfo=conninfo, min_size=1, max_size=max_size)
      _ensure_schema(pool)
      _pool = pool
      return pool
    except psycopg.OperationalError as exc:
      last_error = exc
      time.sleep(wait)

  raise RuntimeError("Unable to establish database connection") from last_error


def _ensure_schema(pool: ConnectionPool) -> None:
  """Create the storage table if it doesn't exist."""
  # Guard schema creation so multiple gunicorn workers don't race on startup.
  lock_id = int(os.getenv("DB_SCHEMA_LOCK_ID", "4242"))
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute("SELECT pg_advisory_lock(%s)", (lock_id,))
      try:
        cur.execute(
          """
          CREATE TABLE IF NOT EXISTS short_urls (
            id BIGSERIAL PRIMARY KEY,
            short_id VARCHAR(32) UNIQUE NOT NULL,
            original_url TEXT UNIQUE NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
          );
          """
        )
        conn.commit()
      except (errors.DuplicateTable, errors.UniqueViolation):
        # Another worker finished the creation first; ignore and continue.
        conn.rollback()
      finally:
        cur.execute("SELECT pg_advisory_unlock(%s)", (lock_id,))
        conn.commit()


def _get_or_create_short_id(pool: ConnectionPool, original_url: str) -> str:
  """Fetch an existing mapping or insert a new short id."""
  while True:
    with pool.connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
          "SELECT short_id FROM short_urls WHERE original_url = %s",
          (original_url,),
        )
        row = cur.fetchone()
        if row:
          return row[0]

        short_id = _generate_short_id()
        try:
          cur.execute(
            "INSERT INTO short_urls (short_id, original_url) VALUES (%s, %s) RETURNING short_id",
            (short_id, original_url),
          )
          assigned = cur.fetchone()[0]
          conn.commit()
          return assigned
        except errors.UniqueViolation:
          conn.rollback()
          continue


def _resolve_short_id(pool: ConnectionPool, short_id: str) -> Optional[str]:
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute(
        "SELECT original_url FROM short_urls WHERE short_id = %s",
        (short_id,),
      )
      row = cur.fetchone()
  return row[0] if row else None


def _dump_store(pool: ConnectionPool) -> List[Dict[str, str]]:
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute(
        """
        SELECT short_id, original_url, created_at
        FROM short_urls
        ORDER BY created_at DESC
        LIMIT 100
        """
      )
      rows = cur.fetchall()

  result: List[Dict[str, str]] = []
  for short_id, original_url, created_at in rows:
    created_at_iso = created_at.isoformat() if isinstance(
      created_at, datetime) else str(created_at)

    result.append(
      {
        "short_id": short_id,
        "original_url": original_url,
        "created_at": created_at_iso,
      }
    )
  return result


def create_app():
  app = Flask(__name__)
  allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
  ]
  CORS(app, origins=allowed_origins)
  pool = _init_pool()
  app.config["DB_POOL"] = pool

  @app.get("/ping")
  def ping():
    return jsonify({"status": "ok", "data": "pong"}), 200

  @app.get("/shorten")
  def shorten():
    original_url = (request.args.get("url") or "").strip()
    if not original_url:
      return jsonify({"error": "Missing required 'url' query parameter"}), 400
    # @todo check if url is valid (https is req)

    short_id = _get_or_create_short_id(pool, original_url)

    proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    host = request.headers.get("X-Forwarded-Host", request.host)

    actual_host = os.getenv("SHORT_HOST", host)

    short_link = f"{proto}://{actual_host}/{short_id}"
    return jsonify(
      {
        "original_url": original_url,
        "short_id": short_id,
        "short_url": short_link,
      }
    ), 201

  @app.get("/debug/log-stores")
  def log_stores():
    return jsonify({"rows": _dump_store(pool)}), 200

  @app.get("/<short_id>")
  def resolve_short(short_id: str):
    target = _resolve_short_id(pool, short_id)
    if not target:
      return jsonify({"error": "Unknown short link"}), 404
    return redirect(target)

  return app


if __name__ == "__main__":
  port = int(os.getenv("PORT", "8000"))
  create_app().run(host="0.0.0.0", port=port)
