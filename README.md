# Go Game in Python

A complete Go (围棋) game implementation with modern PyQt6 GUI, state machine architecture, and SGF file support.

## Features

- **Complete Go Rules**: Stone placement, capture mechanics, ko rule, suicide prevention
- **Modern PyQt6 GUI**: Clean and intuitive graphical interface
- **State Machine Architecture**: Robust game flow management
- **SGF Support**: Smart Game Format file loading and saving
- **Game Recording**: Save and replay games with move-by-move navigation
- **Move Validation**: Real-time Go rules enforcement

## Requirements

- Python 3.8+
- PyQt6

## Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/xiaoshaoning/go_game_in_python.git
   cd go_game_in_python
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Game

```bash
python go_game.py
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

### SGF Navigation
- **First/Previous/Next/Last**: Navigate through SGF moves
- **Load SGF**: Import existing game records
- **Save Game**: Export current game to SGF format

## File Structure

```
go_game_in_python/
├── go_game.py          # Main GUI application
├── go_state_machine.py # State machine implementation
├── go_rules.py         # Go rules validation engine
├── sgf_parser.py       # SGF file parser
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── *.sgf              # Example SGF game files
```

## Game Rules

- **Board**: 19x19 grid (standard professional size)
- **Komi**: 6.5 points for white (standard compensation)
- **Capture**: Stones with no liberties are captured
- **Ko**: Immediate repetition of board position is forbidden
- **Suicide**: Self-capture moves are not allowed
- **Scoring**: Territory + captured stones + komi

## Development

This project uses a state machine architecture for robust game flow management:

- **State Machine**: `go_state_machine.py`
- **GUI**: `go_game.py` (PyQt6-based interface)
- **Rules Engine**: `go_rules.py` (Complete Go rules implementation)
- **SGF Parser**: `sgf_parser.py` (Smart Game Format support)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Go rules implementation based on standard Japanese rules
- SGF format support for game recording and playback
- PyQt6 for the modern graphical interface