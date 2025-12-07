import cv2
import cv2.aruco as aruco

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Set HD for better detection
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    params = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, params)

    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip horizontally for natural view
        frame = cv2.flip(frame, 1)

        # Convert to grayscale (sometimes helps detection)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None and len(ids) > 0:
            print("Detected IDs:", ids.flatten())
            # Draw markers on the original color frame
            aruco.drawDetectedMarkers(frame, corners, ids)

        cv2.imshow("ArUco Test - 4x4_50", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
