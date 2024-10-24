import RPi.GPIO as GPIO  
from time import sleep     # this lets us have a time delay (see line 15)  
GPIO.setmode(GPIO.BOARD)     # set up BCM GPIO numbering  
GPIO.setup(11, GPIO.IN)
GPIO.setup(7, GPIO.IN)  
GPIO.setup(13, GPIO.IN)      # set GPIO25 as input (button)  
GPIO.setup(31, GPIO.OUT) 
GPIO.setup(29, GPIO.OUT) 
GPIO.setup(33, GPIO.OUT)   # set GPIO24 as an output (LED)  
from threading import Thread


class Buttons():
    
    def __init__(self):
        self.flag=False
        self.data=""
        self.thread = Thread(target = self.work)
        self.thread.start()


    def work(self):
        try:  
            while True:            # this will carry on until you hit CTRL+C  
                if GPIO.input(11): # if port 25 == 1 close
                    self.flag=True                    
                    self.data="close" 
                    #self.flag=False
                    GPIO.output(31, 1)         # set port/pin value to 1/HIGH/True  
                else:  
                    
                    GPIO.output(31, 0)         # set port/pin value to 0/LOW/False  
                sleep(0.1)         # wait 0.1 seconds  
                if GPIO.input(7): # if port 25 == 1 durr
                    self.flag=True  
                    self.data="stop"                    
                    #self.flag=False
                    GPIO.output(29, 1)         # set port/pin value to 1/HIGH/True  
                else:  
                    
                    GPIO.output(29, 0)         # set port/pin value to 0/LOW/False  
                sleep(0.1)         # wait 0.1 seconds  
                if GPIO.input(13): # if port 25 == 1 acc
                    self.flag=True  
                    self.data="open"
                    #self.flag=False 
                    GPIO.output(33, 1)         # set port/pin value to 1/HIGH/True  
                else:  
                     
                    GPIO.output(33, 0)         # set port/pin value to 0/LOW/False  
                sleep(0.1)         # wait 0.1 seconds  
          
        finally:
            self.flag=False                   # this block will run no matter how the try block exits  
            GPIO.cleanup()  
