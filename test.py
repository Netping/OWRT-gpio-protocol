#!/usr/bin/python3

from gpioproto import *




def main():
    gpio = GPIOProto()

    gpio.writeGPIO('Relay 1', 'ON')
    gpio.writeGPIO('Relay 2', 'ON')
    ret = gpio.readGPIO('Device IO 1')

    print('Ret is:')
    print(ret)

if __name__ == "__main__":
    main()
