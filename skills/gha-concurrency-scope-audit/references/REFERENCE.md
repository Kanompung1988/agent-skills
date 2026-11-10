# Audit rules

| Code | Meaning |
|---|---|
| CC001 | Missing or invalid concurrency group/shape. |
| CC002 | Queue max conflicts with literal cancellation true. |
| CC003 | Release/deploy-named scope cancels in-progress work. |
| CC004 | Invalid cancel flag type. |
| CC005 | Unsupported queue value. |
| CC006 | Literal workflow group uses default single queue, potentially replacing pending runs. |
| CC007 | More than one inspected scope uses a casefold-identical literal group. |

All findings are static review candidates, not definite runtime errors. GitHub expressions are not evaluated; workflows must be supplied together for cross-file comparison. No API, secret reads or writes. Files larger than 2 MB and symlink paths are rejected. See official GitHub documentation before changing a pipeline.
