# System Memory: Architectural Decisions & Patterns (ADR)

This document records the foundational architectural decisions (ADRs) and structural design patterns for this Home Assistant repository to prevent regressions, preserve system contracts, and guide future configuration changes.

---

## ADR 01: Packages-Based Configuration Pattern
- **Status**: Accepted & Invariant
- **Context**: The standard monolithic `configuration.yaml` / `automations.yaml` approach becomes unmaintainable as entity counts grow beyond 100.
- **Decision**: All entities, helpers, scripts, and automations are organized into modular domain packages within `include/` using `packages: !include_dir_named include`.
- **Consequences**:
  - Automations must NEVER be placed in root `automations.yaml` (reserved exclusively for the HA UI editor).
  - New areas/rooms must follow `include/automations/<area>/<area>_<purpose>.yaml`.
  - Helpers reside in `include/input/input_<area>.yaml`.

---

## ADR 02: Centralized Voice & Notification Routing
- **Status**: Accepted & Invariant
- **Context**: Calling `tts.speak` or `media_player` directly causes harsh volume spikes at night, interrupts ongoing media without resuming, and makes multilingual announcements difficult.
- **Decision**: All spoken voice messages must route through [`script.play_media_tts_message`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/play_media_tts_message.yaml).
- **Consequences**:
  - Guarantees automatic volume ducking (20% sleeping or away / 40% awake) and restoration.
  - Automatically handles optional bilingual Chinese audio (`input_boolean.home_chinese_tts_enabled`).

---

## ADR 03: Dimmable Light Low-Before-Off Pattern
- **Status**: Accepted & Invariant
- **Context**: Many smart bulbs remember their last brightness/color. If switched off at 100% cool white, turning them on at 3 AM momentarily blinds residents before Home Assistant can apply circadian/night dimming.
- **Decision**: Turning off dimmable lights always executes [`script.light_low_before_off`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/light_low_before_off.yaml).
- **Consequences**: The light bulb hardware is pre-loaded with dim red hue at brightness 1 prior to cutting power.

---

