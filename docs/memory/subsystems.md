# System Memory: Core House Subsystems

This document preserves operational knowledge and architectural invariants for Home Assistant. Consult this memory file when modifying cross-cutting house features.

---

## 1. Presence Engine Contract
- **State Definition**:
  - `input_boolean.presence_home = on`: Home & Awake. Normal daytime lighting, 40% announcement volume, automatic motion triggers enabled.
  - `input_boolean.presence_home = off`: Away or Sleeping. Red/dim night lights, 20% announcement volume limit, motion lights use ultra-dim nightlight mode.
- **Synchronization & Single Source of Truth**:
  - `input_boolean.presence_home` is the sole source of truth for home/away status (`on` = home & awake, `off` = away or sleeping).
  - `switch.presence_away` is an interactive template switch in [`include/template/template_presence.yaml`](include/template/template_presence.yaml) whose state is the exact inverse of `presence_home`. Toggling it on the Bubble Card dashboard directly controls `presence_home`.
  - [`include/automations/home/home_presence_detection.yaml`](include/automations/home/home_presence_detection.yaml) synchronizes `group.residents` (hybrid GPS & Wi-Fi trackers for Julian & Xingyang) with manual wall switches and `presence_home` without needing sync loops or mirror helpers.
  - **Hybrid Resident Tracking (GPS + Wi-Fi)**:
    - Companion App Wi-Fi SSID sensors (`sensor.julian_wifi_connection`, `sensor.xingyang_ssid`) feed template device trackers (`device_tracker.julian_wifi`, `device_tracker.xingyang_wifi` in [`include/template/template_presence.yaml`](include/template/template_presence.yaml)) matching home SSID (`Nudelauflauf`).
    - Adding these stationary trackers to `person.julian` and `person.xingyang` provides instant arrival detection (zero geofence lag) while GPS prevents false "away" triggers during phone Wi-Fi sleep at night.
- **Morning Auto-Wake & Sunrise Architecture**:
  - Scheduled Alarm: [`bedroom_morning_routine.yaml`](include/automations/bedroom/bedroom_morning_routine.yaml) (and [`baby_room_morning_routine.yaml`](include/automations/baby_room/baby_room_morning_routine.yaml)) handles gentle wake-up (sunrise light effect, blinds opening, and bedside TTS greeting) without turning on `presence_home`. This preserves dim nightlight behavior for motion sensors between alarm time and dawn.
  - Sunrise Wake-Up: [`home_presence_detection.yaml`](include/automations/home/home_presence_detection.yaml) automatically turns `presence_home = on` silently at astronomical sunrise if residents are home (`group.residents = home`), shifting thermostats to daytime setpoints and enabling daytime motion lighting brightness.

---

## 2. Audio & TTS Pipeline
- **Never call `tts.speak` directly in automations**:
  - Route through [`script.play_media_tts_message`](include/scripts/play_media_tts_message.yaml).
- **Behavioral Pipeline**:
  1. Caches the current speaker volume.
  2. Sets temporary volume based on house state (0.2 if sleeping/away, 0.4 if awake, or custom override).
  3. Plays German announcement via Google Cloud TTS.
  4. If `input_boolean.home_chinese_tts_enabled` is on, waits for German playback to finish and plays Chinese translation (`cmn-CN-Chirp3-HD-Achernar`).
  5. Restores original speaker volume.
- **Natural, Varied Phrasing Standard (Anti-Ear-Fatigue)**:
  - All automated voice feedback scripts ([`play_media_tts_window_opened`](include/scripts/play_media_tts_window_opened.yaml), [`play_media_tts_window_closed`](include/scripts/play_media_tts_window_closed.yaml), [`play_media_tts_humidity_warning`](include/scripts/play_media_tts_humidity_warning.yaml), [`play_media_tts_shower_warning`](include/scripts/play_media_tts_shower_warning.yaml), [`play_media_tts_washer_humidity`](include/scripts/play_media_tts_washer_humidity.yaml), [`play_media_tts_person_zone`](include/scripts/play_media_tts_person_zone.yaml), [`play_media_tts_dishwasher`](include/scripts/play_media_tts_dishwasher.yaml), [`play_media_tts_laundry`](include/scripts/play_media_tts_laundry.yaml)) use an 8-variant randomized pool with concise, natural phrasing.
  - Avoids patronizing or repetitive clichés; maintains intelligent, calm butler-like demeanor in German and Chinese.
