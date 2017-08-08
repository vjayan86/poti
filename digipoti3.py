import RPi.GPIO as GPIO             			## import GPIO library and give it a new name
import time							## import time library which contains 'sleep'

#===========Class_Digi_Pot_as_SPI_bus object============================ using simple system - single pot

class class_digital_pot_spi:

	def __init__(self, typ, res, cur, CS=24, MOSI=19, MISO=21, SCLK=23, play=False):
		
		## typ = a string with the serial number e.g. 4162-502
		## res = the maximum resistance value for this type
		## cur = the initial value to set the pot to
		## CS = pin for cable select control line
		## MOSI = pin for Master Out Slave In
		## MISO = pin for Mater In Slave Out
		## SCLK = pin for clocking in bits
		## play - if True will display debug information
		
		self.demo = play							## if true uses demo mode					
		
		if self.demo:
			GPIO.setwarnings(True)
		else:
			GPIO.setwarnings(False)
		
		self.SPI_CS00 = CS							## cable select pin used
		self.SPI_MOSI = MOSI						## Master Out Slave In pin
		self.SPI_MISO = MISO						## Master In Slave Out pin
		self.SPI_SCLK = SCLK						## Pin used for clock
		self.typ_pot = typ							## Type of pot - part num
		self.max_res = res							## maximum resistance ohms
		self.cur_res = cur							## value requested at init ohms
		self.lin_log = True										## switch between linear and log on percentage - default is linear - not yet implemented
		self.mn = 0											 	## sets up a minimum value for the pot - default is zero - not yet implemented
		self.mx = self.max_res									## sets up a maximum value for the pot - default is hardware maximum - not yet implemented
		
		GPIO.setup(self.SPI_CS00,GPIO.OUT)			## sets pin 24 to output
		GPIO.setup(self.SPI_MISO,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)			
			## last line sets pin 21 to input with a weak pull down enabled 
		GPIO.setup(self.SPI_MOSI,GPIO.OUT)			## sets pin 19 to output
		GPIO.setup(self.SPI_SCLK,GPIO.OUT)			## sets pin 23 to output
		
		GPIO.output(self.SPI_CS00, True)			## sets CS pin high
		GPIO.output(self.SPI_MOSI,False)			## sets MOSI pin low
		GPIO.output(self.SPI_SCLK,False)			## sets idle state of clock pin low
		
		if self.demo:
			print "Initialising digital potentiometer controller in DEMO mode:"
			print "Type is:                 " + self.get_typ()
			print "Cable select on pin:     " + str(self.get_CS())
			print "Master Out Slave In pin: " + str(self.get_MOSI())
			print "Master In Slave Out pin: " + str(self.get_MISO())
			print "Clock ticks on pin:      " + str(self.get_SCLK()) 					
		
		self.set_r(self.cur_res)					## set initial value
		
		if self.demo:
			print "set up with inital value of: " + str(self.get_r())
		
		return	
	
	#==============SOME UTILITIES=======================================
		#----------rotation of bits in binary to left and right---------
	
	def rot_r(self, v, r = 1, m = 16):				## move MSB to LSB and shift rest right
		mask = (2**r) - 1
		mask_bits = v & mask
		return (v >> r)|(mask_bits << (m-r))

	def rot_l(self, v, r = 1, m = 16): 				## move LSB to MSB and shift rest left
		return self.rot_r(v, m-r, m)
	
		#---A method to format binary numbers as string for outputs-----
	
	def bin2str(self, x, d=0):
		oct2bin = ['000','001','010','011','100','101','110','111']
		binstrg = [oct2bin[int(n)] for n in oct(x)]
		return ''.join(binstrg).lstrip('0').zfill(d)
	
	#==============Methods to return present status at object level=====
	def bugger(self):								## toggles embedded debugger code
		self.demo = not self.demo
		if self.demo:
			a = "================= POT class DEBUGGING is ON ============="
		else:
			a = "================= POT class DEBUGGING is OFF ============"
		return a
		
		#---------------------------------------------------------------
	def get_typ(self):								## return string with type of pot
		if self.demo:
			print "using get_typ()"
			if self.typ_pot == "4162-502":
				print "instruction set known"
			else:
				print "instruction set unknown"
		return self.typ_pot
		
		#---------------------------------------------------------------
	def get_CS(self):								## return string with CS for SPI bus pot
		if self.demo:
			print "using get_CS()"
		return self.SPI_CS00
		
		#---------------------------------------------------------------
	def get_MOSI(self):								## return string with MOSI pin for SPI
		if self.demo:
			print "using get_MOSI()"
		return self.SPI_MOSI	
		
		#----------------------------------------------------------------
	def get_MISO(self):								## return string with MISO pin for SPI
		if self.demo:
			print "using get_MISO()"
		return self.SPI_MISO	
	
		#---------------------------------------------------------------
	def get_SCLK(self):								## return string with Clock pin for SPI
		if self.demo:
			print "using get_SCLK()"
		return self.SPI_SCLK	
	
		#---------------------------------------------------------------
	def get_r(self):								## get present resistance absolute
		return self.cur_res
	
		#------------------------------------------------------------------	
	def get_p(self):								## get present resistance as percentage
		return (self.cur_res/self.max_res)*100
				
	#===========The bit banger==========================================
	def bit_bang(self, command):
		if self.demo:
			print "=================BIT BANG STARTED===================="
		MISO_echo = 0b0000000000000000				# template for echo from digital pot
		for bit in range(16):
			command = self.rot_l(command, 1, 16)	## shift command to move to the next bit i.e shift the MSB to the LSB
			if self.demo:
				print "new instruction: " + self.bin2str(command, 16)
			
			# now transmit the LSB of the command
			if command & 1:							## If data AND 00000001 is true i.e if LSB is 1
				GPIO.output(self.SPI_MOSI, True)
			else:									## if LSB is 0
				GPIO.output(self.SPI_MOSI,False)
			
			if self.demo:
				print "MISO pin status before tick: " + str(GPIO.input(self.SPI_MISO))
			
			GPIO.output(self.SPI_SCLK, True)		## send a clock tick
			
			if self.demo:
				print "MISO pin status during tick: " + str(GPIO.input(self.SPI_MISO))
			
			# now take the MISO pin value which is 0 or 1, and 'or' it with previous MISO_echo and rotate the resuting bytes
				
			MISO_echo = MISO_echo | GPIO.input(self.SPI_MISO)
			MISO_echo = self.rot_l(MISO_echo, 1, 16)
			
			if self.demo:
				print "MISO pin status during tick: " + str(GPIO.input(self.SPI_MISO))
			
			GPIO.output(self.SPI_SCLK,False)		## end clock tick
			
			if self.demo:
				print "MISO pin status after tick : " + str(GPIO.input(self.SPI_MISO))
				
		return MISO_echo
	
	#=========Methods to get current values at hardware level===========
	def get_r_hard(self):							## get resitor settings from chip hardware
		if self.demo:
			print "software says setting is : " + str(self.get_r())
		
		command = 0b0000111111111111	
		
		# the above command has the command byte xxxx11nn which should read memory location xxxx
			# the command xxxx00nn writes memory location xxxx
			# the command xxxx11nn reads memory locations xxxx
			# memory locations for the MCP4162 are defined as:
				# 0000 - volatile wiper RAM
				# 0010 - non-volatile wiper EEPROM
				# 0100 - TCON register RAM
				# 0110 - STATUS register RAM
				# higher numbers - data EEPROM stores of 10 bytes
		
		MISO_echo = self.bit_bang(command)			## clock out the bits from the 16 bit sequence and read what comes back					
		
		if self.demo:
			print "hardware gives MISO as   : " + self.bin2str(MISO_echo, 16)
		
		return MISO_echo
		
	#=========Methods to set values=====================================
	
		#---------------------------------------------------------------
	def set_r(self, data):							## set absolute value of resistor in volatile memeory
		if self.demo:
			print "setting to: " + str(data) + " ohms"
			print "maximum restistance is: " + str(self.max_res)
		
		r = int((data/self.max_res) * 255)
		
		if self.demo:
			print "..so value byte is: " + bin(r)
			
		r = r|0b0000000000000000				    ## OR the DATA with 16-bit number to add the DATA to the Command
		
		if self.demo:
			print "..so command is:    " + str(r)
			
		GPIO.output(self.SPI_CS00,False)			## sets first ChipSelect CS pin low	GPIO.output(SPI_CS01,False)	
		time.sleep(0.1)								## time delay needed from when CS pin goes active until clock starts
		
		## NB SPI mode is either 00 or 11 depending on the state of the SCLK pin when the CS transitions to active - low in this case
		## as the order used is set CS then set SDI then pulse on SCLK, mode OO is being used - i.e. the idele state of SCLK is low
		
		
		MISO_echo = self.bit_bang(r)				## clock out the bits from the 16 bit sequence and read what comes back
		GPIO.output(self.SPI_CS00, True)			## sets first CS pin back to high
		
		GPIO.output(self.SPI_MOSI,False)			## might not be needed depending on last bit sent
		
		r = r&0b0000000011111111					## extract the value bits from the command bytes
													## NB when MISO is working can use MISO echo to confirm - but MISO isn't working!
		self.cur_res = (float(r)/255) * self.max_res
		
		if self.demo:
			print "echoed on MISO:     " + self.bin2str(MISO_echo, 16) + " = " + str(MISO_echo)
			print "resistance set to:  " + self.bin2str(r, 16) + " = " + str(r)
			print "resistance set to:  " + str(self.get_r())
		return MISO_echo

		#-------------------------------------------------------------------
	def set_p(self, p):								## set to percentage of maximum range
		if self.demo:
			print "setting to: " + str(p) + "% of " + str(self.max_res) + " ohms"
			print " = " +  str((self.max_res*p)/100) + " ohms"
		
		MISO_echo = self.set_r(int((self.max_res*p)/100))		## set % value of resistor in volatile memory
		return MISO_echo
	
		#-------------------------------------------------------------------	
	def set_n(self):								## make present settings non-volatile
		return

	#----------set equivalent pot by KBROYGBVW colour code--------------
		#-blacK-Brown-Red-Orange-Yellow-Green-Blue-Violet-White-------------
		#-for example 'BKR' = 1k ohms---------------------------------------
	def set_colour(self):
		return
											## not yet implemented
	#----------get nearest KBROYGBVW colour code for pot----------------
		#-blacK-Brown-Red-Orange-Yellow-Green-Blue-Violet-White-------------
	def get_colour(self):
		return
		
											## not yet implemented
	#----------save contents to file as nnn.res --------------------------
													## not yet implemented
	
	#----------read contents from file as nnn.res ------------------------
													## not yet implemented
	

#=======================================================================
#						NOW TRY IT ALL OUT
#=======================================================================

GPIO.setmode(GPIO.BOARD)

#------------------------set a single pot-------------------------------

pot = class_digital_pot_spi("4162-502", 5000.0, 2500.0, 24, 19, 21, 23, True)

#------------------------flash the LED using the pot--------------------
print pot.bugger()
print bin(pot.set_r(4500))
print bin(pot.set_r(10))
print bin(pot.set_r(4700))
print pot.bugger()

try:
	#while True:									
	pot.get_r_hard()

finally:											## always do this
	GPIO.cleanup()
