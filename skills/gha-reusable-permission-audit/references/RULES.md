# Reusable caller boundary checks

GRP001 review: external called workflow uses mutable branch/tag rather than full SHA.
GRP002 high: `secrets: inherit` passed to an external called workflow.
GRP003 review: no explicit caller token permission (actual default depends on repository settings).
GRP004 high: `write-all` token permissions.
GRP005 review: elevated explicit write token scopes.
GRP006 review: malformed local/external reusable call or permissions syntax.
GRP007 review: explicit named secret mappings to external caller; names/values are never emitted.
GRP008 high: `pull_request_target` combined with broad token or inherited secrets.

This is one local YAML and does not fetch callee or GitHub repo settings; a clean result is not an authorization guarantee. Primary sources: https://docs.github.com/en/actions/how-tos/sharing-automations/reusing-workflows and https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication.
