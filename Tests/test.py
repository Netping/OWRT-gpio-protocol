#!/usr/bin/python3
import ubus
import os
import time

# config info
config1 = "gpioconf"
config2 = "directionconf"
config_path = "/etc/config/"

# for test python methods
try:
    from gpioproto import *
except:
    print('"gpioproto" import error. You must install "OWRT-gpio-protocol" module.')
    exit(-1)

try:
    ubus.connect()
except:
    print("Can't connect to ubus")

def test_conf1_existance():
    ret = False

    try:
        ret = os.path.isfile(f"{config_path}{config1}")
    except:
        assert ret

    assert ret

def test_conf1_valid():
    ret = False

    try:
        confvalues = ubus.call("uci", "get", {"config": config1})
        for confdict in list(confvalues[0]['values'].values()):
            # check globals
            if confdict['.type'] == 'globals' and confdict['.name'] == 'globals':
                assert confdict['protocol'] == ['D_triger_IO.Д-триггер-Ввод/Вывод', 'D_triger_Relay.Д-триггер-реле', 'Fake_IO.Имитация']
            # check prototype
            if confdict['.type'] == 'device' and confdict['.name'] == 'prototype':
                assert confdict['name'] == 'prototype'
                assert confdict['protocol'] == 'Fake_IO'
    except:
        assert ret

def test_conf2_existance():
    ret = False

    try:
        ret = os.path.isfile(f"{config_path}{config2}")
    except:
        assert ret

    assert ret

def test_conf2_valid():
    ret = False

    try:
        confvalues = ubus.call("uci", "get", {"config": config2})
        for confdict in list(confvalues[0]['values'].values()):
            # check Settings section existanse
            if confdict['.type'] == 'info' and confdict['.name'] == 'Settings':
                ret = True
        assert ret
    except:
        assert ret

def test_python_methods():
    ret = False

    devtest = 'DeviceTest'

    #create device in config1
    try:
        testsection = 'testdevice'
        if os.system(f"uci set {config1}.{testsection}=device"):
            raise ValueError("Can't create new section")

        if os.system(f"uci set {config1}.{testsection}.name={devtest}"):
            raise ValueError("Can't set option name")

        if os.system(f"uci set {config1}.{testsection}.protocol='Fake_IO'"):
            raise ValueError("Can't set option protocol")

        if os.system(f"uci set {config1}.{testsection}.sig_TRIG='GPIO5-output'"):
            raise ValueError("Can't set option protocol")

        if os.system(f"uci set {config1}.{testsection}.sig_PULL_UP='GPIO6-output'"):
            raise ValueError("Can't set option protocol")

        if os.system(f"uci set {config1}.{testsection}.sig_OUT_UP='GPIO7-output'"):
            raise ValueError("Can't set option protocol")

        if os.system(f"uci set {config1}.{testsection}.sig_OUT_DOWN='GPIO8-output'"):
            raise ValueError("Can't set option protocol")

        if os.system(f"uci set {config1}.{testsection}.sig_IN='GPIO9-input'"):
            raise ValueError("Can't set option protocol")

        # uci commit
        if os.system("uci commit"):
            raise ValueError("Can't commit uci")

        #send commit signal for module
        if os.system("ubus send commit '{\"config\":\"" + config1 + "\"}'"):
            raise ValueError("Can't send commit signal to {config1}")

        #wait for notify getting value
        time.sleep(5)
    except:
        assert ret

    try:
        gpio = GPIOProto()
        res = gpio.writeGPIO(devtest, 'ON')
        print(f'RESULT writeGPIO is {res}')
        assert type(res) == type({})
        gpio.writeGPIO(devtest, 'OFF')
        print(f'RESULT writeGPIO is {res}')
        assert type(res) == type({})
        res = gpio.readGPIO(devtest)
        print(f'RESULT readGPIO is {res}')
        assert res == None
    except:
        assert ret

    #delete section from config
    print('delete test device')
    os.system(f"uci delete {config1}.testdevice")
    os.system(f"uci commit {config1}")
    os.system("ubus send commit '{\"config\":\"" + config1 + "\"}'")
