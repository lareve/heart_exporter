# heart_exporter

Prometheus exporter for Animus home.

Queries the /rest/devices API endpoint for devices (and stores the name). Since
the Animus has a daily limit (at the time of writing this) on the amount of API
calls this only done every 4:e query since sensors and sensor names are not
expected to change particular often.

The /rest/functions endpoint is queried for sensors.
- temperature
- humidity
- light
- battery
- motion

The metric name is sensor_temperature, sensor_humidity and so on.

Example output (/metric):
```
sensor_temperature{name="Förråd"} 13.2
sensor_temperature{name="Multisensor 2"} 23.8
sensor_temperature{name="Multisensor 1"} 24.3
sensor_humidity{name="Förråd"} 73.0
sensor_humidity{name="Multisensor 2"} 47.0
sensor_humidity{name="Multisensor 1"} 47.0
sensor_light{name="Multisensor 2"} 20.0
sensor_light{name="Multisensor 1"} 99.0
sensor_light{name="Heart Halo"} 0.0
sensor_battery{name="Multisensor 2"} 100.0
sensor_battery{name="Multisensor 1"} 100.0
sensor_motion{name="Multisensor 2"} 0.0
sensor_motion{name="Multisensor 1"} 0.0
```

This currently tested with:
- Animus Framework version: 1.3.17
- Animus System version: 1.3.10
- Telldus 433 Thermometer and hygrometer
- Aeotec Multisensor 6
