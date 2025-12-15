import cv2
import cv2.aruco as aruco
from pathlib import Path
from aruco_config import ARUCO_DICT

aruco_dict = aruco.getPredefinedDictionary(ARUCO_DICT)

out_dir = Path("markers_final")
out_dir.mkdir(exist_ok=True)

for marker_id in range(8):
    marker = aruco.generateImageMarker(aruco_dict, marker_id, 700)
    cv2.imwrite(str(out_dir / f"marker_{marker_id}.png"), marker)
