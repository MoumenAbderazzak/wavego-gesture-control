🐕 Wavego Robot Dog – Remote Hand-Gesture Control via MQTT
📌 Project Overview

This project enables remote real-time control of a Wavego Robot Dog using hand gestures detected by a Raspberry Pi camera.

Hand gestures are recognized on the Raspberry Pi using computer vision, then transmitted wirelessly via MQTT to the ESP32 onboard the Wavego robot.
At the same time, a live video stream from the robot’s camera allows full teleoperation without direct line-of-sight.

The system works entirely over a portable Android hotspot, making it ideal for mobile robotics experiments.

✨ Features

✋ Hand-gesture robot control (MediaPipe + OpenCV)

📡 Wireless MQTT communication

📷 Live onboard camera stream from the robot

🎮 Remote teleoperation without seeing the robot physically

🔐 Safe command logic with priority handling (V3)

⚡ Automatic WiFi connection on robot boot

🧠 System Architecture
[ USB Camera ]
      │
      ▼
Raspberry Pi
(Hand Detection)
      │
      │  MQTT Commands
      ▼
Mosquitto Broker
      │
      ▼
ESP32 (Wavego Robot)
      │
      ├── Servo & Motion Control
      └── Camera Stream (Port 81)

[ Android Phone Hotspot ]
      └── Shared WiFi Network

🧰 Hardware Used

Wavego Robot Dog (ESP32-based)

Raspberry Pi (any model with USB & HDMI)

USB Camera (hand detection)

Android smartphone (WiFi hotspot)

HDMI display (for Raspberry Pi)

🧑‍💻 Software Stack
Raspberry Pi

Python 3

OpenCV

MediaPipe

Mosquitto MQTT Broker

paho-mqtt

Robot (ESP32)

Arduino framework

WiFi

MQTT client

Servo control firmware

HTTP camera server

📂 Repository Structure
wavego-gesture-control/
│
├── raspberry_pi/
│   ├── hand_detection_V2.py
│   ├── hand_detection_V3.py
│   └── Instruction.txt
│
├── esp32/
│   ├── WAVEGO.ino          ← modified
│   ├── app_httpd.cpp       ← modified
│   ├── InitConfig.h
│   ├── PreferencesConfig.h
│   ├── ServoCtrl.h
│   └── WebPage.h
│
├── README.md
└── LICENSE

📶 WiFi Setup on the Wavego Robot
🔧 Where WiFi Credentials Are Defined

WiFi credentials are hardcoded in the ESP32 firmware inside:

WAVEGO.ino

You must set:

Hotspot SSID

Hotspot password

These must match your Android phone hotspot.

🔁 Automatic Connection (Important)

✅ Once the firmware is flashed:

The ESP32 automatically connects to WiFi on every boot

No configuration, buttons, or web interface required

Just power on the robot while the hotspot is active

✅ How to Verify Network Connection

Open Hotspot settings on your Android phone

Check Connected devices

You should see two devices:

Raspberry Pi

ESP32 (Wavego robot)

If both are present → network is correctly configured.

📥 ESP32 Flashing Instructions (Arduino IDE)
1️⃣ Install Arduino IDE

Download from:

https://www.arduino.cc/en/software

2️⃣ Install ESP32 Board Support

Open Arduino IDE

Go to
File → Preferences

Add this URL to Additional Board Manager URLs:

https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json


Go to
Tools → Board → Boards Manager

Search for ESP32 and install esp32 by Espressif Systems

3️⃣ Open the Project

Open esp32/WAVEGO.ino

Ensure all files are in the same folder:

app_httpd.cpp

.h files

4️⃣ Configure Board & Port

Board: ESP32 Dev Module

Upload Speed: 921600 (or lower if unstable)

Port: Select the ESP32 serial port

5️⃣ Set WiFi Credentials

Inside WAVEGO.ino, edit:

const char* ssid = "YOUR_HOTSPOT_NAME";
const char* password = "YOUR_HOTSPOT_PASSWORD";

6️⃣ Upload Firmware

Click Upload

If prompted:

Hold BOOT button on ESP32

Wait until upload completes

Open Serial Monitor (optional) to confirm WiFi connection

✅ The robot will now auto-connect on every power-up.

🚀 Raspberry Pi Setup
1️⃣ Install MQTT Broker
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto


Test:

mosquitto_sub -t test/topic
mosquitto_pub -t test/topic -m "hello"

2️⃣ Python Environment
python3 -m venv handenv
source handenv/bin/activate
pip install opencv-python mediapipe paho-mqtt

3️⃣ Run Gesture Detection
python hand_detection_V2.py
# or
python hand_detection_V3.py

✋ Gesture Control
🔹 Version 2 – Simple Control
Gesture	Command
✋ Open Palm	FORWARD
✊ Fist	REVERSE
✌️ Peace	LEFT
☝️ Index	RIGHT
4 Fingers	STOP
🔹 Version 3 – Dual-Hand Control (Recommended)
Left Hand – Actions (Priority)
Gesture	Command
✋ Open Palm	HANDSHAKE
✌️ Peace	JUMP
✊ Fist	STAYLOW
4 Fingers	STEADY
Right Hand – Movement
Gesture	Command
✋ Open Palm	FORWARD
✊ Fist	REVERSE
✌️ Peace	LEFT
☝️ Index	RIGHT
4 Fingers	STOP
📺 Live Camera Stream (IMPORTANT)

To view the robot’s onboard camera:

Connect Raspberry Pi to the same hotspot

Open a browser on the Raspberry Pi

Go to:

http://10.207.231.89:81/stream


This live feed enables full remote navigation.

🧪 How to Use (End-to-End)

Enable Android hotspot

Power on Wavego robot

Confirm ESP32 & Pi appear in hotspot device list

Open camera stream

Start MQTT broker

Run hand detection script

Control robot using gestures

🔜 Future Improvements

PID-based smoother motion

Web control dashboard

Gesture recording & playback

Autonomous navigation modes

Multi-robot support

🏁 Final Notes

✔ ESP32 WiFi is automatic
✔ MQTT ensures reliable command delivery
✔ Camera stream enables true teleoperation
✔ Modular design allows easy expansion

This project is a complete robotics teleoperation pipeline combining vision, networking, and embedded control.
