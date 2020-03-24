# coding: utf-8
import time
READY = False
JEEDOM_COM = ''
KNOWN_DEVICES = {}
LEARN_MODE = False
IFACE_DEVICE = 0
LEARN_BEGIN = int(time.time())
lastevent={}
lastdata={}
donglemac = ''


uniqueHeader = '0201041BFFB602'
headerVV = '01'
headerFS = '01'
uuidController = '443884'
uniquekey = '9f5b9cced150d9d051b0b7da4c4e2de6'
jeedomkey = ''

ac = {'off' : '00', 'on' : '01' , 'toggle' : '02','up':'05','down':'06','stop':'07', 'goto':'20', 'customerScenes' : '0C','schneiderScenes' : '0D' , 'groups' : '0B'}

cftarget = {'switch' : '0F', 'dcl' : '1F' , 'generic' : '2F' ,'shutter':'3F','plug' : '4F','dimmer' : '5F','scene' : 'FF','groupdcl' :'1F','groupshutter':'3F','groupplug':'4F','groupdimmer':'5F'}

types = {'shutter':'8f44','dcl' : '9844', 'generic' : '9244','switch' : '8e44', 'plug' : '9044', 'dimmer' : '9144', 'gateway' : 'A244' }

gateway = {'advertisement' : 'A0' , 'binding' : 'A1'}

scenes = {'schneider' : 'FD' , 'custom' : 'FC'}
