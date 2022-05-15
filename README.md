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
```yml
nano /etc/systemd/system/rabbitmonitor.service
