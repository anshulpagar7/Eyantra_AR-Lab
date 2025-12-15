import cv2
import cv2.aruco as aruco
from pathlib import Path

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)

out_dir = Path("markers_clean")
out_dir.mkdir(exist_ok=True)

for marker_id in range(8):
    marker = aruco.generateImageMarker(aruco_dict, marker_id, 600)

    marker = cv2.copyMakeBorder(
        marker, 80, 80, 80, 80,
        cv2.BORDER_CONSTANT, value=255
    )

    cv2.imwrite(str(out_dir / f"marker_{marker_id}.png"), marker)
    print(f"Generated marker {marker_id}")
