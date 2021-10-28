import ubus
import os
from threading import Thread
from threading import Lock
from time import sleep
from journal import journal




module_name = "GPIO Protocol"

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
            if p['direction'] == 'in':
                e = {}

                with open("/sys/class/gpio/gpio" + p['gpio'] + "/value", "r") as f:
                    e[p['name']] = f.read()

                ret.append(e)

        return ret

class D_Triger_IO_proto(protocols):
    def configure(pins, value):
        trig_gpio = None
        out_up_gpio = None
        out_down_gpio = None

        #get gpio's from pins
        for p in pins:
            if trig_gpio and out_up_gpio and out_down_gpio:
                break

            if p['name'] == 'OUT_UP' and p['direction'] == 'out':
                out_up_gpio = p['gpio']

            if p['name'] == 'OUT_DOWN' and p['direction'] == 'out':
                out_down_gpio = p['gpio']

            if p['name'] == 'TRIG' and p['direction'] == 'out':
                trig_gpio = p['gpio']

        if not (trig_gpio and out_up_gpio and out_down_gpio):
            #print("Error: wrong ping configuration! Check gpioconf for device")
            journal.WriteLog(module_name, "Normal", "error", "wrong ping configuration! Check gpioconf for device")
            return

        if value.upper() == 'ON':
            if os.system("echo \"1\" > /sys/class/gpio/gpio" + out_up_gpio + "/value"):
                #print("Error: can't set value for gpio " + out_up_gpio)
                journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + out_up_gpio)

            if os.system("echo \"0\" > /sys/class/gpio/gpio" + out_down_gpio + "/value"):
                #print("Error: can't set value for gpio " + out_down_gpio)
                journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + out_up_gpio)

        elif value.upper() == 'OFF':
            if os.system("echo \"0\" > /sys/class/gpio/gpio" + out_up_gpio + "/value"):
                #print("Error: can't set value for gpio " + out_up_gpio)
                journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + out_up_gpio)

            if os.system("echo \"1\" > /sys/class/gpio/gpio" + out_down_gpio + "/value"):
                #print("Error: can't set value for gpio " + out_down_gpio)
                journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + out_up_gpio)
        else:
            #print('Error: unknown value')
            journal.WriteLog(module_name, "Normal", "error", "unknown value")
            return

        #turn on CLK for 100ms
        if os.system("echo \"1\" > /sys/class/gpio/gpio" + trig_gpio + "/value"):
            #print("Error: can't set value for gpio " + trig_gpio)
            journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + trig_gpio)

        sleep(0.1)

        if os.system("echo \"0\" > /sys/class/gpio/gpio" + trig_gpio + "/value"):
            #print("Error: can't set value for gpio " + trig_gpio)
            journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + trig_gpio)

    def read(pins):
        trig_gpio = None
        pull_up_gpio = None

        #get gpio's from pins
        for p in pins:
            if trig_gpio and pull_up_gpio:
                break

            if p['name'] == 'PULL_UP' and p['direction'] == 'out':
                pull_up_gpio = p['gpio']

            if p['name'] == 'TRIG' and p['direction'] == 'out':
                trig_gpio = p['gpio']

        if not (trig_gpio and pull_up_gpio):
            #print("Error: wrong pin reading! Check gpioconf for device")
            journal.WriteLog(module_name, "Normal", "error", "wrong pin reading! Check gpioconf for device")
            return

        #init reading
        if os.system("echo \"1\" > /sys/class/gpio/gpio" + pull_up_gpio + "/value"):
            #print("Error: can't set value for gpio " + pull_up_gpio)
            journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + pull_up_gpio)

        #turn on CLK for 100ms
        if os.system("echo \"1\" > /sys/class/gpio/gpio" + trig_gpio + "/value"):
            #print("Error: can't set value for gpio " + trig_gpio)
            journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + trig_gpio)

        sleep(0.1)

        if os.system("echo \"0\" > /sys/class/gpio/gpio" + trig_gpio + "/value"):
            #print("Error: can't set value for gpio " + trig_gpio)
            journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + trig_gpio)

        ret = super().read(pins)

        #deinit reading
        if os.system("echo \"0\" > /sys/class/gpio/gpio" + pull_up_gpio + "/value"):
            #print("Error: can't set value for gpio " + pull_up_gpio)
            journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + pull_up_gpio)

        return ret

class D_triger_Relay_proto(protocols):
    def configure(pins, value):
        trig_gpio = None
        relay_gpio = None

        #get TRIG_CLK gpio
        for p in pins:
            if trig_gpio and relay_gpio:
                break

            if p['name'] == 'RELAY_INT' and p['direction'] == 'out':
                relay_gpio = p['gpio']

            if p['name'] == 'TRIG_CLK' and p['direction'] == 'out':
                trig_gpio = p['gpio']

        if not (trig_gpio and relay_gpio):
            #print("Error: wrong ping configuration! Check gpioconf for device")
            journal.WriteLog(module_name, "Normal", "error", "wrong ping configuration! Check gpioconf for device")
            return

        if value.upper() == 'ON':
            if os.system("echo \"1\" > /sys/class/gpio/gpio" + relay_gpio + "/value"):
                #print("Error: can't set value for gpio " + relay_gpio)
                journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + relay_gpio)

        elif value.upper() == 'OFF':
            if os.system("echo \"0\" > /sys/class/gpio/gpio" + relay_gpio + "/value"):
                #print("Error: can't set value for gpio " + relay_gpio)
                journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + relay_gpio)
        else:
            #print('Error: unknown value')
            journal.WriteLog(module_name, "Normal", "error", "unknown value")
            return

        #turn on CLK for 100ms
        if os.system("echo \"1\" > /sys/class/gpio/gpio" + trig_gpio + "/value"):
            #print("Error: can't set value for gpio " + trig_gpio)
            journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + trig_gpio)

        sleep(0.1)

        if os.system("echo \"0\" > /sys/class/gpio/gpio" + trig_gpio + "/value"):
            #print("Error: can't set value for gpio " + trig_gpio)
            journal.WriteLog(module_name, "Normal", "error", "can't set value for gpio " + trig_gpio)

    def read(pins):
        return super().read(pins)

