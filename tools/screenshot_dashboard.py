#!/usr/bin/env python3
# ====================================================================
# Dashboard Screenshot Generator
# - Headless browser automation for multi-resolution dashboard preview
# - Supports presets: tablet, phone, pc, or custom resolution
# - Injects Home Assistant authentication tokens automatically
# ====================================================================

import argparse
import json
import os
import sys
import time
import urllib.request

# Automatically re-execute in the isolated venv if run from system python
VENV_PYTHON = os.path.expanduser("~/.venvs/ha-tools/bin/python3")
if os.path.isfile(VENV_PYTHON) and sys.executable != VENV_PYTHON:
    os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: Playwright is not installed in the current environment.", file=sys.stderr)
    print("👉 Please run with ~/.venvs/ha-tools/bin/python3 or install playwright.", file=sys.stderr)
    sys.exit(1)

DEFAULT_HA_URL = "http://192.168.178.100:8123"

PRESETS = {
    # User Primary Hardware Presets
    "tablet": {"width": 1130, "height": 706, "scale": 1.7, "desc": "Huawei MediaPad M5 Kiosk (1130x706 @1.7x)"},
    "tablet_m5": {"width": 1130, "height": 706, "scale": 1.7, "desc": "Huawei MediaPad M5 Kiosk (1130x706 @1.7x)"},
    "pc": {"width": 1854, "height": 959, "scale": 1.0, "desc": "Desktop PC Viewport (1854x959 @1.0x)"},
    "phone": {"width": 412, "height": 828, "scale": 2.6, "desc": "Google Pixel 7 Pro Viewport (412x828 @2.6x)"},
    "phone_pixel7pro": {"width": 412, "height": 828, "scale": 2.6, "desc": "Google Pixel 7 Pro Viewport (412x828 @2.6x)"},

    # Generic Fallbacks
    "generic_tablet_hd": {"width": 1920, "height": 1200, "scale": 1.0, "desc": "Generic Full HD Tablet (1920x1200)"},
    "generic_pc_fhd": {"width": 1920, "height": 1080, "scale": 1.0, "desc": "Generic Full HD Desktop (1920x1080)"},
}

def get_ha_config():
    """Resolves HA URL and Access Token securely."""
    ha_url = os.environ.get("HA_URL", DEFAULT_HA_URL).rstrip("/")
    token = os.environ.get("HA_TOKEN")

    if not token:
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

