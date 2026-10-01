# Home Assistant Entity Catalog & System Index

This catalog serves as the single source of truth for entity IDs, helper names, and physical devices across all areas of the home. 

---

## 🛋️ Living Room (`living_room`)

| Domain | Entity ID | Role / Device | Notes |
| :--- | :--- | :--- | :--- |
| **Light** | `light.living_room_light_group` | Living Room Ceiling Group | Controls all 4 spots together |
| **Light** | `light.living_room_light_1` ... `3` | Spot Lights 1 to 3 | Individual ceiling fixtures |
| **Light** | `light.living_room_light_google` | Google Assistant Light Template | Exposed to voice integration |
| **Switch** | `switch.living_room_spot_lights` | Spot Light Relay Switch | Main switch |
| **Switch** | `switch.living_room_tv` | TV Smart Plug | Power toggle & metering |
| **Switch** | `switch.living_room_desktop` | Desktop PC Smart Plug | Power toggle & metering |
| **Switch** | `switch.living_room_laptop` | Laptop Smart Plug | Power toggle |
| **Switch** | `switch.living_room_tablet_screen` | Dashboard Tablet Screen | Controls tablet screen on/off |
| **Climate** | `climate.living_room_thermostat` | Living Room Radiator Valve | Linked to window contact |
| **Cover** | `cover.living_room_curtain_left` | Left Window Curtain | Smart curtain motor |
| **Cover** | `cover.living_room_curtain_right`| Right Window Curtain | Smart curtain motor |
| **Sensor** | `binary_sensor.living_room_motion_sensor_occupancy` | Motion / Occupancy Sensor | Triggers daytime/night scenes |
| **Sensor** | `binary_sensor.living_room_window_contact` | Window Contact Sensor | Auto shutoff for thermostat |
| **Sensor** | `sensor.living_room_multi_sensor_temperature` | Ambient Temperature | Displayed on dashboard |
| **Sensor** | `sensor.living_room_multi_sensor_humidity` | Relative Humidity | Monitored for ventilation alerts |
| **Sensor** | `sensor.living_room_humidity_change` | Calculated Humidity Derivation | Rate of humidity change (venting) |
| **Air** | `select.living_room_air_purifier_led_brightness` | Air Purifier Display LED | Dimmed during night motion |
| **Switch Event**| `event.living_room_light_switch_action` | Wall Button Events | Single/double/hold actions |
| **Media** | `media_player.living_room` | Google Cast Speaker Group | Audio playback |
| **Media** | `media_player.living_room_cast` | Living Room Google Cast Target | Target for TTS broadcasts |
| **Power** | `sensor.living_room_desktop_power` | Desktop Power (Watts) | Real-time usage |
| **Power** | `sensor.living_room_tv_power` | TV Power (Watts) | Real-time usage |
| **Power** | `sensor.living_room_nintendo_power` | Switch Power (Watts) | Real-time usage |
| **Helper** | `input_number.dashboard_thermostat_setpoint_living_room` | UI Thermostat Target | Dashboard slider |
| **Helper** | `input_boolean.vacuum_clean_living_room` | Room Vacuum Clean Toggle | Dispatched by Robi schedule |

---

## 🛏️ Bedroom (`bedroom`)

