# Home Assistant: Tram 1 Augsburg Integration & Core 2026.9 Migration Guide

This document serves as an actionable technical specification and prompt guide for maintaining, updating, and extending Home Assistant via VSCode.

---

## 1. Project Context & Objectives

1. **Augsburg Tram Linie 1 Integration (Curtiusstraße stop):**
   * Direction 1: Inbound toward **Königsplatz** (Tram destination board displays **Göggingen**).
   * Direction 2: Outbound toward **Lechhausen Neuer Ostfriedhof**.
   * Live dispatch, delays, next departure ($T_1$), and subsequent departure ($T_2$).
   * Dynamic walking time status ("Leave now", "Run", "Plenty of time") calibrated to walking distance from home to Curtiusstraße.
2. **Safe Core Upgrade (`2025.12.3` $\rightarrow$ `2026.9.3`):**
   * Resolve breaking changes in **Kiosk Mode**, **Bubble Card v3.x**, and custom CSS / `card-mod`.
   * Migrate deprecated Material Design tokens (`--mdc-*`).
   * Audit legacy service calls (`tts.google_cloud_say` $\rightarrow$ unified `action: tts.speak`).
   * Safeguard Music Assistant and Zigbee2MQTT device bindings.

---

## 2. Transit Sensor Architecture (AVV / SWA Linie 1)

### 2.1 Provider & Stop Mapping

Augsburg public transit (SWA) feeds all real-time schedule and GTFS-RT/EFA data through the **AVV (Augsburger Verkehrs- und Tarifverbund)** backend.

* **Integration:** `OpenPublicTransport` (available via HACS)
* **Regional Provider:** `AVV (Augsburg)`
* **Station Name:** `Curtiusstraße` (or `Augsburg, Curtiusstraße`)
* **Line Filter:** `1`

| Physical Direction | Platform / Destination Filter | Displayed Headsign on Tram |
| :--- | :--- | :--- |
| **Southbound (Inbound)** | `Göggingen` | `Göggingen` (passes via Königsplatz) |
| **Northbound (Outbound)**| `Lechhausen` / `Neuer Ostfriedhof` | `Lechhausen Neuer Ostfriedhof` |

---

### 2.2 Template Sensors (`templates.yaml` or `configuration.yaml`)

Add these template sensors to expose the next departure, second departure, delay offsets, and a walking recommendation.

