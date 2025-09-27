// view Brian Douglas video on theory of complementary filters
#include "compFilterIMU.h"
float Ax,Ay,Az;
float aPitch, aRoll;

float Gx,Gy,Gz;
float GxOffset=0,GyOffset=0,GzOffset=0;
float gPitch, gRoll;

float compCoef = 0.1;
float compPitch=0, compRoll=0;

Adafruit_MPU6050 mpu;
sensors_event_t a,g,temp;

unsigned long prevTime;
unsigned long duration;

int led=0;
bool value;


void calculateOffset(){
  int cycleCount =1000;
  for (int i = 0; i <cycleCount;i++){
    mpu.getEvent(&a, &g, &temp);
    GxOffset += g.gyro.x;
    GyOffset += g.gyro.y;
    GzOffset += g.gyro.z;
    led++;
    if(!(led%100)) {
      value = !value;
      digitalWrite(13,value);
    }

  }
  GxOffset = GxOffset/cycleCount; 
  GyOffset = GyOffset/cycleCount; 
  GzOffset = GzOffset/cycleCount; 
}

void sensorCheck(){
    mpu.getEvent(&a, &g, &temp);
    Ax = a.acceleration.x;
    Ay = a.acceleration.y;
    Az = a.acceleration.z;
    Gx = g.gyro.x;
    Gy = g.gyro.y;
    Gz = g.gyro.z;
    Serial.println(String(Ax,4) + String(" ") + String(Ay,4) + String(" ") + String(Az,4) + String(Gx,4) + String(" ") + String(Gy,4) + String(" ") + String(Gz,4));
}

void getValues(){
  mpu.getEvent(&a,&g,&temp);
    Ax = a.acceleration.x;
    Ay = a.acceleration.y;
    Az = a.acceleration.z;
    Gx = (g.gyro.x - GxOffset)*360./2./3.14;
    Gy = (g.gyro.y - GyOffset)*360./2./3.14;
    Gz = (g.gyro.z - GzOffset)*360./2./3.14;
    // Serial.println(String(Ax,4) + String(" ") + String(Ay,4) + String(" ") + String(Az,4) + String(Gx,4) + String(" ") + String(Gy,4) + String(" ") + String(Gz,4));
}

void accAngle(){
  int signX = Ax/abs(Ax);
  int signY = Ay/abs(Ay);
  int signZ = Az/abs(Az);
  aPitch = atan2(Ay, sqrt(Ax*Ax+Az*Az))*360./2./3.14;
  aRoll = atan2(Ax, sqrt(Ay*Ay+Az*Az))*360./2./3.14;
  // Serial.println(String(Ax,3) + String(" ") + String(Ay,3) + String(" ") + String(Az,3) + String(" ") + String(aPitch,3) + String(" ") + String(aRoll,3));
}

void gyroAngle(){
  duration = micros()-prevTime;
  prevTime = micros();
  gPitch+=Gx*duration/1000000.;
  gRoll-=Gy*duration/1000000.;
  // Serial.println(String("Gx:") + String(Gx,2) + " Gy:" + String(Gy,2) + " Gz:" + String(Gz,2) + String(" pitch:") + String(gPitch,2) + " roll:" + String(gRoll,2) + " time:" + String(int(millis())) + " duration:" + String(duration) + " LL:" + String(-180) + " HL:" + String(180));
}

void compAngle(){
  compPitch = compCoef*aPitch + (1-compCoef)*(compPitch + Gx*duration/1000000.);
  compRoll = compCoef*aRoll + (1-compCoef)*(compRoll - Gy*duration/1000000.); // minus in the second term!!!
}