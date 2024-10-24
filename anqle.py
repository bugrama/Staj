from threading import Thread
import time
import spidev

class SensorWorker():
    
    def __init__(self):
        self.thread = Thread(target = self.run)
        self.avg = 0.0    
         
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 7629
        self.fark=0
        self.angle_current = 0
        
        
    def readAI(self,ch):
        if 7 <= ch <= 0:
            raise Exception('MCP3208 channel must be 0-7: ' + str(ch))

        cmd = 128  # 1000 0000
        cmd += 64  # 1100 0000
        cmd += ((ch & 0x07) << 3)
        ret = self.spi.xfer2([cmd, 0x0, 0x0])

        # get the 12b out of the return
        val = (ret[0] & 0x01) << 11  
        val |= ret[1] << 3           
        val |= ret[2] >> 5    
        val = val & 0X0FFF
        #val = val*33.0/4095.0       
        return(val)
        #return (val & 0x0FFF) 
    
    def run(self):
        previous_angle = 0
        previous_speed = 0
        
        while True:
           start_time = time.time()
           current_angle = round(self.read_and_average(20))
           previous_angle = current_angle
           #print(self.angle_current)
           self.angle_current = round(current_angle)-self.fark
           time.sleep(0.01)
           
    def read_and_average(self,num_samples=1):
        values = []
        for _ in range(num_samples):
            value = self.readAI(0)
            values.append(value)
        average = sum(values) / num_samples
       
        return average * (90/1220)

    def sensorRead(self):
        
        self.thread.start()
    
    def ayarla(self,fark):
            self.fark=fark
