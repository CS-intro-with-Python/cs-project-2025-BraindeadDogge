import argparse
import time

import requests


def wait_for_test(base_url: str, timeout: float = 15.0, interval: float = 0.5) -> None:
    deadline = time.time() + timeout
    url = f"{base_url.rstrip('/')}/test"
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(interval)
    raise TimeoutError(f"Timed out waiting for {url}")


def check_ping(base_url: str) -> None:
    url = f"{base_url.rstrip('/')}/ping"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    payload = response.json()
    if payload.get("data") != "pooong":
        raise ValueError(f"Unexpected ping payload: {payload}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check link-shortener routes")
    parser.add_argument("base_url", nargs="?", default="http://localhost:8000")
    args = parser.parse_args()

    wait_for_test(args.base_url)
    check_ping(args.base_url)
    print(f"Routes healthy at {args.base_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
