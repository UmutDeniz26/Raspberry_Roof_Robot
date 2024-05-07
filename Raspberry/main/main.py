import socket
import json

import sys
sys.path.insert(1, 'Tests/Communication_Arduino')
import Raspberry_side as rasp

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5000     

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))  
    s.listen()            
    print(f"Server is listening on {HOST}:{PORT}...")

    while True:
        conn, addr = s.accept()  
        with conn:
            print(f"Connected from {addr}")
            
            message = "this is a gps data"
            conn.sendall(message.encode('utf-8'))
            
            while True:
                data = conn.recv(1024) 
                if not data:
                    break
                
                data_string = data.decode('utf-8')

                # Encode as JSON
                json_data = json.loads(data_string)

                response_ard = rasp.transmit_receive_arduino_message(json_data, 5)
                print(f"Data received from Arduino: {response_ard}")
                print(f"Received data: {data}")

                conn.sendall(data)
