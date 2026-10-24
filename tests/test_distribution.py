"""Standalone checks of an Areazero Agent Skills distribution (stdlib-only)."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SKILLS=[ROOT/'skills'/'openapi-compat-audit',ROOT/'skills'/'ci-log-triage']

class DistributionTest(unittest.TestCase):
    def test_skill_metadata_matches_spec(self):
        """Apply the normative filename, required-field and character constraints."""
        for folder in SKILLS:
            with self.subTest(folder=folder.name):
                data=(folder/'SKILL.md').read_text(encoding='utf-8')
                self.assertTrue(data.startswith('---\n'))
                meta=data.split('---\n',2)[1]
                values={}
                for line in meta.splitlines():
                    if line and not line.startswith(' ') and ':' in line:
                        k,v=line.split(':',1)
                        values[k.strip()]=v.strip().strip('\'"')
                self.assertEqual(values.get('name'),folder.name)
                self.assertRegex(folder.name,r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
                self.assertLessEqual(len(folder.name),64)
                self.assertTrue(values.get('description'))
                self.assertLessEqual(len(values['description']),1024)
                self.assertTrue(set(values).issubset({'name','description','license','compatibility','metadata','allowed-tools'}))
                self.assertIn('Use when',data)
                self.assertIn('Workflow',data)
                self.assertIn('Edge cases',data)
                self.assertLess(len(data.splitlines()),500)
                self.assertTrue((folder/'README.md').is_file())
                self.assertTrue((folder/'LICENSE').is_file())

    def test_skill_local_markdown_links_exist(self):
        pattern=re.compile(r'\]\(([^)]+)\)')
        for folder in SKILLS:
            for target in pattern.findall((folder/'SKILL.md').read_text(encoding='utf-8')):
                if re.match(r'^[a-z]+://',target) or target.startswith('#'):
                    continue
                target=target.split('#',1)[0]
                self.assertTrue((folder/target).is_file(),f'Missing local link: {folder}: {target}')

    def test_python_scripts_never_import_process_or_network(self):
        for folder in SKILLS:
            for script in (folder/'scripts').glob('*.py'):
                import ast
                tree=ast.parse(script.read_text(encoding='utf-8'))
                modules=[]
                for node in ast.walk(tree):
                    if isinstance(node,ast.Import):modules.extend(alias.name.split('.')[0] for alias in node.names)
                    if isinstance(node,ast.ImportFrom) and node.module: modules.append(node.module.split('.')[0])
                self.assertFalse(set(modules)&{'subprocess','socket','requests','urllib','http','ftplib','paramiko'},f'{script}: forbidden dependency')

    def test_openapi_sample_reports_detect_breaking(self):
        program=SKILLS[0]/'scripts'/'compare_openapi.py'
        old=ROOT/'examples'/'openapi-before.json'
        new=ROOT/'examples'/'openapi-after.json'
        result=subprocess.run([sys.executable,str(program),'--old',str(old),'--new',str(new),'--format','json'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2,result.stderr)
        report=json.loads(result.stdout)
        self.assertGreater(report['summary']['breaking'],0)
        self.assertTrue(report['findings'])

    def test_ci_sample_has_redacted_evidence(self):
        program=SKILLS[1]/'scripts'/'triage_ci.py'
        log=ROOT/'examples'/'synthetic-ci.log'
        result=subprocess.run([sys.executable,str(program),'--input',str(log),'--format','json'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        report=json.loads(result.stdout)
        self.assertGreater(report['summary']['signals'],0)
        for finding in report['findings']:
            for evidence in finding['evidence']:
                self.assertGreater(evidence['line'],0)
                self.assertLessEqual(len(evidence['text']),320)

    def test_script_generated_output_does_not_leak_fake_token(self):
        program=SKILLS[1]/'scripts'/'triage_ci.py'
        token='ghp_'+'A'*32
        with tempfile.NamedTemporaryFile('w',encoding='utf8',delete=False) as file:
            file.write(f'ERROR TS2345: problem: {token}\n')
            filename=file.name
        try:
            result=subprocess.run([sys.executable,str(program),'--input',filename,'--format','json'],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertNotIn(token,result.stdout)
            self.assertIn('[REDACTED]',result.stdout)
        finally:
            os.unlink(filename)

if __name__=='__main__':unittest.main()
