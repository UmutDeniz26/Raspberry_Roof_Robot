#include <Adafruit_MPU6050.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>


//MOTOR1 PINS
int ena = 5;
int in1 = 6;
int in2 = 7;
int in3 = 8;
int in4 = 9;
int enb = 10;

Adafruit_MPU6050 mpu;

unsigned long previousTimeMotor = 0;
unsigned long motorInterval = 6000; // Interval for motor movements

unsigned long previousTimeMPU = 0;
unsigned long mpuInterval = 5000000; // Interval for MPU6050 readings
unsigned long stopInterval = 100; // Interval to stop between movements


int RXPin = 2;
int TXPin = 3;
SoftwareSerial gpsSerial(RXPin, TXPin);


// Function prototypes
void forward(int speed);
void stop();
void right(int speed);
void left(int speed);
void backward(int speed);

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

}

int movment_counter = 0;
String GPS_data = "";

String return_output = "";
String data = "";

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

      return_output = "{\"Outputs\": [ ] }";
      
      // Perform action based on JSON data
      if(type == "robot_move" && command == "forward") {
        Serial.print("Forward---");
        forward(255);
      }else if (type == "robot_move" && command == "backward") {
        backward(255);
      }else if (type == "robot_move" && command == "left") {
        left(255);
      }else if (type == "robot_move" && command == "right") {
        right(255);
      }else if (type == "robot_move" && command == "stop") {
        stop();
      }
      else if (type == "gps") {
        //By using gpsSerial.read(), generate GPS_data var
        GPS_data = gpsSerial.read();
        return_output = "{\"Outputs\": [{\"Type\": \"gps\", \"Data\": \"" + GPS_data + "\"}] }";
      }


      Serial.println(return_output);

    } else {
      Serial.println("Failed to parse JSON");
    }
  }

  // Check for motor movements
  /*
  if (currentTime - previousTimeMotor >= motorInterval) {
    movment_counter = (movment_counter+1)%2;

    switch(movment_counter){
      case 0:
        forward(255);
        break;
      case 1:
        forward_left(255);
        break;
    }

    previousTimeMotor = currentTime;
  }
  */
    //else if (currentTime - previousTimeMotor >= motorInterval - stopInterval) {
    //stop(); // Stop the motors after motorInterval - stopInterval
  //}
  
  // Check for MPU6050 readings
  if (currentTime - previousTimeMPU >= mpuInterval) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
  
    /* Print out the values */
    /*
    Serial.print("Acceleration X: ");
    Serial.print(a.acceleration.x);
    Serial.print(", Y: ");
    Serial.print(a.acceleration.y);
    Serial.print(", Z: ");
    Serial.print(a.acceleration.z);
    Serial.println(" m/s^2");
  
    Serial.print("Rotation X: ");
    Serial.print(g.gyro.x);
    Serial.print(", Y: ");
    Serial.print(g.gyro.y);
    Serial.print(", Z: ");
    Serial.print(g.gyro.z);
    Serial.println(" rad/s");
  
    Serial.print("Temperature: ");
    Serial.print(temp.temperature);
    Serial.println(" degC");
    Serial.println("");
    */
    previousTimeMPU = currentTime;
  }
}

void forward_left(int speed) {
  
  //MOTOR_A COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite(ena, 180);

  //MOTOR_B CLOCKWISE MAX SPEED
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enb, 255);

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