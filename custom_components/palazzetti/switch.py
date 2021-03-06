"""Demo platform that has two fake switches."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import DEVICE_DEFAULT_NAME
import logging
from palazzetti_sdk_local_api import exceptions as palexcept
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Demo config entry."""
    myhub = hass.data[DOMAIN][config_entry.entry_id]
    product = myhub.product
    if not product.online:
        return

    _config = product.get_data_config_json()

    entity_list = []

    # no power switch is if BioCC despite config data
    if not myhub.hub_isbiocc:
        entity_list.append(
            OnOffSwitch(product, "ON/OFF", False, "mdi:power", device_class="outlet")
        )

    if _config["_flag_is_air"] and (_config["_flag_has_fan_zero_speed_fan"]):
        entity_list.append(
            ZeroSpeed(product, "Silent", False, "mdi:fan-off", device_class="outlet")
        )
    async_add_entities(entity_list)


class BaseSwitch(SwitchEntity):
    """Representation of a demo switch."""

    should_poll = False

    def __init__(self, product, friendly_name, state, icon, device_class=None):
        """Initialize the Demo switch."""
        self._product = product
        self._fname = friendly_name or DEVICE_DEFAULT_NAME
        self._state = state
        self._icon = icon
        self._device_class = device_class

        # internal variables
        self._assumed = False
        self._deviceid = "device_" + self._fname
        if self._product and self._product.product_id:
            self._deviceid = self._product.product_id

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._deviceid)}}

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._fname

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return self._icon

    @property
    def assumed_state(self):
        """Return if the state is based on assumptions."""
        return self._assumed

    @property
    def device_class(self):
        """Return device of entity."""
        return self._device_class

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


class OnOffSwitch(BaseSwitch):
    """Representation of a demo switch."""

    def __init__(self, product, friendly_name, state, icon, device_class=None):
        """Initialize the Demo switch."""
        super().__init__(product, friendly_name, state, icon, device_class)

        self._key = "_onoff"

        self._unique_id = "vuoto_" + self._key
        if self._product and self._product.product_id:
            self._unique_id = self._product.product_id + "_" + self._key

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def available(self) -> bool:
        """Return True if product and hub is available."""
        return (
            self._product.online
            and self._product.get_data_config_json()["_flag_has_switch_on_off"]
        )

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._product.get_data_config_json()["_value_product_is_on"]

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        if self._product.get_data_config_json()["_flag_has_switch_on_off"]:
            try:
                self._product.power_on()
                self._state = True
                self.schedule_update_ha_state()
            except palexcept.InvalidStateTransitionError:
                print("Errore: non può essere acceso")
                _LOGGER.warning("Error cannot change state")
            except:
                print("Errore generico")
        else:
            print("Errore: non può essere spento")
            _LOGGER.warning("Error cannot change state")

    def turn_off(self, **kwargs):
        """Turn the device off."""
        if self._product.get_data_config_json()["_flag_has_switch_on_off"]:
            try:
                self._product.power_off()
                self._state = False
                self.schedule_update_ha_state()
            except:
                print("Errore: non può essere spento")
                _LOGGER.warning("Error cannot change state")
        else:
            print("Errore: non può essere spento")
            _LOGGER.warning("Error cannot change state")

    async def async_update(self):
        print(f"switch OnOffSwitch Update")


class ZeroSpeed(BaseSwitch):
    """Representation of a demo switch."""

    def __init__(self, product, friendly_name, state, icon, device_class=None):
        """Initialize the Demo switch."""
        super().__init__(product, friendly_name, state, icon, device_class)

        self._key = "silent"

        # internal variables
        self._unique_id = "vuoto_" + self._key
        if product and product.product_id:
            self._unique_id = product.product_id + "_" + self._key

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return self._product.online

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._product.get_data_config_json()["_value_fan_main"] == 0

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        if not self._product.get_data_config_json()["_value_fan_main"] == 0:
            try:
                self._product.set_fan_silent_mode()
                self._state = True
                self.schedule_update_ha_state()
            except palexcept.InvalidStateTransitionError:
                print("Errore: non può essere acceso")
                _LOGGER.warning("Error cannot change state")
            except:
                print("Errore generico")
        else:
            print("Errore: non può essere spento")
            _LOGGER.warning("Error cannot change state")

    def turn_off(self, **kwargs):
        """Turn the device off."""
        if self._product.get_data_config_json()["_value_fan_main"] == 0:
            try:
                self._product.set_fan(1, 1)
                self._state = False
                self.schedule_update_ha_state()
            except:
                print("Errore: non può essere spento")
                _LOGGER.warning("Error cannot change state")
        else:
            print("Errore: non può essere spento")
            _LOGGER.warning("Error cannot change state")

    async def async_update(self):
        print(f"switch ZeroSpeed Update")