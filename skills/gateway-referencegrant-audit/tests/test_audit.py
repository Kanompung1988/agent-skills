"""Synthetic offline regression suite: no cluster/API access."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit


def obj(kind, ns="app", spec=None, name="test"):
    return {"apiVersion": "gateway.networking.k8s.io/v1", "kind": kind,
            "metadata": {"name": name, "namespace": ns}, "spec": spec or {}}


def route(target="shared", namespace="app", kind="HTTPRoute", backend=None, **kwargs):
    b = backend if backend is not None else {"name": "server", "namespace": target}
    return obj(kind, namespace, {"parentRefs": kwargs.get("parents", [{"name": "gw"}]),
                                  "rules": [{"backendRefs": [b]}]})


def grant(source="app", target="shared", route_kind="HTTPRoute", target_kind="Service",
          name=None, group=""):
    to = {"group": group, "kind": target_kind}
    if name:
        to["name"] = name
    return obj("ReferenceGrant", target, {"from": [{"group": audit.GROUP, "kind": route_kind,
                                                    "namespace": source}], "to": [to]})


def run(*items):
    return audit.inspect([("input.yaml", item) for item in items])


class Contracts(unittest.TestCase):
    def test_same_namespace_no_grant(self):
        self.assertEqual(run(route("app")), [])
    def test_cross_namespace_requires_grant(self):
        self.assertEqual(run(route())[0]["code"], "RG001")
    def test_correct_grant(self):
        self.assertEqual(run(route(), grant()), [])
    def test_wrong_source_namespace(self):
        self.assertEqual(run(route(), grant(source="other"))[0]["code"], "RG001")
    def test_wrong_target_namespace(self):
        self.assertEqual(run(route(), grant(target="other"))[0]["code"], "RG001")
    def test_wrong_source_kind(self):
        self.assertEqual(run(route(), grant(route_kind="GRPCRoute"))[0]["code"], "RG001")
    def test_named_grant_exact(self):
        self.assertEqual(run(route(), grant(name="server")), [])
    def test_named_grant_mismatch(self):
        self.assertEqual(run(route(), grant(name="other"))[0]["code"], "RG001")
    def test_wrong_target_group(self):
        self.assertEqual(run(route(), grant(group="example.com"))[0]["code"], "RG001")
    def test_grpc_route_grant(self):
        self.assertEqual(run(route(kind="GRPCRoute"), grant(route_kind="GRPCRoute")), [])
    def test_tcp_route_without_grant(self):
        self.assertEqual(run(route(kind="TCPRoute"))[0]["code"], "RG001")
    def test_parent_gateway_not_backend(self):
        self.assertEqual(run(obj("HTTPRoute", spec={"parentRefs": [{"namespace": "infra", "name": "gw"}]})), [])
    def test_mesh_consumer_scope_skipped(self):
        self.assertEqual(run(route(parents=[{"kind": "Service", "name": "mesh", "namespace": "another"}])), [])
    def test_certificate_cross_namespace(self):
        gateway = obj("Gateway", "infra", {"listeners": [{"tls": {"certificateRefs": [
            {"name": "tls", "namespace": "certs"}]}}]})
        self.assertEqual(run(gateway)[0]["code"], "RG001")
        self.assertEqual(run(gateway, grant("infra", "certs", "Gateway", "Secret")), [])
    def test_mirror_filter(self):
        r = obj("HTTPRoute", spec={"rules": [{"filters": [{"type": "RequestMirror",
            "requestMirror": {"backendRef": {"name": "mirror", "namespace": "shared"}}}]}]})
        self.assertEqual(run(r)[0]["code"], "RG001")
    def test_empty_grant(self):
        self.assertEqual(run(grant(name="server", source="app"), route()), [])
        g = grant()
        g["spec"]["to"] = []
        self.assertEqual({x["code"] for x in run(g)}, {"RG002"})
    def test_missing_to_group(self):
        g = grant()
        del g["spec"]["to"][0]["group"]
        self.assertEqual(run(g)[0]["code"], "RG003")
    def test_missing_backend_name(self):
        self.assertEqual(run(route(backend={"namespace": "shared"}))[0]["code"], "RG005")
    def test_non_string_namespace(self):
        self.assertEqual(run(route(backend={"namespace": 3, "name": "svc"}))[0]["code"], "RG004")
    def test_default_namespace(self):
        r = route(target="other")
        del r["metadata"]["namespace"]
        self.assertEqual(run(r, grant(source="default", target="other")), [])
    def test_invalid_api_group_ignored(self):
        r = route()
        r["apiVersion"] = "example.io/v1"
        self.assertEqual(run(r), [])
    def test_bad_yaml_is_input_error(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.yaml"
            p.write_text("metadata: [\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                audit.collect(p)
    def test_directory_multiple_docs(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "x.yaml").write_text("---\nkind: Namespace\nmetadata:\n  name: a\n", encoding="utf-8")
            self.assertEqual(len(audit.collect(td)), 1)
    def test_empty_document_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.yaml"
            p.write_text("---\n# blank\n---\nkind: Namespace\n", encoding="utf-8")
            self.assertEqual(len(audit.collect(p)), 1)
    def test_scalar_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.yaml"
            p.write_text("- a\n- b\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                audit.collect(p)
    def test_missing_path_rejected(self):
        with self.assertRaises(ValueError):
            audit.collect("unlikely-nonexisting-gateway-7345.yaml")


if __name__ == "__main__":
    unittest.main()
