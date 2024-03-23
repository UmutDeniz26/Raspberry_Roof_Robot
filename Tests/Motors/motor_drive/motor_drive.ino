//MOTOR1 PINS
int ena = 5;
int in1 = 6;
int in2 = 7;
int in3 = 8;
int in4 = 9;
int enb = 10;

void setup() {
  // Set the motor pins as outputs
  pinMode(ena, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(enb, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
}

void loop() {
  forward(255);
  delay(2000);
  stop();
  delay(1000);

  backward(255);
  delay(2000);
  stop();
  delay(1000);

  left(255);
  delay(2000);

  right(255);
  delay(2000);

  stop();
  delay(1000);
}

void stop() {
  //STOP
  digitalWrite(in1,LOW);
  digitalWrite(in2,LOW);
  digitalWrite(in3,LOW);
  digitalWrite(in4,LOW);
}

void forward(int speed) {
  //MOTOR_A CLOCKWISE MAX SPEED
  digitalWrite(in1,LOW);
  digitalWrite(in2,HIGH);
  analogWrite(ena, speed);
  
  //MOTOR_B CLOCKWISE MAX SPEED
  digitalWrite(in3,LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enb, speed);
  
}

void backward(int speed) {
  //MOTOR_A COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in1,HIGH);
  digitalWrite(in2,LOW);
  analogWrite(ena, speed);
  
  //MOTOR_B COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in3,HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enb, speed);
  
}

void left(int speed) {
  //MOTOR_A COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in1,HIGH);
  digitalWrite(in2,LOW);
  analogWrite(ena, speed);
  
  //MOTOR_B CLOCKWISE MAX SPEED
  digitalWrite(in3,LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enb, speed);
  
}

void right(int speed) {
  //MOTOR_A CLOCKWISE MAX SPEED
  digitalWrite(in1,LOW);
  digitalWrite(in2,HIGH);
  analogWrite(ena, speed);
  
  //MOTOR_B COUNTERCLOCKWISE MAX SPEED
  digitalWrite(in3,HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enb, speed);
  
}