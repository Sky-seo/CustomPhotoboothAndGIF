#include <Keyboard.h>

const int btnPin = 13;
int lastState = HIGH;

void setup() {
  pinMode(btnPin, INPUT_PULLUP);
  Keyboard.begin();
  Serial.begin(9600);
}

void loop() {
  int btn = digitalRead(btnPin);

  // 버튼 눌림 감지 (낮은 값이 눌림)
  if (btn == LOW && lastState == HIGH) {
    Serial.println("Pressed -> SPACE");
    Keyboard.press(' ');   // space key press
    delay(50);             // short press
    Keyboard.release(' ');
  }

  lastState = btn;
  delay(10);
}
