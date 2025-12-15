import cv2
import cv2.aruco as aruco
from aruco_config import ARUCO_DICT

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

aruco_dict = aruco.getPredefinedDictionary(ARUCO_DICT)
params = aruco.DetectorParameters()
params.errorCorrectionRate = 0.1
detector = aruco.ArucoDetector(aruco_dict, params)

print("Show ONE marker clearly. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        print("Detected IDs:", ids.flatten())
        aruco.drawDetectedMarkers(frame, corners, ids)

    cv2.imshow("ARUCO DEBUG", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
