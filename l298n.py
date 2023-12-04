# motor controller for l298n and raspberry pi
from RPi import GPIO
import time

class Motor():
    def __init__(self, in1=13,in2=12,ena=6,in3=21,in4=20,enb=26) -> None:
        self.IN1= in1
        self.IN2 = in2
        self.ENA= ena
        self.IN3= in3
        self.IN4= in4
        self.ENB= enb
    
        GPIO.setmode(GPIO.BCM)
 
        GPIO.setwarnings(False)
 
        GPIO.setup(self.IN1,GPIO.OUT)
 
        GPIO.setup(self.IN2,GPIO.OUT)
 
        GPIO.setup(self.IN3,GPIO.OUT)
 
        GPIO.setup(self.IN4,GPIO.OUT)
 
        GPIO.setup(self.ENA,GPIO.OUT)
 
        GPIO.setup(self.ENB,GPIO.OUT)
 
        self.stop()
 
        self.PWMA = GPIO.PWM(self.ENA,1000)
 
        self.PWMB = GPIO.PWM(self.ENB,1000)
 
        self.PWMA.start(50)
 
        self.PWMB.start(50)

    def stop(self):
        GPIO.output(self.IN1,GPIO.LOW)
 
        GPIO.output(self.IN2,GPIO.LOW)
 
        GPIO.output(self.IN3,GPIO.LOW)
 
        GPIO.output(self.IN4,GPIO.LOW)
    def forward(self, speedA, speedB):
        MAX_SPEED = 40
        MIN_SPEED = 0
        
        if speedA > MAX_SPEED:
            speedA = MAX_SPEED
        if speedA < MIN_SPEED:
            speedA = MIN_SPEED
        
        if speedB > MAX_SPEED:
            speedB = MAX_SPEED
        if speedB < MIN_SPEED:
            speedB = MIN_SPEED
            
        GPIO.output(self.IN1,GPIO.LOW)
 
        GPIO.output(self.IN2,GPIO.HIGH)

        self.PWMA.ChangeDutyCycle(speedA)
        
        GPIO.output(self.IN3,GPIO.LOW)
 
        GPIO.output(self.IN4,GPIO.HIGH)

        self.PWMB.ChangeDutyCycle(speedB)
        
    def setMotor(self, speedA, speedB):
        if speedA > 100:
            speedA = 100
        elif speedA < -100:
            speedA = -100

        if speedB > 100:
            speedB = 100
        elif speedB < -100:
            speedB = -100

        if speedA > 0:
            GPIO.output(self.IN1,GPIO.LOW)
 
            GPIO.output(self.IN2,GPIO.HIGH)
 
            self.PWMA.ChangeDutyCycle(speedA)
 
        else:
            GPIO.output(self.IN1,GPIO.HIGH)
 
            GPIO.output(self.IN2,GPIO.LOW)
 
            self.PWMA.ChangeDutyCycle(-speedA)
 
        if speedB > 0:
            GPIO.output(self.IN3,GPIO.LOW)
 
            GPIO.output(self.IN4,GPIO.HIGH)
 
            self.PWMB.ChangeDutyCycle(speedB)
 
        else:
            GPIO.output(self.IN3,GPIO.HIGH)
 
            GPIO.output(self.IN4,GPIO.LOW)
 
            self.PWMB.ChangeDutyCycle(-speedB)

