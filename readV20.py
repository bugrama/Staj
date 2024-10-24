from threading import Thread, Lock
import time

class ReadV20():
    
    def __init__(self,rw_operationLock,v20_client):
        
        self.rw_operationLock = rw_operationLock
        self.thread = Thread(target = self.read_v20multi)
        self.client = v20_client
        self.frequency=0
        self.lock = rw_operationLock
        self.current=0
        self.speed = 0
        
        
    def startReadingV20(self):
        self.thread.start()

        
    def stopReadingV20():
        pass
    
    def convert_value(self, value):
        if 60536 <= value <= 65337:
            # Mapping from 60536 to 65337 to -50 to 0
            return (value - 60536) * (50 / (65337 - 60536)) - 51
        elif 0 <= value <= 4999:
            # Mapping from 0 to 4999 to 0 to 50 
            return value * (50 / 4999)
            
        else:
            return value
            
    def read_v20multi(self):
        
            while True:
                    self.lock.acquire()  # Acquire the lock
                    time.sleep(0.5)    
                    registers = self.client.read_registers(23, 3, functioncode=3)  # Read three registers starting from 23
                    self.frequency = registers[0]
                    self.frequency = int(self.convert_value(self.frequency))
                    self.speed = registers[1]
                    self.current = registers[2]
                    self.values = {
                        "read_freq": self.frequency,
                        "read_current": self.current,
                        "read_speed": self.speed
                    }
            
                    #print(f"Frequency: {self.frequency} Hz, Current: {self.current} A, Speed: {self.speed}")
                    self.lock.release()
                  
                    time.sleep(0.05)
                   
                    
    
            
  

    
