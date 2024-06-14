import socket
import sys
import time
import re
import keyboard
import select

HOST = "192.168.32.243"
PORT = 5001


def dict_creater(input_dict):

    if input_dict["Type"] == "gps":
        ret = "{\"Type\": \"" + input_dict["Type"] + "\", \"Command\": \"" + input_dict["Command"] + "\"}\n"
        
    elif input_dict["Type"] == "robot_move":
        ret = "{\"Type\": \"" + input_dict["Type"] + "\", \"Command\": \"" + input_dict["Command"] + "\"," + "\"X\": " 
        + str(input_dict["X"]) + ", \"Y\": " + str(input_dict["Y"]) + "}\n"
        
    elif input_dict["Type"] == "camera_move":
        ret = "{\"Type\": \"" + input_dict["Type"] + "\", \"Command\": \"" + input_dict["Command"] + "\"," + "\"axis\": " 
        + str(input_dict["axis"]) + ", \"direction\": " + str(input_dict["direction"]) + "}\n"

    return ret

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.setblocking(False)  # Set the socket to non-blocking mode
        print(f"Connected to {HOST}:{PORT}\n")
        print("Press 'w' to move forward, 's' to move backward, 'a' to move left, 'd' to move right, 'e' to exit.")
        time.sleep(1)

        hold_message = ""
        hold_X = 0.0
        hold_Y = 0.0
        x = 0.0
        y = 0.0

        while True:
            message = None
            key = ''
            
            # Motor Controls
            if keyboard.is_pressed('s'):
                y = -1#y-0.1 if y-0.1>-1 else -1.0
                key = 's'
            elif keyboard.is_pressed('w'):
                y = 1#y+0.1 if y+0.1<1 else 1.0
                key = 'w'
            elif keyboard.is_pressed('d'):
                x = x+0.1 if x+0.1<1 else 1.0
                x = 0 if x<0 else x
                y = 0
                key = 'd'
            elif keyboard.is_pressed('a'):
                x = x-0.1 if x-0.1>-1 else -1.0
                x = 0 if x>0 else x
                y = 0
                key = 'a'

            # GPS Controls
            elif keyboard.is_pressed('g'):
                key = 'g'
                message = dict_creater("gps", "get")
            
            # Camera Controls
            elif keyboard.is_pressed('z'):
                key = 'z'
                message = dict_creater("camera_move", "move", 0, 1)
            elif keyboard.is_pressed('x'):
                key = 'x'
                message = dict_creater("camera_move", "move", 0, 0)
            elif keyboard.is_pressed('c'):
                key = 'c'
                message = dict_creater("camera_move", "move", 1, 1)
            elif keyboard.is_pressed('v'):
                key = 'v'
                message = dict_creater("camera_move", "move", 1, 0)

            # Exit
            elif keyboard.is_pressed('q'):
                key = 'q'
                print("Exiting from the server...")
                s.close()
                return
            else:
                message = dict_creater("robot_move", "stop", x, y)

            if message == None:
                message = dict_creater("robot_move", "move", x, y)
                time.sleep(0.1)

            if (hold_X == x and hold_Y == y) and hold_message == message:
                time.sleep(0.03)
                continue
            else:
                time.sleep(0.1)
            print(f"X: {x}, Y: {y}", "Message: ", message)

            hold_X = x
            hold_Y = y
            hold_message = message

            s.sendall(message.encode('utf-8'))

            if key == 'g':
                time.sleep(1)
            
            # Wait for data with a timeout
            ready = select.select([s], [], [], 0.5)
            if ready[0]:
                data = s.recv(4096).decode('utf-8')

                print(f"\nSent data: {message}")
                print("Received data: ", data)

if __name__ == "__main__":
    main()
