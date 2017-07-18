from gpiozero import MCP3008

class Sense:
    def mcp3008():
        for x in range(0, 5):
            with MCP3008(channel=x) as reading:
                print("resistance value is : ", reading.value)
                reading = 'resistance value is : {}'.format(reading.value)
        return reading 
        

from tkinter import *
import tkinter

class simpleapp_tk(tkinter.Tk):
    def __init__(self,parent):
        tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()

if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('Resistance values')
    
m1 = PanedWindow(orient=VERTICAL)
m1.pack(fill=NONE, expand=5)
right = Label(m1, text= Sense.mcp3008())
m1.add(right)
mainloop()
