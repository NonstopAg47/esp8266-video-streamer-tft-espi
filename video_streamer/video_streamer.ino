/*
// config.h contains
#pragma once

const char* ssid = "SSID";
const char* password = "PASSWORD";
const char* ipconfig = "192.168.1.3";  //check in cmd -> ipconfig  // server url
const uint16_t NumOfFiles = 52;
#define SerialDebug  //comment out this line to disable serial monitor
*/
#include "config.h"

#ifdef SerialDebug
  template<typename T>
  inline void println(T value) { Serial.println(value); }

  template<typename T>
  inline void println(T value, int format) { Serial.println(value, format); }

  template<typename T>
  inline void print(T value) { Serial.print(value); }
#else
  template<typename T>
  inline void println(T value) {}

  template<typename T>
  inline void println(T value, int format) {}

  template<typename T>
  inline void print(T value) {}
#endif

#include <SPI.h>
#include <TFT_eSPI.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>


TFT_eSPI tft = TFT_eSPI();

// Create a WiFiClient object
HTTPClient http;
WiFiClient wifiClient;




//global allocation to avoid reallocating each time
const uint16_t width = 128;
const uint16_t linesPerChunk = 14; // read 14 lines at once (128x14) (1792 pixels)
// Buffers to hold linesPerChunk lines at a time
uint8_t buf[width * 2 * linesPerChunk];       // raw bytes

void DispImage(const char* baseUrl);
void setup() {
  #ifdef SerialDebug
    Serial.begin(921600);
    delay(1000);
  #endif
  tft.init();
  tft.fillScreen(TFT_BLACK);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    println("Connecting to WiFi...");
  }
  println("Connected to WiFi");

  print("initialising ");
  uint16_t time = millis();


  // fetch and display images (for movie)
  for (uint16_t i = 1; i <= NumOfFiles; i++) {  //00001 to NumOfFiles are folder names
    char urlLoop[50];  // make sure this is large enough for full URL
    // pads with leading zeros automatically if needed to have a fixed length of 5 digits
    sprintf(urlLoop, "http://%s/testingimage/%05d", ipconfig, i); 
  
    DispImage(urlLoop); 

    println(i);
  }
  print("done till ");
  println(NumOfFiles);

  time = millis() - time;
  print("Time taken: ");
  println(time, DEC);  //took these many ms to execute

  pinMode(LED_BUILTIN, OUTPUT);  // Initialize the LED_BUILTIN pin as an output


}



void loop() {
  digitalWrite(LED_BUILTIN, LOW);  // Turn the LED on (Note that LOW is the voltage level
  // but actually the LED is on; this is because
  // it is active low on the ESP-01)
  delay(500);                      // Wait for a second
  digitalWrite(LED_BUILTIN, HIGH);  // Turn the LED off by making the voltage HIGH
  delay(500);                      // Wait for two seconds (to demonstrate the active low LED)
}

// Display a full image by fetching multiple .bin files
void DispImage(const char* baseUrl) {
  char url[70];  // adjust size as needed
  sprintf(url, "%s/output.bin", baseUrl);

  // Optimized function to read a .bin file and display linesPerChunk lines at a time
  http.begin(wifiClient, url);
  http.setReuse(true); 
  int httpCode = http.GET();

  if (httpCode != HTTP_CODE_OK) {
    println("HTTP request failed: " + String(httpCode) + " -> " + url);
    http.end();
    return;
  }

  int contentLength = http.getSize();  //total num of bytes in chunk //2 bytes per pixel
  if (contentLength <= 0) {
    println("Empty file: " + String(url));
    http.end();
    return;
  }

  WiFiClient* stream = http.getStreamPtr();
  uint16_t totalLines = contentLength / (2 * width);

  
  uint16_t linesRead = 0;

  while (linesRead < totalLines) {
    // Determine how many lines to read in this chunk (last chunk may be less than 4)
    uint16_t linesThisChunk = min(linesPerChunk, (uint16_t)(totalLines - linesRead));
    uint32_t bytesToRead = linesThisChunk * width * 2;
    uint32_t bytesRead = 0;
    uint32_t startTime = millis();

    // Read the chunk from the HTTP stream
    while (bytesRead < bytesToRead) {
      if (stream->available()) {
        int n = stream->readBytes(buf + bytesRead, bytesToRead - bytesRead);
        bytesRead += n;
      } else {
        if (millis() - startTime > 5000) {
          println("Stream timeout! -> " + String(url));
          http.end();
          return;
        }
      }
    }

    /*
    // Convert raw bytes to 16-bit color values
    for (uint16_t line = 0; line < linesThisChunk; line++) {
      for (uint16_t x = 0; x < width; x++) {
        //for rgb for display with black tab
        //lineBuffer[line * width + x] = (buf[(line * width + x) * 2] << 8) | buf[(line * width + x) * 2 + 1];

        //for bgr for display with green tab
        uint16_t pixel = (buf[(line * width + x) * 2] << 8) | buf[(line * width + x) * 2 + 1];
        lineBuffer[line * width + x] = ((pixel & 0x001F) << 11) | (pixel & 0x07E0) | ((pixel & 0xF800) >> 11);
      }
    }
    */

    tft.pushImage(0, linesRead, width, linesThisChunk, (uint16_t*)buf);

    linesRead += linesThisChunk;
  }
  http.end();
}


