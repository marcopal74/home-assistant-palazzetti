from homeassistant.components.input_number import InputNumber
import voluptuous as vol
import logging
from .const import DOMAIN
from .helper import get_platform

_LOGGER = logging.getLogger(__name__)


async def create_input_number(hass, config_entry):
    myhub = hass.data[DOMAIN][config_entry.entry_id]
    product = myhub.product
    if not product.online:
        return

    _config = product.get_data_config_json()

    entity_list = []

    # slider impostazione potenza
    if _config["_flag_has_power"]:
        data = {
            "id": f"{config_entry.unique_id}_pwr",
            "initial": _config["_value_power"],
            "max": 5.0,
            "min": 1.0,
            "mode": "slider",
            "name": "Potenza",
            "step": 1.0,
            "icon": "mdi:fire",
        }
        slider_power = MyNumber(hass, data, product, "power", config_entry.unique_id)
        entity_list.append(slider_power)

    # slider impostazione setpoint
    if _config["_flag_has_setpoint"]:
        data2 = {
            "id": f"{config_entry.unique_id}_setpoint",
            "initial": _config["_value_setpoint"],
            "max": _config["_value_setpoint_max"],
            "min": _config["_value_setpoint_min"],
            "mode": "slider",
            "name": "Setpoint",
            "unit_of_measurement": "°C",
            "step": 1.0,
            "icon": "hass:thermometer",
        }
        slider_setpoint = MyNumber(
            hass, data2, product, "setpoint", config_entry.unique_id
        )
        entity_list.append(slider_setpoint)

    # slider impostazione ventilatore principale
    if _config["_flag_has_fan_main"]:
        fan = 1
        data3 = {
            "id": f"{config_entry.unique_id}_fan1",
            "initial": _config["_value_fan_main"],
            "max": _config["_value_fan_limits"][(((fan - 1) * 2) + 1)],
            "min": _config["_value_fan_limits"][((fan - 1) * 2)],
            "mode": "slider",
            "name": "Main Fan",
            "step": 1.0,
            "icon": "mdi:fan",
        }
        slider_fan1 = MyNumber(hass, data3, product, "fan1", config_entry.unique_id)
        entity_list.append(slider_fan1)

    # slider impostazione secondo ventilatore
    if _config["_flag_has_fan_third"]:
        fan = 2
        data4 = {
            "id": f"{config_entry.unique_id}_fan2",
            "initial": _config["_value_fan_second"],
            "max": _config["_value_fan_limits"][(((fan - 1) * 2) + 1)],
            "min": _config["_value_fan_limits"][((fan - 1) * 2)],
            "mode": "slider",
            "name": "Fan L",
            "step": 1.0,
            "icon": "mdi:fan-speed-2",
        }
        slider_fan2 = MyNumber(hass, data4, product, "fan2", config_entry.unique_id)
        entity_list.append(slider_fan2)

    # slider impostazione terzo ventilatore
    if _config["_flag_has_fan_second"]:
        fan = 3
        data5 = {
            "id": f"{config_entry.unique_id}_fan3",
            "initial": _config["_value_fan_third"],
            "max": _config["_value_fan_limits"][(((fan - 1) * 2) + 1)],
            "min": _config["_value_fan_limits"][((fan - 1) * 2)],
            "mode": "slider",
            "name": "Fan R",
            "step": 1.0,
            "icon": "mdi:fan-speed-3",
        }
        slider_fan3 = MyNumber(hass, data5, product, "fan3", config_entry.unique_id)
        entity_list.append(slider_fan3)

    # if no sliders exit
    if not entity_list:
        return

    # apro la piattaforma degli slider: input_number
    platform_name = "input_number"
    input_number_platform = get_platform(hass, platform_name)
    # aggiungo la config_entry alla platform così posso agganciarla ai device
    input_number_platform.config_entry = config_entry

    # aggiunge gli slider alla platform caricata
    await input_number_platform.async_add_entities(entity_list, True)


async def unload_input_number(hass, entry) -> None:
    platform_name = "input_number"
    input_number_platform = get_platform(hass, platform_name)

    if input_number_platform:
        mylist = input_number_platform.entities
        for myentity in mylist:
            myident = mylist[myentity].device_info["identifiers"]
            for field in myident:
                field_check = field[1]
                if field_check == (entry.unique_id + "_prd"):
                    hass.async_create_task(
                        input_number_platform.async_remove_entity(myentity)
                    )


class MyNumber(InputNumber):
    """Representation of a slider."""

    def __init__(self, hass, config, product, tipo, uid):
        """Initialize an input number."""
        super().__init__(config)
        self.hass = hass
        self._name = config.get("name")
        self._id = uid
        self._product = product
        self._type = tipo
        self.editable = True

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def should_poll(self):
        """If entity should be polled."""
        return False

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        await super().async_added_to_hass()
        # Sensors should also register callbacks to HA when their state changes
        if self._product is not None:
            self._product.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        if self._product is not None:
            self._product.remove_callback(self.async_write_ha_state)

    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return self._product and self._product.online

    @property
    def state(self):
        """Return the state of the component."""
        if not self._product:
            return
        if self._type == "power":
            return self._product.get_key("PWR")
        elif self._type == "setpoint":
            return self._product.get_key("SETP")
        elif self._type == "fan1":
            return self._product.get_key("F2L")
        elif self._type == "fan2":
            return self._product.get_key("F3L")
        elif self._type == "fan3":
            return self._product.get_key("F4L")

    @property
    def _minimum(self) -> float:
        """Return minimum allowed value."""
        if self._type == "power":
            return 1.0
        elif self._type == "setpoint":
            return self._product.get_data_config_json()["_value_setpoint_min"]
        elif self._type == "fan1":
            fan = 1
            return self._product.get_data_config_json()["_value_fan_limits"][
                ((fan - 1) * 2)
            ]
        elif self._type == "fan2":
            fan = 2
            return self._product.get_data_config_json()["_value_fan_limits"][
                ((fan - 1) * 2)
            ]
        elif self._type == "fan3":
            fan = 3
            return self._product.get_data_config_json()["_value_fan_limits"][
                ((fan - 1) * 2)
            ]

    @property
    def _maximum(self) -> float:
        """Return maximum allowed value."""
        if self._type == "power":
            return 5.0
        elif self._type == "setpoint":
            return self._product.get_data_config_json()["_value_setpoint_max"]
        elif self._type == "fan1":
            fan = 1
            return self._product.get_data_config_json()["_value_fan_limits"][
                (((fan - 1) * 2) + 1)
            ]
        elif self._type == "fan2":
            fan = 2
            return self._product.get_data_config_json()["_value_fan_limits"][
                (((fan - 1) * 2) + 1)
            ]
        elif self._type == "fan3":
            fan = 3
            return self._product.get_data_config_json()["_value_fan_limits"][
                (((fan - 1) * 2) + 1)
            ]

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._product.product_id)},
        }

    async def async_set_value(self, value):
        """Set new value."""
        num_value = float(value)

        if num_value < self._minimum or num_value > self._maximum:
            raise vol.Invalid(
                f"Invalid value for {self.entity_id}: {value} (range {self._minimum} - {self._maximum})"
            )

        self._current_value = num_value
        if self._type == "power":
            await self._product.async_set_power(int(num_value))
        elif self._type == "setpoint":
            await self._product.async_set_setpoint(int(num_value))
        elif self._type == "fan1" or self._type == "fan2" or self._type == "fan3":
            await self._product.async_set_fan(int(self._type[-1:]), int(num_value))
        self.async_write_ha_state()

    async def async_update(self):
        print(f"input_number Update {self._type}")