## ADR 04: Bubble Card UI Architecture & CSS Scoping
- **Status**: Accepted & Invariant
- **Context**: The tablet and desktop interface uses Bubble Card v3 with Kiosk Mode for clean, modern wall-mounted control.
- **Decision**:
  - Modal interaction patterns use `#bubble_<subsystem>_popup` hash navigation.
  - Custom styling is applied via Bubble Card's native `styles:` block or scoped `card_mod` to avoid shadow-DOM piercing breakage across Home Assistant Core updates.
  - Dashboard architecture:
    - `dashboards/bubble_code/bubble_code.yaml` (`theme: bubble_code_theme`): Primary dashboard interface for wall-mounted tablet and desktop.
  - **Bubble Card Modules Architecture (`bubble_card/modules/`)**:
    - Backend Integration: Powered by [`custom_components/bubble_card_tools`](custom_components/bubble_card_tools/) to enable persistent, local, file-backed module storage.
    - Module Storage: Modules reside as individual YAML files under `bubble_card/modules/<module_name>.yaml` and are fully tracked in Git.
    - Reusability Contract: Instead of inline 20-60 line `styles:` blocks duplicated across cards and dashboards, cards reference shared modules via `modules: [<module_name>]`.
    - **Module Input Arguments / Configuration Parameters**:
      - Modules support user-configurable parameters accessed in JS code via `this.config.<module_id>?.<param_name>`.
      - All badge modules declare an `editor:` schema with a `position` dropdown (`top-right`, `top-left`, `bottom-right`, `bottom-left`).
      - In dashboard YAML, cards can optionally override defaults by adding `<module_id>: position: top-left` directly under the card configuration.
    - Active Module Catalog:
      - `person_home_badge`: Circular presence badge over avatar picture with `mdi:home` icon and theme accent color; conditionally rendered only when person is `home` (supports `position: top-right|top-left|bottom-right|bottom-left`).
      - `room_window_badge`: Circular alert badge on room card icons with `mdi:window-open-variant` icon in sky blue (`#0284c7`); conditionally rendered only when the room's window contact (`binary_sensor.<room>_window_contact`) is `on` (supports `position: top-right|top-left|bottom-right|bottom-left`).
      - `washer_done_badge`: Circular reminder badge on bathroom card icon with `mdi:washing-machine` icon in emerald green (`#10b981`); conditionally rendered when laundry cycle is done (`input_boolean.bathroom_laundry` is `on`) (supports `position: top-right|top-left|bottom-right|bottom-left`).
      - `dishwasher_done_badge`: Circular reminder badge on kitchen card icon with `mdi:dishwasher` icon in emerald green (`#10b981`); conditionally rendered when dishwasher is done (`input_boolean.kitchen_dishwasher_done` is `on`) (supports `position`, defaults to 2 o'clock and auto-shifts to 4 o'clock if window is open).
      - `vacuum_attention_badge`: Circular alert badge on vacuum cards with `mdi:alert` icon in red (`#ef4444`); conditionally rendered when Robi has an error, low water, or requires user attention (supports `position: top-right|top-left|bottom-right|bottom-left`).
      - `climate_heating_badge`: Circular status badge on climate cards with `mdi:fire` icon in warm orange (`#f97316`); conditionally rendered when any thermostat in the house is calling for heat (supports `position: top-right|top-left|bottom-right|bottom-left`).
      - `room_battery_badge`: Circular warning badge on room card icons with `mdi:battery-alert` icon in amber (`#f59e0b`); conditionally rendered when any sensor in that room reports low battery (supports `position: top-left|top-right|bottom-left|bottom-right`).
      - `room_motion_badge`: Minimalist motion indicator dot located at the bottom center of the room icon container in soft glowing indigo (`#818cf8`); conditionally rendered when room motion sensors are active, with multi-sensor room aggregation for bathroom and bedroom, automatic cleanup on clear, and tooltip indicator. Harmoniously balances with top-left battery and top-right window/appliance badges.
      - `bubble_header_separator`: Standardized typography (`font-size: var(--dashboard-header-font-size)`, `font-weight: var(--dashboard-header-font-weight)`) for section separators.
      - `bubble_sidebar_notification`: Handles typography, transparent background, and dynamic auto-collapse height calculation (`fontSize` + `lineHeight * count`) for multi-line sidebar notifications.
      - `bubble_room_climate`: Dynamically inspects room light entity, formats room multi-sensor `Temp C° | Hum %` in `.bubble-state`, and applies threshold warning color when humidity is high.
      - `bubble_footer_button`: Standardized typography, opacity, and text ellipsis truncation for bottom launcher buttons.
  - **CSS Scoping Invariants**:
    - Global Theme Borders: Never set `ha-card-border-width: 1px` or global `ha-card-box-shadow` on the theme root; Bubble Card separator headers, markdown cards, and sidebar containers inherit `ha-card` and will render unwanted border outlines. Card borders must be applied strictly to specific interactive card containers via `bubble-border` or card-level `card_mod`.
    - Active Button Badges: On bright/vibrant active button cards, the default icon background blends into the card background. Active buttons require `.is-on .bubble-icon-container { background-color: rgba(0, 0, 0, 0.28) !important; box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.15) !important; }` and `.is-on .bubble-icon { color: #ffffff !important; }`.
    - Mini Graph Card Humidity Visual Metaphor: Use `rgba(235, 77, 84, 0.1)` bad-zone card background with `#1db954` good-zone line to clearly contrast safe vs excessive moisture levels.
    - Decoupled Popup Controls: High-level room button cards (e.g. `Klima`) display live sensor telemetry (room temperature) and open modal popups, decoupled from lighting state toggles.

---

