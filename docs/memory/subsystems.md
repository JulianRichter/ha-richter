# System Memory: Core House Subsystems

This document preserves operational knowledge and architectural invariants for Home Assistant. Consult this memory file when modifying cross-cutting house features.

---

## 1. Presence Engine Contract
- **State Definition**:
  - `input_boolean.presence_home = on`: Home & Awake. Normal daytime lighting, 40% announcement volume, automatic motion triggers enabled.
  - `input_boolean.presence_home = off`: Away or Sleeping. Red/dim night lights, 20% announcement volume limit, motion lights use ultra-dim nightlight mode.
- **Synchronization**:
  - Automations in [`include/automations/home/home_presence_detection.yaml`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/automations/home/home_presence_detection.yaml) synchronize `group.residents` (GPS trackers for Julian & Xingyang) with manual wall switches and dashboard toggles (`input_boolean.presence_home` & `presence_away`).
  - Condition filters ignore echo sync loops between `presence_home` and `presence_away`.

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
- **AI Briefings**:
  - Morning and evening briefings call [`script.play_media_tts_gemini`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/play_media_tts_gemini.yaml), which passes structured sensor prompts to the Gemini conversation agent and speaks the summarized response.

---

## 3. Lighting & Anti-Blinding Standard
- **The Retina Protection Rule**:
  - When turning off dimmable lights, call [`script.light_low_before_off`](file:///run/user/1000/gvfs/smb-share:server=192.168.178.100,share=config/include/scripts/light_low_before_off.yaml).
  - This sets brightness to 1 and color to red before cutting power, ensuring that when the light is next switched on physically or via default automation, it never flashes at 100% white into a dark room.
- **Motion Triggered Lights**:
  - Motion active + Sun down + `presence_home == on` $\rightarrow$ Warm ambient amber light (brightness 126).
  - Motion active + Sun down + `presence_home == off` $\rightarrow$ Dim red nightlight (brightness 5).
  - Motion cleared $\rightarrow$ Turn off smoothly via `script.light_low_before_off`.

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


