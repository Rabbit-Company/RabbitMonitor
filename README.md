# Rabbit Monitor

> ⚠️ Please note that Rabbit Monitor is now deprecated and has been replaced by [Rabbit Monitor 2](https://github.com/Rabbit-Company/RabbitMonitor2). The new version has been completely rewritten in Rust for improved performance and scalability compared to the previous Python-based implementation.

Rabbit Monitor is a simple program that fetches your computer data every 5 seconds (By default) and create /metrics API endpoint for other programs to collect data from it.

Required packages:
- quart
- psutil
- argparse

API Endpoints:
- /metrics (Support Prometheus)

# Installation (Python and PIP required)
```yml
# Install Python modules
pip install quart psutil argparse
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
ExecStart=python3 -m rabbitmonitor
TimeoutStartSec=0
TimeoutStopSec=2
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
