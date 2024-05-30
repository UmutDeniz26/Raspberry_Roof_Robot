#Include the library files
import RPi.GPIO as GPIO
from gpiozero import AngularServo
from time import sleep


# Include the servo motor pin
servoPin = 18

# Create an object for the servo motor
servo = AngularServo(servoPin,min_angle=0,max_angle=180,min_pulse_width=0.0005,max_pulse_width=0.0025)

while True:
    for i in range(0,180,10):
        # Rotate the servo motor using analog values
        servo.angle = i
        sleep(0.5)
        print(i)

