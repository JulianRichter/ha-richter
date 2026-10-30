#!/usr/bin/env python3
"""
Home Assistant Entity Reference Doctor / Auditor.

Cross-references entity references in YAML against:
1. Live Home Assistant states (via http://<HA_HOST>:8123/api/states using ~/.ha_token).
2. Template & Helper entities declared across YAML packages.

Lightweight, high-speed, and quota-friendly (prints concise results only).
"""

import os
import re
import sys
import json
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
TOKEN_PATH = os.path.expanduser('~/.ha_token')

IGNORED_ACTIONS = {
    'turn_on', 'turn_off', 'toggle', 'open_cover', 'close_cover', 'stop_cover',
    'set_cover_position', 'set_temperature', 'set_hvac_mode', 'set_value',
    'press', 'reload', 'trigger', 'snapshot', 'restore', 'media_play',
    'media_pause', 'media_play_pause', 'media_stop', 'volume_set', 'volume_mute',
    'shuffle_set', 'select_source', 'play_media', 'return_to_base', 'start',
    'pause', 'clean_spot', 'locate', 'set_fan_speed', 'set_preset_mode',
    'get_items', 'get_forecasts', 'svg'
}

DOMAINS_TO_CHECK = {
    'light', 'switch', 'sensor', 'binary_sensor', 'cover', 'climate',
    'media_player', 'vacuum', 'fan', 'input_boolean', 'input_number',
    'input_select', 'input_datetime', 'todo', 'person', 'weather'
}

def get_live_entities():
    if not os.path.isfile(TOKEN_PATH):
        return None
    try:
        with open(TOKEN_PATH, 'r', encoding='utf-8') as f:
            token = f.read().strip()
        url = os.environ.get('HA_URL', 'http://192.168.178.100:8123') + '/api/states'
        req = urllib.request.Request(url, headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=5) as response:
            states = json.load(response)
            return {s['entity_id'] for s in states}
    except Exception as e:
        print(f"⚠️  Live HA state check skipped (could not connect: {e})")
        return None

def collect_yaml_declared_entities():
    declared = set()
    for root, _, files in os.walk(os.path.join(BASE_DIR, 'include')):
        for f in files:
            if f.endswith('.yaml'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8', errors='ignore') as yf:
                    for line in yf:
                        # unique_id declarations
                        m_uid = re.search(r'unique_id:\s*([a-zA-Z0-9_]+)', line)
                        if m_uid:
                            uid = m_uid.group(1)
                            for d in DOMAINS_TO_CHECK:
                                declared.add(f"{d}.{uid}")
                                declared.add(f"{d}.template_{uid}")
                        # input helper top-level keys
                        m_inp = re.match(r'^([a-zA-Z0-9_]+):\s*$', line)
                        if m_inp and 'include/input/' in path:
                            key = m_inp.group(1)
                            # deduce domain from filename
                            bname = os.path.basename(path)
                            # e.g. input_boolean, input_number
                            for d in ['input_boolean', 'input_number', 'input_datetime', 'input_select']:
                                if d in bname:
                                    declared.add(f"{d}.{key}")
    return declared

def audit():
    print("=" * 65)
    print(" 🩺 HOME ASSISTANT ENTITY REFERENCE AUDIT")
    print("=" * 65)
    
    live_entities = get_live_entities()
    declared_entities = collect_yaml_declared_entities()
    
    referenced = {}
    scan_dir = os.path.join(BASE_DIR, 'include')
    for root, _, files in os.walk(scan_dir):
        for f in files:
            if f.endswith('.yaml'):
                rel = os.path.relpath(os.path.join(root, f), BASE_DIR)
                with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as yf:
                    for line_no, line in enumerate(yf, 1):
                        for m in re.finditer(r'\b([a-z_]+)\.([a-z0-9_]+)\b', line):
                            domain = m.group(1)
                            name = m.group(2)
                            if name in IGNORED_ACTIONS:
                                continue
                            if domain in DOMAINS_TO_CHECK:
                                ent = f"{domain}.{name}"
                                referenced.setdefault(ent, []).append(f"{rel}:{line_no}")

    print(f"Audited {len(referenced)} distinct entity references across YAML packages.")
    
    if live_entities is None:
        print("Live instance unreachable; checking against YAML-declared entities only.")
        valid_pool = declared_entities
    else:
        valid_pool = live_entities.union(declared_entities)

    missing = {ent: locs for ent, locs in referenced.items() if ent not in valid_pool}
    
    # Filter known templates/utility meters that might be dynamically generated
    real_missing = {}
    for ent, locs in missing.items():
        # filter placeholders or dynamic entities
        if ent.endswith('_') or 'placeholder' in ent:
            continue
        real_missing[ent] = locs

    if not real_missing:
        print("\n✅ All referenced entity IDs match live HA entities or declared templates!")
        return 0

    print(f"\n⚠️  Found {len(real_missing)} unverified / potentially broken entity references:")
    for ent, locs in sorted(real_missing.items()):
        print(f"  • {ent}")
        print(f"    referenced at: {locs[0]} ({len(locs)} total refs)")
    
    return 1

if __name__ == '__main__':
    sys.exit(audit())

