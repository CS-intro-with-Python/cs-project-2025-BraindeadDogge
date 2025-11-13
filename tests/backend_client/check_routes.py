import argparse
import time
from urllib.parse import urlencode

import requests


def wait_for_ping(base_url: str, timeout: float = 20.0, interval: float = 0.5) -> None:
  """Poll /ping until it responds with the expected payload."""
  deadline = time.time() + timeout
  url = f"{base_url.rstrip('/')}/ping"
  while time.time() < deadline:
    try:
      response = requests.get(url, timeout=2)
      if response.status_code == 200:
        payload = response.json()
        if payload.get("status") == "ok" and payload.get("data") == "pong":
          return
    except requests.RequestException:
      pass
    time.sleep(interval)
  raise TimeoutError(f"Timed out waiting for {url}")


def check_shortener(base_url: str) -> None:
  """Create a short link and verify it redirects to the original URL."""
  base = base_url.rstrip("/")
  target_url = "https://example.com/docs"
  shorten_url = f"{base}/shorten?{urlencode({'url': target_url})}"
  response = requests.get(shorten_url, timeout=5)
  response.raise_for_status()
  payload = response.json()

  short_id = payload.get("short_id")
  short_url = payload.get("short_url")
  if not short_id or not short_url:
    raise ValueError(f"Incomplete payload from /shorten: {payload}")
  if not short_url.endswith(f"/{short_id}"):
    raise ValueError(f"short_url {short_url} doesn't end with /{short_id}")

  redirect_response = requests.get(short_url, timeout=5, allow_redirects=False)
  if redirect_response.status_code != 302:
    raise ValueError(
      f"Expected 302 redirect, got {redirect_response.status_code}")
  if redirect_response.headers.get("Location") != target_url:
    raise ValueError(
        f"Unexpected redirect target {redirect_response.headers.get('Location')}"
    )


def main() -> int:
  parser = argparse.ArgumentParser(description="Check link-shortener routes")
  parser.add_argument("base_url", nargs="?", default="http://localhost:8000")
  args = parser.parse_args()

  wait_for_ping(args.base_url)
  check_shortener(args.base_url)
  print(f"Routes healthy at {args.base_url}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
