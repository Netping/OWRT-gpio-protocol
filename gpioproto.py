import ubus
import enum
import os
from threading import Thread
from threading import Lock




class protocol_type(enum.Enum):
    empty = 0
    IO = 1
    Relay = 2
    Fake_IO = 3

class device:
    name = ""
    protocol = protocol_type.empty
    pins = []

class protocols:
    #TODO
    pass

class GPIOProto:
    hardwareConfName = 'hardwareconf'
    gpioConfName = 'gpioconf'
    pollThread = None
    configThread = None
    default_device = device()
    task_list = []
    devices = []

    protocol_type_map = { 
                            'D_triger_IO' : protocol_type.IO,
                            'D_triger_Relay' : protocol_type.Relay,
                            'Fake_IO' : protocol_type.Fake_IO 
                        }

    direction_map = {
                        'input' : 'in',
                        'output' : 'out',
                        'io' : 'other'
                    }

    mutex = Lock()

    def __init__(self):
        try:
            ubus.connect()

            self.__applyConfig()

            GPIOProto.pollThread = Thread(target=self.__poll, args=())
            GPIOProto.pollThread.start()
        except Exception:
            print(Exception)

    def readGPIO(self, index):
        if not GPIOProto.configThread:
            self.__startConfigThread()

        #TODO

    def writeGPIO(self, index, value):
        if not GPIOProto.configThread:
            self.__startConfigThread()

        t = { 'gpio' : index, 'value' : value }

        GPIO.mutex.acquire()
        GPIOProto.task_list.insert(0, t)
        GPIO.mutex.release()

    def __unexportAll(self):
        #TODO unexport all GPIOs from system
        pass

    def __Write(self, index, value):
        #TODO write value to gpio with index
        pass

    def __startConfigThread(self):
        GPIOProto.configThread = Thread(target=self.__pollConfig, args=())
        GPIOProto.configThread.start()

    def __applyConfig(self):
        self.__unexportAll()

        confvalues = ubus.call("uci", "get", { "config": GPIOProto.gpioConfName })
        for confdict in list(confvalues[0]['values'].values()):
            if confdict['.type'] == 'device' and confdict['.name'] == 'prototype':
                GPIOProto.default_device.name = confdict['name']
                GPIOProto.default_device.protocol = GPIOProto.protocol_type_map[confdict['protocol']]

            if confdict['.type'] == 'device' and confdict['.name'] != 'prototype':
                e = device()

                e.name = confdict['name']
                e.protocol = GPIOProto.protocol_type_map[confdict['protocol']]
                e.pins = []

                pins = [*confdict.keys()]
                #fill pins
                print('\n' + e.name)
                for p in pins:
                    if p.startswith('sig_'):
                        pin = {}
                        pin['name'] = p.replace('sig_', '')
                        pin['gpio'] = confdict[p].split('-')[0].replace('GPIO', '')
                        pin['direction'] = confdict[p].split('-')[1]

                        #Do settings pin
                        #export new pin
                        if os.system("echo \"" + pin['gpio'] + "\" > /sys/class/gpio/export"):
                            print("Error: can't export new pin " + pin['gpio'])

                        #set direction
                        direction = GPIOProto.direction_map[pin['direction']]
                        if direction != 'other':
                            if os.system("echo \"" + direction + "\" > /sys/class/gpio/gpio" + pin['gpio'] + "/direction"):
                                print("Error: can't set direction to " + direction + "for gpio" + pin['gpio'])

                        #set value to 0 if it output
                        if direction == 'out':
                            if os.system("echo \"0\" > /sys/class/gpio/gpio" + pin['gpio'] + "/value"):
                                print("Error: can't set output gpio" + pin['gpio'] + "to low")

                        e.pins.append(pin)

                GPIOProto.devices.append(e)
                print(e.pins)

    def __handleConfig(self, event, data):
        if data['config'] == gpioConfName:
            while (GPIOProto.tasks):
                pass

            GPIOProto.mutex.acquire()

            self.__applyConfig()

            GPIOProto.mutex.release()            

    def __pollConfig(self):
        ubus.listen(("commit", self.__handleConfig))
        ubus.loop()

        ubus.disconnect()

    def __poll(self):
        while True:
            while GPIOProto.task_list:
                GPIOProto.mutex.acquire()

                t = GPIOProto.task_list.pop()
                gpio = t['gpio']
                value = t['value']

                self.__Write(gpio, value)

                GPIOProto.mutex.release()
