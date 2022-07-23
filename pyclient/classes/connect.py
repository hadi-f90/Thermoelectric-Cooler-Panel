from socketIO_client import BaseNamespace
import datetime
import json
import os.path
import requests
import time


class Status(object):
    url = 'http://localhost:3000'
    RecordData = False
    isConnected = False
    TempTarget = 25.0
    radiatorFan = 'OFF'
    housingFan = 'OFF'
    peltierCheck = 'OFF'
    pumpCheck = 'OFF'
    insideFanCheck = 'OFF'  # <<config
    recordInterval = 1
    recordId = 0
    mode = 'hipro'
    voltage = '0'

    def SortData(self, char1, char2):
        return self[self.find(char1) + 1:self.find(char2)]

    def LoadConfig():
        PATH = './config.json'
        if os.path.isfile(PATH):
            print('File exists and is readable')
        else:
            print('No file creating with default template')
            config = {'TempTarget': '24'}
            with open('config.json', 'w') as filez:
                json.dump(config, filez)

        with open('config.json', 'r') as filez:
            config = json.load(filez)
            Status.TempTarget = float(config['TempTarget'])
            print(Status.TempTarget)

    def WriteConfig(self, value):
        with open('config.json', 'r') as filez:
            config = json.load(filez)
            config[self] = value

        with open('config.json', 'w') as f:
            json.dump(config, f)


class Namespace(BaseNamespace):

    def Checkrecords():
        print('got recordinfo')
        r = requests.get(f'{Status.url}/settingz')

        print(f'Record info:{r.text}')
        jsonObject = json.loads(r.text)
        RecordNow = False
        for key in jsonObject:
            field = key['setname']
            value = key['value']
            if field == 'interval':
                Status.recordInterval = int(value)

            elif field == 'recordid':
                Status.recordId = value

            if field == 'mode':
                Status.mode = value
                print(f'mode:{value}')

            if field == 'currentrecord' and value != 'none':
                RecordNow = True

        if RecordNow:
            Status.RecordData = True
            print('record status set to true')
        else:
            Status.RecordData = False
            print('record status set to false')

    def on_connect(self):
        Status.isConnected = True
        Status.RecordData = False
        print('Connected to server')
        self.emit('join', 'raspberrypi zero joined at ' +
                  str(datetime.datetime.now()))
        self.emit('targettemp', str(Status.TempTarget))
        Namespace.Checkrecords()

    def on_reconnect(self):
        self.emit('recordcheck', 'check')
        print('raspberry pi reconnected')
        self.emit('join', 'raspberry pi Zer0 reconnected')
        self.emit('targettemp', str(Status.TempTarget))
        Status.isConnected = True

    def on_disconnect(self):
        Status.isConnected = False
        print('Disconnected from the server trying to reconnect')

    def on_record(self, *args):
        self.emit('join', 'raspberry pi in record mode')
        data = Status.SortData(str(args), '{', '}')
        if data == 'True':
            # Status.RecordData = True
            print('Fetching New Record Data')
            time.sleep(5)
            Namespace.Checkrecords()

        else:
            Status.RecordData = False
            Status.recordId = '0'
            Status.recordInterval = 4
            print('Stop Recording Data')

    def on_gettemptarget(self, *args):
        Status.LoadConfig()
        data = Status.SortData(str(args), '{', '}')
        if data == 'givemetemp':
            self.emit('targettemp', str(Status.TempTarget))

    def on_changetemp(self, *args):
        data = Status.SortData(str(args), '{', '}')
        Status.TempTarget = float(data)
        Status.WriteConfig('TempTarget', str(Status.TempTarget))
        print(f'target changed to: {data}')

    def on_picheck(self, *args):
        data = Status.SortData(str(args), '{', '}')
        if data == 'ping':
            self.emit('picheck', 'pong')
            print('Response pong was sent')

    def on_pimode(self, *args):
        data = Status.SortData(str(args), '{', '}')
        Status.mode = data
        print(f'Mode changed to: {data}')
