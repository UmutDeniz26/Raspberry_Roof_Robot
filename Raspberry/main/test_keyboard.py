
import socket
import sys
import time
import re
import keyboard

HOST = "192.168.1.13"
PORT = 5000

speed = 255

def dict_creater(type_, command, value):
    return "{\"Type\": \"" + type_ + "\", \"Command\": \"" + command + "\", \"Value\": " + str(value) + "}\n"

def main():
    global speed
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")
        print("Press 'w' to move forward, 's' to move backward, 'a' to move left, 'd' to move right, 'q' to stop.")
        time.sleep(1)

        last_message = ""
        while True:

            #Get keyboard key

            if keyboard.is_pressed('+'):
                message = "inc_speed"

            elif keyboard.is_pressed('-'):
                message = "dec_speed"

            elif keyboard.is_pressed('s'):
                message = dict_creater("robot_move", "forward", speed)

            elif keyboard.is_pressed('w'):
                message = dict_creater("robot_move", "backward", speed)

            elif keyboard.is_pressed('d'):
                message = dict_creater("robot_move", "left", speed)

            elif keyboard.is_pressed('a'):
                message = dict_creater("robot_move", "right", speed)

            elif keyboard.is_pressed('e'):
                return
            elif keyboard.is_pressed('g'):
                #GPS
                message = dict_creater("gps", "get", 0)
                time.sleep(1)
            else:
                message = dict_creater("robot_move", "stop", speed)

            if message == last_message:
                continue

            last_message = message
                
            if message == "dec_speed":
                if speed-20 >= 0:
                    speed -= 20
                else:
                    speed = 0                    
                continue
            elif message == "inc_speed":
                if speed+20 <= 255:
                    speed += 20
                else:
                    speed = 255
                continue

            s.sendall(message.encode('utf-8'))
            data = s.recv(4096).decode('utf-8')
            if message == dict_creater("gps", "get", 0):
                s.sendall("\n".encode('utf-8'))
                data += s.recv(4096).decode('utf-8')

            print(f"\nSent data: {message}")
            print("Received data: ", data)




if __name__ == "__main__":
    main()