| Domain | Entity ID | Role / Device | Notes |
| :--- | :--- | :--- | :--- |
| **Light** | `light.bedroom_light_group` | Ceiling Light Group | Left + Right ceiling fixtures |
| **Light** | `light.bedroom_light_left` | Left Bedside Lamp | Controlled by left switch & motion |
| **Light** | `light.bedroom_light_right` | Right Bedside Lamp | Controlled by right switch & motion |
| **Light** | `light.bedroom_light_sphere` | Decorative Sphere Lamp | Ambient lighting fixture |
| **Light** | `light.bedroom_light_google` | Google Template Light | Voice exposed |
| **Light** | `light.bedroom_light_sphere_google` | Google Template Sphere | Voice exposed |
| **Climate** | `climate.bedroom_thermostat` | Bedroom Radiator Thermostat | Interlocked with window contact |
| **Cover** | `cover.bedroom_roller_blinds` | Electric Roller Blinds | Sunset close / morning open |
| **Sensor** | `binary_sensor.bedroom_motion_sensor_left_occupancy` | Left Bed Motion Sensor | Night light (red) / daytime warm |
| **Sensor** | `binary_sensor.bedroom_motion_sensor_right_occupancy`| Right Bed Motion Sensor | Night light (red) / daytime warm |
| **Sensor** | `binary_sensor.bedroom_window_contact` | Window Contact Sensor | Shuts off radiator & caring TTS |
| **Sensor** | `sensor.bedroom_multi_sensor_temperature` | Ambient Temperature | Multi-sensor reading |
| **Sensor** | `sensor.bedroom_multi_sensor_humidity` | Relative Humidity | Multi-sensor reading |
| **Sensor** | `sensor.bedroom_humidity_change` | Rate of Humidity Change | Evaluates ventilation status |
| **Sensor** | `sensor.bedroom_alarms` | Google Home Next Alarm Time | Triggers morning routine 15m prior |
| **Switch Event**| `event.bedroom_light_switch_door_action` | Door Wall Switch | Single: ceiling / Hold: sphere |
| **Switch Event**| `event.bedroom_light_switch_left_action` | Left Bedside Switch | Single: lamp / Hold: Home/Away |
| **Switch Event**| `event.bedroom_light_switch_right_action`| Right Bedside Switch | Single: lamp / Hold: Home/Away |
| **Media** | `media_player.bedroom` | Bedroom Speaker | Audio playback |
| **Media** | `media_player.bedroom_cast` | Bedroom Google Cast Target | TTS target |
| **Helper** | `input_boolean.bedroom_alarm_disabled` | Alarm Override Toggle | Disables morning wake-up routine |
| **Helper** | `input_datetime.bedroom_alarm_time` | Fallback Morning Alarm Time | Used if Google alarm is unset |
| **Helper** | `input_number.dashboard_thermostat_setpoint_bedroom` | UI Setpoint Helper | Thermostat target |
| **Helper** | `input_boolean.vacuum_clean_bedroom` | Room Vacuum Clean Toggle | Dispatched by Robi schedule |
| **Automation** | `automation.bedroom_bedtime_routine` | Bedtime Routine | Phone charging + lamp off -> sleep scene |

---

## 🍼 Baby Room (`baby_room`)

| Domain | Entity ID | Role / Device | Notes |
| :--- | :--- | :--- | :--- |
| **Light** | `light.baby_room_light` | Ceiling Fixture | Night mode: dim red / Day: warm |
| **Light** | `light.baby_room_light_google` | Google Template Light | Voice exposed |
| **Switch** | `switch.baby_room_heater` | Auxiliary Wall Heater | Auto-off after 10m timer |
| **Climate** | `climate.baby_room_thermostat` | Radiator Thermostat | Interlocked with window contact |
| **Cover** | `cover.baby_room_roller_blinds` | Electric Roller Blinds | Sunset close / morning open |
| **Sensor** | `binary_sensor.baby_room_motion_sensor_occupancy` | Occupancy Sensor | Night light / ambient lighting |
| **Sensor** | `binary_sensor.baby_room_window_contact` | Window Contact Sensor | Shuts off radiator & caring TTS |
| **Sensor** | `sensor.baby_room_multi_sensor_temperature` | Ambient Temperature | Multi-sensor reading |
| **Sensor** | `sensor.baby_room_multi_sensor_humidity` | Relative Humidity | Multi-sensor reading |
| **Sensor** | `sensor.baby_room_humidity_change` | Rate of Humidity Change | Evaluates ventilation status |
| **Sensor** | `sensor.baby_room_alarms` | Google Home Alarm Time | Triggers morning routine 15m prior |
| **Switch Event**| `event.baby_room_light_switch_action` | Wall Switch | Single: light / Hold: heater |
| **Media** | `media_player.baby_room` | Baby Room Speaker | Audio playback |
| **Media** | `media_player.baby_room_cast` | Baby Room Google Cast Target | TTS target |
| **Helper** | `input_boolean.baby_room_alarm_disabled` | Alarm Override Toggle | Disables morning wake-up routine |
| **Helper** | `input_datetime.baby_room_alarm_time` | Fallback Morning Alarm Time | Used if Google alarm is unset |
| **Helper** | `input_number.dashboard_thermostat_setpoint_baby_room` | UI Setpoint Helper | Thermostat target |

