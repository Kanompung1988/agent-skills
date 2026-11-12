import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts.audit import ADDR,analyze,audit,assignment,blocks,mask_noncode

class TerraformTests(unittest.TestCase):
    def test_mask_line_comment(self): self.assertNotIn('moved',mask_noncode('# moved {}'))
    def test_mask_slash_comment(self): self.assertNotIn('moved',mask_noncode('// moved {}'))
    def test_mask_block_comment(self): self.assertNotIn('moved',mask_noncode('/* moved {} */'))
    def test_mask_string(self): self.assertNotIn('moved',mask_noncode('x = "moved {}"'))
    def test_mask_escaped_string(self): self.assertNotIn('moved',mask_noncode('x = "\\\" moved {}"'))
    def test_mask_heredoc(self): self.assertNotIn('moved',mask_noncode('x = <<EOF\nmoved {}\nEOF\n'))
    def test_mask_newlines_preserved(self): self.assertEqual(mask_noncode('x="# hi"\n').count('\n'),1)
    def test_find_moved(self): self.assertEqual(next(blocks('moved {\n from = aws_instance.a\n to = aws_instance.b\n}'))[0],'moved')
    def test_find_removed(self): self.assertEqual(next(blocks('removed {\n from = aws_instance.a\n}'))[0],'removed')
    def test_invalid_block(self):
        with self.assertRaises(ValueError): list(blocks('moved {\n'))
    def test_assignment(self): self.assertEqual(assignment('\n from = aws_instance.a\n','from'),'aws_instance.a')
    def test_assignment_missing(self): self.assertIsNone(assignment('froms = x','from'))
    def test_address_resource(self): self.assertIsNotNone(ADDR.fullmatch('aws_instance.old'))
    def test_address_module(self): self.assertIsNotNone(ADDR.fullmatch('module.old'))
    def test_address_nested_module(self): self.assertIsNotNone(ADDR.fullmatch('module.a.module.b.aws_instance.x'))
    def test_address_invalid(self): self.assertIsNone(ADDR.fullmatch('var.foo + 1'))
    def test_missing_from_move(self): self._assert_rule('moved {\n to = aws_instance.b\n}', 'TFM001')
    def test_missing_to_move(self): self._assert_rule('moved {\n from = aws_instance.a\n}', 'TFM001')
    def test_same_address(self): self._assert_rule('moved {\n from = aws_instance.a\n to = aws_instance.a\n}', 'TFM003')
    def test_unsupported_address(self): self._assert_rule('moved {\n from = var.foo + 1\n to = aws_instance.b\n}', 'TFM002')
    def test_missing_from_removed(self): self._assert_rule('removed {\n lifecycle { destroy = false }\n}', 'TFR001')
    def test_missing_lifecycle(self): self._assert_rule('removed {\n from = aws_instance.a\n}', 'TFR003')
    def test_destroy_true(self): self._assert_rule('removed {\n from = aws_instance.a\n lifecycle {\n destroy = true\n }\n}', 'TFR003')
    def test_safe_removed(self): self.assertFalse(self._get_findings('removed {\n from = aws_instance.a\n lifecycle {\n destroy = false\n }\n}'))
    def test_duplicate_source(self): self._assert_rule('moved {\n from = aws_instance.a\n to = aws_instance.b\n}\nmoved {\n from = aws_instance.a\n to = aws_instance.c\n}', 'TFM004')
    def test_duplicate_target(self): self._assert_rule('moved {\n from = aws_instance.a\n to = aws_instance.b\n}\nmoved {\n from = aws_instance.c\n to = aws_instance.b\n}', 'TFM005')
    def test_duplicate_removed(self): self._assert_rule('removed {\n from = aws_instance.a\n lifecycle {\n destroy = false\n }\n}\nremoved {\n from = aws_instance.a\n lifecycle {\n destroy = false\n }\n}', 'TFR004')
    def test_overlap_move_removed(self): self._assert_rule('moved {\n from = aws_instance.a\n to = aws_instance.b\n}\nremoved {\n from = aws_instance.a\n lifecycle {\n destroy = false\n }\n}', 'TFR005')
    def test_cycle(self):
        self._assert_rule('moved {\n from = aws_instance.a\n to = aws_instance.b\n}\nmoved {\n from = aws_instance.b\n to = aws_instance.a\n}', 'TFM006')
    def test_chain_is_valid(self):
        self.assertFalse(self._get_findings('moved {\n from = aws_instance.a\n to = aws_instance.b\n}\nmoved {\n from = aws_instance.b\n to = aws_instance.c\n}'))
    def test_comment_not_counted(self): self.assertFalse(self._get_findings('# removed {\n# from = aws_instance.a\n# }\n'))
    def test_safe_fixture(self):self.assertEqual(audit(Path(__file__).resolve().parents[1]/'examples/safe.tf')[1],[])
    def test_review_fixture(self):self.assertTrue(audit(Path(__file__).resolve().parents[1]/'examples/review.tf')[1])
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):audit(Path(d))
    def test_cli_safe(self):
        root=Path(__file__).resolve().parents[1];p=subprocess.run([sys.executable,str(root/'scripts/audit.py'),str(root/'examples/safe.tf'),'--json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
    def test_cli_review(self):
        root=Path(__file__).resolve().parents[1];p=subprocess.run([sys.executable,str(root/'scripts/audit.py'),str(root/'examples/review.tf'),'--json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,1);self.assertTrue(json.loads(p.stdout)['findings'])
    def test_cli_missing(self):
        root=Path(__file__).resolve().parents[1];p=subprocess.run([sys.executable,str(root/'scripts/audit.py'),'/missing/xyz','--json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
    def _get_findings(self,source):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'main.tf';p.write_text(source)
            return audit(p)[1]
    def _assert_rule(self,source,rule):self.assertIn(rule,[f['rule'] for f in self._get_findings(source)])

if __name__=='__main__':unittest.main()
