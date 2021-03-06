from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    BinarySensorEntity,
)

from .const import DOMAIN, COMPANY


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the binary sensors to handle connectivity status of Hub and Product"""
    myhub = hass.data[DOMAIN][config_entry.entry_id]
    list_binary = []

    # Hub connectivity sensor
    list_binary.append(
        PalBinarySensor(
            myhub,
            "hub",
            myhub.hub_name,
            DEVICE_CLASS_CONNECTIVITY,
        )
    )

    # Product connectivity sensor
    list_binary.append(
        PalBinarySensor(
            myhub,
            "prod",
            "Product",
            DEVICE_CLASS_CONNECTIVITY,
        )
    )

    # MyCli-mate 1..3 connectivity sensor
    # only if Product is online

    # Shape connectivity sensor
    # only if Product is online

    async_add_entities(list_binary)


class PalBinarySensor(BinarySensorEntity):
    """representation of a Demo binary sensor."""

    should_poll = False

    def __init__(
        self,
        hub,
        key_val,
        friendly_name,
        device_class,
    ):
        """Initialize the demo sensor."""

        self._hub = hub
        self._key = key_val
        self._fname = friendly_name
        self._sensor_type = device_class

        # internal variables
        self._product = self._hub.product  # it could be offline
        self._ishub = self._key == "hub"

        self._unique_id = "unique_" + self._key
        self._deviceid = "device" + self._key
        if self._hub and self._hub.hub_id:
            self._unique_id = self._hub.hub_id + "_" + self._key

            self._deviceid = self._hub.hub_id
            if not self._ishub:
                self._deviceid = self._hub.hub_id + "_prd"

    @property
    def device_info(self):
        if not self._hub.online:
            return {
                "identifiers": {(DOMAIN, self._deviceid)},
            }

        # Hub is online:
        if self._ishub:
            return {
                "identifiers": {(DOMAIN, self._deviceid)},
                "name": f"{self._fname} {self._hub.get_attributes()['MAC']}",
                "manufacturer": COMPANY,
                "model": self._hub.get_attributes()["MAC"],
                "sw_version": self._hub.get_attributes()["SYSTEM"],
            }

        # By now no MyCli-mate or Shape
        return {
            "identifiers": {(DOMAIN, self._deviceid)},
            "name": self._hub.label,
            "manufacturer": COMPANY,
            "model": self._product.get_key("SN"),
            "sw_version": f"mod {self._product.get_key('MOD')} v{self._product.get_key('VER')} {self._product.get_key('FWDATE')}",
            "via_device": (DOMAIN, self._hub.hub_id),
        }

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        # either _hub or _prod
        return self._unique_id

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name of the binary sensor."""
        # either ConnBox, BioCC or Product
        return self._fname

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if self.is_on:
            if self._ishub:
                return "mdi:server-network"
            return "mdi:link"
        else:
            if self._ishub:
                return "mdi:server-network-off"
            return "mdi:link-off"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if not self._hub.online:
            return False

        if self._ishub:
            return self._hub.online

        if self._product:
            return self._product.online

        return self._hub.product_online

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        if not self._hub.online:
            return None

        if self._ishub:
            cbox_attrib = self._hub.get_attributes()
            return cbox_attrib

        _prod_attrib = {}
        if not self._hub.product_online:
            _prod_attrib.update({"icon": "mdi:link-off"})
            return _prod_attrib

        if self._product:
            _prod_attrib = self._product.get_attributes()
            _prod_attrib.update({"icon": "mdi:link"})
            return _prod_attrib

        return None

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._hub.register_callback(self.async_write_ha_state)
        if self._product is not None:
            self._hub.register_callback(self.async_write_ha_state)
            self._product.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._hub.remove_callback(self.async_write_ha_state)
        if self._product is not None:
            self._product.remove_callback(self.async_write_ha_state)

    async def async_update(self):
        print(f"binary_sensor PalBinarySensor update: {self._key}")
