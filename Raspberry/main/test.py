import socket
import sys
import time

HOST = "192.168.1.13"
PORT = 5000

test_data_array = [
    "{\"Type\": \"robot_move\", \"Command\": \"forward\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"backward\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"left\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"right\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"stop\"}",
    "{\"Type\": \"gps\",\"Command\": \"get_data\"}"
]



# Sends message to the server
def send_message_to_server(loop_cnt=1):
    print(f"Connected to {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        for i in range(loop_cnt):
            message = test_data_array[i % len(test_data_array)]
            s.sendall(message.encode('utf-8'))
            data = s.recv(1024)
            print(f"Received data: {data.decode('utf-8')}")

            time.sleep(1)


if __name__ == "__main__":
    send_message_to_server(500)
    