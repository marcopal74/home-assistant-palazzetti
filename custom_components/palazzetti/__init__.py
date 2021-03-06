"""
The "palazzetti" custom component.
Configuration:
To use the palazzetti component you will need to add the integration from
the integration menu and set the ip of the Connection Box when asked
"""
import logging, asyncio
from homeassistant.core import HomeAssistant
from homeassistant import exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv, entity_registry
from homeassistant.helpers.event import (
    async_track_time_interval,
)
from homeassistant.const import ATTR_ENTITY_ID
from .const import DOMAIN, INTERVAL, INTERVAL_CNTR, INTERVAL_STDT, INTERVAL_KPAL
from .input_number import create_input_number, unload_input_number
from .helper import setup_platform
import voluptuous as vol
from palazzetti_sdk_local_api import Hub

_LOGGER = logging.getLogger(__name__)

PLATFORMS_LOAD = [
    #  "binary_sensor",
    "switch",
    "sensor",
    "input_number",
    # "climate",
    "cover",
]

PLATFORMS_UNLOAD = [
    "binary_sensor",
    "switch",
    "sensor",
    # "input_number",
    # "climate",
    "cover",
]

LISTENERS = [
    "_listener_alls",
    "_listener_cntr",
    "_listener_stdt",
    "_listener_kalive",
]

SERVICES = ["set_setpoint"]


async def async_keep_alive(hass: HomeAssistant, entry: ConfigEntry):
    myhub = hass.data[DOMAIN][entry.entry_id]
    await myhub.async_update(deep=False)

    if myhub.hub_online:
        if myhub.product_online:
            print("IP now reachable and product is online")
            await hass.config_entries.async_reload(entry.entry_id)
        else:
            print("IP now reachable but product offline")
    else:
        print("IP still not reachable")


async def async_upd_alls(hass: HomeAssistant, entry: ConfigEntry):
    myhub = hass.data[DOMAIN][entry.entry_id]
    # this update takes care to activate callbacks to update UI
    # in case something goes offline
    await myhub.async_update(deep=False)

    if myhub.product_online:
        _api = myhub.product
        if _api:
            await _api.async_get_alls()
    return


async def async_upd_cntr(hass: HomeAssistant, entry: ConfigEntry):
    myhub = hass.data[DOMAIN][entry.entry_id]
    # this update takes care to activate callbacks to update UI
    # in case something goes offline
    await myhub.async_update(deep=True)

    if myhub.product_online:
        _api = myhub.product
        if _api:
            await _api.async_get_cntr()
    return


async def async_upd_stdt(hass: HomeAssistant, entry: ConfigEntry):
    myhub = hass.data[DOMAIN][entry.entry_id]
    # this update takes care to activate callbacks to update UI
    # in case something goes offline
    await myhub.async_update(deep=True)

    if myhub.product_online:
        _api = myhub.product
        if _api:
            await _api.async_get_stdt()
    return


async def async_create_platforms(hass: HomeAssistant, entry: ConfigEntry):
    print("Creating platforms")

    my_api = hass.data[DOMAIN][entry.entry_id].product
    if not my_api.online:
        return

    _config = my_api.get_data_config_json()

    await setup_platform(hass, "input_number")

    for component in PLATFORMS_LOAD:
        if component == "cover":
            if _config["_flag_has_door_control"]:
                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
        elif component == "climate":
            if _config["_flag_has_setpoint"]:
                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
        elif component == "light":
            if _config["_flag_has_light_control"]:
                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
        elif component == "fan":
            if _config["_flag_has_fan"]:
                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
        elif component == "input_number":
            hass.async_create_task(create_input_number(hass, entry))
        else:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, component)
            )


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the GitHub Custom component from yaml configuration."""
    print("Lancia async_setup")
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Init of palazzetti component")
    print("Lancia async_setup_entry")
    # check and remove keep alive loop data
    kalive_key = entry.entry_id + "_listener_kalive"
    if kalive_key in hass.data[DOMAIN]:
        # remove listener
        hass.data[DOMAIN][kalive_key]()
        # cleanup hass.data
        hass.data[DOMAIN].pop(kalive_key)

    # load last known configuration
    #  _config = entry.data["stove"]
    # checks IP
    myhub = Hub(entry.data["host"], entry.data["hub_isbiocc"])
    hass.data[DOMAIN][entry.entry_id] = myhub
    await myhub.async_update(discovery=True)

    # setup binary_sensor for state monitoring
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )

    if (not myhub.online) or (not myhub.product_online):
        print("IP is unreachable or product offline")

        # keep alive loop until ip is reachable
        def keep_alive(event_time):
            return asyncio.run_coroutine_threadsafe(
                async_keep_alive(hass, entry), hass.loop
            )

        # activate a keep alive loop
        listener_kalive = async_track_time_interval(hass, keep_alive, INTERVAL_KPAL)
        hass.data[DOMAIN][entry.entry_id + "_listener_kalive"] = listener_kalive
        return True

    print("IP is reachable and product is online")

    # loop for get dynamic data of stove
    def update_state_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_alls(hass, entry), hass.loop)

    # loop for get counters data of stove
    def update_cntr_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_cntr(hass, entry), hass.loop)

    # loop for get static data of stove
    def update_static_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_stdt(hass, entry), hass.loop)

    listener_alls = async_track_time_interval(hass, update_state_datas, INTERVAL)
    hass.data[DOMAIN][entry.entry_id + "_listener_alls"] = listener_alls
    listener_cntr = async_track_time_interval(hass, update_cntr_datas, INTERVAL_CNTR)
    hass.data[DOMAIN][entry.entry_id + "_listener_cntr"] = listener_cntr
    listener_stdt = async_track_time_interval(hass, update_static_datas, INTERVAL_STDT)
    hass.data[DOMAIN][entry.entry_id + "_listener_stdt"] = listener_stdt

    # create platforms
    await async_create_platforms(hass, entry)

    # services
    print("Creating service")

    # service set_setpoint
    SET_SCHEMA = vol.Schema(
        {
            # vol.Required(ATTR_ENTITY_ID): vol.In(myids),
            vol.Optional(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("value"): cv.string,
        }
    )

    async def set_setpoint(call):
        """Handle the service call 'set'"""

        # mydata = call
        _api = None
        registry = await entity_registry.async_get_registry(hass)
        myentity_ok = registry.async_get(call.data["entity_id"])
        if not myentity_ok or not myentity_ok.platform == DOMAIN:
            raise CannotExecute
        _api = hass.data[DOMAIN][myentity_ok.config_entry_id].product
        # mydata_entry = entry
        if _api:
            myvalue = call.data["value"]
            await _api.async_set_setpoint(myvalue)

    hass.services.async_register(DOMAIN, "set_setpoint", set_setpoint, SET_SCHEMA)

    # Return boolean to indicate that initialization was successfully.
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    print("Unload all")
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS_UNLOAD
            ]
        )
    )

    # unloads input_number entities
    await unload_input_number(hass, entry)

    for mylistener in LISTENERS:
        if entry.entry_id + str(mylistener) in hass.data[DOMAIN]:
            hass.data[DOMAIN][entry.entry_id + str(mylistener)]()
            hass.data[DOMAIN].pop(entry.entry_id + str(mylistener))

    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)

    #  removes services only if no other hubs are connected
    if not hass.data[DOMAIN] and DOMAIN in hass.services._services:
        for myservice in SERVICES:
            if myservice in hass.services._services[DOMAIN]:
                hass.services.async_remove(DOMAIN, myservice)

    return True


class CannotExecute(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""