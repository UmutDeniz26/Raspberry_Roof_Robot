import RPi.GPIO as GPIO
import time

servoPIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

pwm = GPIO.PWM(servoPIN, 50) 
pwm.start(0)

def setAngle(angle):
    x = (1/180) * angle + 1
    duty = x * 5
    pwm.ChangeDutyCycle(duty)

try:
    while True:
        
        for i in range(0, 181, 45):
            print("angle = ", i)
            setAngle(i)
            time.sleep(1)
            
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
