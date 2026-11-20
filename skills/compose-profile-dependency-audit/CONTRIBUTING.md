# Contributing

1. Open an Issue with a small, sanitized YAML reproduction. Do not attach credentials or real secrets.
2. Add an isolated regression test and a fixture for every rule change.
3. Run `python -m pip install -r requirements.txt` and `python -m unittest discover -s tests -v`.
4. Run `python scripts/audit.py fixtures/safe.yaml --format json` (exit 0) and `python scripts/audit.py fixtures/review.yaml --format json` (exit 2).
5. Submit a pull request with the official reference and precise behavioral limitations.

Do not edit or redraw the original Area Zero logo.
