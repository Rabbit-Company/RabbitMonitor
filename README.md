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
python -m rabbitmonitor
```

# Daemonizing (using systemd)
Running Rabbit Monitor in the background is a simple task, just make sure that it runs without errors before doing this. Place the contents below in a file called ```rabbitmonitor.service``` in the ```/etc/systemd/system``` directory.

```service
[Unit]
Description = Starting Rabbit Monitor
After = network.target

[Service]
ExecStart = python -m rabbitmonitor

[Install]
WantedBy = multi-user.target
```
Then, run the commands below to reload systemd and start Rabbit Monitor.
```yml
systemctl enable --now rabbitmonitor
```