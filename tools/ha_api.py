#!/usr/bin/env python3
# ====================================================================
# Home Assistant API Client & Inspection Tool
# - Queries live entity states, attributes, and system logs via REST API
# - Reads Long-Lived Access Token securely from ~/.ha_token or HA_TOKEN env
# ====================================================================

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_HA_URL = "http://192.168.178.100:8123"

def get_ha_config():
    """Resolves HA URL and Access Token securely from environment or local files."""
    ha_url = os.environ.get("HA_URL", DEFAULT_HA_URL).rstrip("/")
    token = os.environ.get("HA_TOKEN")

    if not token:
        # Check standard local paths (on workstation)
        token_paths = [
            os.path.expanduser("~/.ha_token"),
            os.path.expanduser("~/.config/ha/token"),
            os.path.join(os.path.dirname(__file__), ".ha_token"),
            os.path.join(os.path.dirname(__file__), "..", ".ha_token"),
        ]
        for path in token_paths:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        token = f.read().strip()
                        if token:
                            break
                except Exception:
                    pass

    return ha_url, token

def make_request(endpoint, method="GET", data=None):
    """Executes authenticated REST request against Home Assistant API."""
    ha_url, token = get_ha_config()
    if not token:
        print("❌ Error: No Home Assistant access token found.", file=sys.stderr)
        print("👉 Please save your token to ~/.ha_token or set the HA_TOKEN environment variable.", file=sys.stderr)
        sys.exit(1)

    url = f"{ha_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return json.loads(resp.read().decode("utf-8"))
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"❌ HTTP Error {e.code}: {e.reason} for {url}", file=sys.stderr)
        if error_body:
            print(f"   Details: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ Connection Error: {e.reason} connecting to {url}", file=sys.stderr)
        sys.exit(1)

def cmd_check(args):
    """Verifies API connectivity and token authentication."""
    ha_url, _ = get_ha_config()
    print(f"Connecting to Home Assistant at {ha_url}...")
    res = make_request("/api/")
    print(f"✅ Connection successful!")
    print(f"   Message: {res.get('message', 'N/A')}")
    
    cfg = make_request("/api/config")
    print(f"   Instance Name: {cfg.get('location_name', 'Home Assistant')}")
    print(f"   Version: {cfg.get('version', 'Unknown')}")
    print(f"   Time Zone: {cfg.get('time_zone', 'Unknown')}")
    print(f"   State: {cfg.get('state', 'RUNNING')}")

def cmd_state(args):
    """Fetches real-time state and attributes for a specific entity."""
    entity_id = args.entity_id
    res = make_request(f"/api/states/{entity_id}")
    print(json.dumps(res, indent=2))

def cmd_states(args):
    """Lists entities filtered by domain or search keyword."""
    all_states = make_request("/api/states")
    filtered = []
    for s in all_states:
        eid = s.get("entity_id", "")
        if args.domain and not eid.startswith(f"{args.domain}."):
            continue
        if args.search:
            name = s.get("attributes", {}).get("friendly_name", "")
            if args.search.lower() not in eid.lower() and args.search.lower() not in name.lower():
                continue
        filtered.append(s)

    print(f"Found {len(filtered)} matching entities:")
    for s in filtered:
        eid = s.get("entity_id")
        state = s.get("state")
        name = s.get("attributes", {}).get("friendly_name", "")
        print(f" - {eid:40} | state: {state:15} | {name}")

def cmd_reload_lovelace(args):
    """Triggers Home Assistant to reload frontend themes and resources."""
    print("Reloading frontend themes and dashboard resources...")
    make_request("/api/services/frontend/reload_themes", method="POST", data={})
    print("✅ Frontend themes reloaded.")

def cmd_logs(args):
    """Fetches recent errors and warnings from Home Assistant error log."""
    logs = make_request("/api/error_log")
    lines = logs.strip().splitlines()
    limit = args.lines
    print(f"=== Last {min(limit, len(lines))} lines of Home Assistant Error Log ===")
    for line in lines[-limit:]:
        print(line)

def main():
    parser = argparse.ArgumentParser(description="Home Assistant Live Context & Inspection Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check
    subparsers.add_parser("check", help="Verify connection and access token")

    # state
    p_state = subparsers.add_parser("state", help="Get state and attributes of an entity")
    p_state.add_argument("entity_id", help="Entity ID (e.g. sensor.time)")
    p_state.set_defaults(func=cmd_state)

    # states
    p_states = subparsers.add_parser("states", help="Search or list entity states")
    p_states.add_argument("--domain", help="Filter by domain (e.g. light, switch, sensor)")
    p_states.add_argument("--search", help="Search substring in entity ID or friendly name")
    p_states.set_defaults(func=cmd_states)

    # reload-lovelace
    p_reload = subparsers.add_parser("reload-lovelace", help="Reload frontend themes & dashboards")
    p_reload.set_defaults(func=cmd_reload_lovelace)

    # logs
    p_logs = subparsers.add_parser("logs", help="View Home Assistant error log")
    p_logs.add_argument("--lines", type=int, default=30, help="Number of lines to show (default: 30)")
    p_logs.set_defaults(func=cmd_logs)

    args = parser.parse_args()
    if args.command == "check":
        cmd_check(args)
    elif hasattr(args, "func"):
        args.func(args)

if __name__ == "__main__":
    main()
