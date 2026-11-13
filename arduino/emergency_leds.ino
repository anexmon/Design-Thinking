const int RED_LED = 8;
const int GREEN_LED = 9;
String command = "NORMAL";
unsigned long lastBlink = 0;
bool redOn = false;

void setup() {
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  Serial.begin(9600);
  setNormal();
}

void setNormal() {
  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(RED_LED, LOW);
  redOn = false;
}

void loop() {
  if (Serial.available()) {
    String incoming = Serial.readStringUntil('\n');
    incoming.trim();
    if (incoming == "NORMAL" || incoming == "WARNING" || incoming == "EMERGENCY") {
      command = incoming;
    }
  }

  if (command == "NORMAL") {
    setNormal();
  } else if (command == "WARNING") {
    digitalWrite(GREEN_LED, LOW);
    if (millis() - lastBlink >= 350) {
      lastBlink = millis();
      redOn = !redOn;
      digitalWrite(RED_LED, redOn ? HIGH : LOW);
    }
  } else if (command == "EMERGENCY") {
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, HIGH);
  }
}
