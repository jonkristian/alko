# AL-KO Robolinho component for Home Assistant
This component allows you to integrate your AL-KO Robolinho mower in Home Assistant.
For advanced users only, please see further explaination below.

## Supports
- Battery level sensor
- Operation states
- Operation errors
- Remaining blade life
- Toggle **Eco Mode** and **Rain Sensor**
- Start and Stop mowing

## Planned
- Translate operation state strings to something more readable.
- Add reasonable string translations for error codes.
- Translation

# Installation

## Manual or via HACS
If you're using HACS you can add this repo as a custom repository and install, otherwise download or clone and copy the folder `custom_components/alko` into your `custom_components/`. Be sure to restart.
## Finding secret and tokens (Android only | Requires adb)
The AL-KO API is unfortunately not open for 3rd party applications. In order for this component to work you will have to have set up the AL-KO inTOUCH app and a [working adb connection to your phone](https://developer.android.com/studio/command-line/adb). To extract your secret and tokens I've created a very simple and crude script that will output these in the terminal.
- Download [intouch-credentials.sh](https://raw.githubusercontent.com/jonkristian/alko/master/tools/intouch-credentials.sh) (located in tools folder).
- Then `chmod +x intouch-credentials.sh` and `./intouch-credentials.sh` to run.
- Now unlock your phone and click confirm the backup operation (do not encrypt).
- This should print your `client_secret`, `access_token` and `refresh_token` the latter two is required during the integration setup step.
- Add the following to your configuration.yaml.

```yaml
alko:
  client_id: inTouchApp
  client_secret: your_client_secret
```
After a restart you should now be able to add the integration via the integrations page, remember that tokens are short-lived 30 minutes.
***
## Contribute
If you own a smart product from AL-KO and would like to contribute, please don't hesitate getting in touch.

### Regarding the AL-KO Api
It's really sad that many manufacturers don't allow for 3rd party apps, since these APIs are already there and available through their own app most of the time, I personally don't see what the harm is. I've already sent an e-mail to AL-KO requesting that they open up to allow for more advanced home automation platforms like Home Assistant, but weeks have gone and I don't really expect getting a reply back. Maybe they will listen if more people get involved so if you want to try and do something about this, the e-mail I've found is mediamanager@al-ko.de.
***
⭐️ this repository if you found it useful ❤️

<a href="https://www.buymeacoffee.com/jonkristian" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
