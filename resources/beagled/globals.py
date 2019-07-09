# coding: utf-8
import time
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

ac = {'off' : '00', 'on' : '01' , 'toggle' : '02','up':'05','down':'06','stop':'07'}

cftarget = {'switch' : '0F', 'dcl' : '1F' , 'shutter':'3F','plug' : '4F','dimmer' : '5F'}

types = {'shutter':'8f44','dcl' : '9844', 'switch' : '8e44', 'plug' : '9044', 'dimmer' : '9144', 'gateway' : 'A244' }

gateway = {'advertisement' : 'A0' , 'binding' : 'A1'}
