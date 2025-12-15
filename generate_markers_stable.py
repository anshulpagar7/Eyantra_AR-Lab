import cv2
import cv2.aruco as aruco
from pathlib import Path

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
out_dir = Path("markers_final")
out_dir.mkdir(exist_ok=True)

for marker_id in range(8):
    img = aruco.drawMarker(aruco_dict, marker_id, 700)
    cv2.imwrite(str(out_dir / f"marker_{marker_id}.png"), img)
    print(f"Generated marker {marker_id}")
