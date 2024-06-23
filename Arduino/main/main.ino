#include <ArduinoJson.h>
#include <SoftwareSerial.h>

unsigned long currentTime = 0;
unsigned long hold_last_movement = 0;
unsigned long hold_gps_measure_time = 0;

// MOTOR Driver PINS
const int ena = 6; // Motor A
const int in1 = 4; // Controls direction of Motor A
const int in2 = 7; // Controls direction of Motor A

const int enb = 10; // Motor B
const int in3 = 8;  // Controls direction of Motor B
const int in4 = 9;  // Controls direction of Motor B

const unsigned long motor_time_out = 2000; // Interval for motor stop

// Servo PINS
const int servoHorizontalPin = 11;
const int servoVerticalPin = 5;


struct CameraPosition {
  int horizontal_position;
  int vertical_position;
};

CameraPosition camera_position = {90, 90};

const int minPulse = 6; // Minimum pulse width value
const int maxPulse = 31; // Maximum pulse width value

// Servo configuration
int step_angle = 20;
int min_horizontal_angle = 0;
int max_horizontal_angle = 180;
int min_vertical_angle = 0;
int max_vertical_angle = 180;

// GPS configuration
//int RXPin = 2;
//int TXPin = 3;
//SoftwareSerial gpsSerial(RXPin, TXPin);

// Function prototypes
void forward(int speed);
void right(int speed);
void left(int speed);
void backward(int speed);
void stop();

// Camera
CameraPosition camera_control(int axis, int direction, int horizontal_position, int vertical_position);

//Others

struct MotorSpeeds
{
  int left_speed;
  int right_speed;
};

struct MotorCoefs{
  double X;
  double Y;
};

void control_left_motor_forward(int speed);
void control_right_motor_forward(int speed);
void control_left_motor_backward(int speed);
void control_right_motor_backward(int speed);
MotorSpeeds detailed_direction_motor_control(float x, float y);

//String readGPSData();
const unsigned long gps_time_out = 10000;
String GPS_data, data, return_output;
MotorSpeeds speed_output;

