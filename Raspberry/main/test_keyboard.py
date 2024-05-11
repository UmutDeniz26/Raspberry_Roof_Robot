
import socket
import sys
import time
import re
import keyboard

HOST = "192.168.1.89"
PORT = 5000

test_data_array = [
    "{\"Type\": \"robot_move\", \"Command\": \"forward\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"backward\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"left\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"right\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"stop\"}",
    #"{\"Type\": \"gps\",\"Command\": \"get_data\"}"
]


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")
        print("Press 'w' to move forward, 's' to move backward, 'a' to move left, 'd' to move right, 'q' to stop.")
        time.sleep(1)

        last_message = ""
        while True:

            #Get keyboard key
            if keyboard.is_pressed('w'):
                message = test_data_array[0]

            elif keyboard.is_pressed('s'):
                message = test_data_array[1]

            elif keyboard.is_pressed('a'):
                message = test_data_array[2]

            elif keyboard.is_pressed('d'):
                message = test_data_array[3]

            elif keyboard.is_pressed('e'):
                return
            
            else:
                message = test_data_array[4]

            if message == last_message:
                continue

            last_message = message

            s.sendall(message.encode('utf-8'))
            data = s.recv(2048).decode('utf-8')

            print(f"\nSent data: {message}")
            print("Received data: ", data)




if __name__ == "__main__":
    main()