def take_screenshot(
    dashboard_path="bubble-kiosk-dashboard/Home",
    preset="tablet",
    width=None,
    height=None,
    scale=None,
    wait_sec=2.5,
    kiosk=True,
    theme=None,
    output_file=None,
    full_page=False
):
    ha_url, token = get_ha_config()
    if not token:
        print("❌ Error: No Home Assistant access token found.", file=sys.stderr)
        print("👉 Please save your token to ~/.ha_token or set HA_TOKEN environment variable.", file=sys.stderr)
        sys.exit(1)

    # Resolve dimensions
    if preset and preset in PRESETS:
        p = PRESETS[preset]
        viewport_w = width or p["width"]
        viewport_h = height or p["height"]
        device_scale = scale or p["scale"]
    else:
        viewport_w = width or 1920
        viewport_h = height or 1200
        device_scale = scale or 1.0

    # Format URL
    clean_path = dashboard_path.lstrip("/")
    url = f"{ha_url}/{clean_path}"
    if kiosk:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}kiosk"

    # Default output path
    if not output_file:
        slug = clean_path.replace("/", "_").replace("?", "_").replace("&", "_")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(script_dir, ".."))
        screenshots_dir = os.path.join(repo_root, "dashboards", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        preset_name = preset or f"{viewport_w}x{viewport_h}"
        output_file = os.path.join(screenshots_dir, f"{slug}_{preset_name}.png")

    print(f"📸 Capturing Dashboard Screenshot:")
    print(f"   URL:        {url}")
    print(f"   Resolution: {viewport_w}x{viewport_h} (scale: {device_scale}) [Preset: {preset}]")
    print(f"   Output:     {output_file}")

    # Chrome binary path
    chrome_path = "/opt/google/chrome/google-chrome"
    launch_kwargs = {"headless": True}
    if os.path.isfile(chrome_path):
        launch_kwargs["executable_path"] = chrome_path

    is_mobile_device = ("tablet" in preset or "phone" in preset)
    user_agent = None
    if "tablet" in preset:
        user_agent = (
            "Mozilla/5.0 (Linux; Android 9; CMR-W09) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    elif "phone" in preset:
        user_agent = (
            "Mozilla/5.0 (Linux; Android 14; Pixel 7 Pro) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        )

    context_kwargs = {
        "viewport": {"width": viewport_w, "height": viewport_h},
        "device_scale_factor": device_scale,
        "is_mobile": is_mobile_device,
        "has_touch": is_mobile_device,
        "color_scheme": "dark",
    }
    if user_agent:
        context_kwargs["user_agent"] = user_agent

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context(**context_kwargs)

        # Inject Home Assistant Auth into localStorage before page initialization
        hass_tokens_payload = json.dumps({
            "access_token": token,
            "token_type": "Bearer",
            "clientId": f"{ha_url}/",
            "hassUrl": ha_url,
            "expires": 4102444800000,
            "refresh_token": token
        })

        init_js = f"""
            window.localStorage.setItem('hassTokens', {json.dumps(hass_tokens_payload)});
            window.localStorage.setItem('dockedSidebar', '"auto"');
        """
        if theme:
            init_js += f"\nwindow.localStorage.setItem('selectedTheme', JSON.stringify('{theme}'));"

        context.add_init_script(init_js)

        page = context.new_page()

        try:
            # Navigate to the dashboard
            page.goto(url, wait_until="networkidle", timeout=20000)
        except Exception as e:
            # If networkidle times out due to persistent websockets or streams, proceed
            print(f"⚠️  Note: Initial network idle timed out ({e}), proceeding with render check...")

        # Wait for Bubble Card and custom web components to settle animations
        print(f"⏳ Waiting {wait_sec}s for Bubble Card elements & transitions to settle...")
        time.sleep(wait_sec)

        # Save screenshot
        page.screenshot(path=output_file, full_page=full_page)
        browser.close()

    print(f"✅ Screenshot saved successfully: {output_file}")
    return output_file

def grab_live_tablet(entity_id="image.huawei_mediapad_m5_lite_10_screenshot", output_file=None):
    """Fetches real-time hardware screen capture directly from tablet screenshot entity in HA."""
    ha_url, token = get_ha_config()
    if not token:
        print("❌ Error: No Home Assistant access token found.", file=sys.stderr)
        sys.exit(1)

    if not output_file:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(script_dir, ".."))
        screenshots_dir = os.path.join(repo_root, "dashboards", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        output_file = os.path.join(screenshots_dir, "real_tablet_live.png")

    print(f"📡 Fetching live screen directly from physical tablet entity in Home Assistant...")
    print(f"   Entity: {entity_id}")
    url = f"{ha_url}/api/image_proxy/{entity_id}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            with open(output_file, "wb") as f:
                f.write(data)
        print(f"✅ Real hardware screenshot saved: {output_file} ({len(data)} bytes)")
        return output_file
    except Exception as e:
        print(f"❌ Failed to fetch live tablet screenshot: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Home Assistant Dashboard Screenshot Tool")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Fetch real-time hardware screen capture directly from tablet entity (image.huawei_mediapad_m5_lite_10_screenshot)"
    )
    parser.add_argument(
        "--path",
        default="bubble-kiosk-dashboard/Home",
        help="Dashboard path (e.g. bubble-kiosk-dashboard/Home, lovelace/0)"
    )
    parser.add_argument(
        "--preset",
        choices=list(PRESETS.keys()),
        default="tablet",
        help="Display resolution preset (default: tablet)"
    )
    parser.add_argument("--width", type=int, help="Override width in pixels")
    parser.add_argument("--height", type=int, help="Override height in pixels")
    parser.add_argument("--scale", type=float, help="Device scale factor / DPI (e.g. 1.0, 1.5, 2.0)")
    parser.add_argument("--wait", type=float, default=2.5, help="Wait time in seconds after load (default: 2.5)")
    parser.add_argument("--no-kiosk", action="store_true", help="Disable ?kiosk URL parameter")
    parser.add_argument("--theme", help="Optional theme override (e.g. tablet_kiosk_theme)")
    parser.add_argument("--output", help="Custom output image file path")
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page instead of viewport")
    parser.add_argument("--list-presets", action="store_true", help="List available resolution presets")

    args = parser.parse_args()

    if args.list_presets:
        print("Available Display Presets:")
        for name, info in PRESETS.items():
            print(f" - {name:15} : {info['width']}x{info['height']} (scale {info['scale']}) - {info['desc']}")
        sys.exit(0)

    if args.live:
        grab_live_tablet(output_file=args.output)
        sys.exit(0)

    take_screenshot(
        dashboard_path=args.path,
        preset=args.preset,
        width=args.width,
        height=args.height,
        scale=args.scale,
        wait_sec=args.wait,
        kiosk=not args.no_kiosk,
        theme=args.theme,
        output_file=args.output,
        full_page=args.full_page
    )

if __name__ == "__main__":
    main()
