#!/usr/bin/env python3
"""Conservative offline single-file Docker Compose profile/dependency evaluator."""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

PROFILE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]+$")

class UniqueLoader(yaml.SafeLoader):
    pass


def construct_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, (str, int, float, bool)):
            raise ValueError('unsupported mapping key')
        if key in result:
            raise ValueError(f'duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=True)
    return result

UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)


def load(path):
    if path.stat().st_size > 2_000_000:
        raise ValueError('file exceeds 2 MB safety limit')
    docs = list(yaml.load_all(path.read_text(encoding='utf-8'), Loader=UniqueLoader))
    if len(docs) != 1 or not isinstance(docs[0], dict):
        raise ValueError('expected exactly one YAML Compose mapping')
    return docs[0]


def profile_set(service):
    value = service.get('profiles', [])
    if value is None:
        raise ValueError('profiles must be a list, not null')
    if not isinstance(value, list) or not all(isinstance(v, str) and PROFILE.fullmatch(v) for v in value):
        raise ValueError('profiles must be a list of valid profile names')
    if len(value) != len(set(value)):
        raise ValueError('duplicate profile names')
    return set(value)


def dependencies(service):
    refs = []
    dep = service.get('depends_on', [])
    if isinstance(dep, list) and all(isinstance(v, str) for v in dep):
        refs.extend(('depends_on', v) for v in dep)
    elif isinstance(dep, dict):
        for name, config in dep.items():
            if not isinstance(name, str):
                raise ValueError('depends_on service name must be text')
            if config is not None and not isinstance(config, dict):
                raise ValueError('depends_on options must be a mapping')
            # required:false permits optional dependency to be absent; still a review note.
            if isinstance(config, dict) and config.get('required', True) is False:
                continue
            refs.append(('depends_on', name))
    else:
        raise ValueError('depends_on must be a list or mapping')
    for key in ('network_mode', 'pid', 'ipc'):
        v = service.get(key)
        if isinstance(v, str) and v.startswith('service:'):
            refs.append((key, v[len('service:'):]))
    links = service.get('links', [])
    if links is not None:
        if not isinstance(links, list) or not all(isinstance(x, str) for x in links):
            raise ValueError('links must be a list of strings')
        refs += [('links', x.split(':', 1)[0]) for x in links]
    ext = service.get('extends')
    if isinstance(ext, dict) and isinstance(ext.get('service'), str) and not ext.get('file'):
        refs.append(('extends', ext['service']))
    elif isinstance(ext, str):
        refs.append(('extends', ext))
    return refs


def audit(config, active_profiles=(), target=None):
    services = config.get('services')
    if not isinstance(services, dict) or not services:
        raise ValueError('services must be a non-empty mapping')
    for name, service in services.items():
        if not isinstance(name, str) or not isinstance(service, dict):
            raise ValueError('each service must be a named mapping')
    defined = {name: profile_set(service) for name, service in services.items()}
    allprofiles = sorted({p for val in defined.values() for p in val})
    found = []
    seen = set()

    def add(rule, severity, scenario, service, dependency, detail):
        key = (rule, scenario, service, dependency)
        if key not in seen:
            seen.add(key)
            found.append({'rule': rule, 'severity': severity, 'scenario': scenario,
                          'service': service, 'dependency': dependency, 'message': detail})

    for name, profile in defined.items():
        for p in profile:
            if p.startswith('${'):
                add('DYNAMIC_PROFILE', 'review', 'declarations', name, p, 'Interpolation is not a literal profile name')
        for kind, dep in dependencies(services[name]):
            if dep not in services:
                add('UNKNOWN_SERVICE', 'error', 'declarations', name, dep, f'{kind} references undeclared service')
        ext = services[name].get('extends')
        if isinstance(ext, dict) and ext.get('file'):
            add('EXTERNAL_EXTENDS', 'review', 'declarations', name, str(ext.get('service', '')), 'External extends cannot be resolved from this file')

    # Default, one-profile and target-mode scenarios. These are potential invocation contexts,
    # not a claim that the user necessarily invokes Compose in every scenario.
    scenarios = [('default', set(), None)]
    scenarios.extend((f'profile:{profile}', {profile}, None) for profile in allprofiles)
    if active_profiles or target:
        if target is not None and target not in services:
            raise ValueError('target service not declared')
        p = set(active_profiles)
        if p - set(allprofiles):
            raise ValueError('unknown active profile: ' + ', '.join(sorted(p - set(allprofiles))))
        if target:
            p.update(defined[target])
        scenarios.append(('requested', p, target))
    for scenario, profiles, targetname in scenarios:
        enabled = {name for name, p in defined.items() if not p or bool(p & profiles)}
        if targetname:
            enabled.add(targetname)
        for name in sorted(enabled):
            for kind, dep in dependencies(services[name]):
                if dep in services and dep not in enabled:
                    add('INACTIVE_DEPENDENCY', 'review', scenario, name, dep,
                        f'{kind} target excluded by active profile selection; enable a compatible profile')
        # Cycles are not a profile-specific security failure, but invalid Compose graphs.
        graph = {name: [d for k, d in dependencies(services[name]) if k == 'depends_on' and d in enabled] for name in enabled}
        visited = set()
        visiting = []
        def dfs(node):
            if node in visiting:
                add('DEPENDENCY_CYCLE', 'error', scenario, node, node, 'depends_on cycle: ' + ' -> '.join(visiting[visiting.index(node):] + [node]))
                return
            if node in visited:
                return
            visiting.append(node)
            for neighbor in graph.get(node, []):
                dfs(neighbor)
            visiting.pop()
            visited.add(node)
        for name in sorted(enabled):
            dfs(name)
    found.sort(key=lambda x: (x['rule'], x['scenario'], x['service'], x['dependency']))
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('compose', type=Path)
    ap.add_argument('--profile', action='append', default=[], help='active profile for additional requested scenario')
    ap.add_argument('--target', help='explicitly targeted Compose service')
    ap.add_argument('--format', choices=['text', 'json'], default='text')
    args = ap.parse_args(argv)
    try:
        data = load(args.compose)
        findings = audit(data, args.profile, args.target)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        print(f'Input error: {exc}', file=sys.stderr)
        return 1
    report = {'file': str(args.compose), 'finding_count': len(findings), 'findings': findings, 'status': 'review' if findings else 'safe'}
    if args.format == 'json':
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['status'].upper()}: {len(findings)} finding(s) in {args.compose}")
        for f in findings:
            print(f"[{f['severity']}] {f['rule']} ({f['scenario']}) {f['service']} -> {f['dependency']}: {f['message']}")
    return 2 if findings else 0

if __name__ == '__main__':
    sys.exit(main())
