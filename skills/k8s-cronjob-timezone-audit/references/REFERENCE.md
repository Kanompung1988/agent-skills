# CronJob review rules

| Code | Meaning | Disposition |
|---|---|---|
| CJ001 | Schedule is not a five-token expression | Review; **macros such as @hourly are not supported by this bounded checker** |
| CJ002 | TZ/CRON_TZ embedded in schedule | Kubernetes rejects these; use `spec.timeZone` |
| CJ003 | Missing timezone | Controller-manager local zone is used; prefer explicit zone |
| CJ004 | Invalid/unknown timezone input | Host IANA tzdata used as best-effort check |
| CJ005 | Zone has seasonal offset change | Human review of DST gaps/duplicates; not a cron simulator |
| CJ006 | Deadline has invalid type/range | Review configuration |
| CJ007 | Deadline under 10 seconds | Scheduler may miss execution |
| CJ008 | Unsupported concurrency policy | Review manifest |
| CJ009 | Replace potentially stops active job | Confirm job is interruption-safe |
| CJ010 | Forbid with no deadline | Explicitly decide long-running overlap behavior |
| CJ011 | No failed-job history | Confirm alternate observability |
| CJ012 | Suspended job | Check expected operational state |

No live CronJob state, cluster timezone database, completed-job evidence, or cron expression evaluation is performed. A clean result does not prove correctness.
