import serial
import time
import json
import re
import socket
import traceback
import sys
import threading

sys.path.insert(0,"Raspberry")
sys.path.insert(0,".")


from Modules.Distance_Sensor.get_distance import get_max_distance
from others.Stream_operations import get_host_ip_and_port
from Modules.Camera.camera_stream import camera_stream_start

class Common_Operations:
    def __init__(self):
        pass
    
    def str_to_json_dict( self, data_str: str ) -> dict:
        try:
            return json.loads(data_str)
        except:
            print("Error converting string to dictionary : ", data_str)
            return {}

    def dict_to_str(  self, data: dict ) -> str:
        try:
            return json.dumps(data) + "\n"
        except:
            raise ValueError("Error converting dictionary to string.")

    def client_to_arduino_wrapper( self, input_dict ) -> dict:
        
        if input_dict["Type"] == "robot_move":
            return {
                "Command": input_dict["Command"],
                "Type": input_dict["Type"],
                "X": input_dict["X"],
                "Y": input_dict["Y"]
            }
        elif input_dict["Type"] == "camera_move":
            return {
                "Command": input_dict["Command"],
                "Type": input_dict["Type"],
                "axis": 1 if input_dict["axis"] > 1 else 0,
                "direction": 1 if input_dict["direction"] > 1 else 0
            }
    

class Serial_Port_Operations(Common_Operations):
    def __init__(self, dev, baud_rate):
        """
        Initialize the serial port with the given device and baud rate
        :param dev: Device name
        :param baud_rate: Baud rate
        """
        super().__init__()
    
    def init_serial_port(self, baud_rate, dev ):
        try:
            self.ser = serial.Serial( baudrate=baud_rate, port=dev , timeout=1)
            
            # Flush the input and output buffers
            self.reset_buffers()

        except Exception as e:
            print("Serial port is not available. Please check the connection: ", e)


    def write_to_port(self, data:str, ready_to_send=True):
        # Write the data to the serial port
        if type(data) != str:
            print("Data should be in string format")
            return
        
        if ready_to_send == False:
            data = self.client_to_arduino_wrapper( self.str_to_json_dict(data) )
            data = self.dict_to_str(data)
            data = data.encode()

        self.ser.write( data )

    def read_from_port(self):
        # Read the data from the serial port
        return self.ser.readline().decode('utf-8').rstrip()
    
    def transmit_and_receive(self, message:str, timeout=1):
        """
        Transmit the data to the serial port until the response is received
        :param data: Data to transmit

        input_data = {
            <insert here when the code is ready>
        }

        transmitted_data = {
            <insert here when the code is ready>
        }
        """

        # Hold the time when the function is called
        time_hold = time.time()
        
        # Reset the input and output buffers
        self.reset_buffers()

        # Prepare the data to be sent
        message = self.client_to_arduino_wrapper( self.str_to_json_dict(message) )
        message = self.dict_to_str(message)
        message = message.encode()

        # Transmit the data to the serial port until the response is received
        while True:
            # Write the data to the serial port
            self.write_to_port(message, ready_to_send=True)

            # Read the data from the serial port
            response = self.read_from_port()

            if response:
                response = re.sub('[^a-zA-Z0-9}":{\.,*$]', '', response) if "gps" in message.decode('utf-8') else response
                return response
            elif time.time() - time_hold > timeout:
                return { "Error": "Timeout" }
            

    def reset_buffers(self):
        """
        Reset the input and output buffers
        """
        self.ser.flushInput()
        self.ser.flushOutput()

    def __del__(self):
        self.ser.close()

class Client_Server_Operations(Common_Operations):
    def __init__(self, HOST: str, PORT: int):
        """
            Initialize the client.

            Args:
                HOST (str): The IP address to connect to.
                PORT (int): The port to connect to.
        """
        super().__init__()
    
        
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

    
    def get_message_from_client(self) -> str:
        """
            Get a message from the client.

            Returns:
                str: The message received from the client. 
        """
        # Check if the connection object is available
        if not hasattr(self, 'conn'):
            print("Connection object is not available.")
            return None
        
        # Receive the data from the client
        data_received = self.conn.recv(1024) # 1024 is the buffer size in bytes
        return data_received.decode('utf-8')
    
    def send_message_to_client(self, message: str) -> None:
        """
            Send a message to the client.

            Args:
                message (str): The message to send to the client.
        """
        # Check if the connection object is available
        if not hasattr(self, 'conn'):
            print("Connection object is not available.")
            return None
        
        # Send the message to the client
        if type(message) == dict:
            message = self.dict_to_str(message)
            
        self.conn.sendall(message.encode('utf-8'))
    
    def wait_connection(self):
        """
            Wait for a connection.
        """
        while True:
            self.conn, self.addr = self.socket.accept()
            print(f"Connected to {self.addr}")
            
            return self.conn, self.addr

