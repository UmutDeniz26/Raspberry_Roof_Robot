import serial
import time
import math

dict_bit_convert = {
    "robot_move-forward": 0b0000,
    "robot_move-backward": 0b0001,
    "robot_move-left": 0b0010,
    "robot_move-right": 0b0011,
    "robot_move-stop": 0b0100,
    "gps-*": 0b1111,
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

def dict_to_bit(data : dict) -> str:
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
    bit_val = dict_bit_convert[bit_string_key]
    #bit_arr = bit_arr.to_bytes(1, byteorder='big')

    return bit_val


def transmit_receive_arduino_message(message_dict: dict, timeout_limit: int, wait_response: bool):
    """
        Transmit a message to the Arduino and wait for a response.

        Args:
            message_dict (dict): The message to send to the Arduino.
            timeout_limit (int): The time to wait for a response from the Arduino. *Note: The timeout is in seconds.
            wait_response (bool): The Bool value about waiting reponse from Arduino or not.
            
        Returns:
            str: The response from the Arduino. *Note: In form of json string.
    """
    if type(message) == dict:
        message = json_dict_to_string(message_dict)
    elif "\n" not in message:
        return "{'error': 'Message must end with a newline character.'}"
    
    #bit_arr = dict_to_bit(message_dict)
    #print(bit_arr, " Type: ", type(bit_arr), " Size: ", sys.getsizeof(bit_arr))

    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    ser.reset_input_buffer()

    hold = time.time()
    while True:
        ser.write(message.encode('utf-8'))

        if wait_response:
            line = ser.readline().decode('utf-8').rstrip()
            if line:
                return line
            elif time.time() - hold > timeout_limit:
                return "{'error': 'Timeout limit reached.'}"
        
        if math.fabs(time.time() - hold) > 0.5 and (not wait_response):
            return

if __name__ == "__main__":
    pass