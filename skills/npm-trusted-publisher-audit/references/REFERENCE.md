# Static analysis rules

| Rule | Interpretation | Manual verification |
|---|---|---|
| NPM_ID_TOKEN_MISSING | Effective publish job permission lacks id-token write | Check job/workflow permissions |
| NPM_UNSUPPORTED_RUNNER | Publishing job selects self-hosted | Use eligible hosted runner |
| NPM_RUNNER_DYNAMIC | Runner expression cannot be resolved | Inspect actual matrix and labels |
| NPM_PR_PUBLISH_TRIGGER | Pull request event declared for publishing workflow | Confirm job conditions and trust |
| NPM_CALLER_IDENTITY | Reusable publishing workflow | Check npm configured calling workflow |
| NPM_TOKEN_FALLBACK | Token-like env keys on publishing path | Avoid redundant long-lived write token |
| NPM_PROVENANCE_DISABLED | Publish config disables provenance | Review intended provenance requirements |
| NPM_REPOSITORY_MISMATCH | Package metadata differs from local inventory | Inspect package repository URL |
| NPM_WORKFLOW_MISMATCH | Inventory workflow lacks direct publish step | Inspect real npm publisher settings |
| NPM_PUBLISHER_UNVERIFIED | Local inventory absent | Check npm trusted publisher settings manually |
| NPM_NO_PUBLISH_JOB | No directly recognized npm publish invocation | Inspect wrappers and composite actions |

Limitations: not an npm OIDC exchange, provenance verification or exhaustive GitHub Actions interpreter.
