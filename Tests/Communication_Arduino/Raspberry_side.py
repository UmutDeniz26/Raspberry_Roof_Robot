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


# Test the function
def test():
    response = transmit_receive_arduino_message("Hello Arduino! \n", 10)
    print("Response from Arduino:", response)

if __name__ == "__main__":
    test()