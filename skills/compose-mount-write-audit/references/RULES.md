# Rule boundaries

* CMW001 high — Docker socket mount even with :ro can expose Docker API.
* CMW002 high — writable sensitive host source or container destination.
* CMW003 review — host bind defaults writable unless :ro/long read_only.
* CMW005 review — ambiguous mount syntax or unresolved variable.
* CMW006 review — inherited volumes_from not expanded.

Root filesystem read_only is not automatically applied to bind mounts. Static review only, no Compose multi-file merge, include, interpolation, profile selection, symlinks or Docker runtime checks. Primary sources: https://docs.docker.com/reference/compose-file/services/ and https://docs.docker.com/engine/storage/bind-mounts/.
