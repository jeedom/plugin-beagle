import os
import sys
import struct
import bluetooth._bluetooth as bluez
import globals
import logging
import binascii
import _thread as thread
import time

class Beagle():
    def __init__(self,trame,mac):
        self.trame = trame
        self.mac = mac
        self.string = ''
        self.cf = ''
        self.uuid = ''
        self.type = ''
        self.datatrame = ''
        self.data = {}
        self.result={}
        self.ignore = 0
        self.repeat = 0
        self.repeateruuid = ''
        self.numberrepeat = 0

    def parse(self):
        try:
            if self.trame[0:14] in ['0201041bffb602','0201061bffb602']:
                self.datatrame = self.trame[22:]
                self.uuid=self.datatrame[2:8]
                cleanedtrame = self.trame[0:30]+'00'+self.trame[32:]
                if self.uuid in globals.lastevent and globals.lastevent[self.uuid] == cleanedtrame:
                    self.ignore=1
                globals.lastevent[self.uuid] = cleanedtrame
                self.result['mac'] = self.mac
                self.string =''
                self.string += 'Beagle found '
                self.type = self.trame[14:18]
                self.cf= self.datatrame[:2]
                self.uuid=self.datatrame[2:8]
                self.result['uuid'] = self.uuid
                self.data['type'] = ''
                repetitionData = str(bin(int(self.trame[30:32],16)))[2:].ljust(8,'0')
                if (repetitionData[1:2] == '0' and repetitionData[2:4]!= '00') :
                    self.repeat = 1
                elif (repetitionData[1:2] == '1' and repetitionData[2:4]!= '11') :
                    self.repeat = 1
                if (self.repeat == 1) :
                    if (self.uuid in globals.KNOWN_DEVICES):
                        self.type = globals.types[globals.KNOWN_DEVICES[self.uuid]['model']]
                        self.string += ' (repeated data) '
                    else:
                        return
                if self.type == '8e44':
                    self.switch()
                elif self.type == '9844':
                    self.dcl()
                elif self.type == '8f44':
                    self.shutter()
                else:
                    logging.debug('Unknown type ' + str(self.type))
                    return
                self.result['data'] = self.data
                if self.ignore == 1 and self.data['type'] != 'binding':
                    return
                elif self.ignore == 1 and self.data['type'] == 'binding':
                    if self.uuid in globals.KNOWN_DEVICES:
                        return
                logging.debug(self.trame)
                logging.debug(self.string)
                if self.result['model'] != 'switch' and self.data['type'] != 'binding':
                    if self.uuid in globals.lastdata and globals.lastdata[self.uuid] == self.data:
                        return
                globals.lastdata[self.uuid] = self.data
                if self.data['type'] == 'binding':
                    if self.uuid not in globals.KNOWN_DEVICES:
                        if not globals.LEARN_MODE:
                            logging.debug('It\'s a beagle device but this device is not Included and I\'am not in learn mode ' +str(self.uuid))
                            return
                        else:
                            logging.debug('It\'s a beagle device but this device is not Included. I\'am learning it ' +str(self.uuid))
                else:
                    if self.uuid not in globals.KNOWN_DEVICES:
                        logging.debug('It\'s a beagle device but this device is not Included and its not a binding data ' +str(self.uuid))
                        return
                globals.JEEDOM_COM.add_changes('devices::'+self.uuid,self.result)
                if self.result['model'] == 'switch' and self.data['type'] != 'binding':
                    thread.start_new_thread( self.return_state, ('return_state',))
                    logging.debug('Thread return state switch prepared')
        except Exception as e:
            logging.debug(str(e))

    def switch(self):
        self.result['model'] = 'switch'
        self.string += 'This is a switch with UUID ' + self.uuid
        if self.cf == '00':
            self.data['type'] = 'advertisement'
            self.string += ' advertisement'
            self.data['firmware'] = self.trame[34:40]
            if self.trame[32:34] == '02':
                self.data['value'] = '1'
                self.data['label'] = 'Toggle'
                self.string += ' action is toggle'
            elif self.trame[32:34] == '05':
                self.data['value'] = '2'
                self.data['label'] = 'Haut'
                self.string += ' action is up'
            elif self.trame[32:34] == '06':
                self.data['value'] = '3'
                self.data['label'] = 'Bas'
                self.string += ' action is down'
        elif self.cf == '01':
            self.data['type'] = 'binding'
            self.string += ' binding'
        return

    def dcl(self):
        self.result['model'] = 'dcl'
        self.string += 'This is a DCL with UUID '+ self.uuid
        if self.cf == '10':
            self.data['type'] = 'advertisement'
            self.string += ' advertisement'
            self.data['firmware'] = self.trame[58:62]
            if self.trame[32:34] == '01':
                self.data['value'] = '1'
                self.data['label'] = 'Allumé'
                self.string += ' state is ON'
            elif self.trame[32:34] == '00':
                self.data['value'] = '0'
                self.data['label'] = 'Eteint'
                self.string += ' state is OFF'
            elif self.trame[32:34] == '10':
                self.data['paired'] = 'denied'
                self.string += ' pairing denied'
            elif self.trame[32:34] == '11':
                self.data['paired'] = 'ok'
                self.string += ' pairing ok'
            elif self.trame[32:34] == '12':
                self.data['paired'] = 'paired'
                self.string += ' paired'
            elif self.trame[32:34] == '13':
                self.data['paired'] = 'unpaired'
                self.string += ' unpaired'
            self.data['groups'] ={}
            group1uuid = self.trame[36:44]
            self.data['groups'][group1uuid]={'data':{}}
            self.string += ' group1 : ' +group1uuid
            if self.trame[44:46] == '01':
                self.data['groups'][group1uuid]['data']['value'] = '1'
                self.data['groups'][group1uuid]['data']['label'] = 'Allumé'
                self.string += ' state is ON'
            elif self.trame[44:46] == '00':
                self.data['groups'][group1uuid]['data']['value'] = '0'
                self.data['groups'][group1uuid]['data']['label'] = 'Eteint'
                self.string += ' state is OFF'
            group2uuid = self.trame[46:54]
            self.data['groups'][group2uuid]={'data':{}}
            self.string += ' group2 : ' +group2uuid
            if self.trame[54:56] == '01':
                self.data['groups'][group2uuid]['data']['value'] = '1'
                self.data['groups'][group2uuid]['data']['label'] = 'Allumé'
                self.string += ' state is ON'
            elif self.trame[54:56] == '00':
                self.data['groups'][group2uuid]['data']['value'] = '0'
                self.data['groups'][group2uuid]['data']['label'] = 'Eteint'
                self.string += ' state is OFF'
        elif self.cf == '11':
            self.data['type'] = 'binding'
            self.string += ' binding'
        elif self.cf == '1B':
            self.data['type'] = 'group'
            self.string += ' group'
            self.data['groups'] = [self.trame[38:46],self.trame[46:54]]
            self.string += ' ' + str(self.data['groups'])
        elif self.cf == '1C':
            self.data['type'] = 'scene'
            self.data['subtype'] = 'schneider'
            self.string += ' schneiderscene'
            self.data['scenes'] = [self.trame[38:46],self.trame[46:54],self.trame[54:62]]
            self.string += ' ' + str(self.data['scenes'])
        elif self.cf == '1D':
            self.data['type'] = 'scene'
            self.data['subtype'] = 'custom'
            self.string += ' customerscene'
            self.data['scenes'] = [self.trame[38:46],self.trame[46:54],self.trame[54:62]]
            self.string += ' ' + str(self.data['scenes'])
        return

    def shutter(self):
        self.result['model'] = 'shutter'
        self.string += 'This is a Shutter with UUID '+ self.uuid
        if self.cf == '30':
            self.data['type'] = 'advertisement'
            self.data['firmware'] = self.trame[58:62]
            self.string += ' advertisement'
            if self.trame[32:34] == '00':
                self.data['value'] = '100'
                self.data['label'] = 'Ouvert'
                self.string += ' state is opened'
            elif self.trame[32:34] == '01':
                self.data['value'] = '0'
                self.data['label'] = 'Fermé'
                self.string += ' state is closed'
            elif self.trame[32:34] == '05':
                self.data['label'] = 'Ouverture'
                self.string += ' state is moving up'
            elif self.trame[32:34] == '06':
                self.data['label'] = 'Fermeture'
                self.string += ' state is moving down'
            elif self.trame[32:34] == '07':
                self.data['label'] = 'Arrêté'
                position = int(self.trame[44:46],16)
                self.data['value'] = position
                self.string += ' state is stopped with position ' + str(position)
            elif self.trame[32:34] == '10':
                self.data['paired'] = 'denied'
                self.string += ' pairing denied'
            elif self.trame[32:34] == '11':
                self.data['paired'] = 'ok'
                self.string += ' pairing ok'
            elif self.trame[32:34] == '12':
                self.data['paired'] = 'paired'
                self.string += ' paired'
            elif self.trame[32:34] == '13':
                self.data['paired'] = 'unpaired'
                self.string += ' unpaired'
            self.data['groups'] ={}
            group1uuid = self.trame[36:44]
            self.data['groups'][group1uuid]={'data':{}}
            self.string += ' group1 : ' +group1uuid
            if self.trame[44:46] == '00':
                self.data['groups'][group1uuid]['data']['value'] = '100'
                self.data['groups'][group1uuid]['label'] = 'Ouvert'
                self.string += ' state is opened'
            elif self.trame[44:46] == '01':
                self.data['groups'][group1uuid]['data']['value'] = '0'
                self.data['groups'][group1uuid]['data']['label'] = 'Fermé'
                self.string += ' state is closed'
            elif self.trame[44:46] == '05':
                self.data['groups'][group1uuid]['data']['label'] = 'Ouverture'
                self.string += ' state is moving up'
            elif self.trame[44:46] == '06':
                self.data['groups'][group1uuid]['data']['label'] = 'Fermeture'
                self.string += ' state is moving down'
            elif self.trame[44:46] == '07':
                self.data['groups'][group1uuid]['data']['label'] = 'Arrêté'
                self.string += ' state is stopped'
            group2uuid = self.trame[46:54]
            self.data['groups'][group2uuid]={'data':{}}
            self.string += ' group2 : ' +group2uuid
            if self.trame[54:56] == '00':
                self.data['groups'][group2uuid]['data']['value'] = '100'
                self.data['groups'][group2uuid]['data']['label'] = 'Ouvert'
                self.string += ' state is opened'
            elif self.trame[44:46] == '01':
                self.data['groups'][group2uuid]['data']['value'] = '0'
                self.data['groups'][group2uuid]['data']['label'] = 'Fermé'
                self.string += ' state is closed'
            elif self.trame[44:46] == '05':
                self.data['groups'][group2uuid]['data']['label'] = 'Ouverture'
                self.string += ' state is moving up'
            elif self.trame[44:46] == '06':
                self.data['groups'][group2uuid]['data']['label'] = 'Fermeture'
                self.string += ' state is moving down'
            elif self.trame[44:46] == '07':
                self.data['groups'][group2uuid]['data']['label'] = 'Arrêté'
                self.string += ' state is stopped'
        elif self.cf == '31':
            self.data['type'] = 'binding'
            self.string += ' binding'
        elif self.cf == '3B':
            self.data['type'] = 'group'
            self.string += ' group'
            self.data['groups'] = [self.trame[38:46],self.trame[46:54]]
            self.string += ' ' + str(self.data['groups'])
        elif self.cf == '3C':
            self.data['type'] = 'scene'
            self.data['subtype'] = 'schneider'
            self.string += ' schneiderscene'
            self.data['scenes'] = [self.trame[38:46],self.trame[46:54],self.trame[54:62]]
            self.string += ' ' + str(self.data['scenes'])
        elif self.cf == '3D':
            self.data['type'] = 'scene'
            self.data['subtype'] = 'custom'
            self.string += ' customerscene'
            self.data['scenes'] = [self.trame[38:46],self.trame[46:54],self.trame[54:62]]
            self.string += ' ' + str(self.data['scenes'])
        return

    def return_state(self,name):
        try:
            time.sleep(2)
            self.result['data']['value'] = '0'
            self.result['data']['label'] = 'Aucun'
            globals.JEEDOM_COM.add_changes('devices::'+self.uuid,self.result)
        except Exception as e:
            logging.debug(str(e))
