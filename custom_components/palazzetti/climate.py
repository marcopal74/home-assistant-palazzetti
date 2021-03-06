"""Demo platform that offers a fake climate device."""
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    HVAC_MODES,
    SUPPORT_AUX_HEAT,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_HUMIDITY,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_TARGET_TEMPERATURE_RANGE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT
from palazzetti_sdk_local_api import exceptions as palexcept
import logging
from .const import DOMAIN

SUPPORT_FLAGS = 0
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Demo climate devices."""
    climate_id = config.unique_id
    product = hass.data[DOMAIN][config.entry_id].product
    # _config = config.data["stove"]
    # if not _config["_flag_has_setpoint"]:
    # if not hass.data[DATA_DOMAIN].get_data_config_json()["_flag_has_setpoint"]:
    #    return

    if product.get_data_config_json()["_value_product_is_on"]:
        currstate = HVAC_MODE_HEAT
        curraction = CURRENT_HVAC_HEAT
    else:
        currstate = HVAC_MODE_OFF
        curraction = "idle"

    async_add_entities(
        [
            PalClimate(
                product,
                unique_id=climate_id,
                name=product.get_key("LABEL"),
                target_temperature=product.get_key("SETP"),
                unit_of_measurement=TEMP_CELSIUS,
                preset=None,
                current_temperature=product.get_data_config_json()["_value_temp_main"],
                fan_mode=None,
                target_humidity=None,
                current_humidity=None,
                swing_mode=None,
                hvac_mode=currstate,
                hvac_action=curraction,
                aux=None,
                target_temp_high=None,
                target_temp_low=None,
                hvac_modes=[HVAC_MODE_HEAT, HVAC_MODE_OFF],
            ),
        ]
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Demo climate devices config entry."""
    await async_setup_platform(hass, config_entry, async_add_entities)


