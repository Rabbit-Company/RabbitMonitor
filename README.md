# Rabbit Monitor

Rabbit Monitor is a simple program that fetch your computer data every 5 seconds (By default) and create API endpoints for other programs to collect it.

Required packages:
- argparse
- psutil
- py-cpuinfo
- quart

API Endpoints:
- /cpu
- /memory
- /swap
- /storage
- /network
- /sensors
- /system
- /stats
- /metrics (Support Prometheus)

# Installation (Python and PIP required)
```yml
# Install Python modules
pip install argparse psutil py-cpuinfo quart
# Install Rabbit Monitor
pip install rabbitmonitor
# Start monitoring with
python3 -m rabbitmonitor
```

# Daemonizing (using systemd)
Running Rabbit Monitor in the background is a simple task, just make sure that it runs without errors before doing this. Place the contents below in a file called ```rabbitmonitor.service``` in the ```/etc/systemd/system``` directory.

WARNING: Make sure to change the User to the one that have installed pip packages.

```service
[Unit]
Description=Rabbit Monitor 
After=network.target

[Service]
Type=simple
User=root
ExecStart=python3 -m rabbitmonitor --onlymetrics
TimeoutStartSec=0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```
Then, run the commands below to reload systemd and start Rabbit Monitor.
```yml
systemctl enable --now rabbitmonitor
```

# Grafana Dashboard
Rabbit Monitor has a pre-made Grafana dashboard that looks like this:
![Grafana Dashboard](https://user-images.githubusercontent.com/44822563/168747801-a4cfb30d-f214-4eff-9097-9530802761b6.png)
It can be installed from official Grafana website: https://grafana.com/grafana/dashboards/16275
