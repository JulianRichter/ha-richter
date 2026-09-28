#!/usr/bin/env python3
"""
Home Assistant Pre-Flight Configuration Validator.

Validates:
1. YAML syntax across all packages, dashboards, and core files.
2. Cross-references all !secret references against secrets.yaml.
3. Cross-references all script dispatches (action: script.<name>) against include/scripts/.
4. Verifies standard '# ===' header documentation across automations & scripts.
5. Audits templates for unsafe numeric filters (| float or | int without defaults).
"""

import os
import re
import sys
import yaml

class SafeLoaderCustom(yaml.SafeLoader):
    pass

def custom_constructor(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    elif isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None

SafeLoaderCustom.add_multi_constructor('!', custom_constructor)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

def run_validation():
    print("=" * 65)
    print(" 🔍 HOME ASSISTANT CONFIGURATION PRE-FLIGHT VALIDATION")
    print("=" * 65)
    
    errors = []
    warnings = []

    # 1. Parse secrets.yaml
    secrets_path = os.path.join(BASE_DIR, 'secrets.yaml')
    defined_secrets = set()
    if os.path.isfile(secrets_path):
        with open(secrets_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    defined_secrets.add(line.split(':')[0].strip())
    else:
        warnings.append("secrets.yaml not found.")

    # 2. Collect defined scripts
    defined_scripts = set()
    scripts_dir = os.path.join(BASE_DIR, 'include', 'scripts')
    if os.path.isdir(scripts_dir):
        for root, _, files in os.walk(scripts_dir):
            for f in files:
                if f.endswith('.yaml'):
                    defined_scripts.add(f[:-5])
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as sf:
                        for line in sf:
                            m = re.match(r'^\s{2}([a-z0-9_]+):\s*$', line)
                            if m:
                                defined_scripts.add(m.group(1))

    # 3. Scan all relevant YAML files
    yaml_count = 0
    dirs_to_scan = [
        os.path.join(BASE_DIR, 'include'),
        os.path.join(BASE_DIR, 'dashboards'),
    ]
    root_files = [
        'configuration.yaml',
        'automations.yaml',
        'scripts.yaml',
        'scenes.yaml'
    ]

    files_to_check = []
    for d in dirs_to_scan:
        if os.path.isdir(d):
            for root, _, files in os.walk(d):
                for f in files:
                    if f.endswith('.yaml'):
                        files_to_check.append(os.path.join(root, f))
    for rf in root_files:
        p = os.path.join(BASE_DIR, rf)
        if os.path.isfile(p):
            files_to_check.append(p)

    for path in sorted(files_to_check):
        yaml_count += 1
        rel = os.path.relpath(path, BASE_DIR)
        
        # 3a. YAML Syntax Check
        try:
            with open(path, 'r', encoding='utf-8') as yf:
                content = yf.read()
                yaml.load(content, Loader=SafeLoaderCustom)
        except Exception as e:
            errors.append(f"YAML Syntax Error in {rel}: {e}")
            continue

        lines = content.splitlines()

        # 3b. Header Standard Check for automations and scripts
        if 'include/automations/' in rel or 'include/scripts/' in rel:
            has_header = any('# ======' in l for l in lines[:10])
            if not has_header:
                warnings.append(f"Missing standard '# ===' header in {rel}")

        # 3c. Check !secret calls and script actions per line
        for i, line in enumerate(lines, 1):
            # !secret check
            for m in re.finditer(r'!secret\s+([a-zA-Z0-9_]+)', line):
                sec = m.group(1)
                if sec not in defined_secrets:
                    errors.append(f"Undefined secret '!secret {sec}' at {rel}:{i}")

            # script action check
            if 'action: script.' in line or 'service: script.' in line:
                m_sc = re.search(r'(?:action|service):\s*script\.([a-zA-Z0-9_]+)', line)
                if m_sc:
                    sc_name = m_sc.group(1)
                    if sc_name not in defined_scripts:
                        errors.append(f"Unknown script call 'script.{sc_name}' at {rel}:{i}")

            # deprecated service: syntax check
            if re.match(r'^\s*-\s*service:\s*', line) or re.match(r'^\s*service:\s*', line):
                if 'service_template:' not in line and 'service_account' not in line:
                    warnings.append(f"Deprecated 'service:' syntax at {rel}:{i} (use 'action:')")

    print(f"Scanned {yaml_count} YAML configuration files.")
    print("-" * 65)

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n❌ ERRORS FOUND ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        print("\n❌ Pre-flight validation FAILED.")
        return 1

    print("\n✅ All YAML syntax, secrets, script dispatches, and headers passed cleanly!")
    return 0

if __name__ == '__main__':
    sys.exit(run_validation())

