# Docker Compose Profile Dependency Audit — evidence boundaries

The tool evaluates **hypothetical scenarios**: no active profile, each declared profile independently, and an optional requested invocation. A warning in an uninvoked scenario does not mean a real deployment is broken. `depends_on: {svc: {required: false}}` is not treated as a hard dependency. External `extends.file`, variables, service extensions, networks and multi-file merge are unresolved by design.

## Official documentation

- https://docs.docker.com/reference/compose-file/profiles/
- https://docs.docker.com/compose/how-tos/profiles/

## False-positive and false-negative limits

This is a conservative single-file local manifest reviewer. Values can be dynamic and multiple overrides/cluster-level policy/Compose service activation behavior may change observed effects. It is not a deploy-time gate by itself. Interpret review findings manually and test the actual effective system with native official tools.

Input files are parsed through PyYAML SafeLoader with duplicate-mapping-key rejection and a 2MB limit. No dynamic evaluation is performed.
