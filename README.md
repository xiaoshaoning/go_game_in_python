# Go Game - Complete Implementation

This is a complete Go game implementation with PyQt6 GUI and state machine architecture.

## Features

- **Complete Go Rules**: Stone placement, capture mechanics, ko rule
- **PyQt6 GUI**: Modern graphical interface
- **State Machine**: Robust game flow management
- **SGF Support**: Smart Game Format file loading and saving
- **Game Recording**: Save and replay games

## Requirements

- Python 3.8+
- PyQt6

## Installation

1. **Install PyQt6**:
   ```bash
   pip install PyQt6
   ```

2. **Verify Installation**:
   ```bash
   python -c "import PyQt6.QtWidgets; print('PyQt6 installed successfully')"
   ```

## Running the Game

### Option 1: Use the Launcher (Recommended)

```bash
cd generated_go_complete_v4
python run_go_game.py
```

Then select option 1 for GUI version.

### Option 2: Run GUI Directly

```bash
cd generated_go_complete_v4
python go_game_gui.py
```

### Option 3: Test State Machine Only

```bash
cd generated_go_complete_v4
python test_go_game_corrected.py
```

## Game Controls

### GUI Controls
- **New Game**: Start a new game
- **Pass**: Pass your turn
- **Resign**: Resign the current game
- **Load SGF**: Load a Smart Game Format file
- **Save Game**: Save current game as SGF

### Board Interaction
- **Click intersections**: Place stones
- The game automatically handles turn switching and move validation

## Game States

The game uses a state machine with these states:

1. **GUI Initialization**: Initialize PyQt6 components
2. **Main Menu**: Game menu and options
3. **Game Setup**: Configure board size, komi, handicap
4. **Black Turn**: Black player's turn
5. **White Turn**: White player's turn
6. **Move Validation**: Validate move legality
7. **Stone Placement**: Place stone on board
8. **Liberty Check**: Check liberties and capture stones
9. **Ko Check**: Verify ko rule compliance
10. **SGF Loading**: Load SGF files
11. **SGF Playback**: Play SGF moves
12. **Game Recording**: Save games as SGF
13. **Score Calculation**: Calculate final score
14. **Game Over**: Display results

## File Structure

- `gogameenhanced_corrected.py` - Corrected state machine implementation
- `go_game_gui.py` - PyQt6 GUI application
- `run_go_game.py` - Game launcher
- `test_go_game_corrected.py` - State machine test
- `c/` - C language implementation

## Development

### State Machine

The state machine is generated from the specification in:
`../go_game/state_machines/go_game_enhanced_v2.json`

### Code Generation

The Python code was generated using Magic Cube workflow and corrected with:
`../create_corrected_state_machine.py`

## Troubleshooting

### PyQt6 Installation Issues

If you encounter PyQt6 installation issues:

1. **Windows**:
   ```bash
   pip install PyQt6
   ```

2. **macOS**:
   ```bash
   pip3 install PyQt6
   ```

3. **Linux**:
   ```bash
   sudo apt-get install python3-pyqt6
   # or
   pip install PyQt6
   ```

### Import Errors

If you get import errors, make sure you're running from the correct directory:

```bash
cd D:\tools\magic_cube\generated_go_complete_v4
python go_game_gui.py
```

## Game Rules

- **Board**: 19x19 grid
- **Komi**: 6.5 points for white
- **Capture**: Stones with no liberties are captured
- **Ko**: Immediate repetition of board position is forbidden
- **Scoring**: Territory + captured stones + komi

Enjoy playing Go!