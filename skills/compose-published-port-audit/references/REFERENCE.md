# Evidence, semantics and limits

Primary source: [Docker port publishing](https://docs.docker.com/engine/network/port-publishing/) and [Compose ports reference](https://docs.docker.com/reference/compose-file/services/#ports).

- Explicit `0.0.0.0` / `::`: `WILDCARD_HOST_BIND` (high). Publishing to all host addresses is often broader than intended.
- Missing `host_ip`: `DEFAULT_HOST_BIND` (review); defaults can be controlled by daemon/network configuration. This is **not** proof of exposure on the machine.
- Explicit non-loopback interface: `NON_LOOPBACK_BIND` (review). Includes private addresses; not automatically internet-facing.
- Dynamic or invalid mapping: `PORT_SYNTAX_REVIEW` / `DYNAMIC_HOST_BIND` (review). The tool intentionally does not interpolate environment expressions.
- `network_mode: host`: manual review. It is not a normal published mapping.
- `expose` alone: no host port published; the tool omits it.

This tool does not run `docker compose config`, interpret profiles/overrides/extends, inspect deployment mode, Swarm, operating system firewalls, reverse proxies, IPv6 routing, or daemon state. YAML anchors are parsed through PyYAML; custom tags are rejected. Do not provide live secrets.