## ADR 05: Native Gemini AI Integration & Generative TTS Pipeline
- **Status**: Accepted & Invariant
- **Context**: Morning briefings, evening recaps, and dynamic notifications require natural, intelligent language synthesis conditioned on live home state (weather, transit delays, alarms, washer status) rather than static, robotic templates. Furthermore, direct external API calls scattered across automations cause token leaks, duplicate logic, and brittle failure modes.
- **Decision**: 
  - Integrate Gemini directly into Home Assistant via the official Google Generative AI integration (`google_generative_ai_conversation` $\rightarrow$ `conversation.google_ai_conversation`).
  - Standardize all AI generative voice interactions through [`script.play_media_tts_gemini`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/play_media_tts_gemini.yaml).
- **Consequences**:
  - Automations feed templated prompts containing live Jinja2 state data directly into `script.play_media_tts_gemini`.
  - The script queries `conversation.google_ai_conversation` via `conversation.process`, extracts speech text, catches timeout/error states, falls back to a friendly spoken error announcement if needed, and routes the final speech output through `script.play_media_tts_message`.
  - Full volume ducking, multi-room speaker targeting, and audio pipeline safety are preserved automatically.

---

## ADR 06: Headless Dashboard Screenshot & Visual Testing Pipeline
- **Status**: Accepted & Invariant
- **Context**: Designing dashboards for wall-mounted kiosks and mobile devices requires fast visual feedback, but manual physical verification on the mounted tablet is cumbersome. Live hardware screen captures (`image.huawei_mediapad_m5_lite_10_screenshot`) only work for the tablet (not desktop or phone) and cannot preview draft dashboards before loading them on the device. Furthermore, standard desktop browser rendering defaults to light mode and desktop system fonts (causing text clipping like "Curtiuss" instead of "Tram Curtiusst").
- **Decision**:
  - Maintain a dedicated headless automation tool [`tools/screenshot_dashboard.py`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/tools/screenshot_dashboard.py) powered by Playwright Chromium.
  - Automatically enforce `color_scheme="dark"` in the browser context to ensure dark theme backgrounds render correctly.
  - Match device display metrics and font rendering using local Roboto fonts (`~/.local/share/fonts/`) and calibrated presets:
    - `tablet`: `1130 × 706` CSS pixels @ `1.7x` scale (Huawei MediaPad M5 Lite 10).
    - `pc`: `1854 × 959` CSS pixels @ `1.0x` scale.
    - `phone`: `412 × 828` CSS pixels @ `2.6x` scale (Google Pixel 7 Pro).
  - Automatically authenticate using tokens from `~/.ha_token` (or `HA_TOKEN` env var) and run inside the isolated virtual environment (`~/.venvs/ha-tools/bin/python3`).
- **Consequences**:
  - Instant visual regression testing and iteration without physical device access.
  - Exact layout, line-wrapping, and color fidelity across mobile, tablet, and PC form factors.

---

## ADR 07: Live Home Assistant API Client & Token Management
- **Status**: Accepted & Invariant
- **Context**: Development occurs on a developer workstation where the `homeassistant` Python package is not installed and SSH commands cannot be run automatically. However, inspecting live entity states, checking system error logs, and forcing Lovelace frontend theme reloads is essential during development.
- **Decision**:
  - Implement a lightweight, zero-dependency REST client [`tools/ha_api.py`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/tools/ha_api.py).
  - Store the Home Assistant Long-Lived Access Token strictly outside the git/SMB repository at `~/.ha_token` (mode `600`) or via the `HA_TOKEN` environment variable.
  - Provide CLI operations: `check` (health & version), `state <entity_id>`, `states` (filtering by domain/search), `reload-lovelace` (triggering frontend theme reload), and `logs` (fetching `/api/error_log`).
- **Consequences**:
  - Zero risk of committing API tokens to the git repository or sharing them over network shares.
  - Fast, scriptable inspection of live entities and instant theme reloading directly from the terminal.
