#!/usr/bin/env python3

import sys
import time
import spidev
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QMutex, QMutexLocker

#import serial
import minimalmodbus

desired_open_angle = 90
desired_close_angle = 0
tolerance = 5  # angle tolerance for stopping the motor
max_speed = 100  # maximum motor speed
min_speed = 20  # minimum motor speed to ensure movement
deceleration_zone = 20  # angle range to start deceleration
acceleration_step = 5  # incremental speed step for acceleration
door_mass = 1200  # kg
door_width = 2  # meters, adjust as necessary

Form, Window = uic.loadUiType("ui3.ui")

class MainWindow(QMainWindow, Form):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 7629
        
        self.client1 = minimalmodbus.Instrument("/dev/serial0", 1, debug=False)  # port name, slave address (in decimal)
        self.client1.serial.baudrate = 38400  # baudrate
        self.client1.serial.bytesize = 8
        self.client1.serial.parity   = minimalmodbus.serial.PARITY_NONE
        self.client1.serial.stopbits = 1
        self.client1.serial.timeout  = 5   # seconds
        self.client1.address         = 1        # this is the slave address number
        self.client1.mode = minimalmodbus.MODE_RTU # rtu or ascii mode
        self.client1.clear_buffers_before_each_transaction = True
        
        self.read_lock = QMutex()
        self.running = "stop"
        self.stopped = True
        
        
        # Initialize UI
        self.init_ui()

    def init_ui(self):
        self.backward.clicked.connect(self.backward_function)
        self.forward.clicked.connect(self.forward_function)
        self.stop_2.clicked.connect(self.stop_function)
        self.dial.valueChanged.connect(self.update_frequency_label)
        
        self.sensorWorker = SensorWorker()
        
        self.open.clicked.connect(self.automatic_open)
        self.stop.clicked.connect(self.stop_automatic)
        
        self.close.clicked.connect(self.automatic_close)
        self.sensorWorker.sensor_read.connect(self.update_angle)
        
        # Start the read thread
        self.runRead()
        self.sensorRead()
        
    def update_angle(self,angle):
            self.angle = angle
            

        
    def automatic_close(self):
          
          if not self.running == "stop":
                  self.stop_automatic()
                      
          else:
                  self.operateThread = QThread()
                  self.operateWorker = OperateWorker(self.client1, self.read_lock)
                  self.operateWorker.moveToThread(self.operateThread)
                  self.operateThread.started.connect(self.operateWorker.run)
                  self.operateWorker.finished.connect(self.operateThread.quit)
                  self.operateWorker.finished.connect(self.operateWorker.deleteLater)
                  self.operateThread.finished.connect(self.operateThread.deleteLater)
                  self.operateThread.start()
                  self.stopped = False
                  self.running = "closing"
 
          
    def automatic_open(self):
            
            if not self.running == "stop":
                  self.stop_automatic()
                  
            else:
                    self.operateThread = QThread()
                    self.operateWorker = OperateWorker(self.client1, self.read_lock)
                    self.operateWorker.moveToThread(self.operateThread)
                    self.operateThread.started.connect(self.operateWorker.run)
                    self.operateWorker.finished.connect(self.operateThread.quit)
                    self.operateWorker.finished.connect(self.operateWorker.deleteLater)
                    self.operateThread.finished.connect(self.operateThread.deleteLater)
                    self.operateThread.start()
                    self.stopped = False
                    self.running = "opening"
        
          
    def stop_automatic(self):
            
            self.stopped = True
                

    def read_siemens_v20_values(self):
            try:
                time.sleep(0.1)
                frequency = self.client1.read_register(23, functioncode=3)
                time.sleep(0.2)
                current = self.client1.read_register(25, functioncode=3)
                time.sleep(0.2)
                speed = self.client1.read_register(24, functioncode=3)
                
                self.values = {
                    "read_freq": frequency,
                    "read_current": current,
                    "read_speed":  speed
                }
                
                #print(f"Frequency: {frequency} Hz, Current: {current} A, Speed:  {speed}")
                
            except Exception as e:
                print(f"Error reading values from Siemens V20: {e}")
                
    def read_v20multi(self):
        try:
            time.sleep(0.05)    
            registers = self.client1.read_registers(23, 3, functioncode=3)  # Read three registers starting from 23
            frequency = registers[0]
            speed = registers[1]
            current = registers[2]
            
            self.values = {
                "read_freq": frequency,
                "read_current": current,
                "read_speed": speed
            }
            
            #print(f"Frequency: {frequency} Hz, Current: {current} A, Speed: {speed}")
            
        except Exception as e:
            print(f"Error reading values from Siemens V20: {e}")       
            
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

    def runRead(self):
        self.thread = QThread()
        self.readerWorker = ReaderWorker(self.client1, self.read_lock)
        self.readerWorker.moveToThread(self.thread)
        self.thread.started.connect(self.readerWorker.run)
        #self.readerWorker.updated.connect(self.update_actual)
        self.thread.start()
    def sensorRead(self):
        self.thread1 = QThread()
        
        self.sensorWorker.moveToThread(self.thread1)
        self.thread1.started.connect(self.sensorWorker.run)
        #self.readerWorker.updated.connect(self.update_actual)
        self.thread1.start()

    def backward_function(self):
        with QMutexLocker(self.read_lock):  # Acquire the lock
            try:
                time.sleep(0.05)    
                self.client1.write_register(99, 1278, functioncode=6) # reset vfd
                time.sleep(0.1)
                self.client1.write_register(100, mapped_value, functioncode=6) 
                time.sleep(0.1)
                self.client1.write_register(99, 3199, functioncode=6)
                time.sleep(0.05)
                
            except Exception as e:
                print(f"Error: {e}")

    def forward_function(self):
        with QMutexLocker(self.read_lock):  # Acquire the lock
            try:
                time.sleep(0.1)    
                self.client1.write_register(99, 1278, functioncode=6) # reset vfd
                time.sleep(0.1)   
                self.client1.write_register(100, mapped_value, functioncode=6) 
                time.sleep(0.1)
                self.client1.write_register(99, 1151, functioncode=6) 
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error: {e}")

    def stop_function(self):
        with QMutexLocker(self.read_lock):  # Acquire the lock
            try:
                time.sleep(0.1)    
                self.client1.write_register(100, 0, functioncode=6) # freq
                time.sleep(0.1)
                self.client1.write_register(99, 1278, functioncode=6) # reset vfd
                time.sleep(0.1)
                self.client1.write_register(99, 1150, functioncode=6) # Stop
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error: {e}")

    def update_frequency_label(self, value):
        global frequency, mapped_value
        frequency = value
        mapped_value = int((frequency / 50) * 16384)  
        self.frequency.setText(f"{frequency}")

    def update_actual(self):
        self.actual_freq = self.convert_value(self.values['read_freq'])
        self.actual_freq = round(self.actual_freq, 2)
        self.actual_frequency.setText(f"{self.actual_freq}")
        
    def convert_value(self, value):
        if 60536 <= value <= 65337:
            # Mapping from 60536 to 65337 to -50 to 0
            return (value - 60536) * (50 / (65337 - 60536)) - 51
        elif 0 <= value <= 4999:
            # Mapping from 0 to 4999 to 0 to 50 
            return value * (50 / 4999)
            
        else:
            return value
            
    def read_and_average(self,num_samples=1):
        values = []
        for _ in range(num_samples):
            value = self.readAI(0)
            values.append(value)
        average = sum(values) / num_samples
        return average * (90/1220)
        
    def weighted_moving_average(self,avg,value,q=0.1):
        return(avg * ( 1.0 - q)) + (value * q)
        
        
    def calculate_momentum(self, current_speed):
        # Moment of inertia for a rectangular door (rotating about one edge)
        I = (1 / 3) * door_mass * (door_width ** 2)
        angular_velocity = current_speed * (3.14 / 180)  # Convert degrees to radians
        momentum = I * angular_velocity
        
        return momentum

    def adjust_tolerance_based_on_momentum(self, current_speed):
        momentum = self.calculate_momentum(current_speed)
        if momentum > 1000:  # Example threshold, adjust as necessary
            self.tolerance = 5
        elif momentum > 500:  # Example threshold, adjust as necessary
            self.tolerance = 3
        else:
            self.tolerance = 1
            
    def calculate_angular_speed(self, previous_angle, current_angle, time_interval):

        # Calculate the change in angle
        angle_difference = current_angle - previous_angle
        # Calculate the angular speed
        angular_speed = angle_difference / time_interval
        return angular_speed*100
        
    def calculate_speedDX(self, previous_angle, current_angle, time_interval):

        # Calculate the change in angle
        angle_difference = current_angle - previous_angle
        # Calculate the angular speed
        angular_speed = angle_difference / time_interval
        return angular_speed*100             

       


