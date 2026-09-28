# Home Assistant Architecture & Subsystem Guide

This repository contains the declarative Home Assistant Core configuration for the house. It is designed around modularity, package-based domain isolation, predictable state contracts, and humane automation principles.

---

## 🏛️ Architectural Topology & Directory Structure

Configuration is dynamically assembled via Home Assistant Packages using `homeassistant.packages: !include_dir_named include` in [`configuration.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/configuration.yaml).

```
├── configuration.yaml         # Core bootstrapping, recorder, tts, lovelace definitions
├── automations.yaml           # Reserved exclusively for HA UI editor (keep empty list [])
├── scripts.yaml / scenes.yaml # Reserved for UI-managed scripts and scenes
├── secrets.yaml               # Encrypted/private credentials and URLs (!secret)
├── GEMINI.md                  # Operational AI agent rules and invariant directives
└── include/                   # Dynamic package hierarchy (all real logic lives here)
    ├── automations/<area>/    # Room & area automations (<area>_<purpose>.yaml)
    ├── input/                 # Helpers (input_boolean, input_datetime, input_number)
    ├── scripts/               # Reusable action sequences and pipelines
    ├── template/              # Calculated sensors, lights, and sidebar widgets
    ├── sensor/                # Integration sensors (power, persistence, humidity)
    ├── utility_meter/         # Cyclic energy meters (daily, monthly tracking)
    ├── light/ & cover/        # Group and cover platform definitions
    └── themes/                # Dashboard theme styling
```

> [!IMPORTANT]
> **No Automations in Root**: Never add automations to root `automations.yaml`. Always place automations in `include/automations/<area>/<area>_<purpose>.yaml`.

---

## ⚙️ Core House Subsystems & Contracts

### 1. Presence Engine Contract
Presence is tracked through a dual-layer model separating physical location from house wakefulness:
- **`input_boolean.presence_home`**:
  - `on` = Residents are home and **awake**.
  - `off` = Residents are **away or sleeping**.
- **`group.residents`**: Real-time GPS location tracking for residents.
- **Synchronization**: Managed by [`home_presence_detection.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/home/home_presence_detection.yaml). When GPS detects everyone left, `presence_home` flips to `off`. When arriving home, it flips to `on`. Bedside wall switches toggle `presence_home` to signal sleeping/waking without waiting for GPS changes.

### 2. Audio & Voice Notification Pipeline
Spoken house notifications follow a strict pipeline to prevent startling residents or clipping media:
- **Central Dispatcher**: All spoken announcements route through [`script.play_media_tts_message`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/play_media_tts_message.yaml).
- **Volume Safety**: Caches existing speaker volume, applies a presence-aware limit (20% when sleeping/away, 40% when awake), plays the message, and restores original volume.
- **Bilingual Support**: Announcements play in German, followed conditionally by Chinese if `input_boolean.home_chinese_tts_enabled` is active.
- **AI Briefings**: The morning and evening briefings leverage [`play_media_tts_gemini.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/play_media_tts_gemini.yaml) to synthesize dynamic, natural status updates.

### 3. Circadian & Anti-Blinding Lighting
- **Anti-Blinding Standard**: Dimmable lights call [`script.light_low_before_off`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/light_low_before_off.yaml) before powering off. This transitions the fixture to minimum brightness / red hue before cutting power, ensuring that subsequent turn-ons never produce a blinding flash.
- **Occupancy Modes**: When motion triggers below the horizon:
  - `presence_home: on` $\rightarrow$ Warm ambient illumination (e.g. 50% brightness, amber hue).
  - `presence_home: off` $\rightarrow$ Ultra-dim red nightlight (e.g. 2% brightness, pure red) to preserve night vision.
- **Wall Switch Ergonomics**:
  - *Single tap*: Toggles local fixture state or brightness levels.
  - *Hold*: Activates house scenes (e.g., holding off activates Away/Bedtime scene).

### 4. Climate & Window Synchronization
- **HVAC Interlock**: Opening any exterior window immediately shuts off the corresponding room thermostat to eliminate wasted energy. Closing the window restores thermostat operation.
- **Caring Humidity Feedback**: Window opening and closing events trigger contextual TTS feedback, evaluating ambient humidity against comfort thresholds (`input_number.dashboard_humidity_threshold_*`) to gently advise when ventilation is sufficient.

### 5. Automated Vacuum Cleaning
- Configured via [`home_vacuum_cleaning.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/home/home_vacuum_cleaning.yaml) and [`vacuum_start.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/vacuum_start.yaml).
- Runs once per calendar day at `input_datetime.vacuum_cleaning_time`.
- Checks individual room cleaning helper switches; if any are active, cleans only those rooms and resets their toggles; otherwise performs a complete house cleaning.

---

## 📐 Coding & Commenting Standard

Every automation, script, and template file conforms to this standardized structure:

```yaml
automation:
  # ====================================================================
  # <Area> - <Name>
  # - <Summary bullet 1: trigger and primary action>
  # - <Summary bullet 2: key conditions, variables, or edge case handling>
  # ====================================================================

  - id: "<area>_<action_name>"
    alias: "<Area> - <Name>"
    mode: single

    trigger:
      # Clear trigger label
      - trigger: state
        entity_id: ...

    condition: []

    action:
      # Logical block label
      - action: ...
```

### Critical Development Rules:
1. **Modern Syntax**: Use `action:` (never deprecated `service:`), `trigger:` (never `platform:` in automations).
2. **Safe Jinja Filters**: Always supply fallback defaults to numeric filters (e.g. `| float(0)`, `| int(0)`).
3. **SMB Performance**: The workspace is mounted over SMB. Avoid recursive full-disk scans or grep searches; inspect specific target folders directly.
4. **Secrets**: Never commit credentials, URLs, or personal identifiers inline; always use `!secret <name>`.

