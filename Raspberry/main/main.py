import socket
import time

# Sample function for reading data from the sensor
def read_distance_sensor():
    # In a real application, data would be read from the sensor here
    # For example: return some_sensor_library.read_distance()
    return "5 meters"

# Getting the host IP dynamically
host = socket.gethostbyname(socket.gethostname())
port = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()

    print(f"Server is listening on {host}:{port}")

    conn, addr = s.accept()
    with conn:
        print(f"Connected to {addr}")
        while True:
            try:
                # Read distance data from the sensor
                # distance = read_distance_sensor()
                # Send the data
                conn.sendall(f"Distance: {5}\n".encode('utf-8'))
                # Send updates every second
                time.sleep(1)
            except BrokenPipeError:
                # If the client disconnects, break the loop
                print("Client disconnected.")
                break
