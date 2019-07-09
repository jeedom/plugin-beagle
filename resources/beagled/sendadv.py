# coding: utf-8
import time
import struct
import os
import binascii
import base64
import globals
import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.primitives.ciphers import algorithms

def build_trame(device,type,data =''):
    targetUUID = device['uuid']
    cfModel = globals.cftarget[device['model']]
    header = globals.uniqueHeader+globals.types['gateway']+globals.headerVV+globals.headerFS
    if type == 'pair':
        logging.debug('Building pairing data with key ' + str(device['key']))
        data = globals.gateway['binding']+globals.uuidController+str(device['key'])
    else:
        dataAc = globals.ac[data['ac']]
        data = globals.gateway['advertisement']+globals.uuidController+'01'+dataAc + cfModel +'FF'+targetUUID+'FFFFFF'
        counter = str(random())
        data = data+counter
    return header+data

def random():
    counter = binascii.b2a_hex(os.urandom(1)) +binascii.b2a_hex(os.urandom(1))
    return counter.decode().upper()

def compute(macaddr,trame):
    mac = "".join(reversed([macaddr.replace(':','')[i:i+2] for i in range(0, len(macaddr.replace(':','')), 2)])).lower()
    replaced = trame[22:30]+'FF'+trame[32:]
    payload = replaced.replace(' ','').lower()
    s = mac + payload
    logging.debug('Mac payload is ' + str(s))
    buffer = binascii.unhexlify(str(s))
    return buffer

def hash(secret,buffer):
    print(secret)
    c = cmac.CMAC(algorithms.AES(binascii.unhexlify(secret)), backend=default_backend())
    c.update(buffer)
    hash =binascii.hexlify(bytearray(c.finalize()))
    return hash

def sendCmd(device,type,data=''):
    logging.debug('Sending command for device ' + str(device))
    trame = str(build_trame(device,type,data))
    logging.debug('Command data is ' + str(trame))
    buffer = compute(globals.donglemac,trame)
    key = (globals.gateway['binding']+globals.uuidController+str(device['key'])).replace(' ','').lower()
    if type == 'pair':
        key = globals.uniquekey.replace(' ','').lower()
    hashed = hash(key,buffer)
    logging.debug('Hashed data is ' + str(hashed))
    cmac = hashed.decode()[0:8]
    payload = (trame+cmac).upper()
    logging.debug('Final payload is ' + str(payload))
    finalpayload = ' '.join(payload[i:i+2] for i in range(0, len(payload), 2)).upper()
    send(finalpayload)

def send(payload):
    logging.debug('Sending Payload ' + str(payload))
    #os.system('sudo hciconfig hci0 up')
    os.system('sudo hcitool -i hci0 cmd 0x08 0x0008 1F '+ str(payload))
    os.system('sudo hcitool -i hci0 cmd 0x08 0x0006 A0 00 A0 00 03 00 00 00 00 00 00 00 00 07 00')
    os.system('sudo hcitool -i hci0 cmd 0x08 0x000a 01')
    time.sleep(0.5)
    os.system('sudo hcitool -i hci0 cmd 0x08 0x000a 00')