---

## 🍳 Kitchen (`kitchen`)

| Domain | Entity ID | Role / Device | Notes |
| :--- | :--- | :--- | :--- |
| **Light** | `light.kitchen_light_group` | Main Kitchen Light Group | Left + Right kitchen fixtures |
| **Light** | `light.kitchen_light_left` | Left Counter Spot | Direct illumination |
| **Light** | `light.kitchen_light_right` | Right Counter Spot | Direct illumination |
| **Switch** | `switch.kitchen_fridge` | Refrigerator Smart Plug | Monitored power draw |
| **Switch** | `switch.kitchen_microwave` | Microwave Smart Plug | Monitored power draw |
| **Climate** | `climate.kitchen_thermostat` | Radiator Thermostat | Interlocked with window contact |
| **Sensor** | `binary_sensor.kitchen_motion_sensor_occupancy` | Motion Sensor | Auto light on/off |
| **Sensor** | `binary_sensor.kitchen_window_contact` | Window Contact Sensor | Shuts off radiator & caring TTS |
| **Sensor** | `sensor.kitchen_multi_sensor_temperature` | Ambient Temperature | Multi-sensor reading |
| **Sensor** | `sensor.kitchen_multi_sensor_humidity` | Relative Humidity | Multi-sensor reading |
| **Sensor** | `sensor.kitchen_humidity_change` | Rate of Humidity Change | Evaluates cooking/venting |
| **Power** | `sensor.kitchen_fridge_power` | Fridge Power (Watts) | Integration sensor base |
| **Power** | `sensor.kitchen_microwave_power` | Microwave Power (Watts) | Integration sensor base |
| **Power** | `sensor.kitchen_dish_washer_power` | Dishwasher Power (Watts) | Usage tracking |
| **Power** | `sensor.kitchen_kettle_power` | Electric Kettle Power (Watts) | Usage tracking |
| **Power** | `sensor.kitchen_sink_power` | Under-sink Boiler Power (Watts) | Usage tracking |
| **Switch Event**| `event.kitchen_light_switch_action` | Wall Switch Events | Up: On / Down: Off |
| **Media** | `media_player.kitchen` | Kitchen Speaker | Audio playback |
| **Media** | `media_player.kitchen_cast` | Kitchen Google Cast Target | TTS target |
| **Helper** | `input_number.dashboard_thermostat_setpoint_kitchen` | UI Setpoint Helper | Thermostat target |
| **Helper** | `input_boolean.vacuum_clean_kitchen` | Room Vacuum Clean Toggle | Dispatched by Robi schedule |

---

## 🚿 Bathroom (`bathroom`)

| Domain | Entity ID | Role / Device | Notes |
| :--- | :--- | :--- | :--- |
| **Light** | `light.bathroom_light` | Bathroom Ceiling Fixture | Occupancy controlled |
| **Sensor** | `binary_sensor.bathroom_motion_sensor_occupancy` | Main Bathroom Motion | Auto turns on light |
| **Sensor** | `binary_sensor.bathroom_shower_motion_sensor_occupancy` | Shower Motion Sensor | Prolongs light during shower |
| **Sensor** | `binary_sensor.template_bathroom_washer` | Washing Machine Active State | On when power > 3.0W (5m delay off) |
| **Sensor** | `sensor.bathroom_washer_power` | Washing Machine Power (Watts) | Power metering |
| **Sensor** | `sensor.bathroom_multi_sensor_temperature` | Ambient Temperature | Multi-sensor reading |
| **Sensor** | `sensor.bathroom_multi_sensor_humidity` | Relative Humidity | High threshold triggers shower alerts |
| **Media** | `media_player.bathroom` | Bathroom Speaker | Audio playback |
| **Media** | `media_player.bathroom_cast` | Bathroom Google Cast Target | Morning briefing & TTS announcements |
| **Helper** | `input_boolean.bathroom_laundry` | Laundry Finished Reminder | Active when washer completes |
| **Helper** | `input_boolean.bathroom_humidity_warning_active` | Shower Humidity Lock | Prevents repetitive TTS spam |
| **Helper** | `input_boolean.vacuum_clean_bathroom` | Room Vacuum Clean Toggle | Dispatched by Robi schedule |

