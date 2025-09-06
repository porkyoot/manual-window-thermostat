# Manual Window Thermostat

The **Manual Window Thermostat** is a custom Home Assistant integration that acts as a **climate entity**. It suggests when to open or close a window based on inside and outside temperature, while also considering weather conditions. It provides a simple, manual way to manage home climate without an automated system.

## ✨ Features

* **Manual Control**: It is a climate entity in Home Assistant, allowing you to set a target temperature just like a regular thermostat.
* **Intelligent Suggestions**: The thermostat compares your set target temperature with the current inside and outside temperatures. Based on this, it suggests whether to **open** 🪟 or **close** 🔒 the window to reach your desired temperature.
* **Bad Weather Alerts**: The integration monitors weather conditions and alerts you if the window should be closed due to rain, snow, lightning, or high winds. ⛈️
* **Notifications**: It can send a notification to a specified Home Assistant `notify` entity whenever the suggestion to open or close the window changes.
* **Customizable**: You can customize various parameters, including the tolerance for temperature difference and wind speed thresholds.

## ⚙️ Installation

### HACS (Recommended)

1.  Open the **HACS** dashboard in your Home Assistant instance.
2.  Go to the **Integrations** section.
3.  Click on the three dots in the top right corner and select **Custom repositories**.
4.  Enter the URL of this repository (`https://github.com/porkyoot/manual-window-thermostat`) and select **Integration** as the category.
5.  Click **Add**.
6.  Search for "Manual Window Thermostat" in HACS and click **Download**.
7.  Restart Home Assistant.

### Manual Installation

1.  Navigate to the `custom_components` folder in your Home Assistant configuration directory. If it doesn't exist, create it.
2.  Create a new folder named `manual_window_thermostat` inside `custom_components`.
3.  Download all files (`__init__.py`, `climate.py`, `config_flow.py`, `manifest.json`, `strings.json`, etc.) from the repository and place them in the new folder.
4.  Restart Home Assistant.

## 🔧 Configuration

After installation, configure the integration through the Home Assistant UI.

1.  Go to **Settings** -> **Devices & Services** -> **Add Integration**.
2.  Search for "Manual Window Thermostat".
3.  The configuration flow will prompt you to provide the following information:
    * **Name**: A name for your thermostat entity.
    * **Window Entity ID (Optional)**: A `binary_sensor` or `cover` entity representing the window's state (e.g., `binary_sensor.window_open`).
    * **Temperature Sensor Entity ID (Required)**: An entity with the `device_class: temperature` that measures the inside temperature.
    * **Weather Entity ID (Required)**: A `weather` entity that provides outside weather data.
    * **Outside Temperature Sensor Entity ID (Optional)**: A `sensor` entity with the `device_class: temperature` for outside temperature, which is preferred over the `weather` entity's temperature attribute if provided.
    * **Notification Entity ID (Optional)**: A `notify` entity to which suggestions will be sent.
    * **Tolerance (Optional)**: The temperature difference (in Celsius) within which no suggestion is made (default: 0.5).
    * **Wind Threshold (Optional)**: The wind speed (in km/h) above which rain and wind will trigger a bad weather alert (default: 20).
    * **High Wind Threshold (Optional)**: The wind speed (in km/h) above which a high wind alert is triggered, regardless of other conditions (default: 50).

## 📄 License

This project is licensed under the **MIT License**.