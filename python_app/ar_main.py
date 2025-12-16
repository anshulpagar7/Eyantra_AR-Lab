import sys
import os
import re
from pathlib import Path

# ---------- FIX FOR IMPORT PATH ----------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
# -----------------------------------------

import cv2
import cv2.aruco as aruco

from circuit_engine.loader import load_series_circuit_from_json
from circuit_engine.solver import solve_series_circuit


# ---------------- ASSETS ----------------
ASSETS_DIR = Path("assets")

COMPONENT_IMAGES = {
    "V": ASSETS_DIR / "voltage_source.png",
    "R": ASSETS_DIR / "resistor.png",
    "LED": ASSETS_DIR / "led.png",
}


# ---------------- HELPERS ----------------
def extract_components(step_text: str):
    """Extract component IDs like V1, R1, LED1 from step text."""
    pattern = r"(V\d+|R\d+|LED\d+)"
    return re.findall(pattern, step_text.upper())


def get_component_type(comp_id: str):
    if comp_id.startswith("LED"):
        return "LED"
    return comp_id[0]  # V or R


def auto_layout_position(index):
    """Auto horizontal layout for components."""
    start_x = 300
    gap = 180
    y = 360
    x = start_x + index * gap
    return x, y


def overlay_image(frame, img, x, y):
    """Overlay image (supports PNG with alpha)."""
    h, w = img.shape[:2]
    x1, y1 = x - w // 2, y - h // 2
    x2, y2 = x1 + w, y1 + h

    if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
        return

    if img.shape[2] == 4:
        alpha = img[:, :, 3] / 255.0
        for c in range(3):
            frame[y1:y2, x1:x2, c] = (
                alpha * img[:, :, c]
                + (1 - alpha) * frame[y1:y2, x1:x2, c]
            )
    else:
        frame[y1:y2, x1:x2] = img


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
        return None, None, None, f"Missing file: {json_path}"

    circuit, steps = load_series_circuit_from_json(json_path)

    if exp_id in [0, 1, 3, 4]:
        result = solve_series_circuit(circuit)
    else:
        result = {}

    return circuit, steps, result, f"Loaded: {file_map[exp_id]}"


# ---------------- MAIN ----------------
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)

    # -------- STATE --------
    current_marker_id = None
    current_step_index = 0
    steps = []
    result = {}
    status_msg = "No marker detected"

    visible_components = []     # ["V1", "R1", ...]
    component_images = {}       # comp_id -> image
    wires = []                  # [(0,1), (1,2), ...]

    print("✅ eYantra AR started")
    print("Keys: N = Next step | R = Reset | Q = Quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1️⃣ Detect ArUco on RAW frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, aruco_dict)

        if ids is not None and len(ids) > 0:
            aruco.drawDetectedMarkers(frame, corners, ids)
            marker_id = int(ids[0][0])

            if marker_id != current_marker_id:
                _, steps, result, status_msg = load_experiment_json(marker_id)
                current_marker_id = marker_id
                current_step_index = 0
                visible_components.clear()
                component_images.clear()
                wires.clear()

        # 2️⃣ Flip for display
        frame_display = cv2.flip(frame, 1)

        # 3️⃣ Status text
        cv2.putText(
            frame_display,
            status_msg,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        # 4️⃣ Step text
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

        # 5️⃣ DRAW WIRES
        for from_idx, to_idx in wires:
            x1, y1 = auto_layout_position(from_idx)
            x2, y2 = auto_layout_position(to_idx)
            cv2.line(frame_display, (x1, y1), (x2, y2), (0, 255, 0), 4)

        # 6️⃣ DRAW COMPONENTS
        for idx, comp_id in enumerate(visible_components):
            x, y = auto_layout_position(idx)
            img = component_images.get(comp_id)
            if img is not None:
                overlay_image(frame_display, img, x, y)
                cv2.putText(
                    frame_display,
                    comp_id,
                    (x - 25, y + 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

        cv2.imshow("eYantra AR - Circuit Builder", frame_display)

        # 7️⃣ Key handling
        key = cv2.waitKey(1) & 0xFF

        if key == ord("n") and steps:
            if current_step_index < len(steps) - 1:
                current_step_index += 1
                step_text = steps[current_step_index].get("text", "")
                comps = extract_components(step_text)

                for comp in comps:
                    if comp not in visible_components:
                        comp_type = get_component_type(comp)
                        img_path = COMPONENT_IMAGES.get(comp_type)

                        if img_path and img_path.exists():
                            img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
                            if img is not None:
                                img = cv2.resize(img, (120, 120))
                                component_images[comp] = img

                        # ADD COMPONENT
                        visible_components.append(comp)

                        # ADD WIRE (previous → current)
                        if len(visible_components) > 1:
                            wires.append(
                                (len(visible_components) - 2,
                                 len(visible_components) - 1)
                            )

        elif key == ord("r"):
            current_step_index = 0
            visible_components.clear()
            component_images.clear()
            wires.clear()

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
