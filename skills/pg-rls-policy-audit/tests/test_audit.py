import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout
path = Path(__file__).resolve().parents[1] / 'scripts' / 'audit.py'
spec = importlib.util.spec_from_file_location('audit_module', path)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class RlsTests(unittest.TestCase):
    def codes(self, sql): return [x['code'] for x in a.audit(sql)]
    def test_empty(self): self.assertEqual(self.codes(''), [])
    def test_complete(self): self.assertEqual(self.codes("ALTER TABLE invoices ENABLE ROW LEVEL SECURITY; ALTER TABLE invoices FORCE ROW LEVEL SECURITY; CREATE POLICY tenant ON invoices TO tenant USING (tenant_id = current_setting('app.tenant_id'));"), [])
    def test_policy_no_enable(self): self.assertIn('ENABLE_NOT_SHOWN', self.codes('CREATE POLICY p ON invoices USING (tenant = 1);'))
    def test_owner_bypass(self): self.assertIn('OWNER_BYPASS_REVIEW', self.codes('ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;'))
    def test_force(self): self.assertNotIn('OWNER_BYPASS_REVIEW', self.codes('ALTER TABLE invoices ENABLE ROW LEVEL SECURITY; ALTER TABLE invoices FORCE ROW LEVEL SECURITY;'))
    def test_force_then_enable(self): self.assertNotIn('OWNER_BYPASS_REVIEW', self.codes('ALTER TABLE invoices FORCE ROW LEVEL SECURITY; ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;'))
    def test_no_force(self): self.assertIn('OWNER_BYPASS_REVIEW', self.codes('ALTER TABLE invoices FORCE ROW LEVEL SECURITY; ALTER TABLE invoices NO FORCE ROW LEVEL SECURITY; ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;'))
    def test_disable(self): self.assertIn('RLS_DISABLED', self.codes('ALTER TABLE invoices DISABLE ROW LEVEL SECURITY;'))
    def test_enable_no_policy(self): self.assertIn('NO_POLICY_IN_INPUT', self.codes('ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;'))
    def test_using_true(self): self.assertIn('UNRESTRICTED_USING', self.codes('CREATE POLICY p ON t USING (true);'))
    def test_check_true(self): self.assertIn('UNRESTRICTED_CHECK', self.codes('CREATE POLICY p ON t WITH CHECK (TRUE);'))
    def test_public(self): self.assertIn('PUBLIC_POLICY', self.codes('CREATE POLICY p ON t TO PUBLIC USING (id=1);'))
    def test_quoted_names(self): self.assertEqual(a.canonical('"Mixed.Schema"."My.Table"'), 'Mixed.Schema.My.Table')
    def test_quoted_table_policy(self): self.assertIn('UNRESTRICTED_USING', self.codes('CREATE POLICY "p1" ON "Mixed"."MyTable" USING (true);'))
    def test_schema(self): self.assertEqual(a.canonical('Public.Invoices'), 'public.invoices')
    def test_ignore_comment(self): self.assertEqual(self.codes('-- ALTER TABLE t DISABLE ROW LEVEL SECURITY;\n'), [])
    def test_ignore_block_comment(self): self.assertEqual(self.codes('/* CREATE POLICY p ON t USING (true); */'), [])
    def test_ignore_nested_block(self): self.assertEqual(self.codes('/* a /* b */ CREATE POLICY p ON t */'), [])
    def test_ignore_string_body(self): self.assertEqual(self.codes("SELECT 'CREATE POLICY p ON t USING (true);';"), [])
    def test_ignore_dollar_body(self): self.assertEqual(self.codes('DO $tag$ CREATE POLICY p ON t USING (true); $tag$;'), [])
    def test_split_sql(self): self.assertEqual(len(a.statements("select 'a;b'; select 1;")), 2)
    def test_line(self): self.assertEqual(a.audit('\n\nCREATE POLICY p ON t;')[0]['line'], 1)
    def test_multiline(self): self.assertIn('OWNER_BYPASS_REVIEW', self.codes('ALTER\nTABLE x\nENABLE ROW LEVEL SECURITY;'))
    def test_multiple_tables(self): self.assertIn('RLS_DISABLED', self.codes('ALTER TABLE a DISABLE ROW LEVEL SECURITY; ALTER TABLE b ENABLE ROW LEVEL SECURITY;'))
    def test_json_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.sql';p.write_text('ALTER TABLE a DISABLE ROW LEVEL SECURITY;')
            out=io.StringIO()
            with redirect_stdout(out): ret=a.main([str(p), '--json'])
            self.assertEqual(ret,1);self.assertEqual(json.loads(out.getvalue())['count'],1)
    def test_safe_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.sql';p.write_text('CREATE TABLE a(id int);')
            with redirect_stdout(io.StringIO()): ret=a.main([str(p)])
            self.assertEqual(ret,0)

if __name__ == '__main__': unittest.main()
