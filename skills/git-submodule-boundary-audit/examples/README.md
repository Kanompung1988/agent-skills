# Offline fixture construction

The unit tests use `git init`, a staged `.gitmodules` file and an index `160000` gitlink using `git update-index --cacheinfo`. No network or nested repository is required. To inspect your own checkout, run `python scripts/audit.py . --json` after staging intended `.gitmodules` changes.
