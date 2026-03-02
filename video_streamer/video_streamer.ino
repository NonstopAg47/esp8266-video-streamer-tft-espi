
#include <SPI.h>
#include <TFT_eSPI.h>
#include "RGB.h"


TFT_eSPI tft = TFT_eSPI();

void setup() {
  Serial.begin(921600);
  tft.init();
  tft.fillScreen(TFT_BLACK);
}


void loop() {

  tft.pushImage(0, 0, 128, 160, legion);  //rename array from image_data to legion in .h file


 
}
