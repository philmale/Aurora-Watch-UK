# AuroraWatch UK – Status Report

A minimal, production-ready Python script that polls the
AuroraWatch UK **alerting-site activity** feed and exposes the latest
magnetometer reading and alert status as a JSON object.
Suitable for a Home Assistant command line sensor or anything else that ingests JSON.

Designed to be:
- simple,
- robust,
- dependency-free (stdlib only),
- and suitable for long-term unattended use.

## Credits

The [AuroraWatch project](https://aurorawatch.lancs.ac.uk) is a fantastic project, a huge thanks
to everyone involved there and credit to [Lancaster University](https://www.lancaster.ac.uk) for making
this available for everyone to use.

Here is where you can find a description of the [AuroraWatch API](https://aurorawatch.lancs.ac.uk/api-info/).

## What it does

On each poll, the script:

1. Fetches the official AuroraWatch UK XML feed.
2. Extracts the **latest `<activity>` sample**.
3. Outputs a single JSON object for Home Assistant containing:
   - sensor state = magnetometer value (nT),
   - alert status (green / yellow / amber / red),
   - timestamp of the reading,
   - feed update time,
   - polling time,
   - site code,
   - a sensible UI icon.

Home Assistant ingests this via the `command_line` integration.

## Why `command_line`

Home Assistant’s REST sensor cannot define arbitrary attributes, and XML→JSON
parsing support varies by version.
Using `command_line` gives:

- one entity,
- predictable parsing,
- no HA templating gymnastics,
- full control over attributes.

## Requirements

- Home Assistant (Container, Core, or OS)
- `python3` available inside the HA runtime
- Internet access to `aurorawatch-api.lancs.ac.uk`

No third-party Python packages are required.

## Installation

### 1. Copy the script

Place the script under your HA config directory, for example:

/config/scripts/aurorawatch_uk.py

Make it executable (optional but recommended):

chmod +x /config/scripts/aurorawatch_uk.py

Edit the configuration section at the top of the script and set a contact email
for the User-Agent string.

### 2. Configure Home Assistant

Add a command-line sensor.

Example `command_line.yaml`:
```
- sensor:
    name: "Aurora Watch UK"
    unique_id: aurorawatch_uk
    scan_interval: 300
    command_timeout: 30
    command: "python3 /config/scripts/aurorawatch_uk.py"
    value_template: "{{ value_json.state }}"
    unit_of_measurement: "nT"
    state_class: measurement
    json_attributes:
      - status
      - data_datetime
      - updated
      - alerting_site
      - polled_at
      - url
      - icon
```
Include it from `configuration.yaml`:
```
command_line: !include command_line.yaml
```
Restart Home Assistant.

## Resulting entity

The sensor exposes:

- **State**
  - Latest magnetometer value (nanotesla)

- **Attributes**
  - `status` – alert level (`green`, `yellow`, `amber`, `red`)
  - `data_datetime` – timestamp of the reading
  - `updated` – feed update time
  - `alerting_site` – site code (e.g. `SUM`)
  - `polled_at` – when HA fetched the data
  - `icon` – `mdi:flare` for amber/red, sunny otherwise

## Error handling

If the feed is unreachable or malformed:
- the script emits a valid JSON payload,
- the sensor state becomes `unknown`,
- Home Assistant remains stable.

No exceptions are raised into HA.

## Notes

- This script uses the [AuroraWatch API](https://aurorawatch.lancs.ac.uk/api-info/).
- AuroraWatch UK does not publish an officially supported Python SDK; this
  approach mirrors their documented usage pattern.
- Polling every 5 minutes is well within reasonable usage for the service.
- Written for the Home Assistant community.
- Author [Phil Male](https://phil-male.com).

