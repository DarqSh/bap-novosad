#pragma once
#include <Arduino.h>
#include <LiquidCrystal.h>

extern const int d4;
extern const int en;
extern const int rs;
extern const int d5;
extern const int d6;
extern const int d7;

extern LiquidCrystal lcd; // declaring LiquidCrystal object

extern unsigned long refreshTime;

void WriteResult();