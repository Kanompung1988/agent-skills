import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pg_auditor', BASE/'scripts/audit.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class PGTests(unittest.TestCase):
    def codes(self, sql): return [f['code'] for f in a.audit_sql(sql)]
    def test_missing_search_path(self): self.assertIn('MISSING_SEARCH_PATH',self.codes('CREATE FUNCTION a() RETURNS int SECURITY DEFINER LANGUAGE sql AS $$ SELECT 1; $$;'))
    def test_safe_search_path(self): self.assertEqual([],self.codes('CREATE FUNCTION a() RETURNS int AS $$SELECT 1;$$ LANGUAGE sql SECURITY DEFINER SET search_path = admin, pg_temp;'))
    def test_pg_temp_missing(self): self.assertIn('PG_TEMP_MISSING',self.codes('CREATE FUNCTION a() RETURNS int SECURITY DEFINER SET search_path = admin AS $$SELECT 1$$ LANGUAGE sql;'))
    def test_pg_temp_bad_order(self): self.assertIn('PG_TEMP_ORDER',self.codes('CREATE FUNCTION a() RETURNS int SECURITY DEFINER SET search_path = pg_temp, admin AS $$SELECT 1$$ LANGUAGE sql;'))
    def test_public_schema(self): self.assertIn('UNTRUSTED_SCHEMA_REVIEW',self.codes('CREATE FUNCTION a() RETURNS int SECURITY DEFINER SET search_path = public, pg_temp AS $$SELECT 1$$ LANGUAGE sql;'))
    def test_user_schema(self): self.assertIn('UNRESOLVED_SEARCH_PATH',self.codes('CREATE FUNCTION a() RETURNS int SECURITY DEFINER SET search_path = "$user", pg_temp AS $$SELECT 1$$ LANGUAGE sql;'))
    def test_security_invoker_ignored(self): self.assertEqual([],self.codes('CREATE FUNCTION a() RETURNS int SECURITY INVOKER AS $$SELECT 1$$ LANGUAGE sql;'))
    def test_regular_function_ignored(self): self.assertEqual([],self.codes('CREATE FUNCTION a() RETURNS int AS $$SELECT 1$$ LANGUAGE sql;'))
    def test_function_in_comment_ignored(self): self.assertEqual([],self.codes('-- CREATE FUNCTION a() RETURNS int SECURITY DEFINER;'))
    def test_comment_block(self): self.assertEqual([],self.codes('/* CREATE FUNCTION a() RETURNS int SECURITY DEFINER; */'))
    def test_nested_comment(self): self.assertEqual([],self.codes('/* foo /* CREATE FUNCTION a() RETURNS int SECURITY DEFINER; */ */'))
    def test_body_keyword_not_security(self): self.assertEqual([],self.codes('CREATE FUNCTION a() RETURNS text LANGUAGE sql AS $$SELECT \'SECURITY DEFINER\';$$;'))
    def test_body_keyword_not_searchpath(self): self.assertIn('MISSING_SEARCH_PATH',self.codes('CREATE FUNCTION a() RETURNS text SECURITY DEFINER AS $$ SELECT \'SET search_path = admin, pg_temp\'; $$ LANGUAGE sql;'))
    def test_dollar_tagged_body(self): self.assertIn('MISSING_SEARCH_PATH',self.codes('CREATE FUNCTION a() RETURNS int SECURITY DEFINER AS $body$ SELECT 1; SELECT 2; $body$ LANGUAGE sql;'))
    def test_procedure(self): self.assertIn('MISSING_SEARCH_PATH',self.codes('CREATE PROCEDURE x() SECURITY DEFINER AS $$BEGIN NULL; END$$ LANGUAGE plpgsql;'))
    def test_multiple_functions(self): self.assertEqual(2, len(a.audit_sql('CREATE FUNCTION a() RETURNS int SECURITY DEFINER AS $$SELECT 1$$ LANGUAGE sql; CREATE FUNCTION b() RETURNS int SECURITY DEFINER AS $$SELECT 2$$ LANGUAGE sql;')))
    def test_multiline_line_numbers(self): self.assertEqual(3, a.audit_sql('\n\nCREATE FUNCTION a() RETURNS int SECURITY DEFINER AS $$SELECT 1$$ LANGUAGE sql;')[0]['line'])
    def test_or_replace(self): self.assertIn('MISSING_SEARCH_PATH',self.codes('CREATE OR REPLACE FUNCTION test() RETURNS int SECURITY DEFINER AS $$SELECT 1$$ LANGUAGE sql;'))
    def test_from_current(self): self.assertIn('UNRESOLVED_SEARCH_PATH',self.codes('CREATE FUNCTION a() RETURNS int SECURITY DEFINER SET search_path FROM CURRENT AS $$SELECT 1$$ LANGUAGE sql;'))
    def test_all_quoted(self): self.assertIn('UNRESOLVED_SEARCH_PATH',self.codes('CREATE FUNCTION a() RETURNS int SECURITY DEFINER SET search_path = "trusted", pg_temp AS $$SELECT 1$$ LANGUAGE sql;'))
    def test_works_with_language_before_security(self): self.assertEqual([],self.codes('CREATE FUNCTION a() RETURNS int AS $$SELECT 1$$ LANGUAGE sql SECURITY DEFINER SET search_path TO admin, pg_temp;'))
    def test_cli_safe(self):
        r=subprocess.run([sys.executable,str(BASE/'scripts/audit.py'),str(BASE/'fixtures/safe.sql'),'--strict'],capture_output=True,text=True)
        self.assertEqual(0,r.returncode,r.stderr)
    def test_cli_review(self):
        r=subprocess.run([sys.executable,str(BASE/'scripts/audit.py'),str(BASE/'fixtures/review.sql'),'--strict','--format','json'],capture_output=True,text=True)
        self.assertEqual(2,r.returncode,r.stderr); self.assertTrue(json.loads(r.stdout)['count']>=2)
    def test_unreadable_path(self):
        r=subprocess.run([sys.executable,str(BASE/'scripts/audit.py'),'missing.sql'],capture_output=True,text=True)
        self.assertEqual(1,r.returncode)
    def test_deterministic(self):
        src='CREATE FUNCTION z() RETURNS int SECURITY DEFINER AS $$SELECT 1$$ LANGUAGE sql;'
        self.assertEqual(a.audit_sql(src),a.audit_sql(src))

if __name__=='__main__': unittest.main()
