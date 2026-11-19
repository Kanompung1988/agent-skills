"""Checks essential Agent Skills metadata, packaging, and brand integrity."""
import hashlib
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml

root = Path(__file__).resolve().parents[1]
skill = (root / 'SKILL.md').read_text(encoding='utf-8')
assert skill.startswith('---\n')
parts = skill.split('---', 2)
assert len(parts) == 3 and parts[2].strip()
meta = yaml.safe_load(parts[1]); assert isinstance(meta, dict)
assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', meta['name'])
assert meta['name'] == root.name
assert isinstance(meta['description'], str) and 1 <= len(meta['description']) <= 1024
assert meta.get('license') == 'MIT'
assert len(meta.get('compatibility', '')) <= 500
assert isinstance(meta.get('metadata'), dict)
assert (root / 'LICENSE').is_file()
for file in ('README.md', 'CONTRIBUTING.md', 'references/REFERENCE.md', 'assets/hero.svg'):
    assert (root / file).is_file(), file
original = root / 'assets/area-zero-logo-full.svg'
assert hashlib.sha256(original.read_bytes()).hexdigest() == '89b459e6a4e61748d2d56d54da2cd17ff2b55deafbbc90e45e43d4c319462d16', 'Original logo must remain byte-identical'
ET.parse(original)
ET.parse(root / 'assets/hero.svg')
print('Metadata, packaging, and original SVG integrity validated.')
