from pathlib import Path
import hashlib, re, sys
root=Path(__file__).parents[1]
skill=(root/'SKILL.md').read_text(encoding='utf-8')
match=re.match(r"^---\n(.*?)\n---\n", skill, re.S)
assert match, 'SKILL.md frontmatter missing'
front=match.group(1)
assert re.search(r"^name: k8s-runtimeclass-contract-audit$", front, re.M)
assert re.search(r"^description: .{1,1024}$", front, re.M)
for path in ['README.md','LICENSE','requirements.txt','scripts/audit.py','references/REFERENCE.md','fixtures/safe.yaml','fixtures/review.yaml','assets/area-zero-logo-full.svg','assets/hero.svg']:
    assert (root/path).is_file(), f'missing {path}'
logo=(root/'assets/area-zero-logo-full.svg').read_bytes()
assert hashlib.sha256(logo).hexdigest() == '89b459e6a4e61748d2d56d54da2cd17ff2b55deafbbc90e45e43d4c319462d16', 'official logo bytes changed'
print('package layout and SKILL.md frontmatter: PASS')
