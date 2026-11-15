# Rule reference

| Code | Finding | Interpretation |
|---|---|---|
| AR001 | Neither metric success nor failure condition defined | May produce Inconclusive, sometimes intentional |
| AR002 | failureLimit=-1 and consecutiveSuccessLimit=0 | Both threshold gates disabled |
| AR003 | Limits invalid integer or out of range | Correct failureLimit>=-1, consecutiveSuccessLimit>=0 |
| AR004 | Provider missing or multiple provider types | Exactly one provider is expected |
| AR005 | Invalid metric count | Count must be non-negative; zero behaves differently for inline vs background analysis |
| AR006 | Duplicate metric names in one template | Choose unique names |
| AR007 | Referenced template absent from provided set | Verify separately in cluster/bundle |
| AR008 | Required template args not supplied | Provide args or defaults |
| AR009 | Metric name absent | Name metrics |
| AR010 | Condition blank/nonstring | Validate expression manually |
| AR011 | Duplicate template identity in supplied manifests | Deduplicate rendered templates |
| AR012 | Template has no metrics | Review intentional empty analysis |
| AR013 | Canary startingStep outside declared steps | Use zero-based index in steps |
| AR014 | Missing templateName | Fix reference |

The analyzer is not a CEL interpreter, controller simulation or safety certification. `consecutiveSuccessLimit` requires Argo Rollouts v1.8+. Runtime failureLimit rules and conditions can produce Inconclusive states, and multiple templates may be merged at runtime. Cross-namespace references are not supported by this static scope.
