from quart import Quart, websocket
from cpuinfo import get_cpu_info
import psutil
import platform
import argparse
from threading import Thread
from time import sleep

app = Quart(__name__)

data = {
  'cpu': {},
  'memory': {},
  'swap': {},
  'storage': {},
  'network': {},
  'sensors': {},
  'system': {}
}

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

@app.route("/system")
async def system():
  return data.get('system')

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

def startDataFetcher():
  while True:
    fetchData()
    sleep(refresh)

def startSlowDataFetcher():
  while True:
    slowFetchData()
    sleep(60)

def fetchData():
  global data
  memory = psutil.virtual_memory()
  swap = psutil.swap_memory()
  storage = psutil.disk_usage('/')

  addresses = formatAddresses(psutil.net_if_addrs())
  connections = formatConnections(psutil.net_connections())
  counters = formatCounters(psutil.net_io_counters(1,1))
  status = formatStatus(psutil.net_if_stats())

  load = formatLoad(psutil.getloadavg())
  frequency = formatFrequency(psutil.cpu_freq(0))
  frequencies = formatFrequencies(psutil.cpu_freq(1))

  temperatures = formatTemperatures(psutil.sensors_temperatures())
  fans = formatFans(psutil.sensors_fans())
  battery = formatBattery(psutil.sensors_battery())

  data['cpu']['load'] = load
  data['cpu']['frequency'] = frequency
  data['cpu']['frequencies'] = frequencies

  data['memory']['total'] = memory[0]
  data['memory']['available'] = memory[1]
  data['memory']['percent'] = memory[2]
  data['memory']['used'] = memory[3]
  data['memory']['free'] = memory[4]
  data['memory']['active'] = memory[5]
  data['memory']['inactive'] = memory[6]
  data['memory']['buffers'] = memory[7]
  data['memory']['cached'] = memory[8]
  data['memory']['shared'] = memory[9]

  data['swap']['total'] = swap[0]
  data['swap']['used'] = swap[1]
  data['swap']['free'] = swap[2]
  data['swap']['percent'] = swap[3]

  data['storage']['total'] = storage[0]
  data['storage']['used'] = storage[1]
  data['storage']['free'] = storage[2]
  data['storage']['percent'] = storage[3]

  data['network']['addresses'] = addresses
  data['network']['status'] = status
  data['network']['counters'] = counters
  data['network']['connections'] = connections

  data['sensors']['temperatures'] = temperatures
  data['sensors']['fans'] = fans
  data['sensors']['battery'] = battery

def slowFetchData():
  global data
  info = platform.freedesktop_os_release()

  data['name'] = platform.node()
  data['cpu']['name'] = get_cpu_info()['brand_raw']
  data['cpu']['cores'] = psutil.cpu_count(0)
  data['cpu']['threads'] = psutil.cpu_count(1)
  data['system']['name'] = info['NAME']
  data['system']['id'] = info['ID']
  data['system']['pretty_name'] = info['PRETTY_NAME']
  data['system']['version'] = info['VERSION']
  data['system']['version_id'] = info['VERSION_ID']
  data['system']['logo'] = info['LOGO']

def formatLoad(load):
  return {
    '1min': load[0],
    '5min': load[1],
    '15min': load[2]
  }

def formatFrequency(frequency):
  return{
    'current': frequency[0],
    'min': frequency[1],
    'max': frequency[2]
  }

def formatFrequencies(frequencies):
  new = []
  for i in range(len(frequencies)):
    new.append({
      'current': frequencies[i][0],
      'min': frequencies[i][1],
      'max': frequencies[i][2]
    })
  return new

def formatAddresses(addresses):
  new = {}
  for key in addresses:
    new[key] = []
    for i in range(len(addresses[key])):
      new[key].append({
        'family': addresses[key][i][0],
        'address': addresses[key][i][1],
        'netmask': addresses[key][i][2],
        'broadcast': addresses[key][i][3],
        'ptp': addresses[key][i][4]
      })
  return new

def formatConnections(connections):
  new = []
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
    new.append({
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
    })
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

def formatTemperatures(temperatures):
  new = {}
  for key in temperatures:
    new[key] = []
    for i in range(len(temperatures[key])):
      new[key].append({
        'label': temperatures[key][i][0],
        'current': temperatures[key][i][1],
        'high': temperatures[key][i][2],
        'critical': temperatures[key][i][3],
      })
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

  Thread(target=startDataFetcher).start()
  Thread(target=startSlowDataFetcher).start()

  app.run(args.host, args.port, args.debug)