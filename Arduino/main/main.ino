#include <ArduinoJson.h>
#include <SoftwareSerial.h>
#include <Servo.h>

unsigned long currentTime = 0;
unsigned long hold_last_movement = 0;

// MOTOR Driver PINS
const int ena = 4; // Motor A
const int in1 = 6; // Controls direction of Motor A
const int in2 = 7; // Controls direction of Motor A

const int enb = 10; // Motor B
const int in3 = 8;  // Controls direction of Motor B
const int in4 = 9;  // Controls direction of Motor B

const unsigned long motor_time_out = 5000; // Interval for motor stop

// Servo PINS
const int servoHorizontalPin = 3;
const int servoVerticalPin = 5;

Servo servoHorizontal;
Servo servoVertical;

// Servo configuration
int step_angle = 20;
int min_horizontal_angle = 0;
int max_horizontal_angle = 180;
int min_vertical_angle = 0;
int max_vertical_angle = 180;

// GPS configuration
int RXPin = 11;
int TXPin = 12;
SoftwareSerial gpsSerial(RXPin, TXPin);

// Function prototypes
void forward(int speed);
void right(int speed);
void left(int speed);
void backward(int speed);
void stop();
void camera_control(int axis, int direction, int horizontal_position, int vertical_position);

struct MotorSpeeds
{
  int left_speed;
  int right_speed;
};

MotorSpeeds detailed_direction_motor_control(float x, float y);
String readGPSData();

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
  servoHorizontal.attach(servoHorizontalPin);
  servoVertical.attach(servoVerticalPin);

  gpsSerial.begin(9600);
  Serial.begin(19200);
}

String GPS_data, data, return_output;

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

        float x = doc["X"];
        float y = doc["Y"];

        MotorSpeeds speeds = detailed_direction_motor_control(x, y);

        return_output = "{\"X\": " + String(x) + ", \"Y\": " + String(y) + ", \"Left Speed\": " + String(speeds.left_speed) + ", \"Right Speed\": " + String(speeds.right_speed) + "}";
        hold_last_movement = currentTime;
      }
      else if (type == "camera_move")
      {
        // Get the axis and direction values
        int axis = doc["axis"];
        int direction = doc["direction"];

        //
        camera_control(axis, direction, servoHorizontal.read(), servoVertical.read());

        return_output = "{\"axis\": " + String(axis) + ", \"direction\": " + String(direction) +
                        ", \"horizontal_position\": " + String(servoHorizontal.read()) + ", \"vertical_position\": " + String(servoVertical.read()) + "}";
      }
      else if (type == "gps")
      {
        GPS_data = readGPSData();
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
}

void camera_control(int axis, int direction, int horizontal_position, int vertical_position)
{
  // Move the camera
  if (axis == 0)
  {
    // Horizontal
    if (direction == 0)
    {
      // Move left
      horizontal_position = horizontal_position - step_angle;
    }
    else if (direction == 1)
    {
      // Move right
      horizontal_position = horizontal_position + step_angle;
    }
  }
  else if (axis == 1)
  {
    // Vertical
    if (direction == 0)
    {
      // Move up
      vertical_position = vertical_position - step_angle;
    }
    else if (direction == 1)
    {
      // Move down
      vertical_position = vertical_position + step_angle;
    }
  }

  // Move the servo to the target position
  if (axis == 0)
  {
    // Horizontal
    servoHorizontal.write(horizontal_position);
    delay(500); // Small delay to allow the servo to move
  }
  else if (axis == 1)
  {
    // Vertical
    servoVertical.write(vertical_position);
    delay(500); // Small delay to allow the servo to move
  }
}

void stop()
{
  // STOP
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}

void control_left_motor_forward(int speed)
{

  // if speed larger than 255, set it to 255
  speed = speed > 255 ? 255 : speed;
  speed = speed < 0 ? 0 : speed;

  // MOTOR_A COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  analogWrite(ena, speed);
}

void control_right_motor_forward(int speed)
{

  // if speed larger than 255, set it to 255
  speed = speed > 255 ? 255 : speed;
  speed = speed < 0 ? 0 : speed;

  // MOTOR_B CLOCKWISE MAX SPEED
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enb, speed);
}

void control_left_motor_backward(int speed)
{

  // if speed larger than 255, set it to 255
  speed = speed > 255 ? 255 : speed;
  speed = speed < 0 ? 0 : speed;

  // MOTOR_A CLOCKWISE MAX SPEED
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite(ena, speed);
}

