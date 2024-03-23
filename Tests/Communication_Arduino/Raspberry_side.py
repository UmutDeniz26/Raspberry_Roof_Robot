#!/usr/bin/env python3
import serial
import time

def transmit_receive_arduino_message( message, wait_delay = 0 ):

    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Open serial port
    ser.flushInput()  # To clear the input buffer
    
    #ser.write(b"{}\n".format(message).encode('utf-8'))  # Send message to Arduino
    ser.write(message.encode('utf-8'))  

    # Wait for the Arduino to process the message
    if wait_delay > 0:
        hold_time = time.time()
        # if wait_delay is 1000 then it will wait for 1 second
        while time.time() - hold_time < wait_delay:
            line = ser.readline().decode('utf-8').rstrip()
            if line:
                print("Message taken while waiting.")
                break
    
    if not line:
        line = ser.readline().decode('utf-8').rstrip()
        print("Message taken after waiting.")

    if line:
        recieved = line
    else:
        recieved = {"error": "No response from Arduino"}
    
    ser.close()

    return recieved


if __name__ == '__main__':
    print("Use main function to send message to Arduino")