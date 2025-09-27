#pragma once
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
extern float Ax,Ay,Az;
extern float aPitch, aRoll;

extern float Gx,Gy,Gz;
extern float GxOffset,GyOffset,GzOffset;
extern float gPitch, gRoll;

extern float compCoef;
extern float compPitch, compRoll;

extern Adafruit_MPU6050 mpu;
extern sensors_event_t a,g,temp;

extern unsigned long prevTime;
extern unsigned long duration;

extern int led;
extern bool value;

void calculateOffset();
void sensorCheck();
void getValues();
void accAngle();
void gyroAngle();
void compAngle();