eYantra – AR-Based Circuit Visualization Lab

eYantra is an Augmented Reality (AR)–based virtual electronics lab designed to help students visualize, understand, and interact with electronic circuits in real time.
Using ArUco markers and a webcam, the system dynamically loads experiments and builds circuits step-by-step, showing components, connections, and explanations just like a real lab.

🚀 Key Features

📷 Marker-based AR interaction using ArUco codes

🧩 Step-by-step circuit construction (press N to proceed)

🔌 Supports multiple circuit types

Series circuits

Parallel circuits

LED circuits

RC circuits

Transistor-based circuits

🖼️ Visual component rendering

Resistor, LED, Capacitor, Diode, Transistor, Voltage Source, Ground

🧠 Circuit logic engine

Computes current, voltage drops (for supported circuits)

🧱 Modular & extensible design

New experiments can be added via JSON

🎓 Education-first approach

Mirrors how labs are taught in real classrooms

🛠️ Tech Stack
Current Stack

Python 3.11

OpenCV (cv2 + ArUco module) – AR marker detection & rendering

JSON – experiment definitions and step logic

Custom Circuit Engine

loader.py – loads experiment data

solver.py – solves basic circuits

PNG assets (RGBA) – component images

Git & GitHub

Python virtual environment (venv)

Planned Enhancements

Connection-aware auto layout

Animated wire drawing

Current flow visualization

RC charging/discharging animation

Optional web-based AR version

📂 Project Structure
Eyantra_AR-Lab/
│
├── assets/                # Component images (PNG with transparency)
├── experiments/           # JSON experiment definitions
├── circuit_engine/        # Circuit logic & solvers
│   ├── loader.py
│   └── solver.py
├── python_app/
│   └── ar_main.py         # Main AR application
├── markers/               # Generated ArUco markers
├── venv/                  # Python virtual environment
└── README.md

▶️ How to Run
1️⃣ Activate Virtual Environment (Windows)
venv\Scripts\activate


You should see:

(venv) Eyantra_AR-Lab>

2️⃣ Run the AR Application
python python_app\ar_main.py

3️⃣ Controls

N → Next step

R → Reset current experiment

Q → Quit application

Show an ArUco marker to the camera to load the corresponding experiment.

🧪 Experiments Included

Ohm’s Law (Single Resistor)

Series Resistors (Equivalent Resistance)

Parallel Resistors (Current Division)

LED with Current-Limiting Resistor

Voltage Divider

RC Charging & Discharging

Transistor Basics

Threshold / Logic Experiments

Each experiment is fully configurable via JSON.

🎯 Educational Use Case

This project is intended for:

Electronics & Electrical Labs

Demonstrations during practical sessions

Concept visualization for beginners

Hybrid / virtual lab environments

Teachers can explain circuit behavior visually, not just theoretically.

🔮 Future Scope

Fully topology-aware circuit rendering

Animated current flow

Auto-play demo mode

Web-based AR version (Three.js / WebXR)

Support for more complex IC-based circuits
