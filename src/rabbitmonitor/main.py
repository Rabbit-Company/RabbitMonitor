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
  info = platform.freedesktop_os_release()
  global serverInfo
  serverInfo = {
    'name': platform.node(),
    'cpu': {
      'name': get_cpu_info()['brand_raw'],
      'cores': psutil.cpu_count(0),
      'threads': psutil.cpu_count(1),
    },
    'system': {
      'name': info['NAME'],
      'id': info['ID'],
      'pretty_name': info['PRETTY_NAME'],
      'version': info['VERSION'],
      'version_id': info['VERSION_ID'],
      'logo': info['LOGO']
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

  addresses = formatAddresses(psutil.net_if_addrs())
  connections = formatConnections(psutil.net_connections())
  counters = formatCounters(psutil.net_io_counters(1,1))
  status = formatStatus(psutil.net_if_stats())

  fans = formatFans(psutil.sensors_fans())
  battery = formatBattery(psutil.sensors_battery())

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
      'addresses': addresses,
      'status': status,
      'counters': counters,
      'connections': connections
    },
    'sensors': {
      'temperatures': psutil.sensors_temperatures(),
      'fans': fans,
      'battery': battery
    }
  }

def formatAddresses(addresses):
  new = {}
  for key in addresses:
    new[key] = {}
    for i in range(len(addresses[key])):
      new[key][i] = {
        'family': addresses[key][i][0],
        'address': addresses[key][i][1],
        'netmask': addresses[key][i][2],
        'broadcast': addresses[key][i][3],
        'ptp': addresses[key][i][4]
      }
  return new

def formatConnections(connections):
  new = {}
  for i in range(len(connections)):
    lip = lpo = rip = rpo = None
    if len(connections[i][3]) > 0:
      lip = connections[i][3][0]
    if len(connections[i][3]) > 1:
      lpo = connections[i][3][1]
    if len(connections[i][4]) > 0:
      rip = connections[i][4][0]
    if len(connections[i][4]) > 1:
      rpo = connections[i][4][1]
    new[i] = {
      'fd': connections[i][0],
      'family': connections[i][1],
      'type': connections[i][2],
      'local_address': {
        'ip': lip,
        'port': lpo
      },
      'remote_address': {
        'ip': rip,
        'port': rpo
      },
      'status': connections[i][5],
      'pid': connections[i][6]
    }
  return new

def formatCounters(speeds):
  new = {}
  for key in speeds:
    new[key] = {
      'bytes_sent': speeds[key][0],
      'bytes_received': speeds[key][1],
      'packets_sent': speeds[key][2],
      'packets_received': speeds[key][3],
      'error_in': speeds[key][4],
      'error_out': speeds[key][5],
      'drop_in': speeds[key][6],
      'drop_out': speeds[key][7]
    }
  return new

def formatStatus(status):
  new = {}
  for key in status:
    new[key] = {
      'is_up': status[key][0],
      'duplex': status[key][1],
      'speed': status[key][2],
      'mtu': status[key][3]
    }
  return new

def formatFans(fans):
  new = {}
  for key in fans:
    new[key] = {}
    for i in range(len(fans[key])):
      new[key] = {
        'label': fans[key][i][0],
        'rpm': fans[key][i][1]
      }
  return new

def formatBattery(battery):
  new = None
  if battery is not None:
    new = {
      'percent': battery[0],
      'seconds_left': battery[1],
      'power_plugged': battery[2]
    }
  return new

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