import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from Tkinter import *
import time
import Adafruit_MCP3008

# Software SPI configuration:
CLK  = 11
MISO = 9
MOSI = 10
CS   = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} |'.format(*range(1)))
print('-' * 65)

root = Tk()
var = StringVar()
var.set('hello')
l1 = Label (root, textvariable = var)
l1.pack()
# Main program loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*5
    volt = [0]*5
    curr = [0]*5
    resis = [0]*5
    v = 3.278
    bit = 1023
    for i in range(5):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = (mcp.read_adc(i) * v / bit)
        print(mcp.read_adc(i))
        volt = values[:]
#        values[i] = round(values[i], 3)
        values[i] = v - values[i]
        curr[i] = values[i] / 11000
        resis[i] = volt[i] / curr[i]
        if resis[i] == 0:
                continue
        else:
                resis[i] = resis[i]
        resis[i] = resis[i] / 1000
        resis[i] = round(resis[i], 2)
    # Print the ADC values.
    print('| {0:>4} KOhm | {1:>4} KOhm | {2:>4} KOhm | {3:>4} KOhm | {4:>4} KOhm |'.format(*resis))
    var.set('KOhm '.join(str(e) for e in resis))
    root.update_idletasks()
    # Pause for half a second.
    time.sleep(1)
