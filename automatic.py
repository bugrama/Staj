import time
import threading 
import anqle

class Automatic():
	
	def __init__(self,shouldStop,WriteV20,SensorWorker,ReadV20,MainExecuter):
        
		
		self.shouldStop = shouldStop
		self.writer=WriteV20
		self.sensor=SensorWorker
		self.sensorV20=ReadV20
		self.carpan=1
		#self.angle=self.sensor.angle_current*self.carpan
		self.fark=0
		
		self.mainex=MainExecuter
		self.stopCheckTime = 10
		self.old_freq=0
		self.flag= False
		
		self.thread = threading.Thread(target = self.ayarla,)
		self.thread.start()
	def Move(self,direction):
		
		self.writer._vfdReset()
		
		if direction =="stop":
			#reset
			print("stop-----------")
			self.mainex.condition = "stop"
			self.old_freq=0
			self.shouldStop =True
			self.writer.stop()
			
			timer=threading.Timer(self.stopCheckTime,self.writer.checkstop,args=(self.mainex,self.sensorV20,))
			timer.start()
			
			
		elif direction =="close":
			#reset
			print("kapanıo------------------")
			self.mainex.condition="closing"
			self.shouldStop = False
			
			self.mainex.shouldStop = False
			
		
			while self.angle > 0 and self.mainex.shouldStop == False :
				
				
				if self.angle >= 60  :
					
					time.sleep(0.1)
					if self.old_freq!=7000:
						self.writer.writeOperation(7000,"backward")
						self.old_freq=7000
					
					
				elif 30 <= self.angle < 60 :
					time.sleep(0.1)
					if self.old_freq!=6000:
						self.writer.writeOperation(6000,"backward")
						self.old_freq=6000
					
					
				elif 20 <= self.angle < 30 :
					time.sleep(0.1)
					if self.old_freq!=5800:
						self.writer.writeOperation(5800,"backward")
						self.old_freq=5800
					
					
				elif 10 <= self.angle < 20 :
					time.sleep(0.1)
					if self.old_freq!=5000:
						self.writer.writeOperation(5000,"backward")
						self.old_freq=5000
					
					
				elif 2 <= self.angle < 10:
					#time.sleep(0.1)
					
					if self.old_freq!=2500:
						self.writer.writeOperation(2500,"backward")
						self.old_freq=2500
					
					
				elif self.angle < 2:
					#time.sleep(0.1)
					#self.Move("stop")
					self.writer.stop()
					print("geldim")
			print("closing exit")
			self.writer.stop()
				

		elif direction == "open":
			#reset
			print("acılıyor-------------")
			self.mainex.condition="opening"
			self.shouldStop = False
			
			self.mainex.shouldStop = False
			
			while self.angle < 85 and self.mainex.shouldStop == False:
				
				
				if 80 <= self.angle < 85:
					time.sleep(0.1)
					if self.old_freq!=3000:
						self.writer.writeOperation(3000,"forward")
						self.old_freq=3000
				elif 60 <= self.angle < 80:
					time.sleep(0.1)
					if self.old_freq!=5800:
						self.writer.writeOperation(5000,"forward") 
						self.old_freq=5800
				elif 10 <= self.angle < 60:
					time.sleep(0.1)
					if self.old_freq!=6000:
						self.writer.writeOperation(6000,"forward")
						self.old_freq=6000
				elif 0 <= self.angle < 10:
					
					time.sleep(0.1)
					if self.old_freq!=5000:
						self.writer.writeOperation(5000,"forward")
						self.old_freq=5000 
				
			print("opening exit")
			self.writer.stop()
			#self.Move("stop")
			
			
	def ayarla(self,):
		while True:
			
			self.angle=self.sensor.angle_current*self.carpan
			
	def konum_ayar(self,konum):
		if konum =="acilma":
			if self.sensor.angle_current<360:
				self.fark=self.sensor.angle_current
				self.sensor.ayarla(self.fark)
		else:
			if self.sensor.angle_current>=30:
				self.carpan=90/self.sensor.angle_current
			else:
				print("daha büyük iste")
