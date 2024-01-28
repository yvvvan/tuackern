#include <Servo.h>

Servo myservo; 
const int dry = 614;
const int wet = 311;
int humidityTimer = 0;
int waterStartTimer = 0;
int lightState = LOW; 
int waterState = LOW; 
int smartState = LOW; 
int currentMillis = millis();

void setup() {
  Serial.begin(9600);
  pinMode(10, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  myservo.attach(9);
  myservo.write(90);
}

void loop() {
  currentMillis = millis();
  if (Serial.available() > 0) {
        char received = Serial.read();
        // handle the received char signal
        if (received == 'A') {
            light();
        } else if (received == 'B') {
            waterStart(currentMillis);
        } else if (received == 'C') {
            smart();
        }
  }
  if(waterState == HIGH && currentMillis - waterStartTimer > 5000){ 
    // after 5 seconds, turn off water
    waterStop();
  }
  if(currentMillis - humidityTimer > 10000){ 
    // every 10 seconds
    humidityTimer = currentMillis;
    humidity();
  }
  delay(1000);
}


void humidity(){
  int sensorVal = analogRead(A0);
  // int humidityPercent = map(sensorVal, wet, dry, 100, 0);
  Serial.println(sensorVal);
  // Serial.print("-");
  // Serial.println(humidityPercent);
  // Serial.print("%");
}

void light(){
  if(lightState == LOW){
    lightState = HIGH;
    digitalWrite(10, HIGH);  
  }else{
    lightState = LOW;
    digitalWrite(10, LOW);   
  }  
}
void waterStart(int currentMillis){
  waterStartTimer = currentMillis;
  digitalWrite(12, HIGH);  
  myservo.write(0);
  waterState = HIGH;
}

void waterStop()
{
  myservo.write(90); 
  digitalWrite(12, LOW);
  waterState = LOW;
}

// void water(int currentMillis){
//   if(waterState == LOW){
//     waterTimer = currentMillis;
//     waterState = HIGH;
//     digitalWrite(12, HIGH);  
//     pos = 256;
//     myservo.write(pos);              // tell servo to go to position in variable 'pos'
//   }else{
//     waterState = LOW;
//     digitalWrite(12, LOW);   
//     delay(500);
//     digitalWrite(12, HIGH); 
//     delay(500); 
//     digitalWrite(12, LOW);   
//     delay(500);
//     digitalWrite(12, HIGH); 
//     delay(500); 
//     digitalWrite(12, LOW);   
//     delay(500);
//     digitalWrite(12, HIGH); 
//     delay(500); 
//     digitalWrite(12, LOW);   
//     pos = 0;
//     myservo.write(pos); 
//   }
// }

void smart(){
  if(smartState == LOW){
    smartState = HIGH;
    digitalWrite(11, HIGH);  
  }else{
    smartState = LOW;
    digitalWrite(11, LOW);   
  }
}
