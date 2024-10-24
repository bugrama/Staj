from threading import Thread, Lock
import time

class WriteV20():
    
    def __init__(self,rw_operationLock,client1,freqReg,vfdReg,directionReg):
        
        self.rw_operationLock = rw_operationLock
        self.client = client1
        self.lock = rw_operationLock
        self.client=client1
        
        self.freqReg = freqReg
        self.vfdReg = vfdReg
        self.directionReg = directionReg
  
      
    
            
    def _setFreq(self, frequency):
        try:
            time.sleep(0.1)
            self.client.write_register(self.freqReg, frequency, functioncode=6) 
            
        except Exception as e:
                print(f"Error: {e}")
        
    def _setDirection(self, direction):
        time.sleep(0.1)
        try:
            if direction == "backward" :
                self.client.write_register(self.directionReg, 3199, functioncode=6)
            elif direction == "forward":
                self.client.write_register(self.directionReg, 1151, functioncode=6) 
        except Exception as e:
                print(f"Error: {e}")
        
    def _vfdReset(self):
        with self.lock:
            time.sleep(0.1)    
            self.client.write_register(self.vfdReg, 1278, functioncode=6) # reset vfd
        
    def stop(self):
        with self.lock:
            time.sleep(0.1)    
            self.client.write_register(100, 0, functioncode=6) # freq
            time.sleep(0.1)
            self.client.write_register(99, 1278, functioncode=6) # reset vfd
            time.sleep(0.1)
            self.client.write_register(99, 1150, functioncode=6) # Stop
            time.sleep(0.1)

    def checkstop(self,mainex,sensorV20):
  
        if mainex.condition == "stop" and sensorV20.frequency!=0:
            print("hata")
            
            
        
    def writeOperation(self, frequency, direction):
    
        with self.lock:
           
            self._setFreq(frequency)
            self._setDirection(direction)
          
    
    


            
  
