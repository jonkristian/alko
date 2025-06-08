# AL-KO Robolinho component for Home Assistant
This component allows you to integrate your AL-KO Robolinho mower in Home Assistant.

## Supports
- **Lawn Mower Integration**
  - Start
  - Pause
  - Dock

- **Sensors**
  - Battery level
  - Operation state (IDLE, WORKING, HOMING)
  - Operation errors (with detailed error codes)
  - Remaining blade life
  - Rain detection status
  - Frost detection status
  - Mowing permission status (rain/frost conditions)

- **Settings**
  - Toggle Eco Mode
  - Toggle Rain Sensor
  - Toggle Frost Sensor
  - Rain sensitivity (1-10)
  - Rain delay
  - Frost threshold temperature
  - Frost delay
  - Reset blade life

- **Device Information**
  - Firmware version
  - Hardware version
  - Serial number
  - Model information

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
