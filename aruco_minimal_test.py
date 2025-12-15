import cv2
import cv2.aruco as aruco
import numpy as np

# ---------- CREATE A MARKER (ID = 0) ----------
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
marker = aruco.generateImageMarker(aruco_dict, 0, 600)

# add thick white border
marker = cv2.copyMakeBorder(
    marker, 80, 80, 80, 80,
    cv2.BORDER_CONSTANT, value=255
)

cv2.imwrite("TEST_MARKER.png", marker)
print("Generated TEST_MARKER.png (ID = 0)")

# ---------- CAMERA DETECTION ----------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Show TEST_MARKER.png FULL SCREEN. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, _ = aruco.detectMarkers(gray, aruco_dict)

    if ids is not None:
        print("DETECTED:", ids.flatten())
        aruco.drawDetectedMarkers(frame, corners, ids)

    cv2.imshow("ARUCO MINIMAL TEST", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
