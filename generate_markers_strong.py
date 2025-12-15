import cv2
import cv2.aruco as aruco
from pathlib import Path

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

out_dir = Path("markers_strong")
out_dir.mkdir(exist_ok=True)

for marker_id in range(8):
    marker = aruco.generateImageMarker(aruco_dict, marker_id, 600)

    # add white border manually (VERY important)
    bordered = cv2.copyMakeBorder(
        marker, 50, 50, 50, 50,
        cv2.BORDER_CONSTANT,
        value=255
    )

    path = out_dir / f"marker_{marker_id}.png"
    cv2.imwrite(str(path), bordered)
    print(f"Saved {path}")
