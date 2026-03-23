# ESP8266 - Wi-Fi to TFT OLED ST7735 Video Streamer (TFT_eSPI)
#### Program runs on an ESP8266 and streams images over Wi-Fi from a server to a 1.8" TFT OLED ST7735 screen. I streamed over wifi because ram and flash is limited and I didnt bother buying an sd card reader.
## SETUP
* Install [XAMPP 8.0.25](https://sourceforge.net/projects/xampp/files/XAMPP%20Windows/8.0.25/) or 
your preferred server

* Install [Python 3.9.5](https://www.python.org/downloads/release/python-395/)

* Install [Arduino IDE 2.1.1](https://github.com/arduino/arduino-ide/releases/tag/2.1.1)

* Arduino IDE -> File -> Preferences -> Additional boards manager URLs -> https://arduino.esp8266.com/stable/package_esp8266com_index.json

* Arduino IDE -> Tools -> Board -> esp8266 -> NodeMCU 1.0 (ESP-12E Module)

* Arduino IDE -> Tools -> Upload Speed -> 912600

* Arduino IDE -> Tools -> Serial Monitor -> 921600

* Arduino IDE -> Tools -> CPU Frequency -> 160 MHz

* Arduino IDE -> Sketch -> Include Libraries -> Manage Libraries ->
	* Install `TFT_eSPI by Bodmer`

* Arduino IDE -> File -> Preferences -> Sketchbook location -> Go to that directory -> libraries ->
	* TFT_eSPI -> Replace `User_Setup_Select.h`
	* Add `TFT_eSPI_NonstopAG47_Setups/` inside libraries

* Setup and activate env if preferred

## MAIN
### PREPROCESSING
* Run `./preprocess.sh "path_to_input_video" "path_to_temp_dir" "interval" "path_to_output_dir"`

    * Eg: `./preprocess.sh "C:/Users/Desktop/project/ironman.mp4" "C:/Users/Desktop/project/temp_dir" "20" "C:/Users/xampp/htdocs/testingimage/"`

* Run XAMPP Apache Server or your preferred server

* Configure `video_streamer/config.h`

* Run `video_streamer/video_streamer.ino`

## NOTE
> I use git bash on windows to run .sh
>
> Interval alters FPS and speed of video
>
> Path to output dir is where server files are served. Eg: `"/xampp/htdocs/testingimage/"`
>
> Delete temp directory after running `preprocess.sh`
>
> URL in `video_streamer/video_streamer.ino` follows the format `http://domain-url/testingimage/00001"`. Ensure folder name matches in server or modify the format

