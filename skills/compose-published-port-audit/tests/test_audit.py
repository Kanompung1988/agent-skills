import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('compose_auditor', BASE / 'scripts/audit.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class PortTests(unittest.TestCase):
    def check(self, port, code, **opts):
        docs = {'services': {'svc': {'ports': [port], **opts}}}
        actual = a.audit_compose(docs)
        self.assertIn(code, [v['code'] for v in actual])

    def test_explicit_wildcard_ipv4(self): self.check('0.0.0.0:8080:80', 'WILDCARD_HOST_BIND')
    def test_explicit_wildcard_ipv6(self): self.check('[::]:8080:80', 'WILDCARD_HOST_BIND')
    def test_unset_ip(self): self.check('8080:80', 'DEFAULT_HOST_BIND')
    def test_ephemeral_host_port(self): self.check('80', 'DEFAULT_HOST_BIND')
    def test_integer_container_port(self): self.check(80, 'DEFAULT_HOST_BIND')
    def test_loopback_ip(self): self.assertEqual([], a.audit_compose({'services':{'x':{'ports':['127.0.0.1:1234:80']}}}))
    def test_loopback_ipv6(self): self.assertEqual([], a.audit_compose({'services':{'x':{'ports':['[::1]:1234:80']}}}))
    def test_external_ip(self): self.check('192.0.2.22:443:443', 'NON_LOOPBACK_BIND')
    def test_dynamic_ip(self): self.check('${BIND_IP}:8080:80', 'PORT_SYNTAX_REVIEW')
    def test_port_range(self): self.check('5000-5002:80-82', 'DEFAULT_HOST_BIND')
    def test_udp(self): self.check('3000:3000/udp', 'DEFAULT_HOST_BIND')
    def test_bad_protocol(self): self.check('3000:3000/ftp', 'PORT_SYNTAX_REVIEW')
    def test_bad_syntax(self): self.check('foo:bar:baz', 'PORT_SYNTAX_REVIEW')
    def test_long_unset(self): self.check({'target':80,'published':8080}, 'DEFAULT_HOST_BIND')
    def test_long_wildcard(self): self.check({'target':80,'host_ip':'0.0.0.0'}, 'WILDCARD_HOST_BIND')
    def test_long_loopback(self): self.assertEqual([], a.audit_compose({'services':{'x':{'ports':[{'target':80,'host_ip':'127.0.0.1'}]}}}))
    def test_long_bad_mode(self): self.check({'target':80,'mode':'what'}, 'PORT_SYNTAX_REVIEW')
    def test_long_no_target(self): self.check({'host_ip':'0.0.0.0'}, 'PORT_SYNTAX_REVIEW')
    def test_expose_only(self): self.assertEqual([], a.audit_compose({'services':{'x':{'expose':['80']}}}))
    def test_host_network(self): self.assertEqual('HOST_NETWORK', a.audit_compose({'services':{'x':{'network_mode':'host'}}})[0]['code'])
    def test_invalid_services(self):
        with self.assertRaises(ValueError): a.audit_compose({'services':[]})
    def test_invalid_ports(self): self.assertEqual('PORTS_INVALID', a.audit_compose({'services':{'x':{'ports':'80'}}})[0]['code'])
    def test_invalid_doc(self):
        with self.assertRaises(ValueError): a.audit_compose(None)
    def test_deterministic_order(self):
        docs={'services':{'z':{'ports':['80']}, 'a':{'ports':['90']}}}
        self.assertEqual(['a','z'],[x['service'] for x in a.audit_compose(docs)])
    def test_safe_cli(self):
        p=subprocess.run([sys.executable,str(BASE/'scripts/audit.py'), str(BASE/'fixtures/safe.yaml'), '--strict'],capture_output=True,text=True)
        self.assertEqual(0,p.returncode,p.stderr)
    def test_review_cli(self):
        p=subprocess.run([sys.executable,str(BASE/'scripts/audit.py'), str(BASE/'fixtures/review.yaml'), '--strict','--format','json'],capture_output=True,text=True)
        self.assertEqual(2,p.returncode,p.stderr)
        self.assertTrue(json.loads(p.stdout)['count']>=2)
    def test_unknown_input_error(self):
        p=subprocess.run([sys.executable,str(BASE/'scripts/audit.py'), 'does-not-exist.yaml'],capture_output=True,text=True)
        self.assertEqual(1,p.returncode)

if __name__ == '__main__': unittest.main()
