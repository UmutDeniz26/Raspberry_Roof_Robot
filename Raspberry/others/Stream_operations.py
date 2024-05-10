
import socket
import json
import subprocess
import errno

def is_port_in_use(ip,port):
    """
        Check if a port is in use.
        Args:
            ip (str): The IP address to check.
            port (int): The port to check.
        Returns:
            bool: True if the port is in use, False otherwise.
    """
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # Bind the socket to the IP address and port
            # Binding is a process of associating a socket with an IP address and port number
            s.bind((ip, port))
        except OSError as e:
            # Check if the port is in use
            if e.errno == errno.EADDRINUSE:
                return True
            print("An error occurred other than the port being in use, error: ", e)
    print(f"Port {port} is available")
    return False

def get_ip_address():
    """
        
        Get the IP address of the Raspberry Pi.
        *Note: This function assumes that the Raspberry Pi is connected to a network. And only works for the wlan0 interface.

        Args:
            None
        Returns:
            str: The IP address of the Raspberry Pi.
    """

    try:
        # Run the ifconfig command to get network interface information
        result = subprocess.run(['ifconfig', 'wlan0'], capture_output=True, text=True)
        # Extract the IP address from the command output
        ip_address = result.stdout.split('inet ')[1].split(' ')[0]
        
        return ip_address
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return None

def get_host_ip_and_port():
    """
        Get the IP address and port of the Raspberry Pi.
        Args:
            None
        Returns:
            tuple: The IP address and port of the Raspberry Pi.
    """
    ip_address = get_ip_address()

    if ip_address is None:
        raise Exception("Error getting IP address")
    
    init_port = 5000

    while is_port_in_use(ip_address, init_port):
        init_port += 1

    return ip_address, init_port

def main():
    HOST, PORT = get_host_ip_and_port()
    print(f"Host: {HOST}, Port: {PORT}")   

if __name__ == "__main__":
    main()
