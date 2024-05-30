import json

def str_to_json_dict( data_str: str ) -> dict:
    """
        Convert a string to a json dictionary.
        
        Args:
            data_str (str): The string to convert to a json dictionary.
        
        Returns:
            dict: The json dictionary.
    """
    try:
        return json.loads(data_str)
    except:
        print("Error converting string to dictionary : ", data_str)
        return {}

def dict_to_str( data: dict ) -> str:
    """
        Convert a dictionary to a string.
        
        Args:
            data (dict): The dictionary to convert to a string.
        
        Returns:
            str: The string.
    """
    try:
        return json.dumps(data) + "\n"
    except:
        raise ValueError("Error converting dictionary to string.")

def convert_to_dict( Command, Type, X=None, Y=None):
    """
    """
    if Type == "gps":
        return {
                "Type": Type,
                "Command": Command
            }
    elif Type == "robot_move":
        return {
                "Type": Type,
                "Command": Command,
                "X": X,
                "Y": Y
            }

       

def convert_message_to_bytes(message) -> bytes:
    """
        Convert a message to bytes.
        
        Args:
            message (str or dict): The message to convert to bytes.
        
        Returns:
            output (bytes): The message converted to bytes.
    """
    if type(message) == dict:
        output = dict_to_bit(message) + "\n"
    elif type(message) == str and message[-1] == "\n":
        output = message.encode('utf-8')
    else:
        return "{'error': 'Message must be str or dict. If it is a str, it must end with a newline character.'}", False

    return output, True




BIT_MAP = {
    "robot_move-forward": "0000",
    "robot_move-backward": "0001",
    "robot_move-left": "0010",
    "robot_move-right": "0011",
    "robot_move-stop": "0100",
    "gps-*": "1111",
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
        bit_val = BIT_MAP[bit_string_key]
        #bit_arr = bit_arr.to_bytes(1, byteorder='big')

        return bit_val
