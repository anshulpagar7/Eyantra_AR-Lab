import sys
import os

# ---------- FIX FOR IMPORT PATH ----------
# Make project root discoverable so "circuit_engine" can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
# -----------------------------------------

import cv2
import cv2.aruco as aruco
from pathlib import Path

from circuit_engine.loader import load_series_circuit_from_json
from circuit_engine.solver import solve_series_circuit


def load_experiment_json(exp_id: int):
    """Load correct JSON based on marker ID."""
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
        return None, None, f"No experiment mapped to ID {exp_id}"

    json_path = Path(f"experiments/{file_map[exp_id]}")

    if not json_path.exists():
        return None, None, f"File missing: {json_path}"

    # Load circuit + steps
    circuit, steps = load_series_circuit_from_json(json_path)

    # Solve only for supported series-type circuits for now
    if exp_id in [0, 1, 3, 4]:
        result = solve_series_circuit(circuit)
    else:
        result = {"info": "This circuit type is not solved yet (visual only later)"}

    return circuit, result, f"Loaded: {file_map[exp_id]}"


def main():
    # 1. Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Optional: set HD resolution for better detection
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # 2. Prepare ArUco detection
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    params = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, params)

    experiment_cache = {}  # Cache loaded experiments for each marker ID

    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip horizontally so it looks natural and fixes mirror issues
        frame = cv2.flip(frame, 1)

        # 3. Detect markers
        corners, ids, _ = detector.detectMarkers(frame)

        status_msg = "No marker detected"

        if ids is not None and len(ids) > 0:
            # For now, just use the first detected marker
            marker_id = int(ids[0][0])
            aruco.drawDetectedMarkers(frame, corners, ids)

            # Load experiment once per marker and cache it
            if marker_id not in experiment_cache:
                circuit, result, status_msg = load_experiment_json(marker_id)
                experiment_cache[marker_id] = (circuit, result, status_msg)

            circuit, result, status_msg = experiment_cache[marker_id]

            # 4. Display calculation results (for series circuits)
            y = 60
            if isinstance(result, dict):
                # Show current if available
                current = result.get("current", None)
                if current is not None:
                    cv2.putText(
                        frame,
                        f"I = {current:.4f} A",
                        (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 255),
                        2,
                    )
                    y += 30

                # Show voltage drops if available
                vdrops = result.get("voltage_drops", {})
                for comp, drop in vdrops.items():
                    cv2.putText(
                        frame,
                        f"{comp}: {drop:.2f} V",
                        (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 200, 0),
                        2,
                    )
                    y += 30

        # 5. Status message (what experiment / error)
        cv2.putText(
            frame,
            status_msg,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        cv2.imshow("eYantra AR - Experiment Loader", frame)

        # 6. Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
