# Evidence, semantics and limits

Primary source: [PostgreSQL CREATE FUNCTION — Writing SECURITY DEFINER Functions Safely](https://www.postgresql.org/docs/current/sql-createfunction.html).

PostgreSQL recommends setting a privileged function's `search_path` to trusted schemas, and explicitly appending `pg_temp` **last**. A malicious object in a schema writable by an untrusted role could otherwise shadow the intended object. Routine ownership, schema privileges and default `PUBLIC` function execute permissions must be reviewed separately.

Finding codes:
- `MISSING_SEARCH_PATH` (high): no function-level `SET search_path` found in the parsed CREATE statement.
- `PG_TEMP_MISSING` (review): no explicit `pg_temp` in a simple path.
- `PG_TEMP_ORDER` (review): explicit `pg_temp` is not last.
- `UNTRUSTED_SCHEMA_REVIEW` (review): simple path uses `public` or `$user`; actual trust depends on schema ACLs.
- `UNRESOLVED_SEARCH_PATH` (review): path cannot be confidently parsed, including `FROM CURRENT` and quoted schema identifiers.

**Limits:** This is a conservative lexical review, not a PostgreSQL parser. It recognizes `CREATE [OR REPLACE] FUNCTION/PROCEDURE` statements and masks SQL comments, string literals and dollar-quoted bodies before inspecting routine-level clauses. It cannot reliably validate all PostgreSQL grammar, `ALTER FUNCTION` changes, dynamic SQL, extension scripts, ACLs, schema existence, execution privilege defaults or current database configuration. Verify all suggested changes against your actual PostgreSQL version and application.
