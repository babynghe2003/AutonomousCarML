from RPi import GPIO
import time
from l298n import Motor

motor = Motor()

while True:
    print("forward")
    motor.setMotor(30,30)
    time.sleep(1)
    motor.setMotor(-30,-30)
    time.sleep(1)