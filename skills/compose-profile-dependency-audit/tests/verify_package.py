from pathlib import Path
import hashlib, re, xml.etree.ElementTree as ET
import yaml
root=Path(__file__).resolve().parents[1]
name='compose-profile-dependency-audit'
text=(root/'SKILL.md').read_text(encoding='utf-8')
match=re.match(r'\A---\n(.*?)\n---\n',text,re.S)
assert match,'SKILL.md must begin with YAML frontmatter'
front=yaml.safe_load(match.group(1))
assert front['name']==name and len(name)<=64
assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name)
assert isinstance(front['description'],str) and 1<=len(front['description'])<=1024
assert len(front['compatibility'])<=500
assert front['license']=='MIT'
expected='89b459e6a4e61748d2d56d54da2cd17ff2b55deafbbc90e45e43d4c319462d16'
assert hashlib.sha256((root/'assets/area-zero-logo-full.svg').read_bytes()).hexdigest()==expected,'original logo SHA256 changed'
ET.parse(root/'assets/area-zero-logo-full.svg')
ET.parse(root/'assets/hero.svg')
for path in ['README.md','LICENSE','requirements.txt','references/REFERENCE.md','CONTRIBUTING.md','SECURITY.md']:
    assert (root/path).is_file(),path
print('Agent Skill package metadata, original SVG and documentation validated')
