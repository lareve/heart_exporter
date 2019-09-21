from prometheus_client import start_http_server, Metric, REGISTRY, Gauge
from prometheus_client.core import GaugeMetricFamily
import unicodedata
import json
import requests
import sys
import time
import pprint

#
# Prometheus exporter for sensors connected to an Animus Home
#
# Tested with:
#
# Telldus 433 Thermometer and hygrometer
# Aeotec Multisensor 6
#

class AnimusCollector(object):
  def __init__(self, endpoint, apikey):
    self._endpoint = endpoint
    self._apikey =  apikey
    self.devices = {}
    self.invalidate_devices_counter = 0
  def collect(self):
    if not self.devices:
        print("debug: no devices cached, checking...")
        dev_query = json.loads(requests.get(self._endpoint+"/rest/devices", headers={"Authorization":"Bearer {:s}".format(self._apikey)}).content.decode('UTF-8'))

        for dev in dev_query:
            self.devices[dev]={}
            self.devices[dev]["name"]=dev_query[dev]['properties']['name']
        self.invalidate_devices_counter=0
    else:
        self.invalidate_devices_counter+=1
    
    if self.invalidate_devices_counter == 3:
        print("debug: invalidating cached self.devices list")
        self.devices={}

    fun_query = json.loads(requests.get(self._endpoint+"/rest/functions", headers={"Authorization":"Bearer {:s}".format(self._apikey)}).content.decode('UTF-8'))
    
    for fun in fun_query:
        dev=fun.split(':')[0]
        if dev not in self.devices:
            print("device does not exist, ignoring for now")
            continue
        pp = pprint.PrettyPrinter(indent=4)
        if "type" in fun_query[fun]["serviceProperties"]:
            type=fun_query[fun]["serviceProperties"]["type"]
            if type == "temperature" or type == "humidity" or type == "uv" or type == "battery":
                self.devices[dev][type]=fun_query[fun]["functionProperties"]["data"]["value"]["level"]
            if type == "light":
                pp.pprint(fun_query[fun])
                if "color" in fun_query[fun]["functionProperties"]:
                    self.devices[dev][type]=fun_query[fun]["functionProperties"]["color"]["value"]["hue"]
                elif "level" in fun_query[fun]["functionProperties"]["data"]["value"]:
                    self.devices[dev][type]=fun_query[fun]["functionProperties"]["data"]["value"]["level"]
                else:
                    self.devices[dev][type]=fun_query[fun]["functionProperties"]["data"]["value"]["value"]
            if type == "motion":
                pp.pprint(fun_query[fun]['functionProperties'])
                self.devices[dev][type]=fun_query[fun]["functionProperties"]["alarm"]["value"]["event"]

    for key in self.devices.keys():
        if len(self.devices[key])==1:
            del self.devices[key]

    temperature_metric = GaugeMetricFamily('sensor_temperature', 'Ambient temperature in degrees celsius',labels=['name'])
    humidity_metric = GaugeMetricFamily('sensor_humidity', 'Humidity in percent',labels=['name'])
    light_metric = GaugeMetricFamily('sensor_light', 'Value for light',labels=['name'])
    battery_metric = GaugeMetricFamily('sensor_battery', 'Battery in %',labels=['name'])
    motion_metric = GaugeMetricFamily('sensor_motion', 'Motion sensor',labels=['name'])

    for sensor_key in self.devices:
        sensor=self.devices[sensor_key]
        if "temperature" in sensor:
            print(u"setting sensor_temperature metric for {} with value {}".format(sensor['name'],sensor['temperature']))
            temperature_metric.add_metric([sensor['name']],value=sensor['temperature'])
        if "humidity" in sensor:
            print(u"setting sensor_humidity metric for {} with value {}".format(sensor['name'],sensor['humidity']))
            humidity_metric.add_metric([sensor['name']],value=sensor['humidity'])
        if "light" in sensor:
            print(u"setting sensor_light metric for {} with value {}".format(sensor['name'],sensor['light']))
            light_metric.add_metric([sensor['name']],value=sensor['light'])
        if "battery" in sensor:
            print(u"setting sensor_battery metric for {} with value {}".format(sensor['name'],sensor['battery']))
            battery_metric.add_metric([sensor['name']],value=sensor['battery'])
        if "motion" in sensor:
            print(u"setting sensor_motion metric for {} with value {}".format(sensor['name'],sensor['motion']))
            motion_metric.add_metric([sensor['name']],value=sensor['motion'])

    yield temperature_metric
    yield humidity_metric
    yield light_metric
    yield battery_metric
    yield motion_metric

if __name__ == '__main__':
  # Usage: heart_exporter.py port endpoint
  start_http_server(int(sys.argv[1]))
  REGISTRY.register(AnimusCollector(sys.argv[2], sys.argv[3]))

  while True: time.sleep(1)
