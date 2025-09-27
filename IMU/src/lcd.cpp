#include "lcd.h"
#include "compFilterIMU.h"
const int rs = 32;
const int en = 33;
const int d4 = 25;
const int d5 = 26;
const int d6 = 27;
const int d7 = 14;

LiquidCrystal lcd(rs, en, d4, d5, d6, d7); // defining LiquidCrystal object

unsigned long refreshTime = 0;


void WriteResult(){
  if(millis() - refreshTime < 100) return; //early return from the function
  refreshTime = millis();
  lcd.setCursor(2,0);
  lcd.print("      ");
  lcd.setCursor(2,0);
  lcd.print(String(compRoll,2));
  lcd.setCursor(2,1);
  lcd.print("      ");
  lcd.setCursor(2,1);
  lcd.print(String(compPitch,2));

}