```yaml
template:
  - sensor:
      # ==========================================
      # DIRECTION: KÖNIGSPLATZ / GÖGGINGEN
      # ==========================================
      - name: "Tram 1 Königsplatz Next Departure"
        unique_id: tram_1_koenigsplatz_next
        icon: mdi:tram
        state: >
          {% set deps = state_attr('sensor.curtiusstrasse_departures', 'departures') %}
          {% if deps and deps | length > 0 %}
            {{ deps[0].time | default(deps[0].departure_time | as_timestamp | timestamp_custom('%H:%M')) }}
          {% else %}
            unavailable
          {% endif %}
        attributes:
          minutes_to_next: >
            {% set deps = state_attr('sensor.curtiusstrasse_departures', 'departures') %}
            {% if deps and deps | length > 0 %}
              {% set t = deps[0].departure_time | default(deps[0].datetime) | as_datetime %}
              {{ ((t - now()).total_seconds() / 60) | round(0, 'floor') if t else 0 }}
            {% else %}
              -1
            {% endif %}
          delay_minutes: >
            {% set deps = state_attr('sensor.curtiusstrasse_departures', 'departures') %}
            {{ deps[0].delay | default(0) if deps and deps | length > 0 else 0 }}
          second_departure_time: >
            {% set deps = state_attr('sensor.curtiusstrasse_departures', 'departures') %}
            {% if deps and deps | length > 1 %}
              {{ deps[1].time | default(deps[1].departure_time | as_timestamp | timestamp_custom('%H:%M')) }}
            {% else %}
              unavailable
            {% endif %}
          minutes_to_second: >
            {% set deps = state_attr('sensor.curtiusstrasse_departures', 'departures') %}
            {% if deps and deps | length > 1 %}
              {% set t2 = deps[1].departure_time | default(deps[1].datetime) | as_datetime %}
              {{ ((t2 - now()).total_seconds() / 60) | round(0, 'floor') if t2 else 0 }}
            {% else %}
              -1
            {% endif %}

      # Walking status badge for Königsplatz
      - name: "Tram 1 Königsplatz Walk Status"
        unique_id: tram_1_koenigsplatz_walk_status
        icon: mdi:walk
        state: >
          {% set walk_time = 4 %}  {# Set your exact walking time in minutes #}
          {% set mins = state_attr('sensor.tram_1_konigsplatz_next_departure', 'minutes_to_next') | int(-1) %}
          {% if mins < 0 %}
            No departures
          {% elif mins < walk_time %}
            Missed (Take next)
          {% elif mins <= (walk_time + 2) %}
            Leave now!
          {% else %}
            In {{ mins }} min
          {% endif %}

      # ==========================================
      # DIRECTION: LECHHAUSEN NEUER OSTFRIEDHOF
      # ==========================================
      - name: "Tram 1 Lechhausen Next Departure"
        unique_id: tram_1_lechhausen_next
        icon: mdi:tram
        state: >
          {% set deps = state_attr('sensor.curtiusstrasse_lechhausen_departures', 'departures') %}
          {% if deps and deps | length > 0 %}
            {{ deps[0].time | default(deps[0].departure_time | as_timestamp | timestamp_custom('%H:%M')) }}
          {% else %}
            unavailable
          {% endif %}
        attributes:
          minutes_to_next: >
            {% set deps = state_attr('sensor.curtiusstrasse_lechhausen_departures', 'departures') %}
            {% if deps and deps | length > 0 %}
              {% set t = deps[0].departure_time | default(deps[0].datetime) | as_datetime %}
              {{ ((t - now()).total_seconds() / 60) | round(0, 'floor') if t else 0 }}
            {% else %}
              -1
            {% endif %}
          delay_minutes: >
            {% set deps = state_attr('sensor.curtiusstrasse_lechhausen_departures', 'departures') %}
            {{ deps[0].delay | default(0) if deps and deps | length > 0 else 0 }}
          second_departure_time: >
            {% set deps = state_attr('sensor.curtiusstrasse_lechhausen_departures', 'departures') %}
            {% if deps and deps | length > 1 %}
              {{ deps[1].time | default(deps[1].departure_time | as_timestamp | timestamp_custom('%H:%M')) }}
            {% else %}
              unavailable
            {% endif %}
```

---

## 3. Dashboard UI Cards

### 3.1 Bubble Card Implementation
```yaml
type: custom:bubble-card
card_type: button
entity: sensor.tram_1_konigsplatz_next_departure
name: "Linie 1 -> Königsplatz"
sub_button:
  - entity: sensor.tram_1_konigsplatz_walk_status
    show_state: true
    show_icon: true
    icon: mdi:walk
styles: |
  .bubble-button-card-container {
    background: rgba(25, 25, 25, 0.8) !important;
  }
  .bubble-sub-button-1 {
    background: ${state === 'Leave now!' ? 'var(--warning-color)' : 'var(--card-background-color)'} !important;
  }
```

### 3.2 Mushroom Status Card
```yaml
type: custom:mushroom-template-card
primary: "Linie 1 -> Königsplatz"
secondary: >
  Next: {{ states('sensor.tram_1_konigsplatz_next_departure') }} 
  (in {{ state_attr('sensor.tram_1_konigsplatz_next_departure', 'minutes_to_next') }} min) 
  | Next+1: {{ state_attr('sensor.tram_1_konigsplatz_next_departure', 'second_departure_time') }}
icon: mdi:tram
icon_color: >
  {% set mins = state_attr('sensor.tram_1_konigsplatz_next_departure', 'minutes_to_next') | int(-1) %}
  {% if mins < 4 %} red {% elif mins <= 6 %} orange {% else %} green {% endif %}
badge_icon: >
  {% if state_attr('sensor.tram_1_konigsplatz_next_departure', 'delay_minutes') | int(0) > 0 %}
    mdi:clock-alert-outline
  {% endif %}
badge_color: red
```

---

## 4. HA Core Upgrade Audit (`2025.12.3` $\rightarrow$ `2026.9.3`)

### 4.1 Kiosk Mode Breaking Changes
HA 2026.2 and 2026.4 restructured the sidebar and top navigation bars, decoupling the user profile and Settings icons.

