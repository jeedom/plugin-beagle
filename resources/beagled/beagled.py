# This file is part of Jeedom.
#
# Jeedom is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jeedom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jeedom. If not, see <http://www.gnu.org/licenses/>.

import logging
import string
import sys
import os
import time
import datetime
import re
import signal
from optparse import OptionParser
from os.path import join
import json
import argparse
import blescan
import sys
import time
import subprocess
import sendadv
import _thread as thread

import bluetooth._bluetooth as bluez

try:
    from jeedom.jeedom import *
except ImportError as e:
    print("Error: importing module jeedom.jeedom " + str(e))
    sys.exit(1)

def read_socket(name):
    while 1:
        try:
            global JEEDOM_SOCKET_MESSAGE
            if not JEEDOM_SOCKET_MESSAGE.empty():
                logging.debug("Message received in socket JEEDOM_SOCKET_MESSAGE")
                message = JEEDOM_SOCKET_MESSAGE.get().decode('utf-8')
                message =json.loads(message)
                if message['apikey'] != _apikey:
                    logging.error("Invalid apikey from socket : " + str(message))
                    return
                logging.debug('Received command from jeedom : '+str(message['cmd']))
                if message['cmd'] == 'learnin':
                    logging.debug('Enter in learn mode')
                    globals.LEARN_MODE = True
                    globals.LEARN_BEGIN = int(time.time())
                    globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 1});
                elif message['cmd'] == 'learnout':
                    logging.debug('Leave learn mode')
                    globals.LEARN_MODE = False
                    globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0});
                elif message['cmd'] == 'add':
                    logging.debug('Add device : '+str(message['device']))
                    if 'uuid' in message['device']:
                        globals.KNOWN_DEVICES[message['device']['uuid']] = message['device']
                elif message['cmd'] == 'remove':
                    logging.debug('Remove device : '+str(message['device']))
                    if 'uuid' in message['device']:
                        del globals.KNOWN_DEVICES[message['device']['uuid']]
                elif message['cmd'] == 'bind':
                    logging.debug('Binding device : '+str(message['uuid']))
                    sendadv.sendCmd(globals.KNOWN_DEVICES[message['uuid']],'pair')
                elif message['cmd'] == 'send':
                    logging.debug('Sending to device : '+str(message['target']))
                    sendadv.sendCmd(globals.KNOWN_DEVICES[message['target']],'advertisement',message['command'])
        except Exception as e:
            logging.error('Exception on socket : '+str(e))
        time.sleep(0.1)

def heartbeat_handler(delay):
    while 1:
        if globals.LEARN_MODE and (globals.LEARN_BEGIN + 60)  < int(time.time()):
            globals.LEARN_MODE = False
            logging.debug('Quitting learn mode (60s elapsed)')
            globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0});
        time.sleep(1)

def listen():
    jeedom_socket.open()
    try:
        thread.start_new_thread( read_socket, ('socket',))
        logging.debug('Read Socket Thread Launched')
        thread.start_new_thread( ble_scan, ('scanner',))
        logging.debug('Ble Scanner Thread Launched')
        thread.start_new_thread( heartbeat_handler, (19,))
        logging.debug('Heartbeat Thread Launched')
    except KeyboardInterrupt:
        shutdown()

def ble_scan(name):
    dev_id = globals.IFACE_DEVICE
    try:
        sock = bluez.hci_open_dev(dev_id)
        logging.debug("Ble thread started on device " + str(dev_id))
        blescan.hci_le_set_scan_parameters(sock)
        blescan.hci_enable_le_scan(sock)
        while True:
            blescan.parse_events(sock, 10)
    except:
        print("Error accessing bluetooth device...")
        sys.exit(1)


# ----------------------------------------------------------------------------

def handler(signum=None, frame=None):
    logging.debug("Signal %i caught, exiting..." % int(signum))
    shutdown()

def shutdown():
    logging.debug("Shutdown")
    logging.debug("Removing PID file " + str(_pidfile))
    try:
        os.remove(_pidfile)
    except:
        pass
    try:
        jeedom_socket.close()
    except:
        pass
    try:
        jeedom_serial.close()
    except:
        pass
    logging.debug("Exit 0")
    sys.stdout.flush()
    os._exit(0)

# ----------------------------------------------------------------------------

_log_level = "error"
_socket_port = 55556
_socket_host = 'localhost'
_device = 'auto'
_pidfile = '/tmp/beagled.pid'
_apikey = ''
_callback = ''

parser = argparse.ArgumentParser(description='Beagle Daemon for Jeedom plugin')
parser.add_argument("--socketport", help="Socketport for server", type=str)
parser.add_argument("--loglevel", help="Log Level for the daemon", type=str)
parser.add_argument("--callback", help="Callback", type=str)
parser.add_argument("--apikey", help="Apikey", type=str)
parser.add_argument("--cycle", help="Cycle to send event", type=str)
parser.add_argument("--pid", help="Pid file", type=str)
parser.add_argument("--device", help="Device", type=str)
parser.add_argument("--sockethost", help="Socket Host", type=str)
args = parser.parse_args()


if args.device:
    _device = args.device
if args.socketport:
    _socket_port = int(args.socketport)
if args.loglevel:
    _log_level = args.loglevel
if args.callback:
    _callback = args.callback
if args.apikey:
    _apikey = args.apikey
if args.pid:
    _pidfile = args.pid
if args.cycle:
    _cycle = float(args.cycle)
if args.sockethost:
   _sockethost = args.sockethost

jeedom_utils.set_log_level(_log_level)
logging.info('Start blead')
logging.info('Log level : '+str(_log_level))
logging.info('Socket port : '+str(_socket_port))
logging.info('Socket host : '+str(_sockethost))
logging.info('Device : '+str(_device))
logging.info('PID file : '+str(_pidfile))
logging.info('Apikey : '+str(_apikey))
logging.info('Callback : '+str(_callback))
logging.info('Cycle : '+str(_cycle))
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)
globals.IFACE_DEVICE = int(_device[-1:])


cmd = "hciconfig"
device_id = _device
status, output = subprocess.getstatusoutput(cmd)
bt_mac = output.split("{}:".format(device_id))[1].split("BD Address: ")[1].split(" ")[0].strip()
logging.debug('Bluetooth Mac adress is ' + bt_mac)
globals.donglemac = bt_mac
try:
    jeedom_utils.write_pid(str(_pidfile))
    globals.JEEDOM_COM = jeedom_com(apikey = _apikey,url = _callback,cycle=_cycle)
    if not globals.JEEDOM_COM.test():
        logging.error('Network communication issues. Please fixe your Jeedom network configuration.')
        shutdown()
    jeedom_socket = jeedom_socket(port=_socket_port,address=_socket_host)
    listen()
except Exception as e:
    logging.error('Fatal error : '+str(e))
    logging.debug(traceback.format_exc())
    shutdown()
