import appdaemon.plugins.hass.hassapi as hass
import voluptuous as vol

MODULE = 'convert_media_volume'
CLASS = 'ConvertMediaVolume'

CONF_MODULE = 'module'
CONF_CLASS = 'class'


CONF_DEVICE = 'device'
CONF_LOG_LEVEL = 'log_level'
CONF_MAX_VOLUME = 'max_volume'
CONF_MEDIA_PLAYER = 'media_player'
CONF_MIN_VOLUME = 'min_volume'
CONF_NAME = 'name'
CONF_PRECISION = 'precision'
CONF_SENSOR = 'sensor'
CONF_UNIT_OF_MEASUREMENT = 'unit_of_measurement'

LOG_DEBUG = 'DEBUG'
LOG_ERROR = 'ERROR'
LOG_INFO = 'INFO'
LOG_WARNING = 'WARNING'

STATE_ON = 'on'
STATE_OFF = 'off'

STATE = 'state'
ATTRIBUTES = 'attributes'

ATTRIBUTE_FRIENDLY_NAME = 'friendly_name'
ATTRIBUTE_UNIT_OF_MEASUREMENT = CONF_UNIT_OF_MEASUREMENT
ATTRIBUTE_SLOPE = 'slope'
ATTRIBUTE_INTERCEPT = 'intercept'
ATTRIBUTE_VOLUME_LEVEL = 'volume_level'

MIN_LEVEL_SCHEMA = vol.Schema({
    vol.Optional(CONF_DEVICE, default = 0.0): vol.All(vol.Coerce(float), vol.Range(min=-100.0, max=1000.0)),
    vol.Optional(CONF_MEDIA_PLAYER, default = 0.0): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.25)),
})

MAX_LEVEL_SCHEMA = vol.Schema({
    vol.Optional(CONF_DEVICE, default = 100.0): vol.All(vol.Coerce(float), vol.Range(min=-100.0, max=1000.0)),
    vol.Optional(CONF_MEDIA_PLAYER, default = 1.0): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.25)),
})

APP_SCHEMA = vol.Schema({
    vol.Required(CONF_MODULE): MODULE,
    vol.Required(CONF_CLASS): CLASS,
    vol.Required(CONF_MEDIA_PLAYER): str,
    vol.Optional(CONF_NAME): str,
    vol.Optional(CONF_LOG_LEVEL, default=LOG_DEBUG): vol.Any(LOG_INFO, LOG_DEBUG),
    vol.Optional(CONF_MIN_VOLUME, default={}): MIN_LEVEL_SCHEMA,
    vol.Optional(CONF_MAX_VOLUME, default={}): MAX_LEVEL_SCHEMA,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT): str,
    vol.Optional(CONF_PRECISION, default=1): vol.All(vol.Coerce(int), vol.Range(min=0, max=2)),
})

class ConvertMediaVolume(hass.Hass):
    def initialize(self):
        args = APP_SCHEMA(self.args)

        # Set Lazy Logging (to not have to restart appdaemon)
        self._level = args.get(CONF_LOG_LEVEL)
        self.log(args, level=self._level)

        min = VolumePoint(args.get(CONF_MIN_VOLUME))
        max = VolumePoint(args.get(CONF_MAX_VOLUME))
        self._min, self._max = min.x, min.y

        self._entity_id = args.get(CONF_MEDIA_PLAYER)
        name = self.get_state(self._entity_id, attribute=ATTRIBUTE_FRIENDLY_NAME)

        self._name = args.get(CONF_NAME, f"{name} Volume")
        self._sensor_id = f"{CONF_SENSOR}.{self._name.lower().replace(' ','_')}"
        self._units = args.get(CONF_UNIT_OF_MEASUREMENT)

        self._m, self._c = self.trendline(min, max)

        #set precision format for sensor.
        precision = args.get(CONF_PRECISION)
        self._fmat = f"{{0:.{precision}f}}"

        # Set the sensor with the current volume level.
        self.set_level(self.get_state(self._entity_id, attribute = 'all'))

        # create volume listener.
        self.log(f'Creating {self._entity_id} listener.', level = self._level)
        self.handle = self.listen_state(self.media_player_callback, self._entity_id, attribute = 'all')

    def media_player_callback(self, entity, attribute, old, new, kwargs):
        self.log(f"{entity}.{attribute}: {old} -> {new}", level = self._level)
        self.set_level(new)

    def set_level(self, stateobj):
        state = stateobj.get(STATE)
        if state == STATE_ON:
            level = stateobj[ATTRIBUTES].get(ATTRIBUTE_VOLUME_LEVEL)
            if level is not None:
                self.update_sensor(level)
        elif state == STATE_OFF:
            self.update_sensor(self._min)

    def trendline(self, p1, p2):
        """ simple trendline fit to get y=mx+c """
        d = (p2.x - p1.x)
        if d == 0:
            raise ZeroDivisionError("Media player volume minimum cannot equal media player maximum.")
        m = (p2.y - p1.y) / d
        c = p2.y - m * p2.x
        self.log(f"y = {m}x + {c}", level = self._level)
        return m, c

    def update_sensor(self, level):
        attributes = {
            ATTRIBUTE_FRIENDLY_NAME: self._name,
            ATTRIBUTE_SLOPE: self._m,
            ATTRIBUTE_INTERCEPT: self._c,
        }
        if self._units:
            attributes[ATTRIBUTE_UNIT_OF_MEASUREMENT] = self._units
        
        state = self._fmat.format(level * self._m + self._c)
        self.log(f"{self._sensor_id} -> {state}: {attributes}", level = self._level)
        self.set_state(self._sensor_id, state=state, attributes=attributes)

    def terminate(self):
        self.log(f'Canceling {self._entity_id} listener.', level = self._level)
        self.cancel_listen_state(self.handle)

class VolumePoint(object):
    def __init__(self, data):
        """ simple point class, probably overcomplicated """
        self.x = data.get(CONF_MEDIA_PLAYER)
        self.y = data.get(CONF_DEVICE)
