# Head-Controlled Snake Game

A classic Snake game where the snake is controlled by eye and head positionss using computer vision and MediaPipe face mesh detection.

## 🎮 Features

- Control the snake by turning the head in different directions (up, down, left, right)
- Uses MediaPipe face mesh for accurate iris and head position detection
- The system calibrates to your neutral eye position
- Snake stops when you look center
- Collect food to grow and increase your score
- Special yellow food appears every 5 points for extra rewards
- Pause the game anytime with the SPACE key
- Recalibrate eye tracking with C key
- Toggle continuous movement with A key

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd SnakeGame
   ```

2. **Create and activate virtual environment**

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 How to Play

### Eye-Controlled Game

1. **Test eye tracking first** (recommended):
   ```bash
   python test_eye_tracking.py
   ```

2. **Run the main game**:
   ```bash
   python main.py
   ```

3. **Calibration**:
   - When the game starts, look straight ahead at the camera
   - The system will calibrate for 30 frames (~1 second)
   - Keep your head relatively still during calibration

### Keyboard Controls
- `SPACE`: Pause/Resume game
- `C`: Recalibrate eye tracking
- `A`: Toggle auto-move (continues in current direction)
- `R`: Restart game (when game over)
- `ESC`: Quit game


## 🎯 Game Rules

- **Objective**: Control the snake to eat red food and grow longer
- **Movement**: The snake moves step-by-step based on head direction
- **Food**: Red squares are regular food (1 point)
- **Bonus Food**: Yellow squares appear every 5 points (2 points)
- **Collision**: Game ends if the snake hits itself
- **Score**: Points increase for each food eaten

## 📁 Project Structure

```
SnakeGame/
├── main.py                    # Main eye-controlled game
├── test_snake_movement.py     # Keyboard test mode
├── test_eye_tracking.py       # Eye tracking test
├── head_controller.py         # Head tracking controller
├── snake.py                   # Snake class with smart movement
├── food.py                    # Food class
├── game.py                    # Game utilities
├── demo.py                    # Eye tracking demo
├── requirements.txt           # Dependencies
└── README.md                 # This file
```

## 🛠️ Technical Details

- **Eye and head Tracking**: MediaPipe Face Mesh for iris and face detection
- **Game Engine**: Pygame for graphics and game loop
- **Computer Vision**: OpenCV for image processing
- **Threading**: Eye tracking runs in a separate thread for smooth gameplay
- **Movement Logic**: Smart direction validation prevents opposite movement
- **Calibration**: Automatic neutral position detection

## 🎮 Game Modes

### 1. Keyboard Test Mode (`test_snake_movement.py`)
- Arrow key controls
- No webcam required
- Test movement logic
- Debug information

### 2. Eye Tracking Test (`test_eye_tracking.py`)
- Eye tracking visualization
- Calibration testing
- Direction detection testing

## 🚀 Future Enhancements

- [ ] Multiple difficulty levels
- [ ] Power-ups and special effects
- [ ] Multiplayer support
- [ ] Customizable controls
- [ ] Score leaderboard
- [ ] Different game modes

