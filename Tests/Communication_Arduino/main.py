import Raspberry_side
import time
def main():
    json_message = {"message": "Hello Arduino how are you", "transmit_time": get_system_clock_time()}

    string_message = json_dict_to_string(json_message)

    response = Raspberry_side.transmit_receive_arduino_message(string_message, 10)

    print(response)

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

if __name__ == "__main__":
    main()