- **Gemini AI Conversation & Briefing Integration**:
  - Direct integration via official Google Generative AI (`conversation.google_ai_conversation`) enabling fast, direct LLM generation in Home Assistant.
  - Generative alerts and summaries route through [`script.play_media_tts_gemini`](include/scripts/play_media_tts_gemini.yaml).
  - **TTS Sanitization**: Automatic Jinja2 sanitization filters out Markdown asterisks (`**`), hashtags (`#`), backticks, and quotation marks before audio synthesis.
  - **The JARVIS Persona Standard**:
    - Calm, cultured, concise, and subtly witty (inspired by Tony Stark's JARVIS).
    - High information density, zero cheesy exclamation marks, no radio-DJ cheerfulness, no motivational slogans.
    - No names spoken: Never addresses the user by name (no "Julian", no "Sir"); direct "du" form only without names.
    - Spoken numbers/times written out phonetically ("halb drei", "achtzehn Grad", never raw colons "14:30").
  - **Active Briefings & Spoken Alerts**:
    - Morning briefing: [`include/automations/home/home_morning_briefing_julian.yaml`](include/automations/home/home_morning_briefing_julian.yaml) (Pixel Watch charging + bathroom motion; includes weather-adapted clothing recommendation and resilient fallback reporting for tasks/calendar).
    - Evening briefing: [`include/automations/home/home_evening_briefing_julian.yaml`](include/automations/home/home_evening_briefing_julian.yaml) (18:00 daily, living room; resilient fallback for tasks/calendar).
    - Rain alert: [`include/automations/home/home_rain_announcement.yaml`](include/automations/home/home_rain_announcement.yaml) (~2h before rain, living room speaker, only when awake).
- **Bedtime Routine & Master Light Shut-off Contract**:
  - Handled directly via bedside wall switches ([`bedroom_light_switch_left.yaml`](include/automations/bedroom/bedroom_light_switch_left.yaml) and [`bedroom_light_switch_right.yaml`](include/automations/bedroom/bedroom_light_switch_right.yaml)).
  - Hold Down transitions house to night presence (`presence_home = off`, triggering climate setback).
  - 2-Tier Shut-off:
    - If bedroom lights are on: smoothly dims and turns off bedroom lights (`bedroom_light_left`, `bedroom_light_right`, `bedroom_light_sphere`).
    - If bedroom lights are already off: executes master shut-off across all lights in the home (`light.all_lights_group`) and spot switch (`switch.living_room_spot_lights`).

---

## 3. Lighting & Anti-Blinding Standard
- **The Retina Protection Rule**:
  - When turning off dimmable lights, call [`script.light_low_before_off`](include/scripts/light_low_before_off.yaml).
  - Automatically differentiates RGB vs non-RGB fixtures: sets brightness to minimum (default 5 via `input_number.light_brightness_sleep`) and color to red (`input_text.light_color_sleep`) for RGB lights, or brightness-only for non-RGB fixtures (kitchen/bathroom).
  - Supports optional `transition` parameter (e.g. 15s slow fade for motion clearance, 0s/fast for switches) before cutting power.
  - Ensures that when lights are next switched on physically or via default automation, they never flash at 100% white into a dark room.
- **Centralized Lighting Helpers**:
  - `input_number.light_brightness_sleep` (default: 5)
  - `input_number.light_brightness_awake` (default: 126, used by wall switches)
  - `input_number.light_brightness_high` (default: 255, used by wall switches & voice commands)
  - `input_number.light_brightness_motion` (default: 200, used by motion automations)
  - `input_text.light_color_sleep` (default: 255,0,0)
  - `input_text.light_color_awake` (default: 255,166,87)
- **Motion Triggered Lights (Living Room, Baby Room, Bedroom)**:
  - Motion active + `presence_home == on` → Ambient motion light (`light_brightness_motion` = 200).
  - Motion active + `presence_home == off` → Dim nightlight (`light_brightness_sleep` = 5, red if RGB).
  - Motion turn-on contract: Only turns on if target light is `off` or recovering from a clearance fade (`<= light_brightness_sleep` when awake). Lights already on at motion or manual brightness are never modified or re-triggered.
  - Motion clearance contract: When motion clears, lights only turn off if currently at `light_brightness_motion` (`200`) or `<= light_brightness_sleep` (`5`).
  - Manual override contract: Wall switches turn on at 126 (`brightness_awake`) or 255 (`brightness_high`), and voice commands default to 255. Because manual/voice brightness differs from motion brightness, manual interaction automatically overrules motion automations and prevents lights from shutting off when motion clears.
  - Room ambient interlocks: Living room motion lighting suppresses if `switch.living_room_spot_lights` is active. Bedroom motion bedside lights suppress if decorative `light.bedroom_light_sphere` is active.
  - Automation mode: All motion automations use `mode: restart` so re-entering during a clearance fade immediately cancels the fade and restores illumination.
  - Motion cleared → Slow 15s fade-out via `script.light_low_before_off` (1s if already dim; power cut-off is guarded to only turn off lights that are still `<= light_brightness_sleep`).
- **Kitchen & Bathroom Instant Motion & Transition Contract**:
  - `light_low_before_off` is omitted for kitchen and bathroom lights; they turn on and off instantly without transition so there is no split-second ramp-up delay upon entering.
  - When motion clears, the light turns off immediately (`light.turn_off` without transition), preserving its last set brightness in bulb memory for the next activation.
  - Presence mode transitions: If kitchen or bathroom lights are already on when `presence_home` changes state, they smoothly cross-fade over a 10-second transition:
    - Night/Away → Home/Awake: Kitchen ramps smoothly to `brightness_high` (255); Bathroom ramps to `brightness_motion` (200).
    - Home/Awake → Night/Away: Both ramp smoothly to `brightness_sleep` (5).
- **Kitchen Motion & Switch Exception (Fallback Contract)**:
  - Wall switch and motion sensor share the same brightness (`light_brightness_high` = 255) when awake (`light_brightness_sleep` = 5 when asleep).
  - The kitchen wall switch acts as a direct manual fallback for motion lighting: pressing switch UP from off turns on directly to `brightness_high` (255).
  - When motion clears, kitchen lights turn off automatically if at `brightness_high` (255) or `brightness_sleep` (5), whether triggered by motion or by the fallback switch.
  - Down single-click on switch turns off kitchen light instantly without transition.
- **Wall Switch Single-Press Cycling (Other Rooms)**:
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
  - Window open/close events invoke [`script.play_media_tts_window_opened`](include/scripts/play_media_tts_window_opened.yaml) and [`script.play_media_tts_window_closed`](include/scripts/play_media_tts_window_closed.yaml).
  - If ambient humidity exceeds `input_number.dashboard_humidity_threshold_medium`, caring TTS advises airing out or closing windows when optimal.
- **Living Room Window & Curtain Interlock**:
  - `cover.living_room_curtain_group` is a smart template cover in [`include/template/template_cover.yaml`](include/template/template_cover.yaml).
  - Opening `binary_sensor.living_room_window_contact` automatically opens `cover.living_room_curtain_left` via [`living_room_window_sensor.yaml`](include/automations/living_room/living_room_window_sensor.yaml).
  - When the window is open, closing or toggling `cover.living_room_curtain_group` only closes `cover.living_room_curtain_right`, preventing the left curtain from closing.
  - When the window closes, if the right curtain is closed/closing, `cover.living_room_curtain_left` is automatically closed to restore the user's intended room state without requiring manual re-triggering.

---

## 5. Roborock Vacuum Cleaning Dispatch
- **Schedule**: [`home_vacuum_cleaning.yaml`](include/automations/home/home_vacuum_cleaning.yaml) triggers at `input_datetime.vacuum_cleaning_time`.
- **Logic**:
  - Restricts dispatch to once per calendar day (`last_triggered.date() != now().date()`).
  - Calls [`script.vacuum_start`](include/scripts/vacuum_start.yaml).
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
  - [`home_spotify_to_music_assistant.yaml`](include/automations/home/home_spotify_to_music_assistant.yaml) intercepts playback:
    - Triggers only on Cast speakers (`playing` / `media_title` change) with `mode: restart` + 3 s settle delay, because Spotify briefly restores the previous session on launch (stale track).
    - The Cast speaker is the source of truth; `media_player.spotify_julian` playlist/shuffle is only used when it is `playing` the same track (title or track URI).
    - Handshakes playback directly to Music Assistant player entities (`media_player.living_room`, `media_player.kitchen`, etc.).
    - Queues full playlist or enables radio mode for single tracks, preserving shuffle.
    - Ensures clean playback resilience across TTS speech ducking and notifications.
- **1-Click Resume & Memory**:
  - Automation [`home_media_last_played.yaml`](include/automations/home/home_media_last_played.yaml) captures the latest Spotify playlist, track, artist, cover art, and speaker to `input_text.last_played_*`.
  - Script [`script.media_resume_last_played`](include/scripts/media_resume_last_played.yaml) allows 1-click resumption through Music Assistant on the dashboard `#bubble_media_popup`.
---

## 8. Household Appliances (Washer & Dishwasher Lifecycle)
- **Bathroom Washing Machine**:
  - State tracking: [`include/template/template_washer.yaml`](include/template/template_washer.yaml) tracks `sensor.bathroom_washer_power > 3.0W` (5 min delay-off) as `binary_sensor.template_bathroom_washer`.
  - Reminder helper: `input_boolean.bathroom_laundry` turns on during wash cycle.
  - Cycle notification: [`include/automations/bathroom/bathroom_laundry.yaml`](include/automations/bathroom/bathroom_laundry.yaml) announces cycle completion on speaker group `media_player.minis` via randomized 8-variant [`script.play_media_tts_laundry`](include/scripts/play_media_tts_laundry.yaml).
  - Drying humidity notification: [`include/automations/bathroom/bathroom_washer_humidity.yaml`](include/automations/bathroom/bathroom_washer_humidity.yaml) alerts on `media_player.minis` via [`script.play_media_tts_washer_humidity`](include/scripts/play_media_tts_washer_humidity.yaml) when humidity exceeds 60% during wash/dry cycle, with exactly one follow-up reminder after 20 minutes tracked by `input_boolean.bathroom_washer_humidity_warning_active`. Interlocked with [`include/automations/bathroom/bathroom_shower_humidity.yaml`](include/automations/bathroom/bathroom_shower_humidity.yaml) to prioritize showers.
- **Kitchen Dishwasher**:
  - State tracking: [`include/template/template_dishwasher.yaml`](include/template/template_dishwasher.yaml) tracks `sensor.kitchen_dish_washer_power > 3.0W` (5 min delay-off) as `binary_sensor.kitchen_dishwasher`.
  - Reminder helper: `input_boolean.kitchen_dishwasher_done` in [`include/input/input_kitchen.yaml`](include/input/input_kitchen.yaml) latches `on` upon cycle completion and clears when a new cycle starts.
  - Entry-Triggered Announcement: [`include/automations/kitchen/kitchen_dishwasher.yaml`](include/automations/kitchen/kitchen_dishwasher.yaml) waits until someone enters the kitchen (`binary_sensor.kitchen_motion_sensor_occupancy = on`) and `presence_home = on` before announcing via randomized 8-variant [`script.play_media_tts_dishwasher`](include/scripts/play_media_tts_dishwasher.yaml) on `media_player.kitchen`, automatically clearing the helper. If someone is already in the kitchen when it finishes, it announces immediately.

---

## 9. Weather Forecast Pipeline & Tablet Dashboard Resilience
- **Data Pipeline**:
  - Queries Open-Meteo (`weather.home_open_meteo`) every 30 minutes for both `hourly` and `daily` forecasts.
  - Automatically retains last-known-good values during API dropouts/timeouts.
- **Clock & Weather Card 3-Day Forecast Contract**:
  - `clock-weather-card` renders a 3-day forecast with the current temperature indicator dot on the row matching today's local date (`now().date()`).
  - `weather.weather_home_mock` provides `forecast_daily_template` backed by `sensor.weather_home_forecast_daily`, ensuring that past days are strictly filtered out (`as_local(as_datetime(...)).date() >= now().date()`).
  - Row 1 is guaranteed to always represent today (with the indicator dot), preventing yesterday's data from pushing today into the second row during API dropouts or midnight transitions.
  - `forecast_hourly_template` is backed by `sensor.weather_home_forecast` (updated every 30 min) with past-hour date filtering.
  - `sensor.weather_home_forecast_at_midnight` retains today's midnight baseline for ApexCharts 24h precipitation area with self-healing recovery if midnight API calls fail.

---

## 10. Dashboard & Visual Testing Subsystem
- **Dashboard Architecture**:
  - `dashboards/bubble_code/bubble_code.yaml` (`bubble-code-dashboard`): Primary wall kiosk and desktop dashboard (`bubble_code_theme`).
- **Bubble Card Modules Integration**:
  - Reusable CSS & JavaScript styles reside in `bubble_card/modules/*.yaml`.
  - Backed by `bubble_card_tools` custom component for local, Git-versioned file storage.
- **Device Viewport & Scaling Specifications**:
  - **Wall-Mounted Tablet (Huawei MediaPad M5 Lite 10)**:
    - CSS Viewport: `1130 × 706` px @ `1.7x` device pixel ratio (Screen: `1130 × 706`).
    - Font Metrics: Roboto (native Android system font; replicated via `~/.local/share/fonts/Roboto*.ttf`).
    - Preset: `--preset tablet` (or `--preset tablet_m5`).
  - **Desktop PC**:
    - CSS Viewport: `1854 × 959` px @ `1.0x` device pixel ratio (Screen: `1920 × 1080`).
    - Preset: `--preset pc`.
  - **Mobile Phone (Google Pixel 7 Pro)**:
    - CSS Viewport: `412 × 828` px @ `2.6x` device pixel ratio (Screen: `412 × 892`).
    - Preset: `--preset phone` (or `--preset phone_pixel7pro`).
- **CSS Diagnostic Fallback**:
  - If investigating the viewport dimensions of a new device, CSS media query or javascript inspection cards can display `window.innerWidth`, `window.innerHeight`, and `window.devicePixelRatio`.
- **Theme Reloading Workflow**:
  - After creating or editing any theme under `include/themes/`, always run:
    ```bash
    python3 tools/ha_api.py reload-lovelace
    ```
    This triggers `/api/services/frontend/reload_themes` via REST API so Home Assistant reloads frontend theme definitions immediately without restarting Core.
- **Headless Screenshot Workflow**:
  - To visually verify any dashboard across target viewports without physical hardware:
    ```bash
    python3 tools/screenshot_dashboard.py --path <dashboard_slug>/Home --preset tablet
    ```
  - Output is saved to `dashboards/screenshots/<name>.png`.
  - For live physical kiosk hardware capture:
    ```bash
    python3 tools/screenshot_dashboard.py --live
    ```
    (Fetches live screen directly from `image.huawei_mediapad_m5_lite_10_screenshot`).