class Raspberry_Server( Common_Operations ):
    def __init__(self, HOST: str, PORT: int, dev: str, baud_rate: int, camera_port: int):
        """
            Initialize the server.

            Args:
                HOST (str): The IP address to connect to.
                PORT (int): The port to connect to.
                dev (str): The device name of the serial port.
                baud_rate (int): The baud rate of the serial port.
                camera_port (int): The port to start the camera stream on.
        """
        super().__init__()
        
        # Parameters
        self.HOST = HOST; self.PORT = PORT; self.SERIAL_PORT_DEVICE = dev; self.SERIAL_PORT_BAUD_RATE = baud_rate
        self.CAMERA_PORT = camera_port
        
        # Composition of classes
        self.server_operations = Client_Server_Operations(HOST, PORT)
        self.serial_port_operations = Serial_Port_Operations(dev, baud_rate)

        # Initialize components
        self.server_operations.init_server(HOST, PORT)
        self.serial_port_operations.init_serial_port(baud_rate, dev)
        self.start_camera_stream_thread(self.CAMERA_PORT)


        self.print_features()
    
        # Run the server
        self.run()


    def print_features(self) -> None:
        """
            Print the features of the server.
        """
        print("\nServer features:")   
        print(f"  Serving on {self.HOST}:{self.PORT}")
        print(f"  Serial port status:","Active" if hasattr(self.serial_port_operations, 'ser') else "Inactive")
        print(f"  Serial port on {self.SERIAL_PORT_DEVICE} with baud rate {self.SERIAL_PORT_BAUD_RATE}")
        print(f"  Camera is serving on {self.CAMERA_PORT}")
        print()


    def start_camera_stream_thread(self, port: int) -> None:
        """
        Starts the camera stream on a new thread.

        Args:
            port (int): The port to start the camera stream on.
        """
        try:
            thread = threading.Thread(target=camera_stream_start, args=(port,))
            thread.start()
            time.sleep(0.5)
        except Exception as e:
            print(f"An error occurred while starting the camera stream: {e}")

    def run(self):
        """
            Run the server.
        """
        while True:
            print("Waiting for connection...")
            self.server_operations.wait_connection()

            try:
                with self.server_operations.conn:
                    while True:
                        
                        # Receive the data from the client and check if it is available
                        received_data = self.server_operations.get_message_from_client()
                        if received_data is None:
                            continue
                        print(f"Data received from client: {received_data }")
                        
                        # Get the max distance
                        max_distance = get_max_distance( 'Modules/Distance_Sensor/VL53L3CX_rasppi/vl53l3cx_ranging_output.txt' )
                        print("Max distance is ", max_distance)
                            
                        
                        if not hasattr(self.serial_port_operations, 'ser'):
                            print("Serial port is not available, skipping the transmission.")
                            continue

                        # Transmit the data to the Arduino and receive the response
                        response_from_arduino = self.serial_port_operations.transmit_and_receive(received_data)

                        # Sending the message to the Client                        
                        self.server_operations.send_message_to_client(response_from_arduino)
                        
                        # Print the response
                        print(f"Data received from Arduino: {response_from_arduino} \n")
                     
                    # With traceback         
            except Exception as e:
                print("An error occurred: ", e)
                traceback.print_exc()
                # Delete the connection object
                del self.server_operations.conn
                
                continue

# Main function
if __name__ == "__main__":
    
    # Get the IP address and port
    HOST, PORT = get_host_ip_and_port()
    server = Raspberry_Server( 
        HOST=HOST, 
        PORT=PORT, 
        dev='/dev/ttyUSB0',
        baud_rate=19200,
        camera_port=8080
    )
        
