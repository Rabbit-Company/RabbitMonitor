from quart import Quart, websocket
from cpuinfo import get_cpu_info
import psutil
import platform
import argparse
from threading import Thread
from time import sleep

app = Quart(__name__)

user = 'rabbit'
passwd = ''

@app.route("/cpu")
async def cpu():
  return data.get('cpu')

@app.route("/memory")
async def memory():
  return data.get('memory')

@app.route("/swap")
async def swap():
  return data.get('swap')

@app.route("/storage")
async def storage():
  return data.get('storage')

@app.route("/network")
async def network():
  return data.get('network')

@app.route("/sensors")
async def sensors():
  return data.get('sensors')

@app.route("/info")
async def info():
  return serverInfo

@app.route("/stats")
async def stats():
  return data

@app.websocket('/ws')
async def ws():
  while True:
    msg = await websocket.receive()
    endpoints = ['cpu', 'memory', 'swap', 'storage', 'network', 'sensors']
    if msg in endpoints:
      await websocket.send(f"{data.get(msg)}")
    else:
      await websocket.send(f"{data}")

def getInfo():
  data = platform.freedesktop_os_release()
  global serverInfo
  serverInfo = {
    'name': platform.node(),
    'cpu': {
      'name': get_cpu_info()['brand_raw'],
      'cores': psutil.cpu_count(0),
      'threads': psutil.cpu_count(1),
    },
    'system': {
      'name': data['NAME'],
      'id': data['ID'],
      'pretty_name': data['PRETTY_NAME'],
      'version': data['VERSION'],
      'version_id': data['VERSION_ID'],
      'logo': data['LOGO']
    }
  }

def startDataFetcher():
  while True:
    fetchData()
    sleep(refresh)

def fetchData():
  global data
  memory = psutil.virtual_memory()
  swap = psutil.swap_memory()
  storage = psutil.disk_usage('/')
  data = {
    'cpu': {
      'load': psutil.getloadavg(),
      'frequency': psutil.cpu_freq(0),
      'frequencies': psutil.cpu_freq(1)
    },
    'memory': {
      'total': memory[0],
      'available': memory[1],
      'percent': memory[2],
      'used': memory[3],
      'free': memory[4],
      'active': memory[5],
      'inactive': memory[6],
      'buffers': memory[7],
      'cached': memory[8],
      'shared': memory[9]
    },
    'swap': {
      'total': swap[0],
      'used': swap[1],
      'free': swap[2],
      'percent': swap[3]
    },
    'storage': {
      'total': storage[0],
      'used': storage[1],
      'free': storage[2],
      'percent': storage[3]
    },
    'network': {
      'addresses': psutil.net_if_addrs(),
      'stats': psutil.net_if_stats(),
      'speed': psutil.net_io_counters(),
      'connections': psutil.net_connections()
    },
    'sensors': {
      'temperatures': psutil.sensors_temperatures(),
      'fans': psutil.sensors_fans(),
      'battery': psutil.sensors_battery()
    }
  }

if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument("--host", help="bind the server to specific host (default: 0.0.0.0)", type=str, default='0.0.0.0')
  parser.add_argument("--port", help="bind the server to specific port (default: 8088)", type=int, default=8088)
  parser.add_argument("--refresh", help="data will be fetched every x seconds (default: 5)", type=int, default=5)
  parser.add_argument("--username", help="protect api endpoints with an username (default: rabbit)", type=str, default='rabbit')
  parser.add_argument("--password", help="protect api endpoints with a password (default: none)", type=str, default='')
  parser.add_argument("--debug", help="enable debug mode (default: False)", action='store_true', default=False)
  args = parser.parse_args()

  user = args.username
  passwd = args.password
  refresh = args.refresh

  getInfo()
  Thread(target=startDataFetcher).start()

  app.run(args.host, args.port, args.debug)