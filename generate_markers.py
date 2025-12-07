import cv2
import cv2.aruco as aruco
from pathlib import Path

def main():
    output_dir = Path("markers")
    output_dir.mkdir(exist_ok=True)

    # Use the same dictionary as in ar_main.py
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    for marker_id in range(8):  # IDs 0 to 7
        img = aruco.generateImageMarker(aruco_dict, marker_id, 400)  # 400x400 px
        file_path = output_dir / f"aruco_marker_{marker_id}.png"
        cv2.imwrite(str(file_path), img)
        print(f"Saved: {file_path}")

    print("All markers generated inside 'markers/' folder.")

if __name__ == "__main__":
    main()
