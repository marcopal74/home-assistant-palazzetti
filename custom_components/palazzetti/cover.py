"""Demo platform for the cover component."""
from homeassistant.components.cover import (
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    CoverEntity,
)

from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    product = hass.data[DOMAIN][config_entry.entry_id].product
    myposition = product.get_key("DOOR")
    hassposition = 0
    if myposition == 3:
        hassposition = 0
    elif myposition == 4:
        hassposition = 100

    """Set up the Demo covers."""
    async_add_entities(
        [
            PalCover(
                product,
                "fdoor",
                "Fire Door",
                device_class="door",
                position=hassposition,
                supported_features=(SUPPORT_OPEN | SUPPORT_CLOSE),
            ),
        ]
    )


class PalCover(CoverEntity):
    """Representation of a demo cover."""

    should_poll = False

    def __init__(
        self,
        product,
        key_val,
        friendly_name,
        device_class=None,
        position=None,
        supported_features=None,
    ):
        """Initialize the cover."""
        self._product = product
        self._key = key_val
        self._fname = friendly_name
        self._position = position
        self._device_class = device_class
        self._supported_features = supported_features

        # internal variables
        self._is_opening = False
        self._is_closing = False

        self._unique_id = "vuoto_" + self._key
        self._deviceid = "device_" + self._key
        if self._product and self._product.product_id:
            self._unique_id = product.product_id + "_" + self._key
            self._deviceid = self._product.product_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._deviceid)},
        }

    @property
    def unique_id(self):
        """Return unique ID for cover."""
        return self._unique_id

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._device_class

    @property
    def name(self):
        """Return the name of the cover."""
        return self._fname

    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return self._product.online

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        myposition = self._product.get_key("DOOR")
        hassposition = 0
        if myposition == 1:  # opening
            hassposition = 25
            self._is_closing = False
            self._is_opening = True
        elif myposition == 2:  # closing
            hassposition = 75
            self._is_closing = True
            self._is_opening = False
        elif myposition == 3:  # closed
            hassposition = 0
            self._is_closing = False
            self._is_opening = False
        elif myposition == 4:  # open
            hassposition = 100
            self._is_closing = False
            self._is_opening = False
        self._position = hassposition
        return self._position

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self._product.get_key("DOOR") == 3

    @property
    def is_closing(self):
        """Return if the cover is closing."""
        return self._product.get_key("DOOR") == 2 or self._is_closing

    @property
    def is_opening(self):
        """Return if the cover is opening."""
        return self._product.get_key("DOOR") == 1 or self._is_opening

    @property
    def supported_features(self):
        """Flag supported features."""
        if self._supported_features is not None:
            return self._supported_features

    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        if self._position == 0:
            return
        self._is_opening = False
        self._is_closing = True
        await self._product.async_set_door(False)

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        if self._position == 100:
            return
        self._is_opening = True
        self._is_closing = False
        await self._product.async_set_door(True)

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

    async def async_update(self):
        #  await super().async_update()
        print(f"cover Update")