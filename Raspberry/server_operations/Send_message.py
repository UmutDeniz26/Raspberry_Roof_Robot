import serial
import time
import math
import sys

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


def transmit_receive_arduino_message(message_dict: dict, timeout_limit: int):
    """
        Transmit a message to the Arduino and wait for a response.

        Args:
            message_dict (dict): The message to send to the Arduino.
            timeout_limit (int): The time to wait for a response from the Arduino. *Note: The timeout is in seconds.

        Returns:
            str: The response from the Arduino. *Note: In form of json string.
    """
    message = json_dict_to_string(message_dict)

    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    ser.reset_input_buffer()
    
    if "\n" not in message:
        return "{'error': 'Message must end with a newline character.'}"
    
    #bit_arr = dict_to_bit(message_dict)
    #print(bit_arr, " Type: ", type(bit_arr), " Size: ", sys.getsizeof(bit_arr))
    hold = time.time()
    while True:
        ser.write(message.encode('utf-8'))
        if math.fabs(time.time() - hold) > 0.5:
            return
    """
    while True:
        
        ser.write(message.encode('utf-8'))
        time.sleep(0.1)
        line = ser.readline().decode('utf-8').rstrip()
        if line:
            return line
        elif time.time() - hold > timeout_limit:
            return "{'error': 'Timeout limit reached.'}"
    """


def json_dict_to_string(json_dict: dict) -> str:
    """
        Convert a dictionary to a json string. Deletes \n characters from the string. 
        Then adds a newline character at the end.

        Args:
            json_dict (dict): The dictionary to convert to a json string.

        Returns:
            str: The json string.
    """
    json_string = str(json_dict).replace("\n", "").replace("\"", "'")
    return json_string + "\n"


def get_system_clock_time() -> str:
    """
        Get the current system clock time in seconds. In format of hh:mm:ss.

        Returns:
            int: The current system clock time in seconds.
    """
    return time.strftime("%H:%M:%S")

# Test the function
def test():
    # Generate a sample message
    # json_message = {"message": "Hello Arduino how are you", "transmit_time": get_system_clock_time()}
    # string_message = json_dict_to_string(json_message)

    # Transmit the message and receive the response
    # response = transmit_receive_arduino_message(string_message, 10)
    # print(response)

    print(dict_to_bit({"Type": "robot_move", "Command": "backward"}))

if __name__ == "__main__":
    test()