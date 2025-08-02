import cv2
import mediapipe as mp
import numpy as np
import threading
import time

class HeadController:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False, 
            refine_landmarks=True,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = None
        self.calibrated_center = None
        self.frame_count = 0
        self.calibration_frames = 30
        self.current_direction = "CENTER"
        self.is_calibrated = False
        self.running = False
        self.thread = None
        
        # Iris landmark indices for MediaPipe face mesh
        self.left_iris_idx = [474, 475, 476, 477]
        self.right_iris_idx = [469, 470, 471, 472]
        
        # Improved thresholds for better accuracy
        self.threshold_x = 12  # More sensitive for better responsiveness
        self.threshold_y = 10  # More sensitive for better responsiveness
        
    def start(self):
        """Start the eye tracking in a separate thread"""
        if self.running:
            return
            
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
            
        self.running = True
        self.thread = threading.Thread(target=self._track_eyes)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """Stop the eye tracking"""
        self.running = False
        if self.cap:
            self.cap.release()
        if self.thread:
            self.thread.join()
            
    def get_avg_iris_pos(self, landmarks, image_w, image_h, indices):
        """Calculate average position of iris landmarks"""
        coords = []
        for i in indices:
            pt = landmarks.landmark[i]
            coords.append((int(pt.x * image_w), int(pt.y * image_h)))
        coords = np.array(coords)
        center = np.mean(coords, axis=0)
        return center
        
    def _track_eyes(self):
        """Main eye tracking loop"""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.face_mesh.process(rgb)
            
            if result.multi_face_landmarks:
                landmarks = result.multi_face_landmarks[0]
                
                # Get iris positions
                left_iris = self.get_avg_iris_pos(landmarks, w, h, self.left_iris_idx)
                right_iris = self.get_avg_iris_pos(landmarks, w, h, self.right_iris_idx)
                
                # Calculate average iris position
                avg_iris = (left_iris + right_iris) / 2
                cx, cy = int(avg_iris[0]), int(avg_iris[1])
                
                # Calibration phase
                if not self.is_calibrated:
                    if self.calibrated_center is None:
                        self.calibrated_center = np.array([cx, cy], dtype=np.float32)
                    else:
                        self.calibrated_center = 0.9 * self.calibrated_center + 0.1 * np.array([cx, cy], dtype=np.float32)
                    
                    self.frame_count += 1
                    if self.frame_count >= self.calibration_frames:
                        self.is_calibrated = True
                        print("Eye controller calibration complete!")
                else:
                    # Calculate displacement from calibrated center
                    dx, dy = cx - self.calibrated_center[0], cy - self.calibrated_center[1]
                    
                    # Determine direction based on displacement with improved thresholds
                    direction = "CENTER"
                    
                    # Use the larger movement to determine primary direction
                    if abs(dx) > abs(dy):
                        if dx > self.threshold_x:
                            direction = "RIGHT"
                        elif dx < -self.threshold_x:
                            direction = "LEFT"
                    else:
                        if dy > self.threshold_y:
                            direction = "DOWN"
                        elif dy < -self.threshold_y:
                            direction = "UP"
                    
                    # Only update if direction changed
                    if direction != self.current_direction:
                        print(f"Eye direction changed: {self.current_direction} -> {direction} (dx={dx:.1f}, dy={dy:.1f})")
                        self.current_direction = direction
                    
            time.sleep(0.03)  # ~30 FPS
            
    def get_direction(self):
        """Get the current eye direction"""
        if not self.is_calibrated:
            return "CENTER"
        return self.current_direction
        
    def is_calibration_complete(self):
        """Check if calibration is complete"""
        return self.is_calibrated
        
    def reset_calibration(self):
        """Reset calibration"""
        self.calibrated_center = None
        self.frame_count = 0
        self.is_calibrated = False
        self.current_direction = "CENTER"
