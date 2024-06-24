# Raspberry Pi Communication System

## Overview
This repository contains code for a communication system between a Raspberry Pi (Raspberry Side) and an Arduino (Arduino Side), along with a camera streaming functionality. 

### Raspberry Side
The Raspberry Side code consists of modules for handling serial port communication, client-server operations, and camera streaming. It facilitates communication between the Raspberry Pi and the Arduino, as well as serving camera streams over a network.

#### Features
- **Serial Port Operations**: Handles initialization and communication with the serial port connected to the Arduino.
- **Client-Server Operations**: Manages the server-side of the communication system, handling client connections, message exchange, and server initialization.
- **Raspberry Server**: Combines serial port and client-server operations to run the Raspberry Pi server, facilitating communication with the Arduino and clients.
- **Camera Streaming**: Provides functionality to start a camera stream on the Raspberry Pi.

### Arduino Side
The Arduino Side code controls the movement of motors and servos based on commands received from the Raspberry Pi. It also sends back data to the Raspberry Pi in response to commands.

### Camera Side
The Camera Side code sets up a Flask web server to stream video from a camera connected to the Raspberry Pi.

## Installation
1. Clone this repository to your Raspberry Pi.
2. Install the required dependencies listed in each script's documentation.
3. Connect the Arduino and camera to the Raspberry Pi according to the hardware setup.
4. Run the appropriate scripts on the Raspberry Pi and Arduino to establish communication and start the camera stream.

## Usage
1. Run the Raspberry Pi server script (`raspberry_side.py`) to initialize the communication system and start the camera stream.
2. Upload the Arduino script (`arduino_side.ino`) to your Arduino board to enable motor and servo control.
3. Access the camera stream via the provided URL (`http://<Raspberry_Pi_IP>:<Port>/video_feed`).
4. Send commands to the Raspberry Pi server to control the Arduino and receive responses.

## Contributors
- [Your Name]
- [Your Name]

## License
This project is licensed under the [License Name] License - see the [LICENSE.md](LICENSE.md) file for details.

