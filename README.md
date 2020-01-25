# Home Assistant Convert Media Player Volume

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
<br><a href="https://www.buymeacoffee.com/Petro31" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-black.png" width="150px" height="35px" alt="Buy Me A Coffee" style="height: 35px !important;width: 150px !important;" ></a>

_Convert Media Player Volume app for AppDaemon._

This creates a sensor that represents your hardwares volume level.  

Home assistant typically represents it's volume from 0.0 to 1.0.  Many hardware devices have ranges outside these values.  This app will convert the home assistant ranges to your devices ranges!

## Installation

Download the `convert_media_volume` directory from inside the `apps` directory to your local `apps` directory, then add the configuration to enable the `hacs` module.

## Example App configuration

#### Basic
```yaml
#  0 to 100 volume range
zone1_volume:
  module: convert_media_volume
  class: ConvertMediaVolume
  media_player: media_player.bravia
```

#### Alexa Media Player 
```yaml
# Converts volume range from 0 to 10.
zone1_volume:
  module: convert_media_volume
  class: ConvertMediaVolume
  media_player: media_player.alexa
  min_volume:
    device: 0.0
    media_player: 0.0
  max_volume:
    device: 10.0
    media_player: 1.0
  precision: 0
```

#### decibel 
```yaml
# Converts to decibels (dB) - Typical Yamaha Media Player Configuration
zone1_volume:
  module: convert_media_volume
  class: ConvertMediaVolume
  media_player: media_player.yamaha_receiver
  unit_of_measurement: dB
  min_volume:
    device: -80.0
    media_player: 0.2
  max_volume:
    device: 0.0
    media_player: 1.0
  precision: 0
```

#### App Configuration
key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | convert_media_volume | The module name of the app.
`class` | False | string | ConvertMediaVolume | The name of the Class.
`media_player` | False | string | | entity_id of the media_player.
`name` | True | str | `<media player name> Volume` | Friendly name of the Media Player.
`min_volume`| True | map | | A map of the device min volume level and media_player volume level.
`max_volume`| True | map | | A map of the device max volume level and media_player volume level.
`precision`| True | int | 1 | precision of the sensor. e.g. 100.0 has a precision of 1, 1 number after the decimal place.
`log_level` | True | `'INFO'` &#124; `'DEBUG'` | `'INFO'` | Switches log level.

#### Min Map Configuration
key | optional | type | default | description
-- | -- | -- | -- | --
`device` | True | float | 0.0 | Device volume at the lowest possible level.
`media_player` | True | float | 0.0 | `media_player.<entity_id>.attributes.volume_level` at the lowest possible level.

#### Max Map Configuration
key | optional | type | default | description
-- | -- | -- | -- | --
`device` | True | float | 100.0 | Device volume at the highest possible level.
`media_player` | True | float | 1.0 | `media_player.<entity_id>.attributes.volume_level` at the highest possible level.

## Recommended Setup

#### Getting the miminum volume

1.  Turn on the media_player in home assistant.
2.  Slide the volume slider all the way to the left.
3.  Open Developer Tools / States page.
4.  Find the media_player adjusted in step 2.
5.  Record the numerical value for `volume_level` in the configuration `min_volume/media_player`.
6.  Record the numerical value on your device in the configuration `min_volume/device`.

#### Getting the maximum volume

_You don't need to record the maximum.  You just need a value higher than the minimum.  The further away, the better._

1.  Turn on the media_player in home assistant.
2.  Slide the volume slider all the way to the right.
3.  Open Developer Tools / States page.
4.  Find the media_player adjusted in step 2.
5.  Record the numerical value for `volume_level` in the configuration `max_volume/media_player`.
6.  Record the numerical value on your device in the configuration `max_volume/device`.
