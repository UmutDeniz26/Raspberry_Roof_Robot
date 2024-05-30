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

class Raspberry_Server:
    """
        A class to run the server on the Raspberry Pi.
    """
    def __init__(self,HOST:str, PORT:int, echo_server:bool, wait_response:bool, enable_time_measurement:bool, time_out_limit:int,send_ard_bit_or_dict:bool
                , serial_port_baud_rate: int, serial_port_device:str         
        ) -> None:
        
        # Initialize attributes
        self.ser = None
        
        # Set attributes
        self.ECHO_SERVER = echo_server                      # Echo server -> Sends the data back to the client
        self.WAIT_REPONSE_FROM_ARDUINO = wait_response      # Wait for a response from the Arduino
        self.WAIT_REPONSE_TIMEOUT_LIMIT = time_out_limit    # Time out limit for the response from the Arduino
        self.TIME_MEASUREMENT = enable_time_measurement     # Measures processing times
        self.SERIAL_PORT_BAUD_RATE = serial_port_baud_rate  # Baud rate
        self.SERIAL_PORT_DEVICE = serial_port_device        # Connection device
        self.SEND_ARD_BIT_OR_DICT = send_ard_bit_or_dict    # Send the message as a bit or a dictionary
        
        self.init_server(HOST, PORT)
        self.init_serial_port( serial_port_baud_rate, serial_port_device )
        self.timer = Timer() if self.TIME_MEASUREMENT else None

        # Print the features of the server
        self.print_features()
        

    def print_features(self) -> None:
        """
            Print the features of the server.
        """
        print("\nServer features:")   
        print(f"  Serving on {self.HOST}:{self.PORT}")
        print(f"  Serial port status:","Active" if self.ser is not None else "Inactive")
        print(f"  Serial port on {self.SERIAL_PORT_DEVICE} with baud rate {self.SERIAL_PORT_BAUD_RATE}")
        print()

    def init_server(self,HOST: int, PORT: int) -> None:
        """
            Initialize the server.

            Args:
                HOST (str): The IP address to bind the server to.
                PORT (int): The port to bind the server to.
        """
        try:
            # Set the port and host
            self.PORT = PORT;self.HOST = HOST

            # Create a socket object
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # The one liner : bind() to own address, connect() to remote address. 
            self.socket.bind((HOST, PORT))
            self.socket.listen()
            
            print(f"Server is listening on {self.HOST}:{self.PORT}...")
        except Exception as e:
            print(f"An error occurred while initializing the server: {e}")

    def init_serial_port(self, baud_rate, dev ):
        try:
            self.ser = serial.Serial( baudrate=baud_rate, port=dev , timeout=1)
        except Exception as e:
            print("Serial port is not available. Please check the connection: ", e)
            
    def prepare_arduino_message(self, message_raw) -> str:
        """
            Prepare the message to send to the Arduino.

            Args:
                message_raw (Dynamic): The message to send to the Arduino.

            Returns:
                str: The message to send to the Arduino.
        """
        # Encode the message to bytes. If the message is not a string or a dictionary, return an error message.
        if self.SEND_ARD_BIT_OR_DICT:
            message, success = Common.convert_message_to_bytes(message_raw)
            if not success:
                return message
        else:
            if type(message_raw) == str:
                message_raw = Common.str_to_json_dict(message_raw)
            message = Common.convert_to_dict(    
                    message_raw["Command"], message_raw["Type"], message_raw["X"], message_raw["Y"], message_raw["Speed"]
                ).encode('utf-8')


        return message

    def transmit_receive_arduino(self, message_raw) -> str:
        """
            Send a message to the Arduino and receive a response.

            Args:
                message_raw (Dynamic): The message to send to the Arduino.
                time_out_limit (int): The time out limit for the response.

            Returns:
                str: The response from the Arduino.
        """

        # First check if the serial port is available
        if self.ser == None:
            return "{'error':'Serial port is not available.'}"

        # Encode the message to bytes. If the message is not a string or a dictionary, return an error message.
        message = self.prepare_arduino_message(message_raw)

        print("Raw Message Type: ", type(message_raw), " Size: ", sys.getsizeof(message_raw) , " data : ", message_raw)
        print("Processed Message Type: ", type(message), " Size: ", sys.getsizeof(message) , " data : ", message)
        
        self.ser.reset_input_buffer()
        hold = time.time()
        
        while True:
            # Send the message to the Arduino
            self.ser.write(message)

            # Wait for a response from the Arduino
            if self.WAIT_REPONSE_FROM_ARDUINO:
                try:
                    line = self.ser.readline().decode('utf-8').rstrip()
                except UnicodeDecodeError:
                    return "{'error': 'UnicodeDecodeError'}"
                
                if line:
                    # Remove special characters before returning the response if the message is a gps message
                    line = re.sub('[^a-zA-Z0-9\.,*$]', '', line) if message_raw == "1111\n" else line
                    return line
                
                # Check if the time out limit is reached
                elif time.time() - hold > self.WAIT_REPONSE_TIMEOUT_LIMIT:
                    return "{'information': 'Timeout limit reached.'}"
            elif math.fabs(time.time() - hold) > 0.7:
                return "{'information': 'Waiting for response is disabled.'}"

    def get_message_from_client(self, conn) -> str:
        """
            Get a message from the client.

            Args:
                conn (socket): The connection object.

            Returns:
                str: The message from the client.
        """
        try:
            data_received = conn.recv(1024) # 1024 is the buffer size in bytes
            if not data_received:
                return None
            return data_received
        except ConnectionResetError:
            print("Connection was reset by the client")
            return None

    def main_loop(self) -> None:
        """
            The main loop of the server.
        """
        try:

            while True:
                conn, addr = self.socket.accept()
                with conn:

                    print(f"Connected from {addr}")
                    
                    # Receive data from the client
                    while True:
                        data_received = self.get_message_from_client(conn)
                        
                        # Send the data back to the client ( Optional ) ( Echo server )
                        conn.sendall(data_received) if self.ECHO_SERVER else None

                        # Decode the data and convert to json dict.
                        received_data_string = data_received.decode('utf-8')
                        
                        if received_data_string[-1] == "}":
                            received_data_dict = Common.str_to_json_dict(received_data_string)
                            response_from_arduino = self.transmit_receive_arduino( received_data_dict )
                        else:
                            response_from_arduino = self.transmit_receive_arduino( received_data_string )

                        # Sending the message to the Arduino                        
                        conn.sendall(response_from_arduino.encode('utf-8'))
                        
                        # Print the response
                        print(f"Data received from Arduino: {response_from_arduino} \n")
                        self.timer.stop_timer("end_to_end_time") if self.TIME_MEASUREMENT else None
                        
                    self.timer.print_timers() if self.TIME_MEASUREMENT else None

        except Exception as e:
            print(f"An error occurred while running the server: {e}")    

    def __del__(self) -> None:
        """
            Destructor. Closes the socket and serial port.
        """
        self.socket.close()
        if self.ser is not None:
            self.ser.close()


def main():

    # Get the IP address and port
    HOST, PORT = Stream_operations.get_host_ip_and_port()

    server = Raspberry_Server( 
        wait_response=True, echo_server=False, time_out_limit=5 , HOST=HOST, PORT=PORT,
        serial_port_baud_rate=14400,serial_port_device='/dev/ttyUSB0', enable_time_measurement=True, send_ard_bit_or_dict=False
        )
    server.main_loop()
    del server
    print("Server is closed")

if __name__ == "__main__":

    try:
        main()
    except AttributeError as e:
        print("An AttributeError occurred while running the server: ", e)