class PalClimate(ClimateEntity):
    """Representation of a demo climate device."""

    def __init__(
        self,
        product,
        unique_id,
        name,
        target_temperature,
        unit_of_measurement,
        preset,
        current_temperature,
        fan_mode,
        target_humidity,
        current_humidity,
        swing_mode,
        hvac_mode,
        hvac_action,
        aux,
        target_temp_high,
        target_temp_low,
        hvac_modes,
        preset_modes=None,
    ):
        """Initialize the climate device."""
        self._product = product
        self._id = unique_id
        self._unique_id = unique_id + "_climate"
        self._name = name
        self._support_flags = SUPPORT_FLAGS
        if target_temperature is not None:
            self._support_flags = self._support_flags | SUPPORT_TARGET_TEMPERATURE
        if preset is not None:
            self._support_flags = self._support_flags | SUPPORT_PRESET_MODE
        if fan_mode is not None:
            self._support_flags = self._support_flags | SUPPORT_FAN_MODE
        if target_humidity is not None:
            self._support_flags = self._support_flags | SUPPORT_TARGET_HUMIDITY
        if swing_mode is not None:
            self._support_flags = self._support_flags | SUPPORT_SWING_MODE
        if aux is not None:
            self._support_flags = self._support_flags | SUPPORT_AUX_HEAT
        if HVAC_MODE_HEAT_COOL in hvac_modes or HVAC_MODE_AUTO in hvac_modes:
            self._support_flags = self._support_flags | SUPPORT_TARGET_TEMPERATURE_RANGE
        self._target_temperature = target_temperature
        self._target_humidity = target_humidity
        self._unit_of_measurement = unit_of_measurement
        self._preset = preset
        self._preset_modes = preset_modes
        self._current_temperature = current_temperature
        self._current_humidity = current_humidity
        self._current_fan_mode = fan_mode
        self._hvac_action = hvac_action
        self._hvac_mode = hvac_mode
        self._aux = aux
        self._current_swing_mode = swing_mode
        self._fan_modes = ["On Low", "On High", "Auto Low", "Auto High", "Off"]
        self._hvac_modes = hvac_modes
        self._swing_modes = ["Auto", "1", "2", "3", "Off"]
        self._target_temperature_high = target_temp_high
        self._target_temperature_low = target_temp_low

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._product.product_id)},
        }

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return 1.0

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._product.get_data_config_json()["_value_temp_main"]

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._product.get_key("SETP")

    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach."""
        return self._target_temperature_high

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        return self._target_temperature_low

    @property
    def min_temp(self):
        """Return the lowbound target temperature we try to reach."""
        return self._product.get_data_config_json()["_value_setpoint_min"]

    @property
    def max_temp(self):
        """Return the lowbound target temperature we try to reach."""
        return self._product.get_data_config_json()["_value_setpoint_max"]

    @property
    def current_humidity(self):
        """Return the current humidity."""
        return self._current_humidity

    @property
    def target_humidity(self):
        """Return the humidity we try to reach."""
        return self._target_humidity

    @property
    def hvac_action(self):
        """Return current operation ie. heat, cool, idle."""
        if self._product.get_data_config_json()["_value_product_is_on"]:
            currstate = CURRENT_HVAC_HEAT
        else:
            currstate = "idle"
        return currstate

    @property
    def hvac_mode(self):
        """Return hvac target hvac state."""
        if self._product.get_data_config_json()["_value_product_is_on"]:
            currstate = HVAC_MODE_HEAT
        else:
            currstate = HVAC_MODE_OFF
        return currstate

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._hvac_modes

    @property
    def preset_mode(self):
        """Return preset mode."""
        return self._preset

    @property
    def preset_modes(self):
        """Return preset modes."""
        return self._preset_modes

    @property
    def is_aux_heat(self):
        """Return true if aux heat is on."""
        return self._aux

    @property
    def fan_mode(self):
        """Return the fan setting."""
        return self._current_fan_mode

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return self._fan_modes

    @property
    def swing_mode(self):
        """Return the swing setting."""
        return self._current_swing_mode

    @property
    def swing_modes(self):
        """List of available swing modes."""
        return self._swing_modes

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        if self._product is not None:
            self._product.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        if self._product is not None:
            self._product.remove_callback(self.async_write_ha_state)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            # imposta la temperatura
            _oldtemp = self._target_temperature
            _newtemp = kwargs.get(ATTR_TEMPERATURE)
            try:
                await self._product.async_set_setpoint(int(_newtemp))
            except:
                self._target_temperature = _oldtemp
                self.async_write_ha_state()
                return
            self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
        self.async_write_ha_state()

    async def async_set_humidity(self, humidity):
        """Set new humidity level."""
        self._target_humidity = humidity
        self.async_write_ha_state()

    async def async_set_swing_mode(self, swing_mode):
        """Set new swing mode."""
        self._current_swing_mode = swing_mode
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode):
        """Set new fan mode."""
        self._current_fan_mode = fan_mode
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new operation mode."""
        if hvac_mode == HVAC_MODE_OFF:
            try:
                self._product.power_off()
                self._hvac_mode = hvac_mode
                self.async_write_ha_state()
            except palexcept.InvalidStateTransitionError:
                print("Errore: non può essere spento")
                _LOGGER.warning("Error cannot change state")
            except:
                print("Errore generico")

        elif hvac_mode == HVAC_MODE_HEAT:
            try:
                self._product.power_on()
                self._hvac_mode = hvac_mode
                self.async_write_ha_state()
            except palexcept.InvalidStateTransitionError:
                print("Errore: non può essere acceso")
                _LOGGER.warning("Error cannot change state")
            except:
                print("Errore generico")

    async def async_set_preset_mode(self, preset_mode):
        """Update preset_mode on."""
        self._preset = preset_mode
        self.async_write_ha_state()

    async def async_turn_aux_heat_on(self):
        """Turn auxiliary heater on."""
        self._aux = True
        self.async_write_ha_state()

    async def async_turn_aux_heat_off(self):
        """Turn auxiliary heater off."""
        self._aux = False
        self.async_write_ha_state()

    async def async_update(self):
        await super().async_update()
        print(f"climate Update")
