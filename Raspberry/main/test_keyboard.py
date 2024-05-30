import socket
import sys
import time
import re
import keyboard
import select

HOST = "192.168.1.13"
PORT = 5000


def dict_creater(type_, command, X=0.0, Y=0.0, speed=0.0):
    ret = "{\"Type\": \"" + type_ + "\", \"Command\": \"" + command + "\"," + "\"X\": " + str(X) + ", \"Y\": " + str(Y) + ", \"Speed\": " + str(speed) + "}"
    return ret

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.setblocking(False)  # Set the socket to non-blocking mode
        print(f"Connected to {HOST}:{PORT}\n")
        print("Press 'w' to move forward, 's' to move backward, 'a' to move left, 'd' to move right, 'e' to exit.")
        time.sleep(1)

        last_message = ""
        x = 0.0
        y = 0.0
        time_start = time.time()
        while True:
            message = None
            
            if keyboard.is_pressed('s'):
                y = y-0.1 if y-0.1>-1 else -1.0
            elif keyboard.is_pressed('w'):
                y = y+0.1 if y+0.1<1 else 1.0
            elif keyboard.is_pressed('d'):
                x = x+0.1 if x+0.1<1 else 1.0
            elif keyboard.is_pressed('a'):
                x = x-0.1 if x-0.1>-1 else -1.0
            elif keyboard.is_pressed('e'):
                return
            elif keyboard.is_pressed('g'):
                message = dict_creater("gps", "get")
                time.sleep(0.2)
            else:
                message = dict_creater("robot_move", "stop")

            if message == None:
                message = dict_creater("robot_move", "move", x, y, 255.0)
                time.sleep(0.1)

            if message == last_message:
                time.sleep(0.05)
                continue

            last_message = message

            s.sendall(message.encode('utf-8'))
            
            # Wait for data with a timeout
            ready = select.select([s], [], [], 0.5)
            if ready[0]:
                data = s.recv(4096).decode('utf-8')
                if message == dict_creater("gps", "get", []):
                    s.sendall("\n".encode('utf-8'))
                    data += s.recv(4096).decode('utf-8')

                print(f"\nSent data: {message}")
                print("Received data: ", data)

if __name__ == "__main__":
    main()
