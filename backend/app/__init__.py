import os
import secrets
from typing import Dict

from flask import Flask, jsonify, redirect, request

_url_store: Dict[str, str] = {}
_reverse_store: Dict[str, str] = {}


def _generate_short_id(length: int = 6) -> str:
  """Generate a unique and short id"""
  while True:
    candidate = secrets.token_hex(length // 2)
    if candidate not in _url_store:
      return candidate
# TODO - if _url_store is full - extend length


def create_app():
  app = Flask(__name__)

  @app.get("/ping")
  def ping():
    return jsonify({"status": "ok", "data": "pong"}), 200

  @app.get("/shorten")
  def shorten():
    original_url = (request.args.get("url") or "").strip()
    if not original_url:
      return jsonify({"error": "Missing required 'url' query parameter"}), 400

    short_id = _reverse_store.get(original_url)
    if not short_id:
      short_id = _generate_short_id()
      _url_store[short_id] = original_url
      _reverse_store[original_url] = short_id

    proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    host = request.headers.get("X-Forwarded-Host", request.host)
    short_link = f"{proto}://{host}/{short_id}"
    return jsonify(
      {
        "original_url": original_url,
        "short_id": short_id,
        "short_url": short_link,
      }
    ), 201

  @app.get("/<short_id>")
  def resolve_short(short_id: str):
    target = _url_store.get(short_id)
    if not target:
      return jsonify({"error": "Unknown short link"}), 404
    return redirect(target)

  return app


if __name__ == "__main__":
  port = int(os.getenv("PORT", "8000"))
  create_app().run(host="0.0.0.0", port=port)
