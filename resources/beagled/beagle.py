import globals
import logging


class Beagle():
    def __init__(self, trame, mac):
        self.trame = trame
        self.mac = mac
        self.string = ''
        self.cf = ''
        self.uuid = ''
        self.type = ''
        self.datatrame = ''
        self.data = {}
        self.result = {}
        self.ignore = 0
        self.repeat = 0
        self.repeateruuid = ''
        self.numberrepeat = 0

    def parse(self):
        try:
            if self.trame[0:14] in ['0201041bffb602', '0201061bffb602']:
                self.datatrame = self.trame[22:]
                self.uuid = self.datatrame[2:8]
                cleanedtrame = self.trame[0:30]+'00'+self.trame[32:]
                if self.uuid in globals.lastevent and globals.lastevent[self.uuid] == cleanedtrame:
                    self.ignore = 1
                globals.lastevent[self.uuid] = cleanedtrame
                self.result['mac'] = self.mac
                self.string = ''
                self.string += 'Beagle found '
                self.type = self.trame[14:18]
                self.cf = self.datatrame[:2]
                self.uuid = self.datatrame[2:8]
                self.result['uuid'] = self.uuid
                self.data['type'] = ''
                repetitionData = str(bin(int(self.trame[30:32], 16)))[2:].ljust(8, '0')
                if (repetitionData[1:2] == '0' and repetitionData[2:4] != '00'):
                    self.repeat = 1
                elif (repetitionData[1:2] == '1' and repetitionData[2:4] != '11'):
                    self.repeat = 1
                if (self.repeat == 1):
                    if (self.uuid in globals.KNOWN_DEVICES):
                        self.type = globals.types[globals.KNOWN_DEVICES[self.uuid]['model']]
                        self.string += ' (repeated data) '
                if self.type == '8e44':
                    self.switch()
                elif self.type == '9844':
                    self.dcl()
                elif self.type == '8f44':
                    self.shutter()
                elif self.type == '9244':
                    self.generic()
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
                            logging.debug('It\'s a beagle device but this device is not Included and I\'am not in learn mode %s', self.uuid)
                            return
                        else:
                            logging.debug('It\'s a beagle device but this device is not Included. I\'am learning it %s', self.uuid)
                            globals.LEARN_MODE = False
                else:
                    if self.uuid not in globals.KNOWN_DEVICES:
                        logging.debug('It\'s a beagle device but this device is not Included and its not a binding data %s', self.uuid)
                        return
                globals.JEEDOM_COM.add_changes('devices::' + self.uuid, self.result)
        except Exception as e:
            logging.debug(str(e))

    def switch(self):
        self.result['model'] = 'switch'
        self.string += 'This is a switch with UUID ' + self.uuid
        if self.cf == '00':
            self.data['type'] = 'advertisement'
            self.string += ' advertisement'
            self.data['firmware'] = self.trame[34:40]
            if self.trame[32:34] == '00':
                self.data['value'] = '0'
                self.data['label'] = 'Off'
                self.string += ' action is off'
            elif self.trame[32:34] == '01':
                self.data['value'] = '1'
                self.data['label'] = 'On'
                self.string += ' action is on'
            elif self.trame[32:34] == '02':
                self.data['value'] = '2'
                self.data['label'] = 'Toggle'
                self.string += ' action is toggle'
            elif self.trame[32:34] == '03':
                self.data['value'] = '3'
                self.data['label'] = 'Dim Up'
                self.string += ' action is dim up'
            elif self.trame[32:34] == '04':
                self.data['value'] = '4'
                self.data['label'] = 'Dim Down'
                self.string += ' action is dim down'
            elif self.trame[32:34] == '05':
                self.data['value'] = '5'
                self.data['label'] = 'Haut'
                self.string += ' action is up'
            elif self.trame[32:34] == '06':
                self.data['value'] = '6'
                self.data['label'] = 'Bas'
                self.string += ' action is down'
            elif self.trame[32:34] == '07':
                self.data['value'] = '7'
                self.data['label'] = 'Stop'
                self.string += ' action is stop'
            elif self.trame[32:34] == '08':
                self.data['value'] = '8'
                self.data['label'] = 'Scene User'
                self.string += ' action is scene user'
            elif self.trame[32:34] == '09':
                self.data['value'] = '9'
                self.data['label'] = 'Scene In'
                self.string += ' action is scene in'
            elif self.trame[32:34].lower() == '0a':
                self.data['value'] = '10'
                self.data['label'] = 'Scene Out'
                self.string += ' action is scene out'
        elif self.cf == '01':
            self.data['type'] = 'binding'
            self.string += ' binding'
        return

    def dcl(self):
        self.result['model'] = 'dcl'
        self.string += 'This is a DCL with UUID ' + self.uuid
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
            self.data['groups'][group1uuid] = {'data': {}}
            self.string += ' group1 : ' + group1uuid
            if self.trame[44:46] == '01':
                self.data['groups'][group1uuid]['data']['value'] = '1'
                self.data['groups'][group1uuid]['data']['label'] = 'Allumé'
                self.string += ' state is ON'
            elif self.trame[44:46] == '00':
                self.data['groups'][group1uuid]['data']['value'] = '0'
                self.data['groups'][group1uuid]['data']['label'] = 'Eteint'
                self.string += ' state is OFF'
            group2uuid = self.trame[46:54]
            self.data['groups'][group2uuid] = {'data': {}}
            self.string += ' group2 : ' + group2uuid
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
        elif self.cf == '1b':
            self.data['type'] = 'group'
            self.string += ' group'
            self.data['groups'] = [self.trame[38:46],self.trame[46:54]]
            self.string += ' ' + str(self.data['groups'])
        elif self.cf == '1c':
            self.data['type'] = 'scene'
            self.data['subtype'] = 'custom'
            self.string += ' customerscene'
            self.data['scenes'] = [self.trame[38:46],self.trame[46:54], self.trame[54:62]]
            self.string += ' ' + str(self.data['scenes'])
        elif self.cf == '1d':
            self.data['type'] = 'scene'
            self.data['subtype'] = 'schneider'
            self.string += ' schneiderscene'
            self.data['scenes'] = [self.trame[38:46], self.trame[46:54], self.trame[54:62]]
            self.string += ' ' + str(self.data['scenes'])
        return

    def generic(self):
        self.result['model'] = 'generic'
        self.string += 'This is a Generic with UUID ' + self.uuid
        if self.cf == '20':
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
            self.data['groups'] = {}
            group1uuid = self.trame[36:44]
            self.data['groups'][group1uuid] = {'data': {}}
            self.string += ' group1 : ' + group1uuid
            if self.trame[44:46] == '01':
                self.data['groups'][group1uuid]['data']['value'] = '1'
                self.data['groups'][group1uuid]['data']['label'] = 'Allumé'
                self.string += ' state is ON'
            elif self.trame[44:46] == '00':
                self.data['groups'][group1uuid]['data']['value'] = '0'
                self.data['groups'][group1uuid]['data']['label'] = 'Eteint'
                self.string += ' state is OFF'
            group2uuid = self.trame[46:54]
            self.data['groups'][group2uuid] = {'data': {}}
            self.string += ' group2 : ' + group2uuid
            if self.trame[54:56] == '01':
                self.data['groups'][group2uuid]['data']['value'] = '1'
                self.data['groups'][group2uuid]['data']['label'] = 'Allumé'
                self.string += ' state is ON'
            elif self.trame[54:56] == '00':
                self.data['groups'][group2uuid]['data']['value'] = '0'
                self.data['groups'][group2uuid]['data']['label'] = 'Eteint'
                self.string += ' state is OFF'
        elif self.cf == '21':
            self.data['type'] = 'binding'
            self.string += ' binding'
        elif self.cf == '2b':
            self.data['type'] = 'group'
            self.string += ' group'
            self.data['groups'] = [self.trame[38:46],self.trame[46:54]]
            self.string += ' ' + str(self.data['groups'])
        elif self.cf == '2c':
            self.data['type'] = 'scene'
            self.data['subtype'] = 'custom'
            self.string += ' customerscene'
            self.data['scenes'] = [self.trame[38:46],self.trame[46:54], self.trame[54:62]]
            self.string += ' ' + str(self.data['scenes'])
        elif self.cf == '2d':
            self.data['type'] = 'scene'
            self.data['subtype'] = 'schneider'
            self.string += ' schneiderscene'
            self.data['scenes'] = [self.trame[38:46], self.trame[46:54], self.trame[54:62]]
            self.string += ' ' + str(self.data['scenes'])
        return

    def shutter(self):
        self.result['model'] = 'shutter'
        self.string += 'This is a Shutter with UUID ' + self.uuid
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
                position = 100-int(self.trame[44:46], 16)
                self.data['value'] = position
                self.string += ' state is moving up'
            elif self.trame[32:34] == '06':
                self.data['label'] = 'Fermeture'
                position = 100-int(self.trame[44:46], 16)
                self.data['value'] = position
                self.string += ' state is moving down'
            elif self.trame[32:34] == '07':
                self.data['label'] = 'Arrêté'
                position = 100-int(self.trame[44:46], 16)
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
            self.data['groups'] = {}
            group1uuid = self.trame[36:44]
            self.data['groups'][group1uuid] = {'data': {}}
            self.string += ' group1 : ' + group1uuid
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
            self.data['groups'][group2uuid] = {'data': {}}
            self.string += ' group2 : ' + group2uuid
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
        elif self.cf == '3b':
            self.data['type'] = 'group'
            self.string += ' group'
            self.data['groups'] = [self.trame[38:46], self.trame[46:54]]
            self.string += ' ' + str(self.data['groups'])
        elif self.cf == '3c':
            self.data['type'] = 'scene'
            self.data['subtype'] = 'custom'
            self.string += ' customerscene'
            self.data['scenes'] = [self.trame[38:46], self.trame[46:54], self.trame[54:62]]
            self.string += ' ' + str(self.data['scenes'])
        elif self.cf == '3d':
            self.data['type'] = 'scene'
            self.data['subtype'] = 'schneider'
            self.string += ' schneiderscene'
            self.data['scenes'] = [self.trame[38:46], self.trame[46:54], self.trame[54:62]]
            self.string += ' ' + str(self.data['scenes'])
        return
