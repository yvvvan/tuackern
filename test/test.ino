const int dry = 663;
const int wet = 311;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  int sensorVal = analogRead(A0);
  int humidityPercent = map(sensorVal, wet, dry, 100, 0);
  Serial.print(humidityPercent);
  Serial.print("%");
  Serial.print("-");
  Serial.println(sensorVal);
  delay(10000); //10s
}