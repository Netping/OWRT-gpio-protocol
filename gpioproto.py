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

class GPIOProto:
    hardwareConfName = 'hardwareconf'
    gpioConfName = 'gpioconf'
    pollThread = None
    configThread = None
    task_list = []

    protocol_type_map = { 
                            'D_triger_IO' : protocol_type.IO,
                            'D_triger_Relay' : protocol_type.Relay,
                            'Fake_IO' : protocol_type.Fake_IO 
                        }

    mutex = Lock()

    def __init__(self):
        try:
            ubus.connect()

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
            if confdict['.type'] == 'info':
                #TODO parse all keys option which start with 'gpio' and apply values
                #TODO applying value: export gpio and set direction via os.system

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
