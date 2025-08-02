import pygame
import cv2
import sys
import time
import threading
import numpy as np
from snake import Snake
from food import Food
from game import Game
from head_controller import HeadController
import random
import math

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.width = 500  # Smaller square screen
        self.height = 700  # Reduced height
        self.cell_size = 20
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game - Eye Controlled")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.game = Game()
        
        # Eye controller
        self.eye_controller = HeadController()
        
        # Webcam window
        self.cap = None
        self.webcam_thread = None
        self.webcam_running = False
        
        # Game state
        self.running = True
        self.game_over = False
        self.paused = False
        
        # Movement control - improved accuracy
        self.last_direction = "CENTER"
        self.last_move_time = 0
        self.move_delay = 200  # milliseconds - faster for better responsiveness
        self.auto_move_delay = 600  # milliseconds
        self.last_auto_move_time = 0
        self.auto_move_enabled = False
        
        # Bonus food system
        self.bonus_food_active = False
        self.bonus_food_position = None
        self.bonus_food_spawn_time = 0
        self.bonus_food_duration = 5000  # 5 seconds in milliseconds
        self.food_count = 0
        
        # Hit effect
        self.hit_effect_active = False
        self.hit_effect_position = None
        self.hit_effect_start_time = 0
        self.hit_effect_duration = 1000  # 1 second
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.ORANGE = (255, 165, 0)
        self.DARK_ORANGE = (255, 140, 0)
        self.LIGHT_ORANGE = (255, 190, 0)
        self.YELLOW = (255, 255, 0)
        
    def start_eye_tracking(self):
        """Start the eye tracking system"""
        try:
            self.eye_controller.start()
            print("Eye tracking started. Please look straight ahead for calibration...")
        except Exception as e:
            print(f"Error starting eye tracking: {e}")
            return False
        return True
        
    def start_webcam_window(self):
        """Start webcam window in separate thread"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera for webcam window")
            return False
            
        self.webcam_running = True
        self.webcam_thread = threading.Thread(target=self._webcam_loop)
        self.webcam_thread.daemon = True
        self.webcam_thread.start()
        return True
        
    def _webcam_loop(self):
        """Webcam display loop - also controls the snake"""
        import mediapipe as mp
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False, 
            refine_landmarks=True,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Iris landmark indices
        left_iris_idx = [474, 475, 476, 477]
        right_iris_idx = [469, 470, 471, 472]
        
        calibrated_center = None
        frame_count = 0
        calibration_frames = 30
        is_calibrated = False
        
        # Same thresholds as eye controller
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
        
        while self.webcam_running:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
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
                        print("Webcam calibration complete!")
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
                    
                    # Update the eye controller's direction for the game
                    self.eye_controller.current_direction = eye_direction
                    
                    # Draw direction and displacement
                    cv2.putText(frame, f'Eye: {eye_direction}', (30, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)
                    cv2.putText(frame, f'dx: {dx:.1f}, dy: {dy:.1f}', (30, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    
                    # Draw calibrated center
                    cv2.circle(frame, tuple(np.int32(calibrated_center)), 8, (255, 0, 0), 2)
            
            cv2.imshow("Head Movement Monitor", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                break
                
            time.sleep(0.03)  # ~30 FPS
        
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_c:
                    # Recalibrate eye tracking
                    self.eye_controller.reset_calibration()
                    print("Recalibrating eye tracking...")
                elif event.key == pygame.K_a:
                    # Toggle auto-move
                    self.auto_move_enabled = not self.auto_move_enabled
                    print(f"Auto-move {'enabled' if self.auto_move_enabled else 'disabled'}")
                    
    def get_direct_direction(self, eye_direction):
        """Convert eye direction to snake direction (direct control, no mirror)"""
        # Direct control - no mirror effect
        return eye_direction
            
    def handle_eye_controls(self):
        """Handle eye movement controls with step-by-step movement"""
        current_time = pygame.time.get_ticks()
        eye_direction = self.eye_controller.current_direction  # Use the direction from webcam
        
        # Convert eye direction to snake direction (direct control)
        snake_direction = self.get_direct_direction(eye_direction)
        
        # Debug: Print current states every second
        if current_time % 1000 < 50:  # Print every second
            print(f"Eye: {eye_direction}, Snake: {self.snake.direction}")
        
        # Handle direction changes
        if snake_direction != self.snake.direction:
            # Try to change direction (prevents opposite direction movement)
            old_direction = self.snake.direction
            if self.snake.change_direction(snake_direction):
                self.last_direction = snake_direction
                self.auto_move_enabled = False  # Disable auto-move when user gives input
                print(f"Direction changed: {old_direction} -> {snake_direction}")
            else:
                # Direction change was blocked (opposite direction) - PAUSE THE SNAKE
                print(f"Direction change blocked: {old_direction} -> {snake_direction} - PAUSING SNAKE")
                # Set direction to CENTER to pause movement
                self.snake.direction = "CENTER"
                self.auto_move_enabled = False
                
        # Handle center position (stop movement)
        if snake_direction == "CENTER":
            self.auto_move_enabled = False
            
        # Auto-move if enabled and no recent eye input
        elif self.auto_move_enabled and current_time - self.last_auto_move_time >= self.auto_move_delay:
            # Continue in current direction
            self.last_auto_move_time = current_time
            
    def spawn_bonus_food(self):
        """Spawn bonus food"""
        self.bonus_food_position = (random.randint(0, 24), random.randint(0, 24))
        while (self.bonus_food_position in self.snake.body or 
               self.bonus_food_position == self.food.position):
            self.bonus_food_position = (random.randint(0, 24), random.randint(0, 24))
        self.bonus_food_active = True
        self.bonus_food_spawn_time = pygame.time.get_ticks()
        print("Bonus food spawned!")
            
    def update_game(self):
        """Update game state"""
        if self.paused or self.game_over:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Check bonus food timeout
        if (self.bonus_food_active and 
            current_time - self.bonus_food_spawn_time > self.bonus_food_duration):
            self.bonus_food_active = False
            self.bonus_food_position = None
            print("Bonus food expired!")
        
        # Handle eye controls
        self.handle_eye_controls()
        
        # Move snake based on current direction
        if self.snake.direction != "CENTER":
            # Move snake at regular intervals
            if current_time - self.last_move_time >= self.move_delay:
                self.snake.move()
                self.last_move_time = current_time
            
            # Handle boundary wrapping
            head = self.snake.body[0]
            x, y = head
            
            # Wrap horizontally (adjusted for smaller grid)
            if x < 0:
                x = 24
            elif x >= 25:
                x = 0
                
            # Wrap vertically (adjusted for smaller grid)
            if y < 0:
                y = 24
            elif y >= 25:
                y = 0
                
            # Update head position
            self.snake.body[0] = (x, y)
            
            # Check collision with self only (no boundary collision)
            if self.snake.check_self_collision():
                self.game_over = True
                # Create hit effect at collision point
                self.hit_effect_active = True
                self.hit_effect_position = (x, y)
                self.hit_effect_start_time = current_time
                print("Game Over! Snake hit itself!")
                return
            
            # Check collision with regular food
            if self.snake.body[0] == self.food.position:
                self.snake.grow()
                self.food.spawn(self.snake.body)
                self.game.increase_score()
                self.food_count += 1
                print(f"Food eaten! Score: {self.game.score}, Snake length: {len(self.snake.body)}")
                
                # Spawn bonus food every 5 normal foods
                if self.food_count % 5 == 0 and not self.bonus_food_active:
                    self.spawn_bonus_food()
            
            # Check collision with bonus food
            if (self.bonus_food_active and 
                self.snake.body[0] == self.bonus_food_position):
                # Add 5 segments to snake
                for _ in range(5):
                    self.snake.grow()
                self.game.increase_score(5)  # 5 points for bonus food
                self.bonus_food_active = False
                self.bonus_food_position = None
                print(f"Bonus food eaten! Score: {self.game.score}, Snake length: {len(self.snake.body)} (+5 segments)")
            
    def draw_textured_snake(self, win):
        """Draw snake with texture, eyes, and tail"""
        for i, segment in enumerate(self.snake.body):
            x, y = segment[0] * 20 + 10, segment[1] * 20 + 10  # Center of cell
            
            # Head is slightly larger
            radius = 12 if i == 0 else 8
            
            # Draw main segment
            pygame.draw.circle(win, self.ORANGE, (x, y), radius)
            
            # Add texture pattern
            if i == 0:  # Head
                # Add eyes
                self.draw_snake_eyes(win, x, y, self.snake.direction)
                # Add head pattern
                pygame.draw.circle(win, self.DARK_ORANGE, (x, y), radius - 2)
                pygame.draw.circle(win, self.ORANGE, (x, y), radius - 4)
            elif i == len(self.snake.body) - 1:  # Tail
                # Draw tail
                self.draw_snake_tail(win, x, y, self.snake.direction)
            else:  # Body segments
                # Add texture pattern
                pygame.draw.circle(win, self.DARK_ORANGE, (x, y), radius - 2)
                pygame.draw.circle(win, self.LIGHT_ORANGE, (x, y), radius - 4)
                pygame.draw.circle(win, self.ORANGE, (x, y), radius - 6)
                
                # Add small texture dots
                if i % 2 == 0:  # Alternate segments for texture
                    pygame.draw.circle(win, self.DARK_ORANGE, (x - 2, y - 2), 1)
                    pygame.draw.circle(win, self.DARK_ORANGE, (x + 2, y + 2), 1)
            
    def draw_snake_eyes(self, win, x, y, direction):
        """Draw eyes on snake head"""
        # Main eyes
        if direction == 'RIGHT':
            pygame.draw.circle(win, self.BLACK, (x + 4, y - 3), 2)
            pygame.draw.circle(win, self.BLACK, (x + 4, y + 3), 2)
            # Eye highlights
            pygame.draw.circle(win, self.WHITE, (x + 5, y - 4), 1)
            pygame.draw.circle(win, self.WHITE, (x + 5, y + 2), 1)
        elif direction == 'LEFT':
            pygame.draw.circle(win, self.BLACK, (x - 4, y - 3), 2)
            pygame.draw.circle(win, self.BLACK, (x - 4, y + 3), 2)
            # Eye highlights
            pygame.draw.circle(win, self.WHITE, (x - 5, y - 4), 1)
            pygame.draw.circle(win, self.WHITE, (x - 5, y + 2), 1)
        elif direction == 'UP':
            pygame.draw.circle(win, self.BLACK, (x - 3, y - 4), 2)
            pygame.draw.circle(win, self.BLACK, (x + 3, y - 4), 2)
            # Eye highlights
            pygame.draw.circle(win, self.WHITE, (x - 4, y - 5), 1)
            pygame.draw.circle(win, self.WHITE, (x + 2, y - 5), 1)
        elif direction == 'DOWN':
            pygame.draw.circle(win, self.BLACK, (x - 3, y + 4), 2)
            pygame.draw.circle(win, self.BLACK, (x + 3, y + 4), 2)
            # Eye highlights
            pygame.draw.circle(win, self.WHITE, (x - 4, y + 3), 1)
            pygame.draw.circle(win, self.WHITE, (x + 2, y + 3), 1)
            
    def draw_snake_tail(self, win, x, y, direction):
        """Draw tail at the end of snake"""
        # Draw tail segment
        pygame.draw.circle(win, self.DARK_ORANGE, (x, y), 6)
        pygame.draw.circle(win, self.ORANGE, (x, y), 4)
        
        # Draw tail tip based on direction
        if direction == 'RIGHT':
            pygame.draw.circle(win, self.DARK_ORANGE, (x + 6, y), 3)
        elif direction == 'LEFT':
            pygame.draw.circle(win, self.DARK_ORANGE, (x - 6, y), 3)
        elif direction == 'UP':
            pygame.draw.circle(win, self.DARK_ORANGE, (x, y - 6), 3)
        elif direction == 'DOWN':
            pygame.draw.circle(win, self.DARK_ORANGE, (x, y + 6), 3)
            
    def draw_round_food(self, win):
        """Draw round food"""
        x, y = self.food.position[0] * 20 + 10, self.food.position[1] * 20 + 10
        pygame.draw.circle(win, self.GREEN, (x, y), 8)
        
    def draw_bonus_food(self, win):
        """Draw bonus food with heartbeat effect"""
        if self.bonus_food_active and self.bonus_food_position:
            x, y = self.bonus_food_position[0] * 20 + 10, self.bonus_food_position[1] * 20 + 10
            
            # Heartbeat effect
            current_time = pygame.time.get_ticks()
            time_since_spawn = current_time - self.bonus_food_spawn_time
            heartbeat = 1 + 0.3 * math.sin(time_since_spawn * 0.01)  # Pulsing effect
            
            # Calculate remaining time
            remaining_time = max(0, self.bonus_food_duration - time_since_spawn)
            time_ratio = remaining_time / self.bonus_food_duration
            
            # Size based on heartbeat and time remaining
            base_size = 16
            size = int(base_size * heartbeat * (0.5 + 0.5 * time_ratio))
            
            # Color intensity based on time remaining
            color_intensity = int(255 * time_ratio)
            bonus_color = (255, color_intensity, color_intensity)
            
            pygame.draw.circle(win, bonus_color, (x, y), size)
            
            # Draw time remaining indicator
            if remaining_time < 2000:  # Last 2 seconds
                font = pygame.font.SysFont('Arial', 12)
                time_text = font.render(f"{remaining_time//1000}s", True, self.WHITE)
                text_rect = time_text.get_rect(center=(x, y - 25))
                win.blit(time_text, text_rect)
            
    def draw_hit_effect(self, win):
        """Draw hit effect at collision point"""
        if self.hit_effect_active and self.hit_effect_position:
            current_time = pygame.time.get_ticks()
            time_since_hit = current_time - self.hit_effect_start_time
            
            if time_since_hit < self.hit_effect_duration:
                x, y = self.hit_effect_position[0] * 20 + 10, self.hit_effect_position[1] * 20 + 10
                
                # Expanding circle effect
                progress = time_since_hit / self.hit_effect_duration
                size = int(20 * progress)
                alpha = int(255 * (1 - progress))
                
                # Create surface for alpha blending
                effect_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(effect_surface, (255, 0, 0, alpha), (size, size), size)
                win.blit(effect_surface, (x - size, y - size))
            else:
                self.hit_effect_active = False
            
    def draw(self):
        """Draw the game"""
        self.screen.fill(self.BLACK)
        
        # Draw grid (adjusted for smaller size)
        for x in range(0, 500, 20):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, 500))
        for y in range(0, 500, 20):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (500, y))
        
        # Draw snake (textured round with eyes and tail)
        self.draw_textured_snake(self.screen)
        
        # Draw food (round)
        self.draw_round_food(self.screen)
        
        # Draw bonus food with heartbeat
        self.draw_bonus_food(self.screen)
        
        # Draw hit effect
        self.draw_hit_effect(self.screen)
        
        # Draw score
        font = pygame.font.SysFont('Arial', 30)
        text = font.render(f"Score: {self.game.score}", True, self.WHITE)
        self.screen.blit(text, (10, 10))
        
        # Draw instructions in separate area below game
        instructions_area = pygame.Rect(0, 500, 500, 200)
        pygame.draw.rect(self.screen, (40, 40, 40), instructions_area)
        
        font = pygame.font.SysFont('Arial', 16)
        instructions = [
            "Snake Game - Eye Controlled",
            "Move your head to control the snake",
            f"Eye direction: {self.eye_controller.current_direction}",
            f"Snake direction: {self.snake.direction}",
            f"Snake length: {len(self.snake.body)}",
            f"Score: {self.game.score}",
            f"Food count: {self.food_count}",
            f"Bonus food: {'Active' if self.bonus_food_active else 'Inactive'}",
            "SPACE: Pause/Resume",
            "C: Recalibrate eye tracking",
            "R: Restart (when game over)",
            "ESC: Quit"
        ]
        
        for i, text in enumerate(instructions):
            text_surface = font.render(text, True, self.WHITE)
            self.screen.blit(text_surface, (10, 510 + i * 20))
            
        # Draw pause status
        if self.paused:
            font = pygame.font.SysFont('Arial', 36)
            text = font.render("PAUSED", True, self.YELLOW)
            text_rect = text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(text, text_rect)
            
        # Draw game over screen
        if self.game_over:
            font_large = pygame.font.SysFont('Arial', 48)
            font_small = pygame.font.SysFont('Arial', 24)
            
            game_over_text = font_large.render("GAME OVER", True, self.RED)
            score_text = font_small.render(f"Final Score: {self.game.score}", True, self.WHITE)
            restart_text = font_small.render("Press R to restart or ESC to quit", True, self.WHITE)
            
            game_over_rect = game_over_text.get_rect(center=(self.width//2, self.height//2 - 50))
            score_rect = score_text.get_rect(center=(self.width//2, self.height//2))
            restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 50))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)
            
        pygame.display.flip()
        
    def reset_game(self):
        """Reset the game to initial state"""
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.game = Game()
        self.game_over = False
        self.paused = False
        self.last_move_time = 0
        self.last_auto_move_time = 0
        self.auto_move_enabled = False
        self.last_direction = "CENTER"
        self.bonus_food_active = False
        self.bonus_food_position = None
        self.food_count = 0
        self.hit_effect_active = False
        
    def run(self):
        """Main game loop"""
        if not self.start_eye_tracking():
            print("Failed to start eye tracking. Exiting...")
            return
            
        if not self.start_webcam_window():
            print("Failed to start webcam window. Exiting...")
            return
            
        print("Snake Game Started!")
        print("Controls:")
        print("- Move your head to control the snake")
        print("- Look RIGHT → Snake moves RIGHT")
        print("- Look LEFT → Snake moves LEFT")
        print("- Look UP → Snake moves UP")
        print("- Look DOWN → Snake moves DOWN")
        print("- Look CENTER → Snake stops")
        print("- SPACE: Pause/Resume")
        print("- C: Recalibrate eye tracking")
        print("- R: Restart (when game over)")
        print("- ESC: Quit")
        print("- Two windows: Game window + Head movement monitor")
        
        while self.running:
            self.handle_events()
            self.update_game()
            self.draw()
            self.clock.tick(60)  # 60 FPS
            
        # Cleanup
        self.eye_controller.stop()
        self.webcam_running = False
        if self.webcam_thread:
            self.webcam_thread.join()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
