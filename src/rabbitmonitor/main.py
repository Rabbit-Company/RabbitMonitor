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

networkSpeeds = {}
openMetrics = ""

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

@app.route("/metrics")
async def metrics():
  return openMetrics

@app.websocket('/ws')
async def ws():
  while True:
    msg = await websocket.receive()
    endpoints = ['cpu', 'memory', 'swap', 'storage', 'network', 'sensors', 'system']
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

  users = formatUsers(psutil.users())

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

  data['system']['users'] = users

  createMetrics()

def slowFetchData():
  global data
  info = platform.freedesktop_os_release()

  data['name'] = platform.node()
  data['system']['boot_time'] = psutil.boot_time()
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

def formatCounters(counters):
  global data
  global networkSpeeds
  new = {}
  for key in counters:
    try:
      upload = data['network']['counters'][key]['bytes_sent']
      download = data['network']['counters'][key]['bytes_received']

      networkSpeeds[key] = {}
      networkSpeeds[key]['upload'] = calculateSpeed(upload, counters[key][0], refresh)
      networkSpeeds[key]['download'] = calculateSpeed(download, counters[key][1], refresh)
    except KeyError:
      pass
    new[key] = {
      'bytes_sent': counters[key][0],
      'bytes_received': counters[key][1],
      'packets_sent': counters[key][2],
      'packets_received': counters[key][3],
      'error_in': counters[key][4],
      'error_out': counters[key][5],
      'drop_in': counters[key][6],
      'drop_out': counters[key][7]
    }
  return new

def formatStatus(status):
  global networkSpeeds
  download = 0
  upload = 0
  new = {}
  for key in status:
    try:
      download = networkSpeeds[key]['download']
      upload = networkSpeeds[key]['upload']
    except KeyError:
      pass
    new[key] = {
      'is_up': status[key][0],
      'duplex': status[key][1],
      'speed': status[key][2],
      'mtu': status[key][3],
      'download': download,
      'upload': upload
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

def formatUsers(users):
  new = []
  for i in range(len(users)):
    new.append({
      'name': users[i][0],
      'terminal': users[i][1],
      'host': users[i][2],
      'started': users[i][3],
      'pid': users[i][4]
    })
  return new

def calculateSpeed(old, new, time):
  return ((new - old) / time) * 8

def createMetrics():
  global openMetrics
  metrics = ""
  # CPU
  metrics += createMetric('gauge', 'cpu_load_1min', 'CPU load recorded in last minute', data['cpu']['load']['1min'])
  metrics += createMetric('gauge', 'cpu_load_5min', 'CPU load recorded in last 5 minutes', data['cpu']['load']['5min'])
  metrics += createMetric('gauge', 'cpu_load_15min', 'CPU load recorded in last 15 minutes', data['cpu']['load']['15min'])
  # Memory
  metrics += createMetric('gauge', 'memory_total', 'Total memory in bytes', data['memory']['total'])
  metrics += createMetric('gauge', 'memory_available', 'Available memory in bytes', data['memory']['available'])
  metrics += createMetric('gauge', 'memory_percent', 'Used memory in percent', data['memory']['percent'])
  metrics += createMetric('gauge', 'memory_used', 'Used memory in bytes', data['memory']['used'])
  metrics += createMetric('gauge', 'memory_free', 'Free memory in bytes', data['memory']['free'])
  metrics += createMetric('gauge', 'memory_active', 'Active memory in bytes', data['memory']['active'])
  metrics += createMetric('gauge', 'memory_inactive', 'Inactive memory in bytes', data['memory']['inactive'])
  metrics += createMetric('gauge', 'memory_buffers', 'Buffers memory in bytes', data['memory']['buffers'])
  metrics += createMetric('gauge', 'memory_cached', 'Cached memory in bytes', data['memory']['cached'])
  metrics += createMetric('gauge', 'memory_shared', 'Shared memory in bytes', data['memory']['shared'])
  # Swap
  metrics += createMetric('gauge', 'swap_total', 'Total swap storage in bytes', data['swap']['total'])
  metrics += createMetric('gauge', 'swap_used', 'Used swap storage in bytes', data['swap']['used'])
  metrics += createMetric('gauge', 'swap_free', 'Free swap storage in bytes', data['swap']['free'])
  metrics += createMetric('gauge', 'swap_percent', 'Used swap storage in percent', data['swap']['percent'])
  # Storage
  metrics += createMetric('gauge', 'storage_total', 'Total storage in bytes', data['storage']['total'])
  metrics += createMetric('gauge', 'storage_used', 'Used storage in bytes', data['storage']['used'])
  metrics += createMetric('gauge', 'storage_free', 'Free storage in bytes', data['storage']['free'])
  metrics += createMetric('gauge', 'storage_percent', 'Used storage in percent', data['storage']['percent'])
  openMetrics = metrics

def createMetric(type, name, description, value):
  return "# HELP rabbit_%s %s\n# TYPE rabbit_%s %s\nrabbit_%s %s\n" % (name, description, name, type, name, value)

if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument("--host", help="bind the server to specific host (default: 0.0.0.0)", type=str, default='0.0.0.0')
  parser.add_argument("--port", help="bind the server to specific port (default: 8088)", type=int, default=8088)
  parser.add_argument("--refresh", help="data will be fetched every x seconds (default: 5)", type=int, default=5)
  parser.add_argument("--debug", help="enable debug mode (default: False)", action='store_true', default=False)
  args = parser.parse_args()

  refresh = args.refresh

  Thread(target=startDataFetcher).start()
  Thread(target=startSlowDataFetcher).start()

  app.run(args.host, args.port, args.debug)