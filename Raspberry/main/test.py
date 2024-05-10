import socket
import sys
import time
import json

sys.path.insert(1, '.')
from Others.timer import Timer

HOST = "192.168.1.13"
PORT = 5000

test_data_array = [
    "{\"Type\": \"robot_move\", \"Command\": \"forward\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"backward\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"left\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"right\"}",
    "{\"Type\": \"robot_move\", \"Command\": \"stop\"}",
    #"{\"Type\": \"gps\",\"Command\": \"get_data\"}"
]

avg_bit_length = sum([ sys.getsizeof(data) for data in test_data_array ]) / len(test_data_array)
print("Average bit size of test_data_array:", avg_bit_length, "bits")


# Sends message to the server
def send_message_to_server(loop_cnt=1):
    print(f"Connected to {HOST}:{PORT}")

    timer = Timer()
    hold_data = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        for i in range(loop_cnt):

            timer.start_new_timer("send_message_to_server")

            message = test_data_array[i % len(test_data_array)]# if i %2 == 0 else test_data_array[-1]
            s.sendall(message.encode('utf-8'))
            data = s.recv(1024).decode('utf-8')
            print(f"\nSent data: {message}")
            print(f"Received data: {data}")
            time.sleep(0.8)

            """
            if (hold_data+1)%test_data_len != json.loads(data)["data"] and hold_data != 0:
                print(f"Error: {(hold_data+1)%100} != {json.loads(data)['data']}")
                break
            hold_data = json.loads(data)["data"]
            """
            timer.stop_timer("send_message_to_server")
        timer.print_timers()



if __name__ == "__main__":
    send_message_to_server(50)
    