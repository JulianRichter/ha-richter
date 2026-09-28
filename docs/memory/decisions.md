# System Memory: Architectural Decisions (ADR)

This document records the foundational architectural decisions made for this Home Assistant repository to prevent regressions and guide future configuration changes.

---

## ADR 01: Packages-Based Configuration Pattern
- **Status**: Accepted & Invariant
- **Context**: The standard monolithic `configuration.yaml` / `automations.yaml` approach becomes unmaintainable as entity counts grow beyond 100.
- **Decision**: All entities, helpers, scripts, and automations are organized into modular domain packages within `include/` using `packages: !include_dir_named include`.
- **Consequences**:
  - Automations must NEVER be placed in root `automations.yaml` (reserved exclusively for the HA UI editor).
  - New areas/rooms must follow `include/automations/<area>/<area>_<purpose>.yaml`.

---

## ADR 02: Centralized Voice & Notification Routing
- **Status**: Accepted & Invariant
- **Context**: Calling `tts.speak` or `media_player` directly causes harsh volume spikes at night, interrupts ongoing media without resuming, and makes multilingual announcements difficult.
- **Decision**: All spoken voice messages must route through [`script.play_media_tts_message`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/play_media_tts_message.yaml).
- **Consequences**:
  - Guarantees volume ducking (20% sleep / 40% awake) and restoration.
  - Automatically handles optional Chinese audio when enabled.

---

## ADR 03: Dimmable Light Low-Before-Off Pattern
- **Status**: Accepted & Invariant
- **Context**: Many smart bulbs remember their last brightness/color. If switched off at 100% cool white, turning them on at 3 AM momentarily blinds residents before Home Assistant can apply circadian/night dimming.
- **Decision**: Turning off dimmable lights always executes [`script.light_low_before_off`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/light_low_before_off.yaml).
- **Consequences**: The light bulb hardware is pre-loaded with dim red hue at brightness 1 prior to cutting power.

---

## ADR 04: Bubble Card UI Architecture & CSS Scoping
- **Status**: Accepted & Invariant
- **Context**: The tablet interface uses Bubble Card v3 with Kiosk Mode for clean, modern wall-mounted control.
- **Decision**:
  - Modal interaction patterns use `#bubble_<subsystem>_popup` hash navigation.
  - Custom styling is applied via Bubble Card's native `styles:` block or scoped `card_mod` to avoid shadow-DOM piercing breakage across Home Assistant Core updates.

