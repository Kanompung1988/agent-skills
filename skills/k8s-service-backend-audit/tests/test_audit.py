import importlib.util
from pathlib import Path
import tempfile
import unittest

mod=importlib.util.spec_from_file_location("audit",Path(__file__).resolve().parents[1]/"scripts"/"audit.py")
a=importlib.util.module_from_spec(mod);mod.loader.exec_module(a)
def service(selector=None,target="http"):
    return {"kind":"Service","metadata":{"name":"api"},"spec":{"selector":{"app":"api"} if selector is None else selector,"ports":[{"port":80,"targetPort":target}]}}
def deploy(labels=None,ports=None):
    return {"kind":"Deployment","metadata":{"name":"api"},"spec":{"template":{"metadata":{"labels":{"app":"api"} if labels is None else labels},"spec":{"containers":[{"name":"api","ports":[{"name":x,"containerPort":8080} for x in (["http"] if ports is None else ports)]}]}}}}
def scan(*docs):
    return a.audit([("x.yaml",d) for d in docs])
def codes(*docs):
    return [x["code"] for x in scan(*docs)]

class Tests(unittest.TestCase):
    def test_safe(self):self.assertEqual(scan(deploy(),service()),[])
    def test_wrong_selector(self):self.assertEqual(codes(deploy(labels={"app":"web"}),service()),["SV002"])
    def test_namespace_boundary(self):
        d=deploy();d["metadata"]["namespace"]="prod"
        self.assertEqual(codes(d,service()),["SV002"])
    def test_named_target_missing(self):self.assertEqual(codes(deploy(ports=["web"]),service()),["SV003"])
    def test_numeric_port_no_declaration(self):self.assertEqual(scan(deploy(ports=[]),service(target=8080)),[])
    def test_implicit_target(self):
        s=service();del s["spec"]["ports"][0]["targetPort"]
        self.assertEqual(scan(deploy(ports=[]),s),[])
    def test_selectorless_valid(self):self.assertEqual(scan(service(selector={})),[])
    def test_externalname_valid(self):
        s=service();s["spec"]["type"]="ExternalName";s["spec"]["externalName"]="example.net"
        self.assertEqual(scan(s),[])
    def test_invalid_bool_selector(self):self.assertEqual(codes(service(selector={"app":True})),["SV001"])
    def test_invalid_bool_target(self):self.assertEqual(codes(deploy(),service(target=True)),["SV004"])
    def test_invalid_zero_target(self):self.assertEqual(codes(deploy(),service(target=0)),["SV004"])
    def test_invalid_ports_shape(self):
        s=service();s["spec"]["ports"]="bad"
        with self.assertRaises(ValueError):scan(deploy(),s)
    def test_direct_pod(self):
        p={"kind":"Pod","metadata":{"name":"api","labels":{"app":"api"}},"spec":{"containers":[{"name":"api","ports":[{"name":"http","containerPort":8080}]}]}}
        self.assertEqual(scan(p,service()),[])
    def test_multiple_workloads_partial_port(self):
        a1=deploy();b=deploy(ports=["other"]);b["metadata"]["name"]="other"
        self.assertEqual(codes(a1,b,service()),["SV003"])
    def test_multidoc_input(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.yaml";p.write_text("kind: Service\n---\nkind: Deployment\n")
            self.assertEqual(len(a.read(p)),2)
    def test_bad_yaml(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.yaml";p.write_text('!!python/object/apply:os.system ["echo never"]')
            with self.assertRaises(ValueError):a.read(p)
    def test_nonmapping_document(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.yaml";p.write_text("- x")
            with self.assertRaises(ValueError):a.read(p)
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):a.read(td)
    def test_missing_file(self):
        with self.assertRaises(ValueError):a.read("/surely/not/here.yml")
    def test_invalid_service_spec(self):
        s=service();s["spec"]="bad"
        with self.assertRaises(ValueError):scan(s)
    def test_cronjob_template(self):
        d=deploy()
        job={"kind":"CronJob","metadata":{"name":"hourly"},"spec":{"jobTemplate":{"spec":{"template":d["spec"]["template"]}}}}
        self.assertEqual(scan(job,service()),[])
if __name__=="__main__":unittest.main()
