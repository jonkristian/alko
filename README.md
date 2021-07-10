# AL-KO Robolinho component for Home Assistant
This component allows you to integrate your AL-KO Robolinho mower in Home Assistant.
For advanced users only, please see further explaination below.

## Supports
- Battery level sensor
- Operation states
- Operation errors
- Remaining blade life
- Toggle **Eco Mode** and **Rain Sensor**

## Planned
- Translate operation state strings to something more readable.
- Add reasonable string translations for error codes.
- Control mode select which would allow you to start/stop the mower.
- Translations
#

## Installation

The AL-KO API is unfortunately not open for 3rd party applications. In order for this component to work you will have to find a way to extract your AL-KO inTOUCH app `client_secret`, but also `access_token` and `refresh_token` for the initial setup. There might be several ways to do this, but a tested method involves downloading the inTOUCH .xapk, using [apk-mitm](https://github.com/shroudedcode/apk-mitm) to prepare the app for inspection, installing the generated app and using [HTTP Toolkit](httptoolkit.tech/) to intercept communication.

As stated above, this is currently only for advanced users. I won't go into any more details about the approach, but tools and guides are readily available online.

### Installation
If you're using HACS you can add this repo as a custom repository and install, otherwise download or clone and copy the folder `custom_components/alko` into your `custom_components/`\
Add the following to your configuration.yaml.

```yaml
alko:
  client_id: inTouchApp
  client_secret: your_client_secret
```

Once configured you will find AL-KO in the integration popup list. The integration steps requires an `access_token` and a `refresh_token` which you should find via the HTTP Toolkit. 

### Where to look for **access_token** and **refresh_token**
In the HTTP Toolkit you should see a POST request to `adp.al-ko.com/connect/token`, from the response you will find both the `access_token` and `refresh_token` to use in the configuration steps.

## Contribute
If you own a smart product from AL-KO and would like to contribute, please don't hesitate getting in touch.

### Regarding the AL-KO Api
It's really sad that many manufacturers don't allow for 3rd party apps, since these APIs are already there and available through their own app most of the time, I personally don't see what the harm is. I've already sent an e-mail to AL-KO requesting that they open up to allow for more advanced home automation platforms like Home Assistant, but weeks have gone and I don't really expect getting a reply back. Maybe they will listen if more people get involved so if you want to try and do something about this, the e-mail I've found is mediamanager@al-ko.de.
#
⭐️ this repository if you found it useful ❤️

<a href="https://www.buymeacoffee.com/jonkristian" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
