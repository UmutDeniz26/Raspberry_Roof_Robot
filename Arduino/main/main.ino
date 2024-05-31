#include <Adafruit_MPU6050.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

//MOTOR Driver PINS
const int ena = 4; // Motor A
const int in1 = 6; // Controls direction of Motor A
const int in2 = 7; // Controls direction of Motor A

const int enb = 10; // Motor B
const int in3 = 8; // Controls direction of Motor B
const int in4 = 9; // Controls direction of Motor B

//Adafruit_MPU6050 mpu;

unsigned long previousTimeMotor = 0;
const unsigned long motor_time_out = 5000; // Interval for motor movements

unsigned long previousTimeMPU = 0;
const unsigned long mpuInterval = 5000; // Interval for MPU6050 readings

int RXPin = 3;
int TXPin = 2;
SoftwareSerial gpsSerial(RXPin, TXPin);

// Data structure for MPU6050 readings
struct MPUData
{
  float accelX; float accelY; float accelZ;
  float gyroX;  float gyroY;  float gyroZ;
  float temp;
};

// Function prototypes
void forward(int speed);
void right(int speed);
void left(int speed);
void backward(int speed);
void stop();

void detailed_direction_motor_control(float x, float y);

String readGPSData();
struct MPUData getMPUData();
void printMPUData(MPUData data);

void setup() {
  // Set the motor pins as Output
  pinMode(ena, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(enb, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  gpsSerial.begin(9600);
  Serial.begin(19200);

  /*
  // Initialize MPU6050
  if (!mpu.begin()) {
    while (1) {
      Serial.println("Failed to find MPU6050 chip");
      delay(10);
    }
  }
  */
}

String GPS_data,data,return_output;

unsigned long currentTime = 0;
unsigned long hold_last_movement = 0;

void loop() {
  // Get the current time
  currentTime = millis();
  
  // Check for incoming data
  if (Serial.available() > 0) {

    // Read the incoming data *Note: Our stop character is '\n'
    data = Serial.readStringUntil('\n');

    // Parse the JSON data
    DynamicJsonDocument doc(1024); // Adjust the size as needed
    DeserializationError error = deserializeJson(doc, data);
    
    // Verify that the data was received and parsed successfully
    if (!error) {
      // Access JSON data here
      String type = doc["Type"];
      String command = doc["Command"];
      
      // Check the type of command
      if (type == "robot_move"){
        if (command == "stop"){
          stop();
          return_output = "{\"Command\": \"stop\"}";
        }
        else{
          // Get the speed, x and y values
          float x = doc["X"];
          float y = doc["Y"];

          detailed_direction_motor_control(x, y);

          return_output = "{\"X\": "+String(x)+", \"Y\": "+String(y)+"}";
          hold_last_movement = currentTime;
        }
      }
      else if(type=="gps"){
        GPS_data = readGPSData();
        return_output = "{\"gps\": "+GPS_data+"}";   
      }
      // Add more commands here
      else{
        return_output = "{\"Error\":\"Unknown type\"}";
      }
    } 
    else{
      return_output = "{\"Error\":\"Parse Error\"}";
    }
    Serial.println(return_output); // Stop character is '\n'

  }
  else if ( currentTime - hold_last_movement >= motor_time_out){
    hold_last_movement = currentTime;
    stop();
  }

  // Check for MPU6050 readings
  /*
  else if (currentTime - previousTimeMPU >= mpuInterval) {
    MPUData data = getMPUData();
    printMPUData(data);
    Serial.println("0");
    previousTimeMPU = currentTime;
  }
  */
}

void stop() {
  //STOP
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}

void control_left_motor_forward(int speed){
  
  // if speed larger than 255, set it to 255
  speed = speed > 255 ? 255 : speed; speed = speed < 0 ? 0 : speed;

  //MOTOR_A COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  analogWrite(ena, speed);
}

void control_right_motor_forward(int speed){
  
  // if speed larger than 255, set it to 255
  speed = speed > 255 ? 255 : speed; speed = speed < 0 ? 0 : speed;

  //MOTOR_B CLOCKWISE MAX SPEED
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enb, speed);
}

void control_left_motor_backward(int speed){
  
  // if speed larger than 255, set it to 255
  speed = speed > 255 ? 255 : speed; speed = speed < 0 ? 0 : speed;

  //MOTOR_A CLOCKWISE MAX SPEED
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite(ena, speed);
}

void control_right_motor_backward(int speed){
  
  // if speed larger than 255, set it to 255
  speed = speed > 255 ? 255 : speed; speed = speed < 0 ? 0 : speed;

  //MOTOR_B COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enb, speed);
}

// Move the robot in a detailed direction
void detailed_direction_motor_control(float x, float y ){
  // X and Y are the coordinates of the joystick ( between -1 and 1 )
  // Speed is the speed of the motors ( between 0 and 255 )
  // The function will control the motors to move the robot in the direction of the joystick

  int MIN_SPEED = 180;
  int MAX_SPEED = 255;

  int difference_min_max = MAX_SPEED - MIN_SPEED;

  int MAX_SPEED_DIFF = difference_min_max * 1; // This coefficient can be adjusted to change the speed difference between the motors

  int left_speed, right_speed;

  // If the joystick is in the middle, stop the robot
  if (x == 0 && y == 0){
    stop();
  }
  // If the joystick is in the top right corner -> Forward Right
  else if (x > 0 && y > 0){
    // Calculate the speed of the left motor
    left_speed  = MIN_SPEED + (difference_min_max * y) + (MAX_SPEED_DIFF/2 * x);

    if (left_speed > 255){
      left_speed = 255;
      right_speed = MIN_SPEED + (difference_min_max * y) - (MAX_SPEED_DIFF * x);
    }
    else{
      // Calculate the speed of the right motor
      right_speed = MIN_SPEED + (difference_min_max * y) - (MAX_SPEED_DIFF/2 * x);
    }
    
    // Control the left motor
    control_left_motor_forward(left_speed);
    // Control the right motor
    control_right_motor_forward(right_speed);
  }
  // If the joystick is in the top left corner -> Forward Left
  else if (x < 0 && y > 0){
    // Calculate the speed of the left motor
    right_speed = MIN_SPEED + (difference_min_max * y) + (MAX_SPEED_DIFF/2 * -x);

    if (right_speed > 255){
      right_speed = 255;
      left_speed = MIN_SPEED + (difference_min_max * y) - (MAX_SPEED_DIFF * -x);
    }
    else{
      // Calculate the speed of the right motor
      left_speed = MIN_SPEED + (difference_min_max * y) - (MAX_SPEED_DIFF/2 * -x);
    }

    // Control the left motor
    control_left_motor_forward(left_speed);
    // Control the right motor
    control_right_motor_forward(right_speed);
  }
  // If the joystick is in the bottom left corner -> Backward Left
  else if (x < 0 && y < 0){
    
    // Calculate the speed of the right motor
    right_speed = MIN_SPEED + (difference_min_max * -y) + (MAX_SPEED_DIFF/2 * -x);

    if (right_speed > 255){
      right_speed = 255;
      left_speed = MIN_SPEED + (difference_min_max * -y) - (MAX_SPEED_DIFF * -x);
    }
    else{
      // Calculate the speed of the left motor
      left_speed = MIN_SPEED + (difference_min_max * -y) - (MAX_SPEED_DIFF/2 * -x);
    }

    // Control the left motor
    control_left_motor_backward(left_speed);
    // Control the right motor
    control_right_motor_backward(right_speed);
  }
  // If the joystick is in the bottom right corner -> Backward Right
  else if (x > 0 && y < 0){
    // Calculate the speed of the left motor
    left_speed = MIN_SPEED + (difference_min_max * -y) + (MAX_SPEED_DIFF/2 * x);

    if (left_speed > 255){
      left_speed = 255;
      right_speed = MIN_SPEED + (difference_min_max * -y) - (MAX_SPEED_DIFF * x);
    }
    else{
      // Calculate the speed of the right motor
      right_speed = MIN_SPEED + (difference_min_max * -y) - (MAX_SPEED_DIFF/2 * x);
    }
    
    // Control the left motor
    control_left_motor_backward(left_speed);
    // Control the right motor
    control_right_motor_backward(right_speed);
  }
  else if( x == 0 ){
    if( y > 0 ){
      forward(255);
    }
    else{
      backward(255);
    }
  }
  else if( y == 0 ){
    if( x > 0 ){
      right(255);
    }
    else{
      left(255);
    }
  }  
}


void forward(int speed) {
  //MOTOR_A CLOCKWISE MAX SPEED
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite(ena, speed);
  
  //MOTOR_B CLOCKWISE MAX SPEED
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enb, speed);
}

