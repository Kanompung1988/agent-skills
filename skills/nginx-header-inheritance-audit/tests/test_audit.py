import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit import audit_text, main, parse, tokenize

def rules(text, version=None):
    return [item["rule"] for item in audit_text(text, version)]

class NginxAuditTests(unittest.TestCase):
    def test_empty(self): self.assertEqual([], rules(""))
    def test_comment(self): self.assertEqual([], rules("# add_header Fake yes;\n"))
    def test_quotes_and_semicolon(self):
        self.assertEqual([], rules('http { add_header X-Test "value; with spaces" always; }'))
    def test_security_missing_always(self):
        self.assertEqual(["NGH002"], rules("http { add_header X-Frame-Options DENY; }"))
    def test_safe_always(self):
        self.assertEqual([], rules("http { add_header X-Frame-Options DENY always; }"))
    def test_nested_inheritance(self):
        text="http { add_header Strict-Transport-Security max-age=1 always; server { location / { add_header X-Foo bar; } } }"
        self.assertEqual(["NGH001"], rules(text))
    def test_no_loss_when_redeclared(self):
        text="http { add_header X-Frame-Options DENY always; server { add_header X-Frame-Options SAMEORIGIN always; } }"
        self.assertEqual([], rules(text))
    def test_lost_specific_only(self):
        text="http { add_header X-Frame-Options DENY always; add_header X-Test ok; server { add_header X-Test new; } }"
        self.assertEqual(["NGH001"], rules(text))
    def test_merge(self):
        text="http { add_header X-Frame-Options DENY always; server { add_header_inherit merge; add_header X-Test ok; } }"
        self.assertEqual([], rules(text))
    def test_merge_inherited(self):
        text="http { add_header_inherit merge; add_header X-Frame-Options DENY always; server { location / { add_header X-Test ok; } } }"
        self.assertEqual([], rules(text))
    def test_off(self):
        text="http { add_header X-Frame-Options DENY always; server { add_header_inherit off; } }"
        self.assertEqual(["NGH001"], rules(text))
    def test_version_gate(self):
        text="http { add_header_inherit merge; }"
        self.assertEqual(["NGH005"], rules(text,(1,28,0)))
        self.assertEqual([], rules(text,(1,29,3)))
    def test_invalid_inherit(self):
        self.assertEqual(["NGH004"], rules("http { add_header_inherit blah; }"))
    def test_bad_shape(self):
        self.assertEqual(["NGH006"], rules("http { add_header X-Test; }"))
    def test_include(self):
        self.assertEqual(["NGH003"], rules("http { include /etc/nginx/conf.d/*.conf; }"))
    def test_missing_brace(self):
        with self.assertRaises(ValueError): parse("http { server {")
    def test_extra_brace(self):
        with self.assertRaises(ValueError): parse("}")
    def test_missing_semicolon(self):
        with self.assertRaises(ValueError): parse("add_header X-Test ok")
    def test_unclosed_quote(self):
        with self.assertRaises(ValueError): tokenize('add_header X-Test "bad;')
    def test_safe_fixture(self):
        p=Path(__file__).resolve().parents[1]/"examples/safe.conf"
        self.assertEqual(0, main([str(p)]))
    def test_review_fixture(self):
        p=Path(__file__).resolve().parents[1]/"examples/review.conf"
        self.assertEqual(1, main([str(p), "--json"]))
    def test_version_invalid(self):
        p=Path(__file__).resolve().parents[1]/"examples/safe.conf"
        self.assertEqual(2, main([str(p), "--nginx-version", "latest"]))
    def test_missing_path(self):
        self.assertEqual(2, main(["/unlikely/not/here.conf"]))
    def test_linenumbers(self):
        output=audit_text("\nhttp {\n  add_header X-Frame-Options DENY;\n}")
        self.assertEqual(3, output[0]["line"])
    def test_unknown_directive_ignored(self):
        self.assertEqual([], rules("events { worker_connections 128; }"))
    def test_escaped_hash(self):
        self.assertEqual([], rules(r"http { add_header X-Note a\#b always; }"))
if __name__=="__main__": unittest.main()
