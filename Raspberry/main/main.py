import socket
import json
import subprocess
import errno
import time
import sys
sys.path.insert(1,"Raspberry/others")

import get_available_stream # type: ignore
import Send_message as rasp


def main():

    HOST, PORT = get_available_stream.get_host_ip_and_port()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))  
        s.listen()            
        print(f"Server is listening on {HOST}:{PORT}...")
        
        while True:
            conn, addr = s.accept()  
            with conn:
                print(f"Connected from {addr}")
                
                # Receive data from the client
                while True:
                    try:
                        data = conn.recv(1024)
                        conn.sendall(data)
                        
                        if not data:
                            break

                    except ConnectionResetError:
                        print("Connection was reset by the client")
                        break
                    
                    data_string = data.decode('utf-8')

                    # Encode as JSON
                    try:
                        json_data = json.loads(data_string)
                        time_start = time.time()
                        response_ard = rasp.transmit_receive_arduino_message(json_data, 5)
                        print(f"Time taken to send and receive data from Arduino: {time.time() - time_start}")
                        
                        print(f"Data received from Arduino: {response_ard}")
                    except Exception as e:
                        print("Error decoding JSON or sending message : ", data_string)
                        print(e)
                        continue
                    

main()