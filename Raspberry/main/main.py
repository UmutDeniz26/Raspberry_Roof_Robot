import socket
import serial
import math
import time
import sys

sys.path.insert(0,"Raspberry")
sys.path.insert(0,".")
from Raspberry.others import Stream_operations
from others import Common
from server_operations import Send_message as rasp

class Raspberry_Server:
    """
        A class to run the server on the Raspberry Pi.
    """
    def __init__(self,echo_server:bool, wait_response:bool, time_out_limit:int) -> None:
        
        # Set attributes
        self.ECHO_SERVER = echo_server # Echo server -> Sends the data back to the client
        self.WAIT_REPONSE_FROM_ARDUINO = wait_response # Wait for a response from the Arduino
        self.WAIT_REPONSE_TIMEOUT_LIMIT = time_out_limit # Time out limit for the response from the Arduino
        

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

    def init_serial_port(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

    def send_str_message_on_socket(self, message: str) -> None:
        self.socket.sendall(message.encode('utf-8'))

    def send_str_message_on_serial_port(self, message: str) -> None:
        self.ser.write(message.encode('utf-8'))

    def transmit_receive_arduino(self, message_dict: dict) -> str:
        """
            Send a message to the Arduino and receive a response.

            Args:
                message_dict (dict): The message to send to the Arduino.
                time_out_limit (int): The time out limit for the response.

            Returns:
                str: The response from the Arduino.
        """

        if type(message_dict) == dict:
            message = Common.json_dict_to_string(message_dict)
        elif "\n" not in message:
            return "{'error': 'Message must end with a newline character.'}"
    
        self.ser.reset_input_buffer()
        hold = time.time()
        while True:
            
            # Send the message to the Arduino
            message = Common.dict_to_bit(message_dict) + "\n"
            # print(message, " Type: ", type(message), " Size: ", sys.getsizeof(message))

            self.send_str_message_on_serial_port(message) 

            if self.WAIT_REPONSE_FROM_ARDUINO:
                line = self.ser.readline().decode('utf-8').rstrip()
                if line:
                    return line
                elif time.time() - hold > self.WAIT_REPONSE_TIMEOUT_LIMIT:
                    return "{'error': 'Timeout limit reached.'}"
            elif math.fabs(time.time() - hold) > 0.7:
                return "{'information': 'Waiting for response is disabled.'}"


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
                    json_data = Common.str_to_json_dict(data_received_string)
                    
                    # Sending the message to the Arduino
                    time_start = time.time()
                    response_from_arduino = self.transmit_receive_arduino( json_data )
                    print(f"Time taken to send and receive data from Arduino: {time.time() - time_start}")
                    
                    # Print the response
                    print(f"Data received from Arduino: {response_from_arduino}")
                
            

    def __del__(self) -> None:
        """
            Destructor. Closes the socket and serial port.
        """
        self.socket.close()
        self.ser.close()


def main():

    # Get the IP address and port
    HOST, PORT = Stream_operations.get_host_ip_and_port()

    server = Raspberry_Server( wait_response=False, echo_server=False, time_out_limit=5)
    server.init_server(HOST, PORT)
    server.init_serial_port()
    server.main_loop()
 
    del server

if __name__ == "__main__":
    main()