#include <Adafruit_MPU6050.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

//MOTOR Driver PINS
int ena = 5; // Motor A
int in1 = 6; // Controls direction of Motor A
int in2 = 7; // Controls direction of Motor A

int enb = 10; // Motor B
int in3 = 8; // Controls direction of Motor B
int in4 = 9; // Controls direction of Motor B

Adafruit_MPU6050 mpu;

unsigned long previousTimeMotor = 0;
unsigned long motorInterval = 6000; // Interval for motor movements

unsigned long previousTimeMPU = 0;
unsigned long mpuInterval = 5000; // Interval for MPU6050 readings

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
  // Set the motor pins as outputs
  pinMode(ena, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(enb, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  gpsSerial.begin(9600);

  Serial.begin(115200);

  // Initialize MPU6050
  if (!mpu.begin()) {
    while (1) {
      Serial.println("Failed to find MPU6050 chip");
      delay(10);
    }
  }
}

int movment_counter = 0;
String GPS_data = "";
String data = "";
String return_inputs = "";
String return_outputs = "";
String return_data = "";

unsigned long currentTime = 0;

void loop() {

  currentTime = millis();
  
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
      return_inputs = "\"Inputs\": [ {\"Type\": \"" + type + "\", \"Command\": \"" + command + "\"} ]";
      return_outputs = "\"Outputs\": [ ] ";

      if (type == "robot_move"){
        motor_controller(command, 255);
      }
      else if(type=="gps"){
        GPS_data = readGPSData();
        return_outputs = "\"Outputs\": [{\"Type\": \"gps\", \"Data\": \"" + GPS_data + "\"}]";
        //Serial.print(GPS_data);
      }
      

      return_data = "{" + return_inputs + ", " + return_outputs + "}";
      Serial.println(return_data);

      //Serial.write(0);
      //Serial.println("0");
      //Serial.write('\n');

    } else {
      //Serial.write(255);
      Serial.println("255");
      //Serial.write('\n');
    }
  }

  // Check for MPU6050 readings
  if (currentTime - previousTimeMPU >= mpuInterval) {
    MPUData data = getMPUData();
    printMPUData(data);
    Serial.println("0");
    previousTimeMPU = currentTime;
  }
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
  //Serial.println("Stop direction");
  //STOP
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}

void forward(int speed) {
  //Serial.println("Forward direction");

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
  //Serial.println("Right direction");
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
  //Serial.println("Left direction");
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
  //Serial.println("Backward direction");
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
  String gpsData = "";
  // Read GPS data if available
  while (gpsSerial.available() > 0)
  {
    char c = gpsSerial.read();
    gpsData += c;
    delay(5); // Small delay to allow the buffer to fill
  }

  return gpsData;
}

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
