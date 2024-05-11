import socket
import serial
import math
import time
import sys
import re

sys.path.insert(0,"Raspberry")
sys.path.insert(0,".")
from Utils.timer import Timer
from Raspberry.others import Stream_operations
from others import Common
from server_operations import Send_message as rasp

class Raspberry_Server:
    """
        A class to run the server on the Raspberry Pi.
    """
    def __init__(self,HOST:str, PORT:int, echo_server:bool, wait_response:bool, time_out_limit:int) -> None:
        
        # Set attributes
        self.ECHO_SERVER = echo_server # Echo server -> Sends the data back to the client
        self.WAIT_REPONSE_FROM_ARDUINO = wait_response # Wait for a response from the Arduino
        self.WAIT_REPONSE_TIMEOUT_LIMIT = time_out_limit # Time out limit for the response from the Arduino
        
        self.init_server(HOST, PORT)
        self.init_serial_port()
        self.timer = Timer()
        

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
        self.socket.listen()
        
        print(f"Server is listening on {self.HOST}:{self.PORT}...")

    def reset_serial_port(self):
        
        if hasattr(self, "ser") and self.ser is not None:
            self.ser.close()
            self.ser = None
        serial.Serial('/dev/ttyUSB0', 14400, timeout=1).close()
        
    def init_serial_port(self):
        self.reset_serial_port()
        try:
            self.ser = serial.Serial('/dev/ttyUSB0', 14400, timeout=1)
        except serial.serialutil.SerialException:
            print("Serial port is not available. Please check the connection.")
            self.ser = None
            
    def transmit_receive_arduino(self, message_raw) -> str:
        """
            Send a message to the Arduino and receive a response.

            Args:
                message_raw (Dynamic): The message to send to the Arduino.
                time_out_limit (int): The time out limit for the response.

            Returns:
                str: The response from the Arduino.
        """

        if type(message_raw) == dict:
            message_str = Common.dict_to_bit(message_raw) + "\n"  
        else:
            message_str = message_raw
        print("Message_str Type: ", type(message_str), " Size: ", sys.getsizeof(message_str) , " data : ", message_str.replace("\n", ""))

        if message_str[-1] != "\n":
            return "{'error': 'Message must end with a newline character.'}"

        message = message_str.encode('utf-8')
        
        if type(message) != bytes:
            return "{'error': 'Message must be a byte.'}"
        

        print("Encoded Message Type: ", type(message), " Size: ", sys.getsizeof(message) , " data : ", message)
        self.ser.reset_input_buffer()
        hold = time.time()
        while True:
            # Send the message to the Arduino
            self.ser.write(message)

            if self.WAIT_REPONSE_FROM_ARDUINO:
                # Wait for a response from the Arduino
                try:
                    line = self.ser.readline().decode('utf-8').rstrip()
                except UnicodeDecodeError:
                    return "{'error': 'UnicodeDecodeError'}"
                
                # Check if the response is not empty
                if line:
                    # Remove special characters before returning the response
                    line = re.sub('[^a-zA-Z0-9\.,*$]', '', line) if message_str == "1111\n" else line
                    return line
                
                # Check if the time out limit is reached
                elif time.time() - hold > self.WAIT_REPONSE_TIMEOUT_LIMIT:
                    return "{'information': 'Timeout limit reached.'}"
            elif math.fabs(time.time() - hold) > 0.7:
                return "{'information': 'Waiting for response is disabled.'}"


    def main_loop(self) -> None:
        """
            Wait for a connection from a client and send a message to the client.
        """
        if self.ser is None:
            print("Serial port is not available. Exiting the program.")
            return

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
                        self.timer.start_new_timer("end_to_end_time")
                    except ConnectionResetError:
                        print("Connection was reset by the client")
                        break
                    
                    # Send the data back to the client ( Optional ) ( Echo server )
                    conn.sendall(data_received) if self.ECHO_SERVER else None

                    # Decode the data and convert to json dict.
                    data_received_string = data_received.decode('utf-8')
                    if data_received_string[-1] == "}":
                        transmit_data = Common.str_to_json_dict(data_received_string)
                    else:
                        transmit_data = data_received_string
                    
                    # Sending the message to the Arduino
                    response_from_arduino = self.transmit_receive_arduino( transmit_data )
                    conn.sendall(response_from_arduino.encode('utf-8'))
                    
                    # Print the response
                    print(f"Data received from Arduino: {response_from_arduino} \n")
                    self.timer.stop_timer("end_to_end_time")
                    
            self.timer.print_timers()
            

    def __del__(self) -> None:
        """
            Destructor. Closes the socket and serial port.
        """
        self.socket.close()
        if hasattr(self, "ser") and self.ser is not None:
            self.ser.close()


def main():

    # Get the IP address and port
    HOST, PORT = Stream_operations.get_host_ip_and_port()

    server = Raspberry_Server( wait_response=True, echo_server=False, time_out_limit=5 , HOST=HOST, PORT=PORT)
    server.main_loop()
 
    del server

if __name__ == "__main__":

    try:
        main()
    except AttributeError:
        print("An AttributeError occurred.")