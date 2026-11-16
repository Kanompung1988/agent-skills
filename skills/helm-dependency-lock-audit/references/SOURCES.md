# Primary sources

- Helm dependency build (lock vs update): https://helm.sh/docs/helm/helm_dependency_build/
- Chart.yaml dependencies, version ranges and repository alias syntax: https://helm.sh/docs/topics/charts/
- Agent Skills specification: https://agentskills.io/specification

This static checker does not execute Helm, calculate the Helm-generated chart dependency digest or evaluate semantic version ranges. Run `helm dependency build` for actual project checks.
