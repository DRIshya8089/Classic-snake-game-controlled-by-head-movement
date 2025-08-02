import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, refine_landmarks=True)
cap = cv2.VideoCapture(0)

def get_avg_iris_pos(landmarks, image_w, image_h, indices):
    coords = []
    for i in indices:
        pt = landmarks.landmark[i]
        coords.append((int(pt.x * image_w), int(pt.y * image_h)))
    coords = np.array(coords)
    center = np.mean(coords, axis=0)
    return center

calibrated_center = None
frame_count = 0
calibration_frames = 30

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0]

        left_iris_idx = [474, 475, 476, 477]
        right_iris_idx = [469, 470, 471, 472]

        left_iris = get_avg_iris_pos(landmarks, w, h, left_iris_idx)
        right_iris = get_avg_iris_pos(landmarks, w, h, right_iris_idx)

        avg_iris = (left_iris + right_iris) / 2
        cx, cy = int(avg_iris[0]), int(avg_iris[1])

        cv2.circle(frame, tuple(np.int32(left_iris)), 2, (0, 255, 255), -1)
        cv2.circle(frame, tuple(np.int32(right_iris)), 2, (0, 255, 255), -1)

        # Calibrate neutral eye position for first N frames
        if frame_count < calibration_frames:
            if calibrated_center is None:
                calibrated_center = np.array([cx, cy], dtype=np.float32)
            else:
                calibrated_center = 0.9 * calibrated_center + 0.1 * np.array([cx, cy], dtype=np.float32)
            cv2.putText(frame, "Calibrating... Look straight", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            frame_count += 1
        else:
            dx, dy = cx - calibrated_center[0], cy - calibrated_center[1]
            direction = "CENTER"

            # Adaptive threshold
            threshold_x = 25
            threshold_y = 20

            if abs(dx) > abs(dy):
                if dx > threshold_x:
                    direction = "RIGHT"
                elif dx < -threshold_x:
                    direction = "LEFT"
            else:
                if dy > threshold_y:
                    direction = "DOWN"
                elif dy < -threshold_y:
                    direction = "UP"

            cv2.putText(frame, f'Direction: {direction}', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)

    cv2.imshow("Eyeball Tracker (Calibrated)", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
