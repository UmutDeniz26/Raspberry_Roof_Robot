#!/home/umut/roof_robot/bin/python3.11
import serial
import pynmea2
import os
import time
# ... rest of the script ...

#print("User: ", os.getlogin())
#print("Permissions: ", oct(os.stat('/dev/ttyS0').st_mode))

def read_gps_data(serial_port):
        # Check if the user has permission to access the serial port
    try:
        st = os.stat(serial_port)
        permissions = oct(st.st_mode & 0o777)  # Get the permission part of the mode
        if 'group' not in os.getgroups() or 'dialout' not in os.getgroups():
            # If the user is not in the 'dialout' group, fix the permissions
            os.system('sudo chmod 660 {}'.format(serial_port))
            os.system('sudo chown root:dialout {}'.format(serial_port))
    except FileNotFoundError:
        print("Serial port {} not found.".format(serial_port))
    except Exception as e:
        print("Error checking or fixing permissions:", e)


    with serial.Serial(serial_port, baudrate=9600, timeout=1) as ser:
        while True:
            try:
                line = ser.readline().decode('utf-8')
                if line.startswith('$GPGGA'):
                    msg = pynmea2.parse(line)
                    latitude = msg.latitude
                    longitude = msg.longitude
                    print("\nNMEA Sentence: {}".format(line), end='')
                    print("Latitude: {}, Longitude: {}".format(latitude, longitude))
            except serial.SerialException as e:
                print("SerialException: {}".format(e))
                break
            except pynmea2.ParseError:
                print("Parse error: ", line)
            except UnicodeDecodeError:
                print("UnicodeDecodeError")

if __name__ == "__main__":
    serial_port = '/dev/ttyS0'
    while True:
        try:
            read_gps_data(serial_port)
        except serial.SerialException as e:
            print("SerialException: {}. Retrying in 5 seconds...".format(e))
            time.sleep(5)
