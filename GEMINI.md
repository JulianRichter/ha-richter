# Home Assistant Project Rules
- This is a Home Assistant Core configuration repository.
- Always generate valid Home Assistant YAML with strict 2-space indentation.
- Never write credentials inline; reference `!secret <secret_name>` instead.
- Use modern Home Assistant syntax (`action:` instead of deprecated `service:`, `trigger:` for triggers).
- When writing templates, use standard Jinja2 syntax compatible with HA templating and always provide default filters (e.g. `| float(0)`, `| int(0)`).
- Do not attempt to modify binary database files or files ignored by `.geminiignore`.
- Workspace is on a remote SMB network mount without git: avoid slow recursive directory scans; target specific folders directly.

# Architecture & Directory Topology
- Packages pattern: Core configuration dynamically loads packages via `homeassistant.packages: !include_dir_named include`.
- NEVER add automations to root `automations.yaml` (reserved for HA UI editor).
- Directory assignments:
  - Automations: `include/automations/<area>/<area>_<purpose>.yaml`
  - Helpers (`input_boolean`, `input_datetime`, `input_number`, etc.): `include/input/input_<area>.yaml`
  - Scripts: `include/scripts/<script_name>.yaml`
  - Template entities: `include/template/`
  - Sensors & Utility meters: `include/sensor/`, `include/utility_meter/`
  - Themes & Dashboards: `themes/`, `dashboards/`
- Entity Lookup Index: Consult [`docs/memory/entities.md`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/docs/memory/entities.md) for verified entity IDs across all areas and domains. Do not guess entity IDs.

# Developer Verification & Safety Tooling
- Pre-Flight Validation: Before concluding any change, ALWAYS run `python3 tools/validate_config.py` to verify YAML syntax, secrets, scripts, and header consistency.
- Safety Snapshot: Before performing large refactors across multiple files, run `bash tools/backup_config.sh`.

# Core House Subsystem Contracts
- Presence Contract:
  - `input_boolean.presence_home`: `on` = home & awake, `off` = away or sleeping.
  - `group.residents`: Tracks GPS presence. Synchronized via `home_presence_detection.yaml`.
- Audio & TTS Pipeline:
  - Do NOT call `tts.speak` or `media_player` directly for spoken alerts.
  - Always route through `script.play_media_tts_message` (or room-specific wrappers) to support automatic volume ducking/restoration, day/night volume limits, and bilingual German/Chinese announcements.
  - Spotify & Music Assistant: Voice/Cast playback on speakers is automatically intercepted by `home_spotify_to_music_assistant.yaml` to hand over playback to Music Assistant. 1-click resumption routes through `script.media_resume_last_played`.
- Lighting & Anti-Blinding:
  - When dimmable/ambient lights are turned off, route or call `script.light_low_before_off` to prevent bright flash on the next turn-on.
  - Wall switches: single press toggles primary state; hold activates secondary scene or overrides.
- Climate & Windows:
  - Window contacts interlock with thermostats (shut off while open, restore when closed) and trigger caring humidity guidance.

# Code Style & Commenting Standard
- For every Script, Action, or Automation, include a standardized header at the top:
  ```yaml
  # ====================================================================
  # <Area> - <Name>
  # - <Concise summary of trigger/purpose>
  # - <Key behavior, conditions, or edge case handling>
  # ====================================================================
  ```
- Add one-liner comment sections before every logical block (triggers, conditions, choose branches, actions).
- Focus on clean, readable, self-documenting code.

