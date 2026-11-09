import importlib.util
from pathlib import Path
import tempfile
import unittest

module=importlib.util.spec_from_file_location("audit",Path(__file__).resolve().parents[1]/"scripts"/"audit.py")
a=importlib.util.module_from_spec(module);module.loader.exec_module(a)

def deploy():
    return {"kind":"Deployment","metadata":{"name":"web"},"spec":{"template":{"spec":{"containers":[{"name":"app","resources":{"requests":{"cpu":"100m","memory":"64Mi"}}},{"name":"proxy","resources":{"requests":{"cpu":"20m","memory":"32Mi"}}}]}}}}
def hpa():
    return {"kind":"HorizontalPodAutoscaler","apiVersion":"autoscaling/v2","metadata":{"name":"scale"},"spec":{"minReplicas":1,"maxReplicas":4,"scaleTargetRef":{"apiVersion":"apps/v1","kind":"Deployment","name":"web"},"metrics":[{"type":"Resource","resource":{"name":"cpu","target":{"type":"Utilization","averageUtilization":60}}}]}}
def scan(*docs):
    return a.audit([("x.yaml",d) for d in docs])
def codes(*docs):
    return [x["code"] for x in scan(*docs)]

class Tests(unittest.TestCase):
    def test_safe(self):self.assertEqual(scan(deploy(),hpa()),[])
    def test_missing_app_request(self):
        d=deploy();del d["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["cpu"]
        self.assertEqual(codes(d,hpa()),["HP007"])
    def test_missing_sidecar_request(self):
        d=deploy();del d["spec"]["template"]["spec"]["containers"][1]["resources"]["requests"]["cpu"]
        self.assertEqual(codes(d,hpa()),["HP007"])
    def test_missing_memory(self):
        d=deploy();del d["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["memory"]
        h=hpa();h["spec"]["metrics"][0]["resource"]["name"]="memory"
        self.assertEqual(codes(d,h),["HP007"])
    def test_average_value_no_request(self):
        d=deploy();d["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]={}
        h=hpa();h["spec"]["metrics"][0]["resource"]["target"]={"type":"AverageValue","averageValue":"200m"}
        self.assertEqual(scan(d,h),[])
    def test_bounds(self):
        h=hpa();h["spec"]["minReplicas"]=10
        self.assertEqual(codes(deploy(),h),["HP001"])
    def test_bool_max(self):
        h=hpa();h["spec"]["maxReplicas"]=True
        self.assertEqual(codes(deploy(),h),["HP001"])
    def test_missing_ref(self):
        h=hpa();h["spec"]["scaleTargetRef"]={}
        self.assertEqual(codes(deploy(),h),["HP002"])
    def test_duplicate_hpa(self):
        x=hpa();y=hpa();y["metadata"]["name"]="other"
        self.assertEqual(codes(deploy(),x,y),["HP003"])
    def test_target_not_provided(self):self.assertEqual(codes(hpa()),["HP004"])
    def test_other_namespace(self):
        d=deploy();d["metadata"]["namespace"]="prod"
        self.assertEqual(codes(d,hpa()),["HP004"])
    def test_missing_containers(self):
        d=deploy();d["spec"]["template"]["spec"]["containers"]=[]
        self.assertEqual(codes(d,hpa()),["HP005"])
    def test_container_metric(self):
        h=hpa();h["spec"]["metrics"]=[{"type":"ContainerResource","containerResource":{"name":"cpu","container":"app","target":{"type":"Utilization","averageUtilization":60}}}]
        d=deploy();d["spec"]["template"]["spec"]["containers"][1]["resources"]={}
        self.assertEqual(scan(d,h),[])
    def test_unknown_container_metric(self):
        h=hpa();h["spec"]["metrics"]=[{"type":"ContainerResource","containerResource":{"name":"cpu","container":"missing","target":{"type":"Utilization","averageUtilization":60}}}]
        self.assertEqual(codes(deploy(),h),["HP006"])
    def test_other_version(self):
        h=hpa();h["apiVersion"]="autoscaling/v1"
        self.assertEqual(codes(deploy(),h),["HP000"])
    def test_unsafe_yaml(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.yaml";p.write_text('!!python/object/apply:os.system ["echo never"]')
            with self.assertRaises(ValueError):a.read(p)
    def test_nonmap(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.yaml";p.write_text("- x")
            with self.assertRaises(ValueError):a.read(p)
    def test_multidoc(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.yaml";p.write_text("kind: Deployment\n---\nkind: HorizontalPodAutoscaler\n")
            self.assertEqual(len(a.read(p)),2)
    def test_missing_file(self):
        with self.assertRaises(ValueError):a.read("/surely/not/here.yaml")
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):a.read(td)
    def test_invalid_metrics(self):
        h=hpa();h["spec"]["metrics"]="bad"
        with self.assertRaises(ValueError):scan(deploy(),h)

if __name__=="__main__":unittest.main()
