# Hindenburg - Underwater Drone Ground Control Station

Qt-based desktop control application for low-latency teleoperation, video streaming, and telemetry monitoring of the underwater ROV **Hindenburg**.

## Features

* **Keyboard Control:** Currently supported keyboard-based control for ROV movement and thruster operation.
* **Gamepad & Joystick Support:** Proportional analog control via `pygame-ce` — **coming soon**.
* **Video Pipeline:** High-speed JPEG frame decoding using `simplejpeg` with dynamic frame scaling via `opencv-python`.
* **Telemetry Display:** Real-time monitoring of hull temperature, humidity, system performance, thruster output, and ROV position.

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/LowK3/HindenburgDroneClient.git
cd HindenburgDroneClient
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main_client.py
```
