# import needed references from other libraries
import time
import RPi.GPIO as GPIO

# define SPI pins
SPI_CS_PIN = 17
SPI_CLK_PIN = 23
SPI_SDISDO_PIN = 22 # mosi

# define GPIO settings
GPIO.setmode(GPIO.BCM)
GPIO.setup(SPI_CS_PIN, GPIO.OUT)
GPIO.setup(SPI_CLK_PIN, GPIO.OUT)
GPIO.setup(SPI_SDISDO_PIN, GPIO.OUT)

# module that defines the wiper movement
def set_value(value):
    print "here"
    GPIO.output(SPI_CS_PIN, True)

    GPIO.output(SPI_CLK_PIN, False)
    GPIO.output(SPI_CS_PIN, False)

    b = '{0:016b}'.format(value)
    for x in range(0, 16):
        print 'x:' + str(x) + ' -> ' + str(b[x])
        GPIO.output(SPI_SDISDO_PIN, int(b[x]))

        GPIO.output(SPI_CLK_PIN, True)
        GPIO.output(SPI_CLK_PIN, False)

    GPIO.output(SPI_CS_PIN, True)

# main program
# sample program that constantly moves the wiper up and down.
while True:
    for level in range(0, 128): 
        print 'level:' + str(level)
        set_value(level)
        time.sleep(0.1)

    for level in range(127, -1, -1):
        print 'level:' + str(level)
        time.sleep(0.1)
        
        
"""        
set_value(level)
where level is a value between 0 and 127.
set_value(0) should be minimum resistance.
set_value(127) should be maximum resistance.        
"""
