from ast import arg
from xmlrpc.client import Boolean
from flask import Flask, request
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from cpuinfo import get_cpu_info
import psutil
import platform
import argparse

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

user = 'rabbit'
passwd = ''

class CPU(Resource):
  @auth.login_required
  def get(self):
    return {
      'load': psutil.getloadavg(),
      'frequency': psutil.cpu_freq(0),
      'frequencies': psutil.cpu_freq(1)
    }, 200
  pass  
  
class Memory(Resource):
  @auth.login_required
  def get(self):
    memory = psutil.virtual_memory()
    return {
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
    }, 200
  pass

class Swap(Resource):
  @auth.login_required
  def get(self):
    swap = psutil.swap_memory()
    return {
      'total': swap[0],
      'used': swap[1],
      'free': swap[2],
      'percent': swap[3]
    }, 200
  pass

class Storage(Resource):
  @auth.login_required
  def get(self):
    storage = psutil.disk_usage('/')
    return {
      'total': storage[0],
      'used': storage[1],
      'free': storage[2],
      'percent': storage[3]
    }, 200
  pass

class Info(Resource):
  @auth.login_required
  def get(self):
    data = platform.freedesktop_os_release()
    return {
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
    }, 200
  pass

class Stats(Resource):
  @auth.login_required
  def get(self):
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    storage = psutil.disk_usage('/')
    return {
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
      "swap": {
        'total': swap[0],
        'used': swap[1],
        'free': swap[2],
        'percent': swap[3]
      },
      "storage": {
        'total': storage[0],
        'used': storage[1],
        'free': storage[2],
        'percent': storage[3]
      }
    }, 200
  pass

@auth.verify_password
def verify(username, password):
  if(username == user and password == passwd):
    return username

api.add_resource(CPU, '/cpu')
api.add_resource(Memory, '/memory')
api.add_resource(Swap, '/swap')
api.add_resource(Storage, '/storage')
api.add_resource(Info, '/info')
api.add_resource(Stats, '/stats')

if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument("--host", help="bind the server to specific host (default: 0.0.0.0)", type=str, default='0.0.0.0')
  parser.add_argument("--port", help="bind the server to specific port (default: 8088)", type=int, default=8088)
  parser.add_argument("--username", help="protect api endpoints with an username (default: rabbit)", type=str, default='rabbit')
  parser.add_argument("--password", help="protect api endpoints with a password (default: none)", type=str, default='')
  parser.add_argument("--debug", help="enable debug mode (default: False)", action='store_true', default=False)
  args = parser.parse_args()

  user = args.username
  passwd = args.password

  app.run(args.host, args.port, args.debug, threaded=True)