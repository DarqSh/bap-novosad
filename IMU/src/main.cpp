#include "compFilterIMU.h"
#include "lcd.h"
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

void setup() {
  // imu part
  pinMode(13,OUTPUT);
  Serial.begin(115200);
  mpu.begin();
  mpu.setAccelerometerRange(MPU6050_RANGE_2_G); // +- 2G max acceleration
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  prevTime=micros();
  Serial.println("Calculating...");
  calculateOffset();
  Serial.println(String(GxOffset,5) + String(" ") + String(GyOffset,5) + String(" ") + String(GzOffset,5));
  delay(1000);

  // lcd part
  lcd.begin(16,2);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("P:");
  lcd.setCursor(0,1);
  lcd.print("R:");

}

void loop() {
  getValues();
  accAngle();
  gyroAngle();
  compAngle();
  WriteResult();
}