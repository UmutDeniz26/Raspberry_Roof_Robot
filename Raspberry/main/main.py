import socket
import json
import subprocess
import asyncio
import sys
import os
import errno

sys.path.insert(1, 'Tests/Communication_Arduino')
import Raspberry_side as rasp

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                return True
            else:
                raise
    return False

# Weak function to get the host IP. It only works for the Raspberry Pi.
def get_host_ip_and_port():
    try:
        # Run the ifconfig command to get network interface information
        result = subprocess.run(['ifconfig', 'wlan0'], capture_output=True, text=True)
        # Extract the IP address from the command output
        ip_address = result.stdout.split('inet ')[1].split(' ')[0]

        host = 5000
        while is_port_in_use(host):
            host += 1
        
        return ip_address, host
    except Exception as e:
        print(f"Error getting host IP and Port: {e}")
        return None

def main():

    HOST, PORT = get_host_ip_and_port()
    
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
                    except ConnectionResetError:
                        print("Connection was reset by the client")
                        break
                    
                    data_string = data.decode('utf-8')

                    # Encode as JSON
                    try:
                        json_data = json.loads(data_string)
                        #response_ard = rasp.transmit_receive_arduino_message(json_data, 5)
                        #print(f"Data received from Arduino: {response_ard}")
                    except:
                        print("Error decoding JSON")
                        continue
                    

main()