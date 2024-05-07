import socket
import sys

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5000

# Sends message to the server
def send_message_to_server(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        message = "Hello, World!"
        s.connect((HOST, PORT))
        s.sendall(message.encode('utf-8'))
        

if __name__ == "__main__":
    send_message_to_server("Hello, World!")
    