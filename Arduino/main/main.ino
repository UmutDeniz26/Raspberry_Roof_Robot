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
const unsigned long motorInterval = 5000; // Interval for motor movements

unsigned long previousTimeMPU = 0;
const unsigned long mpuInterval = 5000; // Interval for MPU6050 readings

int RXPin = 2;
int TXPin = 3;
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
  Serial.begin(115200);

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
        motor_controller(command, 255);
        return_output = "{\"Output\": [{\"Type\": \"robot_move\", \"Data\": \"" + command + "\"}]}";
        hold_last_movement = currentTime;
      }
      else if(type=="gps"){
        GPS_data = readGPSData();
        return_output = "{\"Output\": [{\"Type\": \"gps\", \"Data\": \"" + GPS_data + "\"}]}";
      }
      // Add more commands here
      else{
        return_output = "{\"Output\": [{\"Type\": \"Error\", \"Data\": \" Unknown type\" }]}";
      }
      Serial.println(return_output); // Stop character is '\n'

    } 
    else{
      Serial.println("{\"Output\": [{\"Type\": \"Error\", \"Data\": \"Parse Error\"}]}");
    }
  }
  else if ( currentTime - hold_last_movement >= motorInterval){
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

void motor_controller(String command, int speed){
  if(command=="forward"){
    forward(speed);
  }
  else if(command=="backward"){
    backward(speed);
  }
  else if(command=="left"){
    left(speed);
  }
  else if(command=="right"){
    right(speed);
  }
  else if(command=="stop"){
    stop();
  }
}

void stop() {
  //STOP
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
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
    gpsData += c;
    delay(5); // Small delay to allow the buffer to fill
  }

  return gpsData;
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

/*
Test request:
{"Type": "robot_move", "Command": "forward"}
*/