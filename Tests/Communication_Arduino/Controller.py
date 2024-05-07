import Raspberry_side as rasp

json_dict = { "command": "forward", "speed": 100 , "transmit_time": rasp.get_system_clock_time() }
    
response = rasp.transmit_receive_arduino_message(json_dict, 5)

print(response)