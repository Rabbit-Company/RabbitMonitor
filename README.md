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