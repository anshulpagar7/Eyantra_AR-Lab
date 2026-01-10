import sys
import os
import json
from pathlib import Path
import numpy as np

# ================= PATH FIX =================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
# ===========================================

import cv2
import cv2.aruco as aruco

from circuit_engine.loader import load_series_circuit_from_json


# ================= ASSETS =================
ASSETS_DIR = Path("assets")

COMPONENT_IMAGES = {
    "V": ASSETS_DIR / "voltage_source.png",
    "R": ASSETS_DIR / "resistor.png",
    "LED": ASSETS_DIR / "led.png",
    "C": ASSETS_DIR / "capacitor.png",
    "D": ASSETS_DIR / "diode.png",
    "Q": ASSETS_DIR / "transistor.png",
    "GND": ASSETS_DIR / "ground.png",
    "GPIO": ASSETS_DIR / "gpio_block.png",
}


# ================= HELPERS =================
def get_component_type(comp_id: str):
    comp_id = comp_id.upper()
    if comp_id.startswith("LED"):
        return "LED"
    if comp_id.startswith("GPIO"):
        return "GPIO"
    if comp_id.startswith("GND"):
        return "GND"
    return comp_id[0]   # V1 -> V, R1 -> R


def base_component(terminal: str):
    return terminal.split(".")[0]


# ===== FINAL BRUTE-FORCE BACKGROUND REMOVAL =====
def force_remove_background(img):
    """
    Aggressive background removal for demo purposes.
    Removes white / grey / checkerboard regardless of alpha.
    """
    if img is None:
        return img

    # Convert to BGR
    if img.shape[2] == 4:
        b, g, r, _ = cv2.split(img)
        bgr = cv2.merge([b, g, r])
    else:
        bgr = img

    # Kill light pixels (checkerboard / white background)
    mask = (
        (bgr[:, :, 0] < 220) |
        (bgr[:, :, 1] < 200) |
        (bgr[:, :, 2] < 200)
    )

    alpha = mask.astype(np.uint8) * 255
    b, g, r = cv2.split(bgr)

    return cv2.merge([b, g, r, alpha])


def overlay_image(frame, img, x, y):
    if img is None:
        return

    h, w = img.shape[:2]
    x1, y1 = x - w // 2, y - h // 2
    x2, y2 = x1 + w, y1 + h

    if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
        return

    alpha = img[:, :, 3] / 255.0

    for c in range(3):
        frame[y1:y2, x1:x2, c] = (
            alpha * img[:, :, c] +
            (1 - alpha) * frame[y1:y2, x1:x2, c]
        )


# ============ SIMPLE LAYOUT ============
def auto_layout_position(comp, visible_components, connections):
    base_x = 250
    gap_x = 170
    base_y = 360
    gap_y = 140

    idx = visible_components.index(comp)
    x = base_x + idx * gap_x
    y = base_y

    # Simple parallel hint (from V1)
    branches = [b for a, b in connections if a == "V1"]
    if comp in branches:
        y = base_y - gap_y if branches.index(comp) == 0 else base_y + gap_y

    return x, y


# ============ EXPERIMENT LOADER ============
def load_experiment_json(exp_id: int):
    file_map = {
        0: "exp1_ohms_law_measurement.json",
        1: "exp2_voltage_divider_load.json",
        2: "exp3_rc_charging_led.json",
        3: "exp4_gpio_led_control.json",
        4: "exp5_gpio_logic_threshold.json",
        5: "exp6_rc.json",
        6: "exp7_transistor.json",
        7: "exp8_threshold.json",
    }

    if exp_id not in file_map:
        return [], "No experiment mapped"

    path = Path("experiments") / file_map[exp_id]

    if not path.exists():
        return [], f"Missing file: {path.name}"

    try:
        _, steps = load_series_circuit_from_json(path)
    except json.JSONDecodeError:
        return [], "Invalid JSON file"

    return steps, f"Loaded: {path.name}"


# ================= MAIN =================
def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)

    current_marker = None
    current_step = -1
    steps = []
    status = "No marker detected"

    visible_components = []
    component_images = {}
    connections = []

    print("✅ eYantra AR running | N: next | R: reset | Q: quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, aruco_dict)

        if ids is not None:
            marker_id = int(ids[0][0])
            aruco.drawDetectedMarkers(frame, corners, ids)

            if marker_id != current_marker:
                steps, status = load_experiment_json(marker_id)
                current_marker = marker_id
                current_step = -1
                visible_components.clear()
                component_images.clear()
                connections.clear()

        frame = cv2.flip(frame, 1)

        # Status
        cv2.putText(frame, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if steps and current_step >= 0:
            step = steps[current_step]
            cv2.putText(frame, step["text"], (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

        # Draw wires
        for a, b in connections:
            if a in visible_components and b in visible_components:
                x1, y1 = auto_layout_position(a, visible_components, connections)
                x2, y2 = auto_layout_position(b, visible_components, connections)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

        # Draw components
        for comp in visible_components:
            x, y = auto_layout_position(comp, visible_components, connections)
            overlay_image(frame, component_images.get(comp), x, y)

            # BLACK component labels
            cv2.putText(frame, comp, (x - 20, y + 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        cv2.imshow("eYantra AR Circuit Lab", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("n") and steps:
            if current_step < len(steps) - 1:
                current_step += 1
                step = steps[current_step]

                if step["type"] == "show_component":
                    comp = step["target"]
                    if comp not in visible_components:
                        img = None
                        img_path = COMPONENT_IMAGES.get(get_component_type(comp))
                        if img_path and img_path.exists():
                            img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
                            img = force_remove_background(img)
                            img = cv2.resize(img, (120, 120))
                        component_images[comp] = img
                        visible_components.append(comp)

                elif step["type"] == "connect":
                    a = base_component(step["from"])
                    b = base_component(step["to"])
                    if a in visible_components and b in visible_components:
                        connections.append((a, b))

        elif key == ord("r"):
            current_step = -1
            visible_components.clear()
            component_images.clear()
            connections.clear()

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
