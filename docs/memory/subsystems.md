# System Memory: Core House Subsystems

This document preserves operational knowledge and architectural invariants for Home Assistant. Consult this memory file when modifying cross-cutting house features.

---

## 1. Presence Engine Contract
- **State Definition**:
  - `input_boolean.presence_home = on`: Home & Awake. Normal daytime lighting, 40% announcement volume, automatic motion triggers enabled.
  - `input_boolean.presence_home = off`: Away or Sleeping. Red/dim night lights, 20% announcement volume limit, motion lights use ultra-dim nightlight mode.
- **Synchronization & Single Source of Truth**:
  - `input_boolean.presence_home` is the sole source of truth for home/away status (`on` = home & awake, `off` = away or sleeping).
  - `switch.presence_away` is an interactive template switch in [`include/template/template_presence.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/template/template_presence.yaml) whose state is the exact inverse of `presence_home`. Toggling it on the Bubble Card dashboard directly controls `presence_home`.
  - [`include/automations/home/home_presence_detection.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/home/home_presence_detection.yaml) synchronizes `group.residents` (GPS trackers for Julian & Xingyang) with manual wall switches and `presence_home` without needing sync loops or mirror helpers.

---

## 2. Audio & TTS Pipeline
- **Never call `tts.speak` directly in automations**:
  - Route through [`script.play_media_tts_message`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/play_media_tts_message.yaml).
- **Behavioral Pipeline**:
  1. Caches the current speaker volume.
  2. Sets temporary volume based on house state (0.2 if sleeping/away, 0.4 if awake, or custom override).
  3. Plays German announcement via Google Cloud TTS.
  4. If `input_boolean.home_chinese_tts_enabled` is on, waits for German playback to finish and plays Chinese translation (`cmn-CN-Chirp3-HD-Achernar`).
  5. Restores original speaker volume.
- **Gemini AI Conversation & Briefing Integration**:
  - Direct integration via official Google Generative AI (`conversation.google_ai_conversation`) enabling fast, direct LLM generation in Home Assistant.
  - Generative alerts and summaries route through [`script.play_media_tts_gemini`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/play_media_tts_gemini.yaml).
  - **Execution Flow**:
    1. Caller automation passes Jinja2 template containing live sensor context (weather, tram departures, washer status, calendar) as `prompt`.
    2. Calls `conversation.process` on `conversation.google_ai_conversation`.
    3. Handles errors/timeouts gracefully with `continue_on_error: true` and spoken fallback (`error_message`).
    4. Hands off the synthesized plain text to `script.play_media_tts_message` for volume ducking, speaker routing, and Chinese TTS if enabled.
  - **Active Briefings & Spoken Alerts**:
    - Morning briefing: [`include/automations/home/home_morning_briefing_julian.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/home/home_morning_briefing_julian.yaml).
    - Evening briefing: [`include/automations/home/home_evening_briefing_julian.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/home/home_evening_briefing_julian.yaml).
    - Rain alert: [`include/automations/home/home_rain_announcement.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/home/home_rain_announcement.yaml) (~2h before rain, living room speaker, only when awake).
  - **Bedtime Routine Contract**:
    - Dedicated automation in [`include/automations/bedroom/bedroom_bedtime_routine.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/bedroom/bedroom_bedtime_routine.yaml).
    - Triggers when Julian's phone is charging AND `light.bedroom_light_left` turns off (between 22:00 and 06:00).
    - Transitions house to night presence (`presence_home = off`, `presence_away = on`), lowers thermostats to night setpoint, and smoothly turns off all remaining lights across living room, kitchen, bathroom, and baby room via `script.light_low_before_off`.

---

## 3. Lighting & Anti-Blinding Standard
- **The Retina Protection Rule**:
  - When turning off dimmable lights, call [`script.light_low_before_off`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/light_low_before_off.yaml).
  - Automatically differentiates RGB vs non-RGB fixtures: sets brightness to minimum (default 5 via `input_number.light_brightness_sleep`) and color to red (`input_text.light_color_sleep`) for RGB lights, or brightness-only for non-RGB fixtures (kitchen/bathroom).
  - Supports optional `transition` parameter (e.g. 15s slow fade for motion clearance, 0s/fast for switches) before cutting power.
  - Ensures that when lights are next switched on physically or via default automation, they never flash at 100% white into a dark room.
