import sys
import os
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
    "GPIO": ASSETS_DIR / "gpio_block.png"
}


# ================= HELPERS =================
def get_component_type(comp_id: str):
    comp_id = comp_id.upper()
    if comp_id.startswith("LED"):
        return "LED"
    if comp_id.startswith("GND"):
        return "GND"
    if comp_id.startswith("Q"):
        return "Q"
    if comp_id.startswith("D"):
        return "D"
    if comp_id.startswith("C"):
        return "C"
    return comp_id[0]


def base_component(terminal: str):
    return terminal.split(".")[0]


# -------- BRANCH-AWARE AUTO LAYOUT --------
def auto_layout_position(comp, visible_components, connections):
    base_x = 260
    gap_x = 180
    base_y = 360
    gap_y = 140

    idx = visible_components.index(comp)
    x = base_x + idx * gap_x
    y = base_y

    # Detect parallel branches from V1
    branches = [b for a, b in connections if a == "V1"]

    if comp in branches:
        branch_idx = branches.index(comp)
        y = base_y - gap_y if branch_idx == 0 else base_y + gap_y

    return x, y


def remove_checkerboard(img):
    if img is None or img.shape[2] != 4:
        return img

    b, g, r, a = cv2.split(img)
    mask = ~(
        ((r > 180) & (r < 255)) &
        ((g > 180) & (g < 255)) &
        ((b > 180) & (b < 255))
    )
    a = mask.astype("uint8") * 255
    return cv2.merge([b, g, r, a])


def overlay_image(frame, img, x, y):
    if img is None or img.shape[2] != 4:
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


def load_experiment_json(exp_id: int):
    file_map = {
        0: "exp1_ohms_law_measurement.json",
        1: "exp2_voltage_divider_load.json",
        2: "exp3_parallel.json",
        3: "exp4_led.json",
        4: "exp5_voltage_divider.json",
        5: "exp6_rc.json",
        6: "exp7_transistor.json",
        7: "exp8_threshold.json",
    }

    path = Path("experiments") / file_map.get(exp_id, "")
    if not path.exists():
        return None, None, None, "No experiment mapped"

    circuit, steps = load_series_circuit_from_json(path)
    result = solve_series_circuit(circuit) if exp_id in [0, 1, 3, 4] else {}
    return circuit, steps, result, f"Loaded: {path.name}"


# ================= MAIN =================
def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)

    current_marker = None
    current_step = 0
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
                _, steps, _, status = load_experiment_json(marker_id)
                current_marker = marker_id
                current_step = 0
                visible_components.clear()
                component_images.clear()
                connections.clear()

        frame = cv2.flip(frame, 1)

        # UI text
        cv2.putText(frame, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if steps:
            step = steps[min(current_step, len(steps) - 1)]
            cv2.putText(frame, f"Step {current_step + 1}/{len(steps)}",
                        (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, step["text"],
                        (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

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
            cv2.putText(frame, comp, (x - 25, y + 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("eYantra AR Circuit Builder", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("n") and steps:
            if current_step < len(steps) - 1:
                current_step += 1
                step = steps[current_step]

                if step["type"] == "show_component":
                    comp = step["target"]
                    if comp not in visible_components:
                        img_path = COMPONENT_IMAGES.get(get_component_type(comp))
                        img = None
                        if img_path and img_path.exists():
                            img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
                            img = remove_checkerboard(img)
                            img = cv2.resize(img, (120, 120))
                        component_images[comp] = img
                        visible_components.append(comp)

                elif step["type"] == "connect":
                    a = base_component(step["from"])
                    b = base_component(step["to"])
                    if a in visible_components and b in visible_components:
                        connections.append((a, b))

        elif key == ord("r"):
            current_step = 0
            visible_components.clear()
            component_images.clear()
            connections.clear()

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
