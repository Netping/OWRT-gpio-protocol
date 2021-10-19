import ubus
import os
from threading import Thread
from threading import Lock
from time import sleep




class device:
    name = ""
    protocol = None
    pins = []

class protocols:
    def configure(pins, values):
        pass

    def read(pins):
        ret = []

        for p in pins:
            if p['direction'] == 'input':
                e = {}

                with open("/sys/class/gpio/gpio" + p['gpio'] + "/value", "r") as f:
                    e[p['name']] = f.read()

                ret.append(e)

        return ret

class D_Triger_IO_proto(protocols):
    def configure(pins, value):
        pass

    def read(pins):
        super().read(pins)

class D_triger_Relay_proto(protocols):
    def configure(pins, value):
        trig_gpio = None

        #get TRIG_CLK gpio
        for p in pins:
            if p['name'] == 'TRIG_CLK':
                trig_gpio = p['gpio']
                break
        #search pin
        keys = [*value.keys()]
        for p in pins:
            if p['name'] in keys and p['name'] != 'TRIG_CLK':
                if p['direction'] == 'output':
                    v = bool(int(value[p['name']]))
                    s = '0'

                    if v:
                        s = '1'

                    if os.system("echo \"" + s + "\" > /sys/class/gpio/gpio" + p['gpio'] + "/value"):
                        print("Error: can't set value for gpio " + p['gpio'])

                    if os.system("echo \"1\" > /sys/class/gpio/gpio" + trig_gpio + "/value"):
                        print("Error: can't set value for gpio " + trig_gpio)

                    sleep(0.1)

                    if os.system("echo \"0\" > /sys/class/gpio/gpio" + trig_gpio + "/value"):
                        print("Error: can't set value for gpio " + trig_gpio)

                break

    def read(pins):
        super().read(pins)

class Fake_IO_proto(protocols):
    def configure(pins, value):
        print("Pins")
        print(pins)
        print("\n")
        print(value)
        print("\n")

        #search pin
        keys = [*value.keys()]
        for p in pins:
            if p['name'] in keys:
                if p['direction'] == 'output':
                    v = bool(int(value[p['name']]))
                    s = '0'

                    if v:
                        s = '1'

                    print("echo \"" + s + "\" > /sys/class/gpio/gpio" + p['gpio'] + "/value")

                break

    def read(pins):
        ret = []

        for p in pins:
            if p['direction'] == 'input':
                e = {}

                #with open("/sys/class/gpio/gpio" + p['gpio'] + "/value", "r") as f:
                #    e[p['name']] = f.read()
                print("read " + "/sys/class/gpio/gpio" + p['gpio'] + "/value " + "to e[p['name']]")
                e[p['name']] = '0'

                ret.append(e)

        return ret

class GPIOProto:
    hardwareConfName = 'hardwareconf'
    gpioConfName = 'gpioconf'
    pollThread = None
    configThread = None
    default_device = device()
    task_list = []
    devices = []

    protocol_type_map = { 
                            'D_triger_IO' : D_Triger_IO_proto,
                            'D_triger_Relay' : D_triger_Relay_proto,
                            'Fake_IO' : Fake_IO_proto
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

            if not GPIOProto.configThread:
                self.__startConfigThread()

            GPIOProto.pollThread = Thread(target=self.__poll, args=())
            GPIOProto.pollThread.start()
        except Exception:
            print(Exception)

    def readGPIO(self, devicename):
        ret = None

        GPIOProto.mutex.acquire()

        dev = None
        for d in GPIOProto.devices:
            if d.name == devicename:
                dev = d
                break

        if dev:
            ret = dev.protocol.read(dev.pins)

        GPIOProto.mutex.release()

        return ret

    def writeGPIO(self, devicename, value):
        t = { 'name' : devicename, 'value' : value }

        GPIOProto.mutex.acquire()
        GPIOProto.task_list.insert(0, t)
        GPIOProto.mutex.release()

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
                        if e.protocol != Fake_IO_proto:
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
                        else:
                            print("echo \"" + pin['gpio'] + "\" > /sys/class/gpio/export")
                            #set direction
                            direction = GPIOProto.direction_map[pin['direction']]
                            if direction != 'other':
                                print("echo \"" + direction + "\" > /sys/class/gpio/gpio" + pin['gpio'] + "/direction")

                            #set value to 0 if it output
                            if direction == 'out':
                                print("echo \"0\" > /sys/class/gpio/gpio" + pin['gpio'] + "/value")

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
                devicename = t['name']
                value = t['value']

                dev = None
                for d in GPIOProto.devices:
                    if d.name == devicename:
                        dev = d
                        break

                if dev:
                    dev.protocol.configure(dev.pins, value)

                GPIOProto.mutex.release()
