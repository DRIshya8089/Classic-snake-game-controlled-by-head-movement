# Eye-Controlled Snake Game

A classic Snake game where the snake is controlled by eye movements using computer vision and MediaPipe face mesh detection. The game features intelligent movement restrictions to prevent instant death from opposite direction movement.

## 🎮 Features

- **Eye Movement Control**: Control the snake by looking in different directions (up, down, left, right)
- **Smart Movement Logic**: Prevents instant death by blocking opposite direction movement
- **Real-time Eye Tracking**: Uses MediaPipe face mesh for accurate iris detection
- **Automatic Calibration**: The system calibrates to your neutral eye position
- **Stop on Center**: Snake stops when you look straight ahead
- **Classic Snake Gameplay**: Collect food to grow and increase your score
- **Bonus Food System**: Special yellow food appears every 5 points for extra rewards
- **Pause/Resume**: Pause the game anytime with SPACE key
- **Recalibration**: Recalibrate eye tracking with C key
- **Auto-move**: Toggle continuous movement with A key
- **Keyboard Test Mode**: Test snake movement with arrow keys

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam
- Good lighting for eye tracking

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd SnakeGame
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv senv
   
   # Activate on Windows
   senv\Scripts\activate
   
   # Activate on macOS/Linux
   source senv/bin/activate
   ```

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

### Keyboard Test Mode

Test snake movement with keyboard controls:
```bash
python test_snake_movement.py
```

## 🎮 Game Controls

### Eye Movement Controls
- **Look LEFT** → Snake moves LEFT (direct control)
- **Look RIGHT** → Snake moves RIGHT (direct control)
- **Look UP** → Snake moves UP (direct control)
- **Look DOWN** → Snake moves DOWN (direct control)
- **Look CENTER** → Snake stops

### Keyboard Controls
- `SPACE`: Pause/Resume game
- `C`: Recalibrate eye tracking
- `A`: Toggle auto-move (continues in current direction)
- `R`: Restart game (when game over)
- `ESC`: Quit game

### Test Mode Controls
- `Arrow Keys`: Control snake direction
- `SPACE`: Show current direction
- `R`: Restart (when game over)
- `ESC`: Quit

## 🎯 Game Rules

- **Objective**: Control the snake to eat red food and grow longer
- **Movement**: The snake moves step-by-step based on eye direction
- **Smart Movement**: Cannot move in opposite direction (snake pauses instead of dying)
- **Food**: Red squares are regular food (1 point)
- **Bonus Food**: Yellow squares appear every 5 points (2 points)
- **Collision**: Game ends if the snake hits itself
- **Score**: Points increase for each food eaten

## 🔧 Smart Movement System

### Opposite Direction Prevention
The game implements intelligent movement logic to prevent instant death:

- **Current Direction**: RIGHT
- **Allowed**: UP, DOWN (90° turns)
- **Blocked**: LEFT (opposite direction) → **Snake pauses**

- **Current Direction**: LEFT  
- **Allowed**: UP, DOWN (90° turns)
- **Blocked**: RIGHT (opposite direction) → **Snake pauses**

- **Current Direction**: UP
- **Allowed**: LEFT, RIGHT (90° turns)  
- **Blocked**: DOWN (opposite direction) → **Snake pauses**

- **Current Direction**: DOWN
- **Allowed**: LEFT, RIGHT (90° turns)
- **Blocked**: UP (opposite direction) → **Snake pauses**

This ensures players must make 90-degree turns to change direction. When an opposite direction is attempted, the snake pauses instead of dying instantly, making the game more forgiving and strategic.

## 📁 Project Structure

```
SnakeGame/
├── main.py                    # Main eye-controlled game
├── test_snake_movement.py     # Keyboard test mode
├── test_eye_tracking.py       # Eye tracking test
├── eye_controller.py          # Eye tracking controller
├── snake.py                   # Snake class with smart movement
├── food.py                    # Food class
├── game.py                    # Game utilities
├── demo.py                    # Eye tracking demo
├── requirements.txt           # Dependencies
└── README.md                 # This file
```

## 🛠️ Technical Details

- **Eye Tracking**: MediaPipe Face Mesh for iris detection
- **Game Engine**: Pygame for graphics and game loop
- **Computer Vision**: OpenCV for image processing
- **Threading**: Eye tracking runs in separate thread for smooth gameplay
- **Movement Logic**: Smart direction validation prevents opposite movement
- **Calibration**: Automatic neutral position detection

## 🎯 Tips for Better Eye Tracking

1. **Good Lighting**: Ensure your face is well-lit
2. **Camera Position**: Position your camera at eye level
3. **Distance**: Stay about 20-30 inches from the camera
4. **Calibration**: Look straight ahead during calibration
5. **Head Movement**: Keep your head relatively still, move only your eyes
6. **Recalibration**: If tracking becomes inaccurate, press 'C' to recalibrate
7. **Test First**: Run `test_eye_tracking.py` to verify eye tracking works

## 🔧 Troubleshooting

### Camera Issues
- Make sure your webcam is connected and working
- Try running `test_eye_tracking.py` first to test eye tracking

### Eye Tracking Problems
- Ensure good lighting on your face
- Keep your head relatively still
- Recalibrate by pressing 'C'
- Check that your face is clearly visible to the camera

### Movement Issues
- **Opposite direction blocked**: This is intentional - you must make 90° turns
- **Snake pauses when trying opposite direction**: This is the new safety feature - the snake pauses instead of dying
- **Snake not responding**: Try recalibrating with 'C' key
- **Mirror effect**: The game uses direct control (no mirror effect)

### Performance Issues
- Close other applications using the camera
- Reduce the game window size if needed
- Ensure your computer meets the minimum requirements

## 📋 Requirements

### System Requirements
- Python 3.8+
- Webcam
- Good lighting
- 4GB RAM minimum
- Modern CPU (for real-time eye tracking)

### Dependencies
- pygame==2.6.1
- opencv-python==4.11.0.86
- mediapipe==0.10.21
- numpy==1.26.4
- dlib==20.0.0

## 🎮 Game Modes

### 1. Eye-Controlled Mode (`main.py`)
- Full eye tracking control
- Real-time webcam feed
- Automatic calibration
- All features enabled

### 2. Keyboard Test Mode (`test_snake_movement.py`)
- Arrow key controls
- No webcam required
- Test movement logic
- Debug information

### 3. Eye Tracking Test (`test_eye_tracking.py`)
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

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please open an issue on the repository.