* **Minimum Required Version:** Kiosk Mode `v14.0.0+`.
* **Obsolete Keys:** Remove `hide_dialog_attributes: true` (deprecated; causes schema validation issues).
* **New Required Key:** Add `hide_settings: true` if you want the decoupled bottom settings gear hidden.

```yaml
# Updated Kiosk Mode Config
kiosk_mode:
  hide_header: true
  hide_sidebar: true
  hide_settings: true
  hide_overflow: true
```

### 4.2 Bubble Card v3.x Upgrades & Popups
* **Centering Glitch:** Pre-v3.1.5 versions calculate screen boundaries against deprecated HA core CSS properties, pushing popups off-center when paired with Kiosk Mode or desktop viewports.
* **Fix:** Update Bubble Card to **v3.1.5 or newer**.
* **CSS Scoping:** Replace raw `card_mod` on Bubble Cards with the native `styles:` or `custom_styles:` block to avoid shadow-root piercing bugs.

### 4.3 Material Design (`--mdc-*`) Token Deprecation
HA 2026.4 completely replaced legacy MDC tokens with standard Home Assistant CSS variables. Audit all `card-mod` blocks:

| Old Deprecated MDC Token | New HA CSS Replacement Variable |
| :--- | :--- |
| `--mdc-theme-primary` | `--primary-color` |
| `--mdc-theme-text-primary-on-background` | `--primary-text-color` |
| `--mdc-text-field-fill-color` | `--input-fill-color` or `transparent` |
| `--mdc-shape-small` / `--mdc-shape-medium` | `--ha-card-border-radius` |
| `--mdc-select-fill-color` | `--input-dropdown-fill-color` |

### 4.4 Google Cloud TTS Action Modernization
Legacy `tts.*_say` services are deprecated in favor of the modern unified action syntax:

```yaml
# OLD (Deprecated)
service: tts.google_cloud_say
data:
  entity_id: media_player.living_room
  message: "Tram 1 departs in 5 minutes."

# NEW (HA 2026.9 Compliant)
action: tts.speak
target:
  entity_id: tts.google_cloud
data:
  media_player_entity_id: media_player.living_room
  message: "Tram 1 departs in 5 minutes."
```

### 4.5 Music Assistant & Zigbee2MQTT
* **Music Assistant:** Ensure the **Music Assistant Server add-on** and the **Music Assistant HACS integration** are upgraded together to match API version contracts.
* **Zigbee2MQTT Port Persistence:** In `zigbee2mqtt/configuration.yaml`, make sure your coordinator path uses persistent USB IDs to prevent port reassignments during OS reboots:
  ```yaml
  serial:
    port: /dev/serial/by-id/usb-ITead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_...
  ```

---

## 5. Execution Checklist for Claude Agent in VSCode

- [ ] **Step 1: Backup Validation**
  - Verify a full system backup exists (`Settings > System > Backups`).
- [ ] **Step 2: Frontend Dependency Updates**
  - Update HACS components: Bubble Card ($\ge$ 3.1.5), Kiosk Mode ($\ge$ 14.0.0), Card-Mod.
  - Update Music Assistant Server and Zigbee2MQTT add-ons.
- [ ] **Step 3: YAML Config Audit**
  - Remove `hide_dialog_attributes: true` from dashboard configs; add `hide_settings: true`.
  - Search codebase for `--mdc-` and replace with corresponding `--ha-*` / `--primary-*` variables.
  - Search automations for `service: tts.` and refactor to `action: tts.speak`.
  - Check `zigbee2mqtt/configuration.yaml` for persistent serial `/dev/serial/by-id/` path.
- [ ] **Step 4: Execute Core Upgrade**
  - Upgrade Core from `2025.12.3` to `2026.9.3`.
- [ ] **Step 5: Client Cache Invalidation**
  - Hard refresh desktop browsers (`Ctrl + F5` or `Cmd + Shift + R`).
  - Flush Companion App frontend cache (`Settings > Companion App > Debugging > Reset frontend cache`).
- [ ] **Step 6: Transit Sensor Deployment**
  - Install `OpenPublicTransport` via HACS.
  - Add Curtiusstraße entities (Directions: Göggingen & Lechhausen).
  - Append template sensors to `templates.yaml` and reload template entities.