# Technical reference and boundaries

Primary source: https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
Workflow syntax: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

The analyzer supports only sibling workflow YAML files in `.github/workflows`. Literal scalar input type tests are conservative; dynamic GitHub expressions cannot be evaluated statically. `secrets: inherit` is allowed but does not prove required secrets exist. An omitted required input with a declared default is treated as fulfilled. Missing local files, remote references and complex YAML are not proof of runtime failure. `on` is preserved using PyYAML BaseLoader to avoid YAML 1.1 boolean coercion. File size capped at 1 MB each. No workflow is run, no GitHub API used, and no secret values read.
