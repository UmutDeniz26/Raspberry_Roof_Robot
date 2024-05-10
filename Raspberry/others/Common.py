import json

def get_json_format( data_str: str ) -> dict:
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
        raise ValueError("Error converting string to json dictionary.")