"""Config flow for tankerkoenig integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_SCAN_INTERVAL,
    CONF_SHOW_ON_MAP,
)
import homeassistant.helpers.config_validation as cv

from .const import CONF_FUEL_TYPES, DOMAIN, FUEL_TYPES

_LOGGER = logging.getLogger(__name__)

DEFAULT_RADIUS = 2
DEFAULT_SCAN_INTERVAL = 30


class TankerkoenigConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Tankerkoenig config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize component."""
        self.data = None

    async def async_step_user(self, user_input=None):
        """User initiated configuration."""
        user_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): cv.positive_int,
                vol.Inclusive(
                    CONF_LATITUDE,
                    "coordinates",
                    "Latitude and longitude must exist together",
                    default=self.hass.config.latitude,
                ): cv.latitude,
                vol.Inclusive(
                    CONF_LONGITUDE,
                    "coordinates",
                    "Latitude and longitude must exist together",
                    default=self.hass.config.longitude,
                ): cv.longitude,
                vol.Required(CONF_RADIUS, default=DEFAULT_RADIUS): vol.All(
                    cv.positive_int, vol.Range(min=1)
                ),
                vol.Optional(CONF_SHOW_ON_MAP, default=True): cv.boolean,
                #                 vol.Optional(CONF_STATIONS, default=[]): vol.All(
                #                     cv.ensure_list, [str]
                #                 ),
            }
        )

        if self._async_current_entries():
            _LOGGER.error("Integration already configured.")
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            _LOGGER.warn("User configuration started: %s", user_input)
            await self.async_set_unique_id(DOMAIN)
            self.data = user_input
            # TODO: check connection
            return await self.async_step_fuel()

        return self.async_show_form(step_id="user", data_schema=user_schema)

    async def async_step_fuel(self, user_input=None):
        """Handle the step where the requested fuel types are configured."""

        fuel_schema = {}

        for fuel in FUEL_TYPES:
            fuel_schema[vol.Optional(fuel, default=True)] = cv.boolean

        errors = {}

        if user_input is not None:
            fuel_types = []
            for (key, value) in user_input.items():
                if value:
                    fuel_types.append(key)
            if fuel_types:
                self.data[CONF_FUEL_TYPES] = fuel_types
                return self.async_create_entry(title=DOMAIN, data=self.data)
            _LOGGER.warning("No fuel types selected")
            errors["base"] = "no_fuel_selected"

        return self.async_show_form(
            step_id="fuel", data_schema=vol.Schema(fuel_schema), errors=errors
        )

    # TODO: Add config options flow for scan interval and additional fuel stations.

    # TODO: Import existing config from YAML
