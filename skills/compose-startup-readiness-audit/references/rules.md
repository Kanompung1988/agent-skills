# Detection scope and attribution

Primary source: Docker Compose services reference https://docs.docker.com/reference/compose-file/services/ and startup ordering https://docs.docker.com/compose/how-tos/startup-order/ .

- `depends_on` short syntax or `condition: service_started` is startup ordering only, not readiness validation (`STARTED_NOT_READY`, review).
- `service_healthy` requires an enabled dependency healthcheck (`MISSING_HEALTHCHECK`, error).
- Unknown condition, undefined dependency, invalid shapes, and cycles are errors.
- `service_completed_successfully` combined with `restart: always` or `unless-stopped` is a review signal, not a definitive validation failure.
- `required: false` is a deliberate option but can permit startup with missing services; review its business logic.
- Healthcheck durations use an intentionally limited Compose duration heuristic. False positives are possible with interpolation and extensions.
- Multi-file Compose merges, variable interpolation, profiles, overrides and runtime image-defined healthchecks are **not** resolved; findings must be verified against fully rendered Compose config for release decisions.