---

## 🌐 House Global Subsystems & Infrastructure

### Presence & Resident Tracking
- `input_boolean.presence_home`: Master house state (`on` = home & awake, `off` = away or sleeping).
- `switch.presence_away`: Interactive template switch (exact inverse of `presence_home`) for Bubble Card dashboard.
- `group.residents`: Tracks GPS location for Julian and Xingyang.
- `person.julian`: Julian's person tracker.
- `person.xingyang`: Xingyang's person tracker.
- `binary_sensor.julian_is_charging`: Phone charging status (used in night routines).

### Audio, Voice & AI Notification Pipeline
- `conversation.google_ai_conversation`: Google Generative AI (Gemini) conversation agent for live briefings & natural language prompts.
- `media_player.spotify_julian`: Active Spotify playback instance.
- `media_player.living_room` / `kitchen` / `bedroom` / `bathroom` / `baby_room`: Music Assistant player targets.
- `media_player.living_room_cast` / `kitchen_cast` / `bedroom_cast` / `bathroom_cast`: Native Cast targets for TTS.
- `script.play_media_tts_message`: Central notification router with volume ducking & bilingual support.
- `script.play_media_tts_gemini`: AI generative status briefing caller (queries `conversation.google_ai_conversation` and broadcasts via `script.play_media_tts_message`).
- `script.media_resume_last_played`: Resumes last played Spotify playlist/track via Music Assistant.
- `sensor.last_played_media_info`: Consolidated template sensor for last played title, artist, picture, and speaker.
- `input_text.last_played_media_id` / `last_played_media_type` / `last_played_speaker`: Persistence helpers for 1-click resume.
- `input_boolean.home_chinese_tts_enabled`: Global switch enabling bilingual Chinese TTS broadcasts.
- `media_player.entrance_cast` / `media_player.minis_cast` / `media_player.wohnzimmer_kuche`: Speaker targets.

### Vacuum (Robi) Dispatch
- `vacuum.robi`: Dreame robot vacuum cleaner.
- `input_datetime.vacuum_cleaning_time`: Daily scheduled departure time.
- `input_boolean.vacuum_mopping_enabled`: Toggles sweeping vs sweeping & mopping.
- `input_boolean.vacuum_clean_entrance` / `input_boolean.vacuum_clean_kidroom`: Individual room toggles.
- `select.robi_suction_level` / `select.robi_cleaning_mode`: Vacuum operational settings.

### Augsburg Tram Linie 1 (Curtiusstraße Stop)
- `sensor.augsburg_curtiusstrasse_koenigsplatz`: Live departures toward Königsplatz / Göggingen.
- `sensor.augsburg_curtiusstrasse_lechh_n_ostfriedh`: Live departures toward Lechhausen Neuer Ostfriedhof.
- `sensor.tram_1_koenigsplatz_walk_status`: Dynamic walking advice (*"Jetzt losgehen!"*, *"In X min"*, *"Verpasst"*).
- `sensor.tram_1_lechhausen_walk_status`: Dynamic walking advice for northbound platform.
- `binary_sensor.augsburg_curtiusstrasse_koenigsplatz_delays`: Delay problem flag.

### Energy & Utility Meters
- `sensor.home_total_power`: Total house power draw aggregated in Watts.
- `sensor.template_bs_energy_basic_usage`: Base load utility meter source.
- `counter.energy_basic_price_increase_counter`: Hourly operational counter for energy cost calculation.
- `input_number.home_energy_price`: Current kWh tariff setpoint.
- `input_number.home_energy_base_price`: Annual fixed base fee setpoint.

### Global Lighting Presets & Anti-Blinding
- `input_number.light_brightness_sleep`: Global sleep / nightlight brightness level (default: 5).
- `input_number.light_brightness_awake`: Global awake / ambient warm brightness level (default: 126).
- `input_number.light_brightness_high`: Global high / daytime brightness level (default: 255).
- `input_text.light_color_sleep`: Global sleep / night RGB color string (default: `"255,0,0"`).
- `input_text.light_color_awake`: Global awake / ambient RGB color string (default: `"255,166,87"`).
- `cover.living_room_curtain_group`: Living Room Curtains group (left + right), auto-opened during morning vacuum schedule.

