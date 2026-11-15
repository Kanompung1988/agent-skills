---
name: argo-rollouts-analysis-audit
description: Review local Argo Rollouts AnalysisTemplate/ClusterAnalysisTemplate metric thresholds and Rollout references for missing templates, disabled failure/success limits, absent conditions, duplicate metrics and missing args. Use before canary or blue-green progressive delivery; offline static analysis, not live traffic validation.
license: MIT
compatibility: Python 3.10+, PyYAML 6; local argoproj.io/v1alpha1 rendered YAML only; no cluster access.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Argo Rollouts analysis threshold review

## Trigger / non-trigger
Use on Argo Rollouts manifest changes that introduce or change canary/blue-green analysis metrics or template references. Do not use as a replacement for real AnalysisRuns, CEL expression evaluation, metric-provider probes or controller-version tests.

## Procedure
1. Export the Rollout plus **all relevant AnalysisTemplates and ClusterAnalysisTemplates** to local YAML files. Missing local references are scope warnings, not evidence they are absent from the cluster.
2. Install `PyYAML>=6,<7` and run `python scripts/audit.py examples/review.yaml --json` or a directory of rendered manifests; no kubeconfig needed.
3. Inspect AR001/AR002: a metric with neither condition can be Inconclusive; `failureLimit: -1` and `consecutiveSuccessLimit: 0` disables both gates. Confirm your controller supports consecutiveSuccessLimit (introduced in Argo Rollouts 1.8).
4. Review AR003–AR006 for invalid limits/count/provider and duplicate metric names; AR007–AR008 for referenced templates or required args absent from the input set; AR010–AR014 for blank expressions, duplicate templates, empty metrics or out-of-bounds startingStep.
5. Manually validate success/failure CEL against representative samples, metric provider permissions/behavior, rollback policy and actual AnalysisRuns. This tool **does not** evaluate conditions or send metrics.
6. Run unit tests and safe/review fixtures; report input scope and remaining unknowns, not “production safe.”

Exit 0 = no findings in provided bundle; 1 = review findings; 2 = invalid input. [Rules](references/REFERENCE.md) · [Primary docs](references/SOURCES.md).
