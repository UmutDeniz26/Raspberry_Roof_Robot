import RPi.GPIO as GPIO
import time


melody = [
  
  # Dart Vader theme (Imperial March) - Star wars 
  # Score available at https://musescore.com/user/202909/scores/1141521
  # The tenor saxophone part was used
  
  5.0, 5.0, 5.0, 5.0, 5.0, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 7.5, 10.0, 7.5,
  5.0, 5.0, 5.0, 5.0, 5.0, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 7.5, 10.0, 7.5,
  5.0, 5.0, 5.0, 7.5, 5.0, 10.0,

  5.0, 7.5, 5.0, 10.0, 7.5, 5.0, 5.0, 5.0, 7.5, 5.0, 10.0,
  5.0, 5.0, 5.0, 7.5, 5.0, 10.0, 7.5, 5.0, 5.0, 5.0, 7.5, 5.0, 10.0,

  5.0, 5.0, 5.0, 5.0, 6.25, 6.25, 6.25, 7.5, 10.0, 7.5,
  5.0, 5.0, 5.0, 5.0, 5.0, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 7.5, 10.0, 7.5,
  5.0, 5.0, 5.0, 7.5, 5.0, 10.0,

  5.0, 5.0, 5.0, 5.0, 6.25, 6.25, 6.25, 7.5, 10.0, 7.5,
  5.0, 5.0, 5.0, 5.0, 5.0, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 7.5, 10.0, 7.5,
  5.0, 5.0, 5.0, 7.5, 5.0, 10.0,
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
        for x in melody:
            p.ChangeDutyCycle(x)
            time.sleep(1.03)


except KeyboardInterrupt:
    GPIO.cleanup()
    