class SensorWorker(QObject):
    sensor_read = pyqtSignal(float)
    
    
    def __init__(self):
        super().__init__()
        self.avg = 0.0

    def run(self):
        previous_angle = 0
        previous_speed = 0
            
        while True:
           start_time = time.time()
           current_angle = round(main_window.read_and_average(20))
           end_time = time.time()
           
           time_interval = end_time - start_time
           time_interval = round(time_interval,10)
           #angular_speed = main_window.calculate_angular_speed(previous_angle, current_angle, time_interval)
          
           
           #speedDx = main_window.calculate_speedDX(previous_speed, angular_speed, time_interval)
           
           
           #previous_speed = angular_speed
           previous_angle = current_angle
           print(current_angle)
           
           
           self.sensor_read.emit(round(current_angle))
           time.sleep(0.01)
           
class OperateWorker(QObject):
    finished = pyqtSignal()
    
    def __init__(self,client,lock):
        super().__init__()
        self.client1 = client
        self.lock = lock

    def run(self):
            
        with QMutexLocker(self.lock):
                
                if main_window.stopped == False and main_window.running == "closing" :   
                        
                        """ RESET VFD"""
                        
                        main_window.client1.write_register(99,1278,functioncode=6) #stop
                        time.sleep(0.1)
                        self.client1.write_register(100, 0, functioncode=6) # zero speed
                        time.sleep(0.1)
                        self.client1.write_register(99, 3199, functioncode=6)   #99 th reg -> 3199 closing side 
                        time.sleep(0.1)
                        
                        """closıng"""
                        
                   
                        while main_window.stopped == False and main_window.angle > 0:
                                   print(main_window.angle)
                                   #7800 = 25hz 4680 = 15
                                
                                   if main_window.angle >= 60:
                                        self.client1.write_register(100, 7000, functioncode=6) 
                                        time.sleep(0.1)
                                   if 30 <= main_window.angle < 60:
                                      self.client1.write_register(100, 6000, functioncode=6) 
                                   if 20 <= main_window.angle < 30:
                                      self.client1.write_register(100, 5800, functioncode=6) 
                                   if 10 <= main_window.angle < 20:
                                      self.client1.write_register(100, 5000, functioncode=6) 
                                   if 0 <= main_window.angle < 10:
                                      self.client1.write_register(100, 2500, functioncode=6) 
                                   if main_window.angle < 2:
                                        time.sleep(0.1)    
                                        self.client1.write_register(100, 0, functioncode=6) # freq
                                        time.sleep(0.1)
                                        self.client1.write_register(99, 1278, functioncode=6) # reset vfd
                                        time.sleep(0.1)
                                        self.client1.write_register(99, 1150, functioncode=6) # Stop
                                        time.sleep(0.1)
                        
                        time.sleep(0.1)
                           
                        self.client1.write_register(100, 0, functioncode=6) # freq
                        time.sleep(0.1)
                        self.client1.write_register(99, 1278, functioncode=6) # reset vfd
                        time.sleep(0.1)
                        self.client1.write_register(99, 1150, functioncode=6) # Stop
                        time.sleep(0.1)
                        
                if main_window.stopped == False and main_window.running == "opening":   
                        
                        main_window.client1.write_register(99,1278,functioncode=6)
                        time.sleep(0.1)
                        self.client1.write_register(100, 0, functioncode=6) 
                        time.sleep(0.1)
                        self.client1.write_register(99, 1151, functioncode=6)   
                        time.sleep(0.1)
                   
                        while main_window.stopped == False and main_window.angle <85 and  main_window.running == "opening":
                                   print(main_window.angle)
                                   #7800 = 25hz 4680 = 15
                                   if 80 <= main_window.angle < 85:
                                      self.client1.write_register(100, 3000, functioncode=6) 
                       
                                   if 60 <= main_window.angle < 80:
                                      self.client1.write_register(100, 5000, functioncode=6) 
                                      
                                   if 10 < main_window.angle < 60:
                                      self.client1.write_register(100, 6000, functioncode=6) 
                                     
                                   if 0 < main_window.angle < 10:
                                      self.client1.write_register(100, 5000, functioncode=6) 
                                   
                        
                        time.sleep(0.1)
                           
                        self.client1.write_register(100, 0, functioncode=6) # freq
                        time.sleep(0.1)
                        self.client1.write_register(99, 1278, functioncode=6) # reset vfd
                        time.sleep(0.1)
                        self.client1.write_register(99, 1150, functioncode=6) # Stop
                        time.sleep(0.1)
                        
                        
                        
                main_window.stopped == True
                main_window.running = "stop"
                print("bye",main_window.angle)
                self.finished.emit()
           
           
class ReaderWorker(QObject):
    updated = pyqtSignal()
    
    
    def __init__(self, client, lock):
        super().__init__()
        self.client = client
        self.lock = lock

    def run(self):
        while True:
           with QMutexLocker(self.lock):  # Acquire the lock
                #main_window.read_v20multi()
                
                self.updated.emit()  # Release the lock when the with block ends
                time.sleep(0.05)
           

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
