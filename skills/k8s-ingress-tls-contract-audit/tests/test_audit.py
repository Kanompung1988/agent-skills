import importlib.util
import tempfile
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('audit',Path(__file__).resolve().parents[1]/'scripts/audit.py')
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

ING="""apiVersion: networking.k8s.io/v1\nkind: Ingress\nmetadata:\n  name: web\n  namespace: prod\nspec:\n  tls:\n    - hosts: [example.com]\n      secretName: web-tls\n  rules:\n    - host: example.com\n"""
SECRET="""apiVersion: v1\nkind: Secret\nmetadata:\n  name: web-tls\n  namespace: prod\ntype: kubernetes.io/tls\ndata:\n  tls.crt: ZmFrZQ==\n  tls.key: ZmFrZQ==\n"""

class TestAudit(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)
    def check(self,ing=ING,sec=SECRET):
        (self.p/'test.yml').write_text(ing+'\n---\n'+sec)
        return audit.inspect([self.p])
    def codes(self,ing=ING,sec=SECRET):return {x['code'] for x in self.check(ing,sec)}
    def test_safe(self):self.assertEqual([],self.check())
    def test_secret_absent_in_batch_review(self):self.assertIn('UNRESOLVED_SECRET',self.codes(sec=''))
    def test_wrong_secret_type(self):self.assertIn('SECRET_TYPE',self.codes(sec=SECRET.replace('kubernetes.io/tls','Opaque')))
    def test_missing_key(self):self.assertIn('SECRET_KEY',self.codes(sec=SECRET.replace('  tls.key: ZmFrZQ==\n','')))
    def test_string_data(self):self.assertEqual([],self.check(sec=SECRET.replace('\ndata:', '\nstringData:')))
    def test_namespace_isolation(self):self.assertIn('UNRESOLVED_SECRET',self.codes(sec=SECRET.replace('namespace: prod','namespace: other')))
    def test_tls_host_no_rule(self):self.assertIn('TLS_HOST_WITHOUT_RULE',self.codes(ing=ING.replace('host: example.com','host: other.example.com')))
    def test_uncovered_rule(self):self.assertIn('RULE_NOT_IN_TLS',self.codes(ing=ING.replace('    - host: example.com','    - host: other.example.com')))
    def test_duplicate_host(self):self.assertIn('DUPLICATE_TLS_HOST',self.codes(ing=ING.replace('hosts: [example.com]','hosts: [example.com, example.com]')))
    def test_optional_secret(self):self.assertIn('NO_SECRET_NAME',self.codes(ing=ING.replace('      secretName: web-tls\n','')))
    def test_no_tls_valid(self):self.assertEqual([],self.check(ing=ING.replace('  tls:\n    - hosts: [example.com]\n      secretName: web-tls\n','')))
    def test_ignore_other_kind(self):self.assertEqual([],self.check(ing=ING.replace('kind: Ingress','kind: Deployment')))
    def test_unsupported_api(self):self.assertEqual([],self.check(ing=ING.replace('networking.k8s.io/v1','extensions/v1beta1')))
    def test_casefold_hosts(self):self.assertEqual([],self.check(ing=ING.replace('hosts: [example.com]','hosts: [EXAMPLE.COM]')))
    def test_empty_docs(self):self.assertEqual([],self.check(ing='',sec=''))
    def test_malformed_yaml(self):
        (self.p/'broken.yml').write_text('test: [oops')
        with self.assertRaises(ValueError):audit.inspect([self.p])
    def test_nonmapping_document(self):self.assertIn('INVALID_DOCUMENT',self.codes(ing='[abc]',sec=''))
    def test_nonmapping_tls(self):self.assertIn('INVALID_TLS',self.codes(ing=ING.replace('    - hosts: [example.com]\n      secretName: web-tls','    - wrong'),sec=''))
    def test_large_file(self):
        (self.p/'large.yml').write_text('a'*1_000_001)
        with self.assertRaises(ValueError):audit.inspect([self.p])
    def test_fail_on_exit(self):
        (self.p/'source.yml').write_text(ING+'\n---\n'+SECRET)
        self.assertEqual(0,audit.main([str(self.p),'--json']))
        (self.p/'source.yml').write_text(ING+'\n---\n'+SECRET.replace('kubernetes.io/tls','Opaque'))
        self.assertEqual(2,audit.main([str(self.p),'--json']))
        self.assertEqual(0,audit.main([str(self.p),'--fail-on','never']))

if __name__=='__main__':unittest.main()