void right(int speed) {
  //MOTOR_A CLOCKWISE MAX SPEED
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite(ena, speed);
  
  //MOTOR_B COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enb, speed);
}

void left(int speed) {
  //MOTOR_A COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  analogWrite(ena, speed);
  
  //MOTOR_B CLOCKWISE MAX SPEED
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enb, speed);
}

void backward(int speed) {
  //MOTOR_A COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  analogWrite(ena, speed);
  
  //MOTOR_B COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enb, speed);
}

/*
// Get MPU6050 readings
MPUData getMPUData()
{
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  MPUData data;
  data.accelX = a.acceleration.x ;//+ 8.80; //Configuration
  data.accelY = a.acceleration.y ;//- 2.30; //Configuration
  data.accelZ = a.acceleration.z ;//+ 3.20; //Configuration
  data.gyroX = g.gyro.x;
  data.gyroY = g.gyro.y;
  data.gyroZ = g.gyro.z;
  data.temp = temp.temperature;

  return data;
}

// Print MPU6050 readings
void printMPUData(MPUData data)
{
  Serial.print("Acceleration X: ");
  Serial.print(data.accelX);
  Serial.print(", Y: ");
  Serial.print(data.accelY);
  Serial.print(", Z: ");
  Serial.print(data.accelZ);
  Serial.print(" m/s^2 ---");

  Serial.print("Rotation X: ");
  Serial.print(data.gyroX);
  Serial.print(", Y: ");
  Serial.print(data.gyroY);
  Serial.print(", Z: ");
  Serial.print(data.gyroZ);
  Serial.print(" rad/s ---");

  Serial.print("Temperature: ");
  Serial.print(data.temp);
  Serial.print(" degC ---");
}
*/

String readGPSData()
{
  // Initialize variables
  const int max_serial_time = 1000;
  char c; String gpsData;
  unsigned long start_time = millis();
  
  // Read GPS data if available
  while (gpsSerial.available() > 0)
  {
    // Break if time exceeds max_serial_time
    if (millis() - start_time > max_serial_time) {break;}
    c = gpsSerial.read();
    if (c == '\n') {
      gpsData += " ";
    }
  else  {
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