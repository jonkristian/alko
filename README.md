# AL-KO Robolinho component for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![maintainer](https://img.shields.io/badge/maintainer-%40jonkristian-blue.svg)](https://github.com/jonkristian)
[![buy_me_a_coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg)](https://www.buymeacoffee.com/jonkristian)
[![License](https://img.shields.io/github/license/jonkristian/alko)](https://github.com/jonkristian/alko/blob/main/LICENSE)

This component allows you to integrate your AL-KO Robolinho mower in Home Assistant.

## Features

### Lawn Mower Integration
- ▶️ Start
- ⏸️ Pause
- 🏠 Dock

### Sensors
- 🔋 Battery level
- 🔄 Operation state (IDLE, WORKING, HOMING)
- ⚠️ Operation errors (with detailed error codes)
- 🔪 Remaining blade life
- 🌧️ Rain detection status
- ❄️ Frost detection status
- 🔌 Charger contact status
- ⏰ Next operation time and details
- 📶 RSSI signal strength
- 🔍 Operation substate
- ℹ️ Operation situation
- ⏱️ Blade operation time
- 👤 User interaction

### Settings
- 🌱 Toggle Eco Mode
- 🌧️ Toggle Rain Sensor
- ❄️ Toggle Frost Sensor
- 🌧️ Rain sensitivity (1-10)
- ⏳ Rain delay
- ❄️ Frost threshold temperature
- ⏳ Frost delay
- 🔄 Reset blade life
- ⏸️ Pause for today

### Calendar
- 📅 View mowing window schedules
- 🔍 Details: Status, Margin Mode, Narrow Passage

### Device Information
- 💾 Firmware version
- 🔧 Hardware version
- 🔑 Serial number
- 📋 Model information

## Services

### Mowing Windows

```yaml
service: alko.alko_update_mowing_window
target:
  entity:
    domain: lawn_mower
data:
  day: monday  # Day of the week (monday-sunday)
  window_number: 1  # Window number (1 or 2)
  start_hour: 9  # Start hour (0-23)
  start_minute: 0  # Start minute (0-59)
  duration: 120  # Duration in minutes (1-360)
  type: mow  # Type of mowing operation (mow, first_mow_border_then_area, narrow_passage, deactivated)
```

### Manual Mowing

```yaml
service: alko.alko_start_manual_mowing
target:
  entity:
    domain: lawn_mower
data:
  duration: 120  # Duration in minutes (1-360)
  type: mow  # Type of mowing operation (mow, first_mow_border_then_area, narrow_passage)
```

# Installation

## Requesting API access
Before installing you should know that you will have to to request access to the API. [Fill out this form](https://alko-garden.com/api-access). If all went well you will receive your credentials.

## Manual or via HACS
If you're using HACS you can add this repo as a custom repository and install, otherwise download or clone and copy the folder `custom_components/alko` into your `custom_components/`. Be sure to restart.

## Setup
1. Go to Settings > Devices & Services
2. Click the "+ ADD INTEGRATION" button
3. Search for "AL-KO" and select it
4. If you haven't added application credentials yet, you'll be prompted to add them first
   - Enter the client ID and client secret you received from AL-KO
5. Once the application credentials are set, enter your AL-KO username and password
6. The integration will now set up your devices automatically

## Contribute
If you own a smart product from AL-KO and would like to contribute, please don't hesitate getting in touch.

***
⭐️ this repository if you found it useful ❤️

<a href="https://www.buymeacoffee.com/jonkristian" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