void setup()
{
  // Set the motor pins as Output
  pinMode(ena, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(enb, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  // Set the servo pins as Output
  pinMode(servoHorizontalPin, OUTPUT);
  pinMode(servoVerticalPin, OUTPUT);

  // Set the servos to 90 degrees
  setServoAngle(90, servoHorizontalPin);
  setServoAngle(90, servoVerticalPin);

  //gpsSerial.begin(9600);
  Serial.begin(19200);

  // First GPS measure
  GPS_data = "";

}


void loop()
{
  // Get the current time
  currentTime = millis();

  // Check for incoming data
  if (Serial.available() > 0)
  {

    // Read the incoming data *Note: Our stop character is '\n'
    data = Serial.readStringUntil('\n');

    // Parse the JSON data
    DynamicJsonDocument doc(1024); // Adjust the size as needed
    DeserializationError error = deserializeJson(doc, data);

    // Verify that the data was received and parsed successfully
    if (!error)
    {
      // Access JSON data here
      String type = doc["Type"];

      // Check the type of command
      if (type == "robot_move")
      {
        // Get the speed, x and y values

        float y = doc["Y"];
        float x = doc["X"];

        if (x > 1 || x < -1 || y > 1 || y < -1){
          x = 0;
          y = 0;
        }

        // Map the y value
        MotorCoefs coefs = map_interval_coeffs(MotorCoefs{x, y});

        speed_output = detailed_direction_motor_control(coefs.X, coefs.Y);

        return_output = "{\"X\": " + String(x) + ", \"Y\": " + String(y) + ", \"Left Speed\": " + String(speed_output.left_speed) + ", \"Right Speed\": " + String(speed_output.right_speed) + "}";
        hold_last_movement = currentTime;
      }
      else if (type == "camera_move")
      {
        // Get the axis and direction values
        int axis = doc["axis"];
        int direction = doc["direction"];

        // Set new camera position and return the new position
        camera_position = camera_control(axis, direction, camera_position);

        return_output = "{\"axis\": " + String(axis) + ", \"direction\": " + String(direction) +
        ", \"horizontal_position\": " + String(camera_position.horizontal_position) + ", \"vertical_position\": " + String(camera_position.vertical_position) + "}";
      }
      else if (type == "gps")
      {
        return_output = "{\"gps\": " + GPS_data + "}";
      }
      // Add more commands here
      else
      {
        return_output = "{\"Error\":\"Unknown type\"}";
      }
    }
    else
    {
      return_output = "{\"Error\":\"Parse Error\"}";
    }
    Serial.println(return_output); // Stop character is '\n'
  }
  else if (currentTime - hold_last_movement >= motor_time_out)
  {
    hold_last_movement = currentTime;
    stop();
  }
  else if (currentTime - hold_gps_measure_time >= gps_time_out)
  {
    hold_gps_measure_time = currentTime;
    //GPS_data = readGPSData();
  }
}

CameraPosition camera_control(int axis, int direction, CameraPosition camera_position)
{
  CameraPosition updated_camera_position = {0, 0};
  int horizontal_position = camera_position.horizontal_position;
  int vertical_position = camera_position.vertical_position;

  // Move the camera
  if (axis == 0)
  {
    // Horizontal
    if (direction == 0)
    {
      // Move left
      horizontal_position = horizontal_position - step_angle;
      if (horizontal_position < min_horizontal_angle){return camera_position;}
    }
    else if (direction == 1)
    {
      // Move right
      horizontal_position = horizontal_position + step_angle;
      if (horizontal_position > max_horizontal_angle){return camera_position;}
    }

    // Horizontal
    smooth_servo_control(camera_position.horizontal_position, horizontal_position, servoHorizontalPin);

  }
  else if (axis == 1)
  {
    // Vertical
    if (direction == 0)
    {
      // Move up
      vertical_position = vertical_position - step_angle;
      if (vertical_position < min_vertical_angle){return camera_position;}
    }
    else if (direction == 1)
    {
      // Move down
      vertical_position = vertical_position + step_angle;
      if (vertical_position > max_vertical_angle){return camera_position;}
    }

    // Vertical
    smooth_servo_control(camera_position.vertical_position, vertical_position, servoVerticalPin);
  }
  updated_camera_position.horizontal_position = horizontal_position;
  updated_camera_position.vertical_position = vertical_position;
  return updated_camera_position;
}
void smooth_servo_control(int current_angle, int target_angle, int servoPin){
  int step = 1;
  if (current_angle < target_angle){
    for (int i = current_angle; i < target_angle; i+=step){
      setServoAngle(i, servoPin);
    }
  }
  else if (current_angle > target_angle){
    for (int i = current_angle; i > target_angle; i-=step){
      setServoAngle(i, servoPin);
    }
  }
}


// Function to set the angle of the servo
void setServoAngle(int angle, int servoPin){
  // Convert the angle to a pulse width between 500 and 2500 microseconds
  int pulseWidth = map(angle, 0, 180, 500, 2500);
  // Write the pulse width to the servo pin
  digitalWrite(servoPin, HIGH);
  delayMicroseconds(pulseWidth);
  digitalWrite(servoPin, LOW);
  // Wait for the servo to move to the desired position
  delay(50); // Adjust this delay as needed

}

void stop()
{
  // STOP
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}

// Move the robot in a detailed direction
MotorSpeeds detailed_direction_motor_control(float x, float y)
{
  // X and Y are the coordinates of the joystick ( between -1 and 1 )
  // Speed is the speed of the motors ( between 0 and 255 )
  // The function will control the motors to move the robot in the direction of the joystick
  MotorSpeeds speeds = {0, 0};

  // If the joystick is in the middle, stop the robot
  if (x == 0 && y == 0)
  {
    stop();
    speeds.left_speed = 0;
    speeds.right_speed = 0;
  }
  // If the joystick is in the top right corner -> Forward Right
  else if (x >= 0 && y >= 0)
  {
    // Calculate the speed of the left motor
    speeds.left_speed = y * 255;
    speeds.right_speed = speeds.left_speed * (1 - x) ;


    // Control the left motor
    control_left_motor_forward(speeds.left_speed);

    // Control the right motor
    control_right_motor_forward(speeds.right_speed);
    
  }
  // If the joystick is in the top left corner -> Forward Left
  else if (x <= 0 && y >= 0)
  {
    // Calculate the speed of the left motor
    speeds.right_speed = y * 255;
    speeds.left_speed = speeds.right_speed * (1 + x);

    // Control the left motor
    control_left_motor_forward(speeds.left_speed);
    // Control the right motor
    control_right_motor_forward(speeds.right_speed);
  }
  // If the joystick is in the bottom left corner -> Backward Left
  else if (x <= 0 && y <= 0)
  {
    // Calculate the speed of the right motor
    speeds.right_speed = -y * 255;
    speeds.left_speed = speeds.right_speed * (1 + x);

    // Control the left motor
    control_left_motor_backward(speeds.left_speed);
    // Control the right motor
    control_right_motor_backward(speeds.right_speed);
  }
  // If the joystick is in the bottom right corner -> Backward Right
  else if (x >= 0 && y <= 0)
  {
    speeds.left_speed = -y * 255;
    speeds.right_speed = speeds.left_speed * (1 - x);

    // Control the left motor
    control_left_motor_backward(speeds.left_speed);
    // Control the right motor
    control_right_motor_backward(speeds.right_speed);
  }

  return speeds;
}

MotorCoefs map_interval_coeffs(MotorCoefs coefs){

  if (coefs.Y<0.1 && coefs.Y > -0.1){
    coefs.Y = 0;
  }
  else if (coefs.Y > 0.6){
    coefs.Y = 1.0;
  }
  else if (coefs.Y > 0) {
    coefs.Y = 0.7 + 0.3 * coefs.Y;
  } 
  else if (coefs.Y < -0.6){
    coefs.Y = -1.0;
  }
  else {
    coefs.Y = -0.7 + 0.3 * coefs.Y;
  }

  coefs.X = coefs.X * 0.4;
  return coefs;
  
}


void control_left_motor_forward(int speed)
{
  // MOTOR_A CLOCKWISE
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  analogWrite(ena, speed);
}

void control_right_motor_forward(int speed)
{
  // MOTOR_B CLOCKWISE
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enb, speed);
}

void control_left_motor_backward(int speed)
{
  // MOTOR_A Counter_CLOCKWISE
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite(ena, speed);
}

void control_right_motor_backward(int speed)
{
  // MOTOR_B COUNTERCLOCKWISE
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enb, speed);
}

/*
String readGPSData()
{
  // Initialize variables
  const int max_serial_time = 1000;
  char c;
  String gpsData;
  unsigned long start_time = millis();

  // Read GPS data if available
  while (gpsSerial.available() > 0)
  {
    // if Serial port is available interrupt the loop
    if (Serial.available() > 0)
    {
      return GPS_data;
    }
    
    // Break if time exceeds max_serial_time
    if (millis() - start_time > max_serial_time)
    {
      return GPS_data;
    }
    c = gpsSerial.read();
    if (c == '\n')
    {
      gpsData += " ";
    }
    else
    {
      gpsData += c;
    }
    delay(5); // Small delay to allow the buffer to fill
  }

  return gpsData;
}
*/