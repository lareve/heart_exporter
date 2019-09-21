# HOWT

This guide is tested on a Raspbian based system (Raspberry Pie) but any linux system should be very similar.

Software used in this setup:
- prometheus (https://prometheus.io)
- grafana (https://grafana.com)
- heart_exporter
- metobs_exporter

# Get access to Animus API

Go to your Animus Home and generate an API key
- Open up a browser and point it towards your Animus (I had to find the IP in the DHCP status of my router but the hostname 'heart' might work in your setup?)
- Login and go to Developer Portal
- Select API keys and generate a new key.

# Start heart_exporter

- Login to your linux system and install Python
```
sudo apt install python python-pip
sudo pip install prometheus_client requests
```
- Start exporter:
```
python heart_exporter.py <port> http://<animus ip> <api key>
```
(running this in a screen or tmux is advisable)
- Check that opening http://\<ip of machine running heart_exporter>:\<port>/metric returns a correct prometheus formated page
```
curl http://192.168.10.2:4000/metric
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
...
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="2",minor="7",patchlevel="13",version="2.7.13"} 1.0
```

# Install grafana

- Goto download page on https://www.grafana.com/ (in this ARM based example the path would be https://grafana.com/grafana/download?platform=arm)
- Download deb and install (version as of writing this)
```
wget https://dl.grafana.com/oss/release/grafana_6.3.5_armhf.deb 
sudo dpkg -i grafana_6.3.5_armhf.deb 
```
- Enable service
```
sudo systemctl enable --now grafana-server
```

# Install prometheus

- Goto download page on https://prometheus.io/download/ and choose correct architecture

Example:
```
wget https://github.com/prometheus/prometheus/releases/download/v2.12.0/prometheus-2.12.0.linux-armv7.tar.gz
tar xf prometheus-2.12.0.linux-armv7.tar.gz
```
- Start prometheus (the 3 month retention time could of course be changed but prometheus doesn't currently do downsampling of older data)
```
cd prometheus-2.12.0.linux-armv7 
./prometheus --storage.tsdb.retention.time=90d
´´´
(running this in a screen or tmux is advisable)

# Configure prometheus
- Edit prometeus.yml and add the heart_exporter in the targets section.
```prometheus.yml
...
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: 'prometheus'

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
    - targets: ['192.168.10.2:9090']
  - job_name: 'animus_heart'
    static_configs:
    - targets: ['192.168.10.2:4000']
...
```

# Configure data source in grafana 
- Configuration -> Data Source -> Add Data Source -> Prometheus
- URL: http://localhost:9090
- Now data with the name sensor_ should be availalble to create your wanted graphs

[![screenshot.png](https://i.postimg.cc/76NZ3qp4/screenshot.png)](https://postimg.cc/mzt4RWLp)
