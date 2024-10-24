#!/usr/bin/env python3

import sys
import time
import spidev
import readV20
import json
from readV20 import *
from threading import Lock
from writeV20 import *
from anqle import *
from automatic import *
from gpio import *
from server2 import *

import minimalmodbus

class MainExecuter():
    
    def __init__(self):
	    
        self.client1 = minimalmodbus.Instrument("/dev/serial0", 1, debug=False)  # port name, slave address (in decimal)
        self.client1.serial.baudrate = 38400  # baudrate
        self.client1.serial.bytesize = 8
        self.client1.serial.parity   = minimalmodbus.serial.PARITY_NONE
        self.client1.serial.stopbits = 1
        self.client1.serial.timeout  = 5   # seconds
        self.client1.address         = 1        # this is the slave address number
        self.client1.mode = minimalmodbus.MODE_RTU # rtu or ascii mode
        self.client1.clear_buffers_before_each_transaction = True
        self.condition="null"
	
        self.rw_operationLock = Lock()
        self.readV20 = ReadV20(self.rw_operationLock,self.client1)
        self.readV20.startReadingV20()
        self.shouldStop = False
	
	
        
        
def main():
	
	mainex= MainExecuter()
	
	
	writer = WriteV20(mainex.rw_operationLock,mainex.client1, 100,99,99)
	anqle_s=SensorWorker()
	
	anqle_s.sensorRead()
	automatic=Automatic(mainex.shouldStop,writer,anqle_s,mainex.readV20,mainex)
	
	data1=data2=""
	buttons= Buttons()
	server=ChatServer()
	tip =0
	
	
	while True:
		if server.bag_flag== True:
			data1="stop"
			print("buranda")
			server.bag_flag=False
				
					
		if server.flag ==True:
			data1=server.gelendata
			tip=server.tip
			deger=server.deger
			deger=int(float(deger))
			yazdı=False
			server.flag =False
		elif buttons.flag==True:
			data1=buttons.data
			tip ="1"
			buttons.flag=False
		
		if tip == "1":
			if data1!=data2:
				mainex.shouldStop = "True"
				print(data1+"11")
				thread=Thread(target=automatic.Move,args=(data1,))
				thread.start()
				data2=data1
		elif tip =="2":
			if yazdı==False:
				if data1=="stop":
					writer.stop()
			
				mainex.shouldStop = "True"
				print(data1+"12")
				writer.writeOperation((deger*100),data1)
				yazdı=True
		elif tip =="3":
			automatic.konum_ayar(data1)	
			
			
		
		
		data={'angle':str(automatic.angle),"frequency":str(mainex.readV20.frequency),"current":str(mainex.readV20.current),"speed":str(mainex.readV20.speed)}
		server.gidendata=json.dumps(data)
		
		
		#server.gidendata=str(anqle_s.angle_current)+" "+str(mainex.readV20.frequency)+" "+str(mainex.readV20.current)+" "+str(mainex.readV20.speed)+"**"
	
	
	
	

	
if __name__=="__main__":
			main()
        
    
