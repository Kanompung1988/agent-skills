# Scope and references

- [gitsubmodules](https://git-scm.com/docs/gitsubmodules): superproject gitlinks contain pinned submodule commit IDs.
- [gitmodules](https://git-scm.com/docs/gitmodules): source URLs, unique paths, optional branch and update behavior.
- [git-submodule](https://git-scm.com/docs/git-submodule): `--remote` opts into upstream tracking; normal `update` uses the pinned gitlink.
- Reads **staged index** and `git show :.gitmodules` not untracked working-tree edits. Stage changes first. Does not verify cryptographic signatures, remote ownership, external availability, remote branch tips or nested submodules. Review GitHub PR commit/URL changes manually.
