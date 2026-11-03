"""Verify the directory is not secretly still the source monorepo."""
import hashlib
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
REPOS=['openapi-compat-audit','ci-log-triage','gha-trust-boundary-audit','env-contract-audit','pg-migration-risk-audit','docker-context-guard','python-artifact-audit','k8s-rbac-rights-audit','terraform-plan-impact-audit','k8s-netpol-scope-audit','codeowners-review-gap-audit','k8s-image-pin-audit','compose-port-exposure-audit','helm-values-contract-audit','aws-github-oidc-trust-audit','npm-export-map-audit','compose-startup-readiness-audit','python-entrypoint-contract-audit','k8s-pdb-scope-audit','pip-index-boundary-audit']
EXPECTED={
 'area-zero-logo-full.svg':'89b459e6a4e61748d2d56d54da2cd17ff2b55deafbbc90e45e43d4c319462d16',
 'area-zero-logo-icon.svg':'f566816db1f90656499b5e8377b04cc96584c45b2a62c8113895f3f24eeb0c68'
}
class PortfolioTests(unittest.TestCase):
 def test_directory_is_exactly_20_unique_skill_links(self):
  self.assertEqual(len(REPOS),20)
  self.assertEqual(len(REPOS),len(set(REPOS)))
  text=(ROOT/'README.md').read_text(encoding='utf-8')
  self.assertIn('independent%20skill%20repos-20-',text)
  self.assertIn('docs/CANDIDATE_RESEARCH_2026-11-03.md',text)
  self.assertIn('**EP.10 — 2026-11-03**',(ROOT/'docs/EPISODES.md').read_text(encoding='utf-8'))

 def test_all_standalone_repos_linked(self):
  readme=(ROOT/'README.md').read_text(encoding='utf-8')
  episodes=(ROOT/'docs/EPISODES.md').read_text(encoding='utf-8')
  for slug in REPOS:
   url='https://github.com/Kanompung1988/'+slug
   self.assertIn(url, readme)
   self.assertIn(url, episodes)
 def test_index_only_no_packaged_skills(self):
  self.assertFalse((ROOT/'skills').exists())
  self.assertFalse((ROOT/'examples').exists())
 def test_brand_svg_bytes_unmodified(self):
  for fname,sha in EXPECTED.items():
   self.assertEqual(hashlib.sha256((ROOT/'assets'/fname).read_bytes()).hexdigest(),sha)
 def test_assets_xml_valid(self):
  for fname in ('hero.svg','area-zero-logo-full.svg','area-zero-logo-icon.svg'):
   ET.parse(ROOT/'assets'/fname)
 def test_portfolio_local_links(self):
  text=(ROOT/'README.md').read_text(encoding='utf-8')
  refs=re.findall(r'\]\(([^)]+)\)',text)+re.findall(r'(?:src|href)="([^"]+)"',text)
  checks=0
  for ref in refs:
   if ref.startswith(('https://','http://','#','mailto:')):continue
   self.assertTrue((ROOT/ref.partition('#')[0]).exists(),ref)
   checks+=1
  self.assertGreater(checks,5)