class Fake_IO_proto(protocols):
    def configure(pins, value):
        print("Pins")
        print(pins)
        print("\n")
        print(value)
        print("\n")

        #search pin
        for p in pins:
            if p['name'] == 'RELAY_INT' and p['direction'] == 'out':
                if value.upper() == "ON":
                    print("echo \"1\" > /sys/class/gpio/gpio" + p['gpio'] + "/value")
                elif value.upper() == "OFF":
                    print("echo \"0\" > /sys/class/gpio/gpio" + p['gpio'] + "/value")
                else:
                    print('Unknown value')

                break

    def read(pins):
        ret = []

        for p in pins:
            if p['direction'] == 'in':
                e = {}

                print("read " + "/sys/class/gpio/gpio" + p['gpio'] + "/value " + "to e[p['name']]")
                e[p['name']] = '0'

                ret.append(e)

        return ret

class GPIOProto:
    directionConfName = 'directionconf'
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
            self.__applyDirectionConfig()

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

    def __startConfigThread(self):
        GPIOProto.configThread = Thread(target=self.__pollConfig, args=())
        GPIOProto.configThread.start()

    def __applyConfig(self):
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
                                #print("Error: can't export new pin " + pin['gpio'])
                                journal.WriteLog(module_name, "Normal", "error", "can't export new pin " + pin['gpio'])

                            #set direction
                            direction = GPIOProto.direction_map[pin['direction']]
                            if direction != 'other':
                                if os.system("echo \"" + direction + "\" > /sys/class/gpio/gpio" + pin['gpio'] + "/direction"):
                                    #print("Error: can't set direction to " + direction + "for gpio" + pin['gpio'])
                                    journal.WriteLog(module_name, "Normal", "error", "can't set direction to " + direction + "for gpio" + pin['gpio'])

                            #set value to 0 if it output
                            if direction == 'out':
                                if os.system("echo \"0\" > /sys/class/gpio/gpio" + pin['gpio'] + "/value"):
                                    #print("Error: can't set output gpio" + pin['gpio'] + "to low")
                                    journal.WriteLog(module_name, "Normal", "error", "can't set output gpio" + pin['gpio'] + "to low")
                        else:
                            print("echo \"" + pin['gpio'] + "\" > /sys/class/gpio/export")
                            #set direction
                            direction = GPIOProto.direction_map[pin['direction']]
                            if direction != 'other':
                                print("echo \"" + direction + "\" > /sys/class/gpio/gpio" + pin['gpio'] + "/direction")

                            #set value to 0 if it output
                            if direction == 'out':
                                print("echo \"0\" > /sys/class/gpio/gpio" + pin['gpio'] + "/value")

                        pin['direction'] = GPIOProto.direction_map[pin['direction']]
                        e.pins.append(pin)

                GPIOProto.devices.append(e)
                print(e.pins)

    def __applyDirectionConfig(self):
        confvalues = ubus.call("uci", "get", { "config": GPIOProto.directionConfName })
        for confdict in list(confvalues[0]['values'].values()):
            if confdict['.type'] == 'info' and confdict['.name'] == 'Settings':
                gpios = [ i.replace('gpio', '') for i in [*confdict.keys()] if i.startswith('gpio') ]

                for e in GPIOProto.devices:
                    for p in e.pins:
                        if p['gpio'] in gpios and p['direction'] == 'other':
                            direction = GPIOProto.direction_map[confdict['gpio' + p['gpio']]]

                            if e.protocol != Fake_IO_proto:
                                if os.system("echo \"" + direction + "\" > /sys/class/gpio/gpio" + p['gpio'] + "/direction"):
                                    #print("Error: can't set direction to " + direction + "for gpio" + p['gpio'])
                                    journal.WriteLog(module_name, "Normal", "error", "can't set direction to " + direction + "for gpio" + p['gpio'])

                                if direction == 'out':
                                    if os.system("echo \"0\" > /sys/class/gpio/gpio" + p['gpio'] + "/value"):
                                        #print("Error: can't set output gpio" + p['gpio'] + "to low")
                                        journal.WriteLog(module_name, "Normal", "error", "can't set output gpio" + p['gpio'] + "to low")
                            else:
                                print("echo \"" + direction + "\" > /sys/class/gpio/gpio" + p['gpio'] + "/direction")

                                if direction == 'out':
                                    print("echo \"0\" > /sys/class/gpio/gpio" + p['gpio'] + "/value")

    def __handleConfig(self, event, data):
        if data['config'] == directionConfName:
            while (GPIOProto.tasks):
                pass

            GPIOProto.mutex.acquire()

            self.__applyDirectionConfig()

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
