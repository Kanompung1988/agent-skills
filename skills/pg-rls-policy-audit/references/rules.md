# Evidence, rule semantics and boundaries

## What is checked
Conservative token masking for strings, comments, dollar-quotes; DDL recognition for ALTER TABLE ENABLE/DISABLE/FORCE/NO FORCE and CREATE POLICY; review TO PUBLIC, literal USING(true), WITH CHECK(true), missing enable in supplied SQL, owner bypass and policy absence in supplied SQL.

## What is not checked
Only supplied DDL is checked; no catalog access, GRANT, BYPASSRLS, actual owner/role membership, ALTER POLICY, SQL execution, runtime policy evaluation, multi-file ordering or full PostgreSQL SQL grammar. Not shown in input does not mean missing in production.

A static finding is a request for human review, not automatically a defect.

## Primary documentation
1. https://www.postgresql.org/docs/current/ddl-rowsecurity.html
2. https://www.postgresql.org/docs/current/sql-createpolicy.html
3. https://www.postgresql.org/docs/current/sql-altertable.html