- **Centralized Lighting Helpers**:
  - `input_number.light_brightness_sleep` (default: 5)
  - `input_number.light_brightness_awake` (default: 126)
  - `input_number.light_brightness_high` (default: 255)
  - `input_text.light_color_sleep` (default: 255,0,0)
  - `input_text.light_color_awake` (default: 255,166,87)
- **Motion Triggered Lights (Kitchen & Bathroom)**:
  - Motion active + `presence_home == on` $\rightarrow$ Daytime / full light (`light_brightness_high`).
  - Motion active + `presence_home == off` $\rightarrow$ Dim nightlight (`light_brightness_sleep`).
  - Motion cleared $\rightarrow$ Slow 15s fade-out via `script.light_low_before_off` (1s if already dim).
- **Wall Switch Single-Press Cycling**:
  - 1st press when OFF: Always turns on in dim/warm ambient mode first (`brightness_awake` / `color_awake`). Anti-blinding guaranteed.
  - 2nd press when ON (dim): Steps up to full daylight brightness (`brightness_high`, 2000K).
  - 3rd press when ON (full): Toggles back down to dim/warm mode.
  - Down press: Smoothly dims and turns off via `script.light_low_before_off`.

---

## 4. Climate & Window Interlocks
- **Window Sensors**:
  - Opening a window contact (`binary_sensor.<room>_window_contact`) turns off the room's radiator valve (`climate.<room>_thermostat`) to prevent wasted heat.
  - Closing the window contact restores thermostat heating.
- **Caring Humidity Feedback**:
  - Window open/close events invoke [`script.play_media_tts_window_opened`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/play_media_tts_window_opened.yaml) and [`script.play_media_tts_window_closed`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/play_media_tts_window_closed.yaml).
  - If ambient humidity exceeds `input_number.dashboard_humidity_threshold_medium`, caring TTS advises airing out or closing windows when optimal.

---

## 5. Roborock Vacuum Cleaning Dispatch
- **Schedule**: [`home_vacuum_cleaning.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/home/home_vacuum_cleaning.yaml) triggers at `input_datetime.vacuum_cleaning_time`.
- **Logic**:
  - Restricts dispatch to once per calendar day (`last_triggered.date() != now().date()`).
  - Calls [`script.vacuum_start`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/vacuum_start.yaml).
  - If individual room toggles (`input_boolean.vacuum_clean_*`) are active, cleans only those rooms and resets their toggles; otherwise defaults to full house clean.
  - Determines sweeping vs sweeping+mopping via `input_boolean.vacuum_mopping_enabled`.

---

## 6. Public Transit (Tram 1 Curtiusstraße)
- **Primary Source Entities**:
  - Inbound (Göggingen / Königsplatz): `sensor.augsburg_curtiusstrasse_koenigsplatz`
  - Outbound (Lechhausen N. Ostfriedhof): `sensor.augsburg_curtiusstrasse_lechh_n_ostfriedh`
- **Derived Template Helpers**:
  - `sensor.tram_1_konigsplatz_walk_status`: Dynamic walking departure recommendation (calibrated to 4 min walk).
  - `sensor.tram_1_lechhausen_walk_status`: Northbound walking status.
- **Dashboard Display**:
  - Live footer button in `dashboards/bubble_code/bubble_code.yaml` with `.bubble-state` countdowns: `Kö: Xm | Ost: Ym`.
  - Detailed modal pop-up (`#bubble_tram_popup`) with full departure boards for Platforms e and a.

---

## 7. Music Assistant & Spotify Pipeline
- **Playback Architecture**:
  - Google Home speakers (`media_player.*_cast`) run the native Spotify Cast receiver when initiated by voice or Spotify Connect.
  - [`home_spotify_to_music_assistant.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/home/home_spotify_to_music_assistant.yaml) intercepts playback:
    - Resolves active Spotify playlist or track URI from `media_player.spotify_julian`.
    - Handshakes playback directly to Music Assistant player entities (`media_player.living_room`, `media_player.kitchen`, etc.).
    - Queues full playlist or enables radio mode for single tracks, preserving shuffle.
    - Ensures clean playback resilience across TTS speech ducking and notifications.
- **1-Click Resume & Memory**:
  - Automation [`home_media_last_played.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/home/home_media_last_played.yaml) captures the latest Spotify playlist, track, artist, cover art, and speaker to `input_text.last_played_*`.
  - Script [`script.media_resume_last_played`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/media_resume_last_played.yaml) allows 1-click resumption through Music Assistant on the dashboard `#bubble_media_popup`.


