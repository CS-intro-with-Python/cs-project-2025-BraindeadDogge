## Tests

This directory contains helper utilities for automated checks. `tests/backend_client/check_routes.py` waits for `/ping` to come up, hits `/shorten`, and ensures the resulting short link redirects correctly during CI and local smoke tests.
