import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

DOMAIN = "manual_window_thermostat"

class ManualWindowThermostatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1
    
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name", default="Manual Thermostat"): str,
                vol.Optional("window_entity_id"): EntitySelector(
                    EntitySelectorConfig(domain=["binary_sensor", "cover"])
                ),
                vol.Required("temperature_sensor_entity_id"): EntitySelector(
                    EntitySelectorConfig(domain=["sensor"], device_class="temperature")
                ),
                vol.Required("weather_entity_id"): EntitySelector(
                    EntitySelectorConfig(domain=["weather"])
                ),
                vol.Optional("outside_temperature_sensor_entity_id"): EntitySelector(
                    EntitySelectorConfig(domain=["sensor"], device_class="temperature")
                ),
                vol.Optional("notification_entity_id"): EntitySelector(
                    EntitySelectorConfig(domain=["notify"])
                ),
                vol.Optional("tolerance", default=0.5): vol.All(float, vol.Range(min=0)),
                vol.Optional("wind_threshold", default=20): vol.All(int, vol.Range(min=0)),
                vol.Optional("high_wind_threshold", default=50): vol.All(int, vol.Range(min=0)),
            }),
            errors=errors,
            description_placeholders=None,
        )
