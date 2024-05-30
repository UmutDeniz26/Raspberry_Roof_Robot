import RPi.GPIO as GPIO
import time

control = [5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10]

melody = [
    5, -4, 5, -4, 5, 16, 5, 16, 5, 16, 5, 16, 5, 8, None, 8,
    5, -4, 5, -4, 5, 16, 5, 16, 5, 16, 5, 16, 5, 8, None, 8,
    5, 4, 5, 4, 5, 4, 6, -8, 6, 16,

    5, 4, 6, -8, 6, 16, 5, 2,  # 4
    7, 4, 7, 4, 7, 4, 8, -8, 6, 16,
    5, 4, 6, -8, 6, 16, 5, 2,

    8, 4, 5, -8, 5, 16, 8, 4, 9, -8, 9, 16,  # 7
    10, 16, 9, 16, 9, 8, None, 8, 5, 8, 9, 4, 9, -8, 8, 16,

    7, 16, 6, 16, 7, 16, None, 8, 5, 8, 6, 4, 5, -8, 6, -16,  # 9
    7, 4, 5, -8, 7, 16, 7, 2,

    8, 4, 5, -8, 5, 16, 8, 4, 9, -8, 9, 16,  # 7
    10, 16, 9, 16, 9, 8, None, 8, 5, 8, 9, 4, 9, -8, 8, 16,

    7, 16, 6, 16, 7, 16, None, 8, 5, 8, 6, 4, 5, -8, 6, -16,  # 9
    5, 4, 5, -8, 6, 16, 5, 2,
]

servo = 22

GPIO.setmode(GPIO.BOARD)

GPIO.setup(servo,GPIO.OUT)
# in servo motor,
# 1ms pulse for 0 degree (LEFT)
# 1.5ms pulse for 90 degree (MIDDLE)
# 2ms pulse for 180 degree (RIGHT)

# so for 50hz, one frequency is 20ms
# duty cycle for 0 degree = (1/20)*100 = 5%
# duty cycle for 90 degree = (1.5/20)*100 = 7.5%
# duty cycle for 180 degree = (2/20)*100 = 10%

p=GPIO.PWM(servo,50)# 50hz frequency

p.start(2.5)# starting duty cycle ( it set the servo to 0 degree )


try:
    while True:
        for x in range(11):
            p.ChangeDutyCycle(control[x])
            time.sleep(1.03)
            print (x)

        for x in range(9,0,-1):
            p.ChangeDutyCycle(control[x])
            time.sleep(1.03)
            print (x)

except KeyboardInterrupt:
    GPIO.cleanup()
    