"""Config flow for Palazzetti integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries, exceptions
from palazzetti_sdk_local_api import Hub

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({"host": str})
STEP_USER_DATA_SCHEMA = vol.Schema({"host": str})


async def validate_input(_user_host):
    """chech if user host is a Palazzetti Hub IP"""

    myhub = Hub(_user_host)
    myconfig = {"hub_id": myhub.hub_id, "host": _user_host}

    # connect to get Hub data
    await myhub.async_update()
    if myhub.online:
        myconfig["hub_isbiocc"] = myhub.hub_isbiocc
        myconfig["label"] = myhub.label
        return myconfig

    raise CannotConnect


class DomainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Palazzetti."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            self.host = user_input["host"]

            # validate host address
            info = await validate_input(self.host)

            # check if already registered
            check_exists = await self.async_set_unique_id(info["hub_id"].lower())

            if check_exists:
                return self.async_abort(reason="host_exists")

            # create config_entry
            return self.async_create_entry(
                title=f"{info['label']} ({self.host})",
                data=info,
            )

        except CannotConnect:
            _LOGGER.error("Error connecting to the ConnBox at %s", self.host)
            errors["base"] = "cannot_connect"

        except InvalidSN:
            _LOGGER.error("Error validating SN to the ConnBox at %s", self.host)
            errors["base"] = "invalid_sn"

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception(
                "Unknown error connecting to the ConnBox at %s", self.host
            )
            errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidSN(exceptions.HomeAssistantError):
    """Error indicating embedded SN is not valid"""
