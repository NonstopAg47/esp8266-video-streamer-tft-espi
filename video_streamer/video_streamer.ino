/*
// config.h contains
#pragma once

const char* ssid = "SSID";
const char* password = "PASSWORD";
const char* ipconfig = "192.168.1.3";  //check in cmd -> ipconfig  // server url
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

  template<typename T>
  inline void print(T value, int format) { Serial.print(value, format); }
#else
  template<typename T>
  inline void println(T value) {}

  template<typename T>
  inline void println(T value, int format) {}

  template<typename T>
  inline void print(T value) {}

  template<typename T>
  inline void print(T value, int format) {}
#endif

#include <SPI.h>
#include <TFT_eSPI.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>


TFT_eSPI tft = TFT_eSPI();

// Create a WiFiClient object
HTTPClient http;
WiFiClient wifiClient;


const uint16_t width = 128;
const uint16_t linesPerChunk = 160; // read linesPerChunk lines at once (128xlinesPerChunk)  //should be divisible by 160 and <= 160
// Buffer to hold linesPerChunk lines at a time
uint8_t buf[width * 2 * linesPerChunk];       // raw bytes

void DispImages(const char* url);
void setup() {
  #ifdef SerialDebug
    Serial.begin(921600);
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

  println("Initialising ");
  uint16_t time = millis();


  // fetch and display images (for movie)
  DispImages(("http://" + String(ipconfig) + "/testingimage/00001/output.bin").c_str()); 


  print("Completed in : ");print(millis() - time, DEC);println(" ms");  //took these many ms to execute
  delay(4000);
  tft.fillScreen(TFT_BLACK);
}

void loop() {}

// Display a full video by fetching .bin file and display linesPerChunk lines at a time
void DispImages(const char* url) {
  http.begin(wifiClient, url);
  //http.setReuse(true); 

  if (http.GET() != HTTP_CODE_OK) {
    println("HTTP request failed: " + String(http.GET()) + " -> " + url);
    http.end();
  }

  WiFiClient* stream = http.getStreamPtr();
  uint16_t totalLines = http.getSize() / (2 * width);  //http.getSize() = total num of bytes //2 bytes per pixel


  uint16_t linesRead = 0;
  uint16_t y_coord = 0;
  uint16_t frame_count = 0;

  while (linesRead < totalLines) {
    // Determine how many lines to read in this chunk (last chunk may be less than 4)
    uint32_t bytesToRead = linesPerChunk * width * 2;
    uint32_t bytesRead = 0;
    uint32_t startTime = millis();

    // Read the chunk from the HTTP stream
    while (bytesRead < bytesToRead) {
      if (stream->available()) {
        //attempts to read bytesToRead number of bytes into buf and increments the value of bytesRead by whatever number of bytes were read
        // to adjust buf for next cycle until whole chunk is read
        bytesRead += stream->readBytes(buf + bytesRead, bytesToRead - bytesRead);
      } else {
        if (millis() - startTime > 5000) {
          println("Stream timeout! -> " + String(url));
          http.end();
        }
      }
    }

    tft.pushImage(0, y_coord, width, linesPerChunk, (uint16_t*)buf); 

    linesRead += linesPerChunk;
    linesRead % 160 == 0 ? y_coord = 0, frame_count++ : y_coord += linesPerChunk;
    println("frame no: " + String(frame_count));

  }
  http.end();
}
