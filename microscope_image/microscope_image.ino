// the push button is attached to digital pin 7
int pushButton = 7;


void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  
  // make the pushbutton's pin an input:
  pinMode(pushButton, INPUT);
}


void loop() {
  // read the input pin:
  // digitalRead reads the value from a specified digital pin(in this case, 7). Value is HIGH or LOW.
  int buttonState = digitalRead(pushButton);
  // print out the state of the button. println prints data to the serial port.
  Serial.println(buttonState);
  // delay in between reads for stability
  delay(1);
}
