# Hindenburg - Underwater ROV Ground Control Station

Desktop ground control application for the **Hindenburg underwater ROV**.

The application provides a graphical interface for remotely controlling the ROV, receiving live video, and monitoring telemetry from the onboard Raspberry Pi.

## Architecture

```text
                    HINDENBURG ROV
                          │
                          │
                          ▼
              ┌──────────────────────┐
              │    Raspberry Pi 4B   │
              │                      │
              │   Onboard Server     │
              │                      │
              │  • Thruster control  │
              │  • Sensors           │
              │  • Telemetry         │
              │  • Video streaming   │
              └──────────┬───────────┘
                  Ethernet cable
                    TCP / UDP
                         │
                         ▼
              ┌──────────────────────┐
              │   Ground Control     │
              │      Station         │
              │                      │
              │  • ROV control       │
              │  • Video display     │
              │  • Telemetry         │
              │  • Operator inputs   │
              └──────────────────────┘
```

The Ground Control Station communicates with the onboard server running on the ROV's Raspberry Pi.

## Features

* **ROV Control:** Keyboard-based control for movement and thruster operation.
* **Video Streaming:** Receives and displays live video from the ROV.
* **Telemetry Display:** Displays available sensor and system telemetry in real time.
* **Gamepad & Joystick Support:** Proportional analog control via `pygame-ce` *(coming soon)*.

## Technology Stack

* **Python 3** — Application development
* **PySide6 / Qt** — Graphical user interface
* **OpenCV** — Video processing and frame scaling
* **simplejpeg** — High-speed JPEG decoding
* **pygame-ce** — Gamepad and joystick support
* **TCP / UDP** — Network communication

## Requirements

* Python 3
* Windows
* Network connection to the Hindenburg onboard server

Python dependencies are listed in `requirements.txt`.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/LowK3/HindenburgDroneClient.git
cd HindenburgDroneClient
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```powershell
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the Ground Control Station

```bash
python main_client.py
```

## Related Repository

The Onboard System Server for the ROV is available here:

- [HindenburgDroneServer](https://github.com/LowK3/HindenburgDroneServer)
