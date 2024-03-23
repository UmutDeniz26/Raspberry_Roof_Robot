import serial
import time

def transmit_receive_arduino_message(message: str, timeout_limit: int):
    """
        Transmit a message to the Arduino and wait for a response.

        Args:
            message (str): The message to send to the Arduino.
            timeout_limit (int): The time to wait for a response from the Arduino. *Note: The timeout is in seconds.

        Returns:
            str: The response from the Arduino. *Note: In form of json string.
    """

    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser.reset_input_buffer()
    hold = time.time()

    if "\n" not in message:
        return "{'error': 'Message must end with a newline character.'}"

    while True:
        
        ser.write(message.encode())
        line = ser.readline().decode('utf-8').rstrip()
        if line:
            return line
        
        if time.time() - hold > timeout_limit:
            return "{'error': 'Timeout limit reached.'}"
        
        time.sleep(0.1)


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
    json_message = {"message": "Hello Arduino how are you", "transmit_time": get_system_clock_time()}
    string_message = json_dict_to_string(json_message)

    # Transmit the message and receive the response
    response = transmit_receive_arduino_message(string_message, 10)
    print(response)

if __name__ == "__main__":
    test()