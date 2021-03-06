


# home-assistant-palazzetti

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

## Description
Definitive Palazzetti SmartStoves integration for Home Assistant

**This component will set up the following platforms.**

| Platform        | Description                                                               |
| --------------- | ------------------------------------------------------------------------- |
| `binary_sensor` | To show the state of the CBox or BioCC: `Connected` or `Disconnected`.        |
| `sensor`        | Show info from product like `temperatures`, `pellet consumption`, etc.        |
| `input_number`  | To set target `setpoint` or fan `speed` or maximum allowed `power level`. |
| `switch`        | Switch something `ON` or `OFF`.                                           |
| `cover`         | For fireplaces with automatic door to `Open` or `Close`.                  |

| Screen | Product type |
|-----------|-----------|
| ![screenshot boiler][exampleimg_boiler] | JP21 Boiler             |
| ![screenshot stove][exampleimg_stove]   | Air Pro3 Stove     |
| ![screenshot WT][exampleimg_wt]         | Monoblocco WT Plus |

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `palazzetti`.
4. Download _all_ the files from the `custom_components/palazzetti/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Palazzetti"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/palazzetti/translations/en.json
custom_components/palazzetti/translations/it.json
custom_components/palazzetti/__init__.py
custom_components/palazzetti/binary_sensor.py
custom_components/palazzetti/config_flow.py
custom_components/palazzetti/const.py
custom_components/palazzetti/cover.py
custom_components/palazzetti/device_trigger.py
custom_components/palazzetti/helper.py
custom_components/palazzetti/input_number.py
custom_components/palazzetti/manifest.json
custom_components/palazzetti/sensor.py
custom_components/palazzetti/services.yaml
custom_components/palazzetti/switch.py
```

## Configuration is done in the UI

In order to properly configure the integration you'll be required to type in the IP address of the ConnectionBox or the BioCC.
To get the IP use the App or the User interface to find it!

## Credits

Readme template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/marcopal74
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/marcopal74/home-assistant-palazzetti.svg?style=for-the-badge
[commits]: https://github.com/marcopal74/home-assistant-palazzetti/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg_boiler]: example_boiler.png
[exampleimg_stove]: example_stove.png
[exampleimg_wt]: example_wt.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/marcopal74/home-assistant-palazzetti.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40marcopal74-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/marcopal74/home-assistant-palazzetti.svg?style=for-the-badge
[releases]: https://github.com/marcopal74/home-assistant-palazzetti/releases
[user_profile]: https://github.com/marcopal74
