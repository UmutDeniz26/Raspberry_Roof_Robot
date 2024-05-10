
def is_port_in_use(ip,port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((ip, port))
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                return True
            
            print("An error occurred: ", e)
    print(f"Port {port} is available")
    return False

def get_ip_address():
    try:
        # Run the ifconfig command to get network interface information
        result = subprocess.run(['ifconfig', 'wlan0'], capture_output=True, text=True)
        # Extract the IP address from the command output
        ip_address = result.stdout.split('inet ')[1].split(' ')[0]
        return ip_address
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return None

# Weak function to get the host IP. It only works for the Raspberry Pi.
def get_host_ip_and_port():
    ip_address = get_ip_address()

    if ip_address is None:
        raise Exception("Error getting IP address")
    
    init_port = 5000

    while is_port_in_use(ip_address, init_port):
        init_port += 1

    return ip_address, init_port
