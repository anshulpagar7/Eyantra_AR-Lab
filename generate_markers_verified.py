import cv2
import cv2.aruco as aruco
from pathlib import Path

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
out = Path("markers_verified")
out.mkdir(exist_ok=True)

for marker_id in range(8):
    marker = aruco.generateImageMarker(aruco_dict, marker_id, 600)

    # add white margin
    marker = cv2.copyMakeBorder(
        marker, 60, 60, 60, 60,
        cv2.BORDER_CONSTANT, value=255
    )

    # ADD TEXT OVERLAY (so you KNOW which file it is)
    marker_color = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)
    cv2.putText(
        marker_color,
        f"ID {marker_id}",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 0, 255),
        3
    )

    cv2.imwrite(str(out / f"marker_{marker_id}.png"), marker_color)
    print(f"Saved marker_{marker_id}.png")
