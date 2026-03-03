# title
#### desc
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
	* Install TFT_eSPI by Bodmer

* Arduino IDE -> File -> Preferences -> Sketchbook location -> Go to that directory -> libraries ->
	* TFT_eSPI -> Replace User_Setup_Select.h
	* Add TFT_eSPI_NonstopAG47_Setups/ inside libraries

* Setup and activate env if preferred

## MAIN
### PREPROCESSING
* Run `./preprocess.sh "path_to_input_video" "path_to_temp_dir" "interval" "path_to_output_dir"`

    * Eg: `./preprocess.sh "C:/Users/Desktop/ironman.mp4" "C:/Users/Desktop/temp_dir" "20" "C:/Users/xampp/htdocs/testingimage/"`

* Run XAMPP Apache Server or your preferred server

* Configure `video_streamer/config.h`

* Run 'video_streamer/video_streamer.ino'

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




## To do
.zip or no ?
//ESP8266 needs periodic yield to prevent watchdog resets.
//Combine all frames into ONE large binary file and stream continuously.
//Optimize this for maximum FPS
//Convert it into a real streaming video player
//get rid of unnecessary code