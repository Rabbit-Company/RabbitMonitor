from quart import Quart
import psutil
import argparse
from threading import Thread
from time import sleep

app = Quart(__name__)

data = {
  'cpu': {},
  'memory': {},
  'swap': {},
  'storage': {},
  'network': {}
}

networkSpeeds = {}
openMetrics = ""
num_threads = psutil.cpu_count(1)

@app.route("/")
async def default():
  return """
  <style>
    td, th {
      border-bottom: 1px solid #000;
      border-right: 1px solid #000;
      text-align: center;
      padding: 8px;
    }
  </style>

  <h1>Rabbit Monitor</h1>
  <b>Version:</b> v2.0.0</br>
  <b>Fetch every:</b> """ + str(refresh) + """ seconds</br></br>
  <table>
    <tr>
      <th>CPU Load</th>
      <td>""" + str(round(data['cpu']['percent'], 2)) + """%</td>
    </tr>
    <tr>
      <th>RAM Usage</th>
      <td>""" + str(data['memory']['percent']) + """%</td>
    </tr>
    <tr>
      <th>Swap Usage</th>
      <td>""" + str(data['swap']['percent']) + """%</td>
    </tr>
    <tr>
      <th>Storage Usage</th>
      <td>""" + str(data['storage']['percent']) + """%</td>
    </tr>
  </table>
  """

@app.route("/metrics")
async def metrics():
  return openMetrics

def startDataFetcher():
  global refresh
  while True:
    fetchData()
    sleep(refresh)

def fetchData():
  load = psutil.getloadavg()
  memory = psutil.virtual_memory()
  swap = psutil.swap_memory()
  storage = psutil.disk_usage('/')
  counters = formatCounters(psutil.net_io_counters(1,1))

  # CPU
  data['cpu']['1min'] = load[0]
  data['cpu']['5min'] = load[1]
  data['cpu']['15min'] = load[2]
  data['cpu']['percent'] = (load[0]/num_threads)*100
  # Memory
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
  # Swap
  data['swap']['total'] = swap[0]
  data['swap']['used'] = swap[1]
  data['swap']['free'] = swap[2]
  data['swap']['percent'] = swap[3]
  # Storage
  data['storage']['total'] = storage[0]
  data['storage']['used'] = storage[1]
  data['storage']['free'] = storage[2]
  data['storage']['percent'] = storage[3]
  # Network
  data['network']['counters'] = counters

  createMetrics()

def calculateSpeed(old, new, time):
  return ((new - old) / time) * 8

def formatCounters(counters):
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
    }
  return new

def createMetrics():
  global openMetrics
  metrics = ""
  # CPU
  metrics += createMetric('gauge', 'cpu_load_1min', 'CPU load recorded in last minute', data['cpu']['1min'])
  metrics += createMetric('gauge', 'cpu_load_5min', 'CPU load recorded in last 5 minutes', data['cpu']['5min'])
  metrics += createMetric('gauge', 'cpu_load_15min', 'CPU load recorded in last 15 minutes', data['cpu']['15min'])
  metrics += createMetric('gauge', 'cpu_load_percent', 'CPU load in percent', data['cpu']['percent'])
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
  # Network
  for key in networkSpeeds:
    bkey = key.replace('-', '')
    metrics += createMetric('gauge', 'network_'+bkey+'_download', 'Download speed on ' + bkey + ' network interface in bits', networkSpeeds[key]['download'])
    metrics += createMetric('gauge', 'network_'+bkey+'_upload', 'Upload speed on ' + bkey + ' network interface in bits', networkSpeeds[key]['upload'])
  openMetrics = metrics

def createMetric(type, name, description, value):
  return "# HELP rabbit_%s %s\n# TYPE rabbit_%s %s\nrabbit_%s %s\n" % (name, description, name, type, name, value)

def start():
  parser = argparse.ArgumentParser()
  parser.add_argument("--host", help="bind the server to specific host (default: 0.0.0.0)", type=str, default='0.0.0.0')
  parser.add_argument("--port", help="bind the server to specific port (default: 8088)", type=int, default=8088)
  parser.add_argument("--refresh", help="data will be fetched every x seconds (default: 5)", type=int, default=5)
  parser.add_argument("--debug", help="enable debug mode (default: False)", action='store_true', default=False)
  args = parser.parse_args()

  global refresh
  refresh = args.refresh

  Thread(target=startDataFetcher).start()

  app.run(args.host, args.port, args.debug)