void control_right_motor_backward(int speed)
{

  // if speed larger than 255, set it to 255
  speed = speed > 255 ? 255 : speed;
  speed = speed < 0 ? 0 : speed;

  // MOTOR_B COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enb, speed);
}
// Move the robot in a detailed direction
MotorSpeeds detailed_direction_motor_control(float x, float y)
{
  // X and Y are the coordinates of the joystick ( between -1 and 1 )
  // Speed is the speed of the motors ( between 0 and 255 )
  // The function will control the motors to move the robot in the direction of the joystick

  int MIN_SPEED = 20;
  int MAX_SPEED = 255;

  int difference_min_max = MAX_SPEED - MIN_SPEED;

  int MAX_SPEED_DIFF = difference_min_max * 1; // This coefficient can be adjusted to change the speed difference between the motors

  MotorSpeeds speeds = {0, 0};

  // If the joystick is in the middle, stop the robot
  if (x == 0 && y == 0)
  {
    stop();
  }
  // If the joystick is in the top right corner -> Forward Right
  else if (x > 0 && y > 0)
  {
    // Calculate the speed of the left motor
    speeds.left_speed = MIN_SPEED + (difference_min_max * y) + (MAX_SPEED_DIFF / 2 * x);

    if (speeds.left_speed > 255)
    {
      speeds.left_speed = 255;
      speeds.right_speed = MIN_SPEED + (difference_min_max * y) - (MAX_SPEED_DIFF * x);
    }
    else
    {
      // Calculate the speed of the right motor
      speeds.right_speed = MIN_SPEED + (difference_min_max * y) - (MAX_SPEED_DIFF / 2 * x);
    }

    // Control the left motor
    control_left_motor_forward(speeds.left_speed);
    // Control the right motor
    control_right_motor_forward(speeds.right_speed);
  }
  // If the joystick is in the top left corner -> Forward Left
  else if (x < 0 && y > 0)
  {
    // Calculate the speed of the left motor
    speeds.right_speed = MIN_SPEED + (difference_min_max * y) + (MAX_SPEED_DIFF / 2 * -x);

    if (speeds.right_speed > 255)
    {
      speeds.right_speed = 255;
      speeds.left_speed = MIN_SPEED + (difference_min_max * y) - (MAX_SPEED_DIFF * -x);
    }
    else
    {
      // Calculate the speed of the right motor
      speeds.left_speed = MIN_SPEED + (difference_min_max * y) - (MAX_SPEED_DIFF / 2 * -x);
    }

    // Control the left motor
    control_left_motor_forward(speeds.left_speed);
    // Control the right motor
    control_right_motor_forward(speeds.right_speed);
  }
  // If the joystick is in the bottom left corner -> Backward Left
  else if (x < 0 && y < 0)
  {
    // Calculate the speed of the right motor
    speeds.right_speed = MIN_SPEED + (difference_min_max * -y) + (MAX_SPEED_DIFF / 2 * -x);

    if (speeds.right_speed > 255)
    {
      speeds.right_speed = 255;
      speeds.left_speed = MIN_SPEED + (difference_min_max * -y) - (MAX_SPEED_DIFF * -x);
    }
    else
    {
      // Calculate the speed of the left motor
      speeds.left_speed = MIN_SPEED + (difference_min_max * -y) - (MAX_SPEED_DIFF / 2 * -x);
    }

    // Control the left motor
    control_left_motor_backward(speeds.left_speed);
    // Control the right motor
    control_right_motor_backward(speeds.right_speed);
  }
  // If the joystick is in the bottom right corner -> Backward Right
  else if (x > 0 && y < 0)
  {
    // Calculate the speed of the left motor
    speeds.left_speed = MIN_SPEED + (difference_min_max * -y) + (MAX_SPEED_DIFF / 2 * x);

    if (speeds.left_speed > 255)
    {
      speeds.left_speed = 255;
      speeds.right_speed = MIN_SPEED + (difference_min_max * -y) - (MAX_SPEED_DIFF * x);
    }
    else
    {
      // Calculate the speed of the right motor
      speeds.right_speed = MIN_SPEED + (difference_min_max * -y) - (MAX_SPEED_DIFF / 2 * x);
    }

    // Control the left motor
    control_left_motor_backward(speeds.left_speed);
    // Control the right motor
    control_right_motor_backward(speeds.right_speed);
  }
  else if (x == 0)
  {
    if (y > 0)
    {
      backward(255);
    }
    else
    {
      forward(255);
    }
  }
  else if (y == 0)
  {
    if (x > 0)
    {
      right(255);
    }
    else
    {
      left(255);
    }
  }

  return speeds;
}

void forward(int speed)
{
  // MOTOR_A CLOCKWISE MAX SPEED
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite(ena, speed);

  // MOTOR_B CLOCKWISE MAX SPEED
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enb, speed);
}

void right(int speed)
{
  // MOTOR_A CLOCKWISE MAX SPEED
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite(ena, speed);

  // MOTOR_B COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enb, speed);
}

void left(int speed)
{
  // MOTOR_A COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  analogWrite(ena, speed);

  // MOTOR_B CLOCKWISE MAX SPEED
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enb, speed);
}

void backward(int speed)
{
  // MOTOR_A COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  analogWrite(ena, speed);

  // MOTOR_B COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enb, speed);
}

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
    // Break if time exceeds max_serial_time
    if (millis() - start_time > max_serial_time)
    {
      break;
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
/*
Test request:
{"Type": "robot_move", "Command": "forward"}
*/