import Raspberry_side as rasp

json_dict = { "command": "forward", "speed": 100 , "transmit_time": rasp.get_system_clock_time() }

string = rasp.json_dict_to_string(json_dict)

response = rasp.transmit_receive_arduino_message(string, 5)

print(response)