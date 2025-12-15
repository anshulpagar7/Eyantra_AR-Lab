import sys
import os
import re

# ---------- FIX FOR IMPORT PATH ----------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
# -----------------------------------------

import cv2
import cv2.aruco as aruco
from pathlib import Path

from circuit_engine.loader import load_series_circuit_from_json
from circuit_engine.solver import solve_series_circuit


def extract_components(step_text: str):
    """Extract component IDs like R1, V1, LED1 from text."""
    pattern = r"(R\d+|V\d+|LED\d+)"
    return re.findall(pattern, step_text.upper())


def load_experiment_json(exp_id: int):
    file_map = {
        0: "exp1_ohm.json",
        1: "exp2_series.json",
        2: "exp3_parallel.json",
        3: "exp4_led.json",
        4: "exp5_voltage_divider.json",
        5: "exp6_rc.json",
        6: "exp7_transistor.json",
        7: "exp8_threshold.json",
    }

    if exp_id not in file_map:
        return None, None, None, f"No experiment mapped to ID {exp_id}"

    json_path = Path(f"experiments/{file_map[exp_id]}")
    if not json_path.exists():
        return None, None, None, f"File missing: {json_path}"

    circuit, steps = load_series_circuit_from_json(json_path)

    if exp_id in [0, 1, 3, 4]:
        result = solve_series_circuit(circuit)
    else:
        result = {}

    return circuit, steps, result, f"Loaded: {file_map[exp_id]}"


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)

    current_marker_id = None
    current_step_index = 0
    steps = []
    result = {}
    status_msg = "No marker detected"

    print("✅ eYantra AR started")
    print("Keys: N = Next step | R = Reset | Q = Quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1️⃣ Detect on raw frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, aruco_dict)

        if ids is not None and len(ids) > 0:
            aruco.drawDetectedMarkers(frame, corners, ids)
            marker_id = int(ids[0][0])

            if marker_id != current_marker_id:
                _, steps, result, status_msg = load_experiment_json(marker_id)
                current_marker_id = marker_id
                current_step_index = 0

        # 2️⃣ Flip for display
        frame_display = cv2.flip(frame, 1)

        # 3️⃣ Status
        cv2.putText(
            frame_display,
            status_msg,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        # 4️⃣ Step text + component highlight
        if steps:
            step = steps[min(current_step_index, len(steps) - 1)]
            step_text = step.get("text", "")

            cv2.putText(
                frame_display,
                f"Step {current_step_index + 1} / {len(steps)}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame_display,
                step_text,
                (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2,
            )

            # 🔹 Highlight components
            components = extract_components(step_text)
            y = 150
            for comp in components:
                cv2.putText(
                    frame_display,
                    f"🔹 Highlight: {comp}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 150, 50),
                    2,
                )
                y += 30

        # 5️⃣ Circuit values
        y = 260
        current = result.get("current")
        if current is not None:
            cv2.putText(
                frame_display,
                f"I = {current:.4f} A",
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 200, 0),
                2,
            )
            y += 30

        for comp, drop in result.get("voltage_drops", {}).items():
            cv2.putText(
                frame_display,
                f"{comp}: {drop:.2f} V",
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 200, 0),
                2,
            )
            y += 30

        cv2.imshow("eYantra AR - Step Highlight Mode", frame_display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("n") and steps:
            if current_step_index < len(steps) - 1:
                current_step_index += 1
        elif key == ord("r"):
            current_step_index = 0
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
