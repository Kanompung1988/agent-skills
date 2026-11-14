import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit import analyze, load, main, InputError

def attr(key,value="redacted"):
    return {"key":key,"value":{"stringValue":value}}

def span(*keys,kind=2):
    return {"kind":kind,"attributes":[attr(k) for k in keys]}

class AuditTests(unittest.TestCase):
    def rules(self,payload,mode="unknown"):
        return [f["rule"] for f in analyze(payload,mode)["findings"]]
    def test_stable_clean(self):
        p={"spans":[span("http.request.method","http.response.status_code","http.route")]}
        self.assertEqual(self.rules(p),[])
    def test_otlp_resource_spans(self):
        p={"resourceSpans":[{"scopeSpans":[{"spans":[span("http.request.method")]}]}]}
        self.assertEqual(analyze(p)["total_spans"],1)
    def test_old_http_method(self):
        self.assertIn("OTEL_HTTP_LEGACY_KEYS",self.rules({"spans":[span("http.method")]}))
    def test_old_status(self):
        self.assertIn("OTEL_HTTP_LEGACY_KEYS",self.rules({"spans":[span("http.status_code")]}))
    def test_old_target(self):
        self.assertIn("OTEL_HTTP_LEGACY_KEYS",self.rules({"spans":[span("http.target")]}))
    def test_old_url(self):
        self.assertIn("OTEL_HTTP_LEGACY_KEYS",self.rules({"spans":[span("http.url")]}))
    def test_dual_emission(self):
        self.assertIn("OTEL_HTTP_DUAL_EMISSION",self.rules({"spans":[span("http.method","http.request.method")]}))
    def test_dup_mode_suppresses_expected_dual(self):
        self.assertEqual(self.rules({"spans":[span("http.method","http.request.method")]},"http/dup"),[])
    def test_stable_only_conflict(self):
        self.assertIn("OTEL_HTTP_OPT_IN_CONFLICT",self.rules({"spans":[span("http.method")]},"http"))
    def test_http_mode_clean_stable(self):
        self.assertEqual(self.rules({"spans":[span("http.request.method")]},"http"),[])
    def test_uuid_in_route(self):
        p={"spans":[{"attributes":[attr("http.route","/users/123e4567-e89b-12d3-a456-426614174000")]}]}
        self.assertIn("OTEL_HTTP_ROUTE_CARDINALITY",self.rules(p))
    def test_numeric_segment(self):
        p={"spans":[{"attributes":[attr("http.route","/users/1234567")]}]}
        self.assertIn("OTEL_HTTP_ROUTE_CARDINALITY",self.rules(p))
    def test_route_template_safe(self):
        p={"spans":[{"attributes":[attr("http.route","/users/{id}")]}]}
        self.assertEqual(self.rules(p),[])
    def test_attribute_values_never_emitted(self):
        p={"spans":[{"attributes":[attr("http.url","https://secret-token.example/private")]}]}
        self.assertNotIn("secret-token",json.dumps(analyze(p)))
    def test_non_http_ignored(self):
        p={"spans":[span("db.system","db.name")]}
        self.assertEqual(analyze(p)["http_spans"],0)
    def test_mapping_attributes(self):
        p={"spans":[{"attributes":{"http.method":"GET"}}]}
        self.assertIn("OTEL_HTTP_LEGACY_KEYS",self.rules(p))
    def test_invalid_root(self):
        with self.assertRaises(InputError): analyze([])
    def test_invalid_schema(self):
        with self.assertRaises(InputError): analyze({"spans":"wrong"})
    def test_invalid_attributes(self):
        with self.assertRaises(InputError): analyze({"spans":[{"attributes":[{"bad":1}]}]})
    def test_invalid_mode(self):
        with self.assertRaises(InputError): analyze({"spans":[]},"invalid")
    def test_file_and_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"spans.json"
            p.write_text(json.dumps({"spans":[span("http.request.method")]}))
            self.assertEqual(main([str(p),"--json"]),0)
            self.assertEqual(load(p)["spans"][0]["kind"],2)
    def test_cli_review_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"spans.json"
            p.write_text(json.dumps({"spans":[span("http.method")]}))
            self.assertEqual(main([str(p),"--json"]),1)
    def test_symlink_file_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"input.json"
            p.write_text("{}")
            link=Path(temp)/"alias.json"
            link.symlink_to(p)
            with self.assertRaises(InputError): load(link)
    def test_large_span_cap(self):
        with self.assertRaises(InputError): analyze({"spans":[{}]*10001})

if __name__=="__main__":
    unittest.main()
