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


BIT_MAP = {
    "robot_move-forward": "0000",
    "robot_move-backward": "0001",
    "robot_move-left": "0010",
    "robot_move-right": "0011",
    "robot_move-stop": "0100",
    "gps-*": "1111",
    "5": 0b0101,
    "6": 0b0110,
    "7": 0b0111,
    "8": 0b1000,
    "9": 0b1001,
    "a": 0b1010,
    "b": 0b1011,
    "c": 0b1100,
    "d": 0b1101,
    "e": 0b1110,
    "f": 0b0101
}

class Raspberry_Server:
    """
        A class to represent a Raspberry Pi server.
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


    def send_str_message_on_socket(self, message: str) -> None:
        """
            Send a string message to the client.

            Args:
                message (str): The message to send to the client.
        """
        self.socket.sendall(message.encode('utf-8'))

    def send_str_message_on_serial_port(self, message: str) -> None:
        """
            Send a string message to the Arduino.

            Args:
                message (str): The message to send to the Arduino.
        """
        self.ser.write(message.encode('utf-8'))

    def init_serial_port(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        

    def dict_to_bit(self,data : dict) -> str:
        """
            Convert a dictionary to a bit string.

            Args:
                data (dict): The dictionary to convert to a bit string.

            Returns:
                str: The bit string.
        """
        # Check if the data is a gps message
        if data["Type"] == "gps":
            data["Command"] = "*"
        
        # Get the type and command from the dictionary
        type_ = data["Type"]
        command = data["Command"]
        
        # Combine the type and command to form a bit string
        bit_string_key = f"{type_}-{command}"
        bit_val = BIT_MAP[bit_string_key]
        #bit_arr = bit_arr.to_bytes(1, byteorder='big')

        return bit_val

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
            message = rasp.json_dict_to_string(message_dict)
        elif "\n" not in message:
            return "{'error': 'Message must end with a newline character.'}"
        
        #bit_arr = dict_to_bit(message_dict);print(bit_arr, " Type: ", type(bit_arr), " Size: ", sys.getsizeof(bit_arr))

        self.ser.reset_input_buffer()

        hold = time.time()
        while True:
            
            # Send the message to the Arduino
            message = self.dict_to_bit(message_dict) + "\n"

            self.send_str_message_on_serial_port(message) 

            if self.WAIT_REPONSE_FROM_ARDUINO:
                line = self.ser.readline().decode('utf-8').rstrip()
                if line:
                    return line
                elif time.time() - hold > self.WAIT_REPONSE_TIMEOUT_LIMIT:
                    return "{'error': 'Timeout limit reached.'}"
            
            if math.fabs(time.time() - hold) > 0.7 and (not self.WAIT_REPONSE_FROM_ARDUINO):
                return


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
                    response_from_arduino = self.transmit_receive_arduino( json_data )
                    print(f"Time taken to send and receive data from Arduino: {time.time() - time_start}")
                    
                    # Print the response
                    print(f"Data received from Arduino: {response_from_arduino}")
                
            

    def __del__(self) -> None:
        """
            Destructor.
        """
        # Close the socket
        self.socket.close()
        self.ser.close()


def main():

    # Get the IP address and port
    HOST, PORT = Stream_operations.get_host_ip_and_port()

    server = Raspberry_Server( wait_response=False, echo_server=False, time_out_limit=5)
    server.init_server(HOST, PORT)
    server.init_serial_port()
    server.main_loop()

if __name__ == "__main__":
    main()