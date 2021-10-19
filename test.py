#!/usr/bin/python3

from gpioproto import *




def main():
    gpio = GPIOProto()

    #gpio.writeGPIO('Relay 2', { 'RELAY_INT' : '1' })
    ret = gpio.readGPIO('Device IO 1')

    print('Ret is:')
    print(ret)

if __name__ == "__main__":
    main()
