import socket
import sys
#import json
#sys.path.insert(1, 'Tests/Communication_Arduino')
#import Raspberry_side as rasp

HOST = '192.168.223.203'  
PORT = 5000     

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))  
    s.listen()            
    print(f"Sunucu {HOST}:{PORT} üzerinde dinleniyor...")

    while True:
        conn, addr = s.accept()  
        with conn:
            print(f"{addr} adresinden bağlanıldı")
            #message = "bu bir gps verisidir"
            #conn.sendall(message.encode('utf-8'))
            while True:
                data = conn.recv(1024) 
                if not data:
                    break
                
                #data_string = data.decode('utf-8')

                # Encode as JSON
                #json_data = json.loads(data_string)

                #response_ard = rasp.transmit_receive_arduino_message( json_data, 5)
                #print(f"Arduino'dan gelen veri: {response_ard}")
                print(f"Alınan veri: {data}")

                conn.sendall(data)
