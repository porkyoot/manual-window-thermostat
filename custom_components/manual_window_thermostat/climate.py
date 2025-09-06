from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature
from homeassistant.const import ATTR_TEMPERATURE

from homeassistant.helpers.entity import async_generate_entity_id

DOMAIN = "manual_window_thermostat"

async def async_setup_entry(hass, config_entry, async_add_entities):
    data = config_entry.data
    async_add_entities([
        ManualWindowThermostat(
            hass,
            data.get("name", "Manual Window Thermostat"),
            data.get("window_entity_id"),
            data["temperature_sensor_entity_id"],
            data["weather_entity_id"],
            data.get("tolerance", 0.5),
            data.get("notification_entity_id"),
            data.get("outside_temperature_sensor_entity_id"),
            data.get("wind_threshold", 20),
            data.get("high_wind_threshold", 50)
        )
    ])


class ManualWindowThermostat(ClimateEntity):
    def __init__(self, hass, name, window_entity_id, temperature_sensor_entity_id, weather_entity_id, tolerance=0.5, notification_entity_id=None, outside_temperature_sensor_entity_id=None, wind_threshold=20, high_wind_threshold=50):
        self.hass = hass
        self._window_entity_id = window_entity_id
        self._temperature_sensor_entity_id = temperature_sensor_entity_id
        self._weather_entity_id = weather_entity_id
        self._outside_temperature_sensor_entity_id = outside_temperature_sensor_entity_id
        self._target_temperature = 20.0
        self._hvac_mode = HVACMode.OFF
        self._attr_name = name
        self._attr_unique_id = async_generate_entity_id(f"climate.{{}}", name, hass=hass)
        self._tolerance = tolerance
        self._notification_entity_id = notification_entity_id
        self._wind_threshold = wind_threshold
        self._high_wind_threshold = high_wind_threshold

    @property
    def temperature_unit(self):
        return "°C"
    
    @property
    def supported_features(self):
        return ClimateEntityFeature.TARGET_TEMPERATURE
    
    @property
    def state(self):
        return self.hvac_mode

    @property
    def hvac_modes(self):
        return [
            HVACMode.OFF,
            HVACMode.HEAT,
            HVACMode.COOL
        ]

    @property
    def target_temperature(self):
        return self._target_temperature

    @property
    def current_temperature(self):
        state = self.hass.states.get(self._temperature_sensor_entity_id)
        self.inside_temperature = None
        try:
            self.inside_temperature = float(state.state) if state else None
            return self.inside_temperature
        except (ValueError, TypeError):
            return None

    @property
    def hvac_mode(self):
        # Ensure extra_state_attributes is called to update window, weather, and outside_temperature
        _ = self.extra_state_attributes
        # Ensure current_temperature is called to update inside_temperature
        _ = self.current_temperature

        if self.window is None or self.window in ['on', 'open', 'opening', 'unlocked', 'unlocked (on)', 'tilted']:
            if (
                self.outside_temperature is not None
                and self.inside_temperature is not None
                and isinstance(self.outside_temperature, (int, float))
                and isinstance(self.inside_temperature, (int, float))
            ):
                # Determine mode based on temperature difference and a tolerance
                temp_diff = self.outside_temperature - self.inside_temperature
                if abs(temp_diff) <= self._tolerance:
                    self._hvac_mode = HVACMode.OFF
                elif temp_diff > self._tolerance:
                    self._hvac_mode = HVACMode.HEAT
                else:
                    self._hvac_mode = HVACMode.COOL
            else:
                self._hvac_mode = HVACMode.OFF
        else:
            self._hvac_mode = HVACMode.OFF
        return self._hvac_mode

    async def async_set_hvac_mode(self, hvac_mode):
        pass  # HVAC mode is determined automatically; manual setting is not supported.


    @property
    def extra_state_attributes(self):
        window_state = self.hass.states.get(self._window_entity_id)
        weather_state = self.hass.states.get(self._weather_entity_id)
        outside_temp_state = self.hass.states.get(self._outside_temperature_sensor_entity_id) if self._outside_temperature_sensor_entity_id else None

        self.window = window_state.state if window_state else None
        if self.window in ['on', 'open', 'opening', 'unlocked', 'tilted']:
            self.window = 'open'
        elif self.window in ['off', 'closed', 'closing', 'locked']:
            self.window = 'closed'
        else: self.window = 'unknown'
        self.weather = weather_state.state if weather_state else None
        # Prefer outside temp sensor if provided, else use weather entity
        def to_celsius(temp, unit):
            if temp is None:
                return None
            if unit == '°F' or unit == 'F':
                return (float(temp) - 32) * 5.0 / 9.0
            return float(temp)

        def to_kmh(speed, unit):
            if speed is None:
                return None
            if unit == 'm/s':
                return float(speed) * 3.6
            return float(speed)

        # Get outside temperature and unit
        outside_temp_unit = None
        if outside_temp_state and outside_temp_state.state not in (None, '', 'unknown', 'unavailable'):
            try:
                outside_temp_unit = outside_temp_state.attributes.get('unit_of_measurement') if hasattr(outside_temp_state, 'attributes') else None
                self.outside_temperature = to_celsius(outside_temp_state.state, outside_temp_unit)
            except (ValueError, TypeError):
                self.outside_temperature = None
        else:
            temp = weather_state.attributes['temperature'] if weather_state and 'temperature' in weather_state.attributes else None
            temp_unit = weather_state.attributes.get('temperature_unit') if weather_state and 'temperature_unit' in weather_state.attributes else None
            self.outside_temperature = to_celsius(temp, temp_unit)

        # --- BAD WEATHER LOGIC ---
        bad_weather = False
        reason = self._hvac_mode if self._hvac_mode != HVACMode.OFF else 'none'
        if weather_state:
            # Check weather condition/state
            condition = weather_state.state.lower() if weather_state.state else ""
            wind_speed = weather_state.attributes.get('wind_speed') if hasattr(weather_state, 'attributes') else None
            wind_unit = weather_state.attributes.get('wind_speed_unit') if weather_state and 'wind_speed_unit' in weather_state.attributes else None
            wind_speed_kmh = to_kmh(wind_speed, wind_unit)
            # Rain + too much wind
            if (('rain' in condition or 'pour' in condition) and wind_speed_kmh is not None and wind_speed_kmh >= self._wind_threshold):
                bad_weather = True
                reason = 'rain_and_wind'
            # Snow, hail, lightning, tornado
            elif any(word in condition for word in ['snow', 'hail', 'lightning', 'tornado']):
                bad_weather = True
                reason = condition
            # Way too much wind
            elif wind_speed_kmh is not None and wind_speed_kmh >= self._high_wind_threshold:
                bad_weather = True
                reason = 'high_wind'


        old_suggestion = getattr(self, 'suggestion', None)
        # Suggestion logic: 
        # If in HEAT mode and inside temp is below target, suggest 'open'.
        # If in COOL mode and inside temp is above target, suggest 'close'.
        # Otherwise, suggest 'close'.
        if self._hvac_mode == HVACMode.HEAT:
                if self.inside_temperature is not None and self._target_temperature is not None:
                    self.suggestion = 'open' if self.inside_temperature < self._target_temperature else 'close'
                else:
                    self.suggestion = 'close'
        elif self._hvac_mode == HVACMode.COOL:
                if self.inside_temperature is not None and self._target_temperature is not None:
                    self.suggestion = 'open' if self.inside_temperature > self._target_temperature else 'close'
                else:
                    self.suggestion = 'close'
        else:
            self.suggestion = 'close'
        
        # Only send notification if window state is not already in the suggested state
        if self.window not in ['open', 'close'] or self.window != self.suggestion:
            # If suggestion changed and notification entity is set, send notification
            if old_suggestion != self.suggestion and self._notification_entity_id:
                # Localize notification message
                # Try to use hass.translation infrastructure if available, fallback to English
                try:
                    message = self.hass.helpers.translation.async_get_localized(
                        'notification.suggestion',
                        'custom_components.manual_thermostat',
                        self.hass.config.language,
                        {
                            'name': self._attr_name,
                            'suggestion': self.suggestion
                        }
                    )
                except Exception:
                    message = f"Thermostat '{self._attr_name}' suggests to {self.suggestion} the window."
                self.hass.services.call('notify', self._notification_entity_id, {'message': message})

        return {
            "window": self.window,
            "weather": self.weather,
            "outside_temperature": self.outside_temperature,
            "suggestion": self.suggestion,
            "bad_weather": bad_weather,
            "reason": reason
        }

    @property
    def icon(self):
        bad_weather = self.extra_state_attributes.get('bad_weather', False)
        if bad_weather:
            return 'mdi:shutter-alert'
        suggestion = getattr(self, 'suggestion', None)
        if suggestion == 'open':
            return 'mdi:window-open'
        elif suggestion == 'close':
            return 'mdi:window-closed'
        return 'mdi:window-closed'

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            self._target_temperature = temperature
            await self.async_write_ha_state()
