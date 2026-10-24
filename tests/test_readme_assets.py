"""Documentation and brand-integrity distribution checks."""
from __future__ import annotations
import hashlib
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
# SHA-256 of unmodified owner-provided official SVG files verified on 2026-10-24.
LOGOS = {
    'area-zero-logo-full.svg': '89b459e6a4e61748d2d56d54da2cd17ff2b55deafbbc90e45e43d4c319462d16',
    'area-zero-logo-icon.svg': 'f566816db1f90656499b5e8377b04cc96584c45b2a62c8113895f3f24eeb0c68',
}


class ReadmeAssetTests(unittest.TestCase):
    def test_official_svg_hashes_unchanged(self):
        for name, digest in LOGOS.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / 'assets' / name).read_bytes()).hexdigest(), digest)

    def test_svg_art_is_valid_xml(self):
        for name in ('hero.svg', 'workflow.svg', *LOGOS.keys()):
            with self.subTest(name=name):
                ET.parse(ROOT / 'assets' / name)

    def test_relative_readme_links_exist(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        md_links = re.findall(r'\]\(([^)]+)\)', readme)
        html_links = re.findall(r'(?:href|src)="([^"]+)"', readme)
        checked = 0
        for link in md_links + html_links:
            if link.startswith(('https://', 'http://', 'mailto:', '#')):
                continue
            with self.subTest(link=link):
                self.assertTrue((ROOT / link.split('#')[0]).exists(), f'Missing file: {link}')
            checked += 1
        self.assertGreater(checked, 15)

    def test_readme_honesty_and_install_paths(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8').lower()
        self.assertIn('synthetic', readme)
        self.assertIn('.agents/skills', readme)
        self.assertIn('.claude/skills', readme)
        self.assertNotIn('release candidate, not yet published', readme)


if __name__ == '__main__':
    unittest.main()
