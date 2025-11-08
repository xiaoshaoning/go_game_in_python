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
├── go_game.py          # Main GUI application (modular architecture)
├── main_window.py      # Main window implementation
├── board_widget.py     # Go board display component
├── control_panel.py    # Game controls and status panel
├── game_manager.py     # Game logic coordinator
├── dependency_injection.py # Dependency injection container
├── event_system.py     # Event-driven communication system
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

## Architecture

This project uses a modular architecture with dependency injection and event-driven design for clean separation of concerns and maintainability.

### Architecture Components

#### 1. Dependency Injection Container

**File: `dependency_injection.py`**

- **DependencyContainer**: Manages service registration and resolution
- **ServiceProvider**: Global access point for services
- Supports three registration types:
  - **Service**: Direct instance
  - **Factory**: Function that creates instance
  - **Singleton**: Factory that creates instance once

#### 2. Event System

**File: `event_system.py`**

- **GameEventType**: Enumeration of all game events
- **GameEvent**: Data container for events
- **EventBus**: Central event distribution with PyQt signal integration
- **EventPublisher**: Global access point for event publishing/subscription

#### 3. Core Modules

- **Game Manager** (`game_manager.py`): Coordinates game logic and state, handles stone placement, pass, resign actions, manages SGF file operations
- **Board Widget** (`board_widget.py`): Displays Go board and stones, handles mouse interactions, publishes stone placement events
- **Control Panel** (`control_panel.py`): Game controls and status display, SGF file operations, navigation controls
- **Main Window** (`main_window.py`): Coordinates all UI components, initializes dependency injection, connects event handlers
- **State Machine** (`go_state_machine.py`): Game flow management
- **Rules Engine** (`go_rules.py`): Complete Go rules implementation
- **SGF Parser** (`sgf_parser.py`): Smart Game Format file support

### Dependency Graph

```
Main Window
    ├── Board Widget
    ├── Control Panel
    └── Game Manager
        ├── State Machine (via DI)
        ├── Go Rules (via DI)
        └── SGF Parser (via DI)
```

### Event Flow

#### Stone Placement Example
1. **User clicks** on board → `BoardWidget.stone_clicked` signal
2. **Main Window** forwards to `GameManager.handle_stone_placement()`
3. **Game Manager** validates move using `GoRules`
4. **If valid**: Publishes `STONE_PLACED` event
5. **Board Widget** receives event and updates display
6. **State Machine** updates game state
7. **Control Panel** receives `PLAYER_CHANGED` event and updates status

#### SGF Loading Example
1. **User clicks** "Load SGF" → `ControlPanel.load_sgf_requested` signal
2. **Main Window** opens file dialog
3. **Game Manager** parses file using `SGFParser`
4. **If successful**: Publishes `SGF_LOADED` event
5. **Control Panel** receives event and updates status
6. **Board Widget** receives `BOARD_CLEARED` and `STONE_PLACED` events

### Benefits

#### 1. Separation of Concerns
- **UI Layer**: BoardWidget, ControlPanel, MainWindow
- **Business Logic**: GameManager, GoRules, StateMachine
- **Data Access**: SGFParser

#### 2. Testability
```python
# Example unit test for GameManager
def test_stone_placement():
    manager = GameManager()
    manager.initialize_services()

    # Mock dependencies
    manager.go_rules = MockGoRules()
    manager.state_machine = MockStateMachine()

    # Test stone placement
    manager.handle_stone_placement(3, 3)

    # Verify events were published
    assert event_bus.has_event(GameEventType.STONE_PLACED)
```

#### 3. Extensibility
- New features can be added as independent modules
- Event system allows loose coupling
- Dependency injection makes swapping implementations easy

#### 4. Maintainability
- Smaller, focused classes
- Clear dependency boundaries
- Easy to understand and modify individual components

### Adding New Features
1. **New Component**: Create module with clear responsibilities
2. **Dependencies**: Register in dependency injection container
3. **Events**: Define new event types and publish/subscribe as needed
4. **Integration**: Connect in MainWindow or appropriate manager

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Go rules implementation based on standard Japanese rules
- SGF format support for game recording and playback
- PyQt6 for the modern graphical interface