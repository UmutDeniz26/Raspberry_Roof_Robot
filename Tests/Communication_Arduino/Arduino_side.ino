

void setup() {
  // Start the serial communication at 9600 baud rate
  Serial.begin(9600);
}
void loop() {
  if (Serial.available() > 0) {
    // Read the incoming data *Note: Our stop character is '\n'
    String data = Serial.readStringUntil('\n');

    // Verify that the data was received
    Serial.print("You sent me: ");
    Serial.println(data);
  }
}