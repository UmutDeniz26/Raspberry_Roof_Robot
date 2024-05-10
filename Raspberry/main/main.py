import socket
import json
import subprocess
import errno
import time
import sys

sys.path.insert(0,"Raspberry")
from Raspberry.others import Stream_operations
from others import Common

from server_operations import Send_message as rasp

class Raspberry_Server:
    """
        A class to represent a Raspberry Pi server.
    """

    def __init__(self,echo_server:bool) -> None:
        
        # Set attributes
        self.ECHO_SERVER = echo_server # Echo server -> Sends the data back to the client
        

    def init_server(self,HOST: int, PORT: int) -> None:
        """
            Initialize the server.

            Args:
                HOST (str): The IP address to bind the server to.
                PORT (int): The port to bind the server to.
        """
        # Set the port and host
        self.PORT = PORT;self.HOST = HOST

        # Create a socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # The one liner : bind() to own address, connect() to remote address.
        self.socket.bind((HOST, PORT))
        
        # Listen for incoming connections
        self.socket.listen()

        print(f"Server is listening on {self.HOST}:{self.PORT}...")


    def send_str_message(self, message: str) -> None:
        """
            Send a string message to the client.

            Args:
                message (str): The message to send to the client.
        """
        self.socket.sendall(message.encode('utf-8'))

    def main_loop(self) -> None:
        """
            Wait for a connection from a client and send a message to the client.
        """
        while True:
            conn, addr = self.socket.accept()
            with conn:
                print(f"Connected from {addr}")
                
                # Receive data from the client
                while True:
                    try:
                        data_received = conn.recv(1024) # 1024 is the buffer size in bytes
                        if not data_received:
                            break
                    except ConnectionResetError:
                        print("Connection was reset by the client")
                        break
                    
                    # Send the data back to the client ( Optional ) ( Echo server )
                    conn.sendall(data_received) if self.ECHO_SERVER else None

                    # Decode the data
                    data_received_string = data_received.decode('utf-8')

                    # Encode as JSON
                    json_data = Common.get_json_format(data_received_string)
                    
                    # Sending the message to the Arduino
                    time_start = time.time()
                    response_from_arduino = rasp.transmit_receive_arduino_message(json_data, 5)
                    print(f"Time taken to send and receive data from Arduino: {time.time() - time_start}")
                    
                    # Print the response
                    print(f"Data received from Arduino: {response_from_arduino}")
                
            

    def __del__(self) -> None:
        """
            Destructor.
        """
        # Close the socket
        self.socket.close()


def main():

    # Get the IP address and port
    HOST, PORT = Stream_operations.get_host_ip_and_port()

    server = Raspberry_Server()
    server.init_server(HOST, PORT)
    server.main_loop()

if __name__ == "__main__":
    main()