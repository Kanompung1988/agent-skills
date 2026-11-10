---
name: gha-concurrency-collision-audit
description: Audit GitHub Actions YAML concurrency groups offline for cross-workflow collisions, release cancellation, head_ref fallback and queue configuration conflicts. Use before CI/CD changes; not a live runner-state checker.
license: MIT
compatibility: Python 3.10+ with PyYAML 6.0.2; no GitHub token required.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# GitHub Actions concurrency review

Use to analyze authorized workflow YAML before changing CI, especially production deployments. Do not treat static findings as actual observed cancellations.

1. Gather the relevant .github/workflows YAML files (scan whole directory to reveal cross-workflow collisions).
2. Install dependency with `python -m pip install -r requirements.txt` and run `python scripts/audit.py .github/workflows --json`.
3. Review CC001–CC009 in `references/REFERENCE.md` and compare suspected collisions with expected run paths.
4. Never evaluate arbitrary GitHub expressions or auto-edit workflows. Seek owner review before changing release locks.
5. Test with `python -m unittest discover -s tests -v` and `examples/` fixtures.

Exit status: 0 clean static checks, 1 findings, 2 invalid input. Scope limitations in README.
