import Raspberry_side



response = Raspberry_side.transmit_receive_arduino_message("Hello Arduino how are you\n", 10)

print(response)