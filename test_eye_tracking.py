import cv2
import mediapipe as mp
import numpy as np
import time

def test_eye_tracking():
    """Simple test to verify eye tracking is working"""
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False, 
        refine_landmarks=True,
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return
        
    # Iris landmark indices
    left_iris_idx = [474, 475, 476, 477]
    right_iris_idx = [469, 470, 471, 472]
    
    calibrated_center = None
    frame_count = 0
    calibration_frames = 30
    is_calibrated = False
    
    # Improved thresholds for better accuracy
    threshold_x = 12
    threshold_y = 10
    
    def get_avg_iris_pos(landmarks, image_w, image_h, indices):
        coords = []
        for i in indices:
            pt = landmarks.landmark[i]
            coords.append((int(pt.x * image_w), int(pt.y * image_h)))
        coords = np.array(coords)
        center = np.mean(coords, axis=0)
        return center
    
    def get_direct_direction(eye_direction):
        """Convert eye direction to snake direction (direct control, no mirror)"""
        # Direct control - no mirror effect
        return eye_direction
    
    print("Eye Tracking Test")
    print("Look straight ahead for calibration...")
    print("Control scheme:")
    print("- Look LEFT → Snake moves LEFT (direct)")
    print("- Look RIGHT → Snake moves RIGHT (direct)")
    print("- Look UP → Snake moves UP (direct)")
    print("- Look DOWN → Snake moves DOWN (direct)")
    
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
            
            # Get iris positions
            left_iris = get_avg_iris_pos(landmarks, w, h, left_iris_idx)
            right_iris = get_avg_iris_pos(landmarks, w, h, right_iris_idx)
            
            # Calculate average iris position
            avg_iris = (left_iris + right_iris) / 2
            cx, cy = int(avg_iris[0]), int(avg_iris[1])
            
            # Draw iris positions
            cv2.circle(frame, tuple(np.int32(left_iris)), 3, (0, 255, 255), -1)
            cv2.circle(frame, tuple(np.int32(right_iris)), 3, (0, 255, 255), -1)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            
            # Calibration phase
            if not is_calibrated:
                if calibrated_center is None:
                    calibrated_center = np.array([cx, cy], dtype=np.float32)
                else:
                    calibrated_center = 0.9 * calibrated_center + 0.1 * np.array([cx, cy], dtype=np.float32)
                
                frame_count += 1
                cv2.putText(frame, f"Calibrating... {frame_count}/{calibration_frames}", 
                           (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                
                if frame_count >= calibration_frames:
                    is_calibrated = True
                    print("Calibration complete!")
            else:
                # Calculate displacement from calibrated center
                dx, dy = cx - calibrated_center[0], cy - calibrated_center[1]
                
                # Determine direction
                eye_direction = "CENTER"
                if abs(dx) > abs(dy):
                    if dx > threshold_x:
                        eye_direction = "RIGHT"
                    elif dx < -threshold_x:
                        eye_direction = "LEFT"
                else:
                    if dy > threshold_y:
                        eye_direction = "DOWN"
                    elif dy < -threshold_y:
                        eye_direction = "UP"
                
                # Get snake direction (direct control)
                snake_direction = get_direct_direction(eye_direction)
                
                # Draw direction and displacement
                cv2.putText(frame, f'Eye: {eye_direction}', (30, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)
                cv2.putText(frame, f'Snake: {snake_direction}', (30, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                cv2.putText(frame, f'dx: {dx:.1f}, dy: {dy:.1f}', (30, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Draw calibrated center
                cv2.circle(frame, tuple(np.int32(calibrated_center)), 8, (255, 0, 0), 2)
        
        cv2.imshow("Eye Tracking Test", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_eye_tracking() 