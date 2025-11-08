#!/usr/bin/env python3
"""
Game Manager Module

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import List, Tuple

from event_system import EventPublisher, GameEventType
from dependency_injection import ServiceProvider


class GameManager:
    """Game manager coordinating game logic and state."""

    def __init__(self):
        self.state_machine = None
        self.go_rules = None
        self.sgf_parser = None
        self.current_player = "black"
        self.board_size = 19
        self.game_history: List[Tuple[str, int, int]] = []
        self.move_counter = 0

        # SGF navigation
        self.loaded_sgf_moves: List[Tuple[str, int, int]] = []
        self.current_move_index = 0

        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Setup event listeners."""
        EventPublisher.subscribe_to_event(GameEventType.STONE_PLACED, self._on_stone_placed)

    def initialize_services(self):
        """Initialize required services."""
        try:
            self.state_machine = ServiceProvider.get_service("state_machine")
            self.go_rules = ServiceProvider.get_service("go_rules")
            self.sgf_parser = ServiceProvider.get_service("sgf_parser")
        except Exception as e:
            print(f"Error initializing services: {e}")

    def start_new_game(self):
        """Start a new game."""
        if self.go_rules:
            self.go_rules.clear_board()

        self.game_history = []
        self.move_counter = 0
        self.current_player = "black"

        # Reset SGF navigation
        self.loaded_sgf_moves = []
        self.current_move_index = 0

        # Reset state machine
        if self.state_machine:
            self.state_machine.handle_event('gui_ready')
            self.state_machine.handle_event('new_game')
            self.state_machine.handle_event('setup_complete')

        EventPublisher.publish_event(GameEventType.BOARD_CLEARED)
        EventPublisher.publish_event(GameEventType.GAME_STARTED)
        EventPublisher.publish_event(GameEventType.PLAYER_CHANGED, {
            'current_player': 'black'
        })

    def handle_stone_placement(self, row: int, col: int):
        """Handle stone placement with full Go rules validation."""
        if not self.state_machine or not self.go_rules:
            return

        current_state = self.state_machine.current_state.__class__.__name__

        # Determine current player color
        if "black_turn" in current_state.lower():
            color = 1  # Black
            current_player = "black"
        elif "white_turn" in current_state.lower():
            color = 2  # White
            current_player = "white"
        else:
            # Not player's turn
            return

        # Validate move using Go rules
        is_valid, error_msg = self.go_rules.is_valid_move(color, row, col)

        if not is_valid:
            # Publish validation failed event
            EventPublisher.publish_event(GameEventType.MOVE_VALIDATED, {
                'valid': False,
                'error': error_msg,
                'row': row,
                'col': col,
                'color': color
            })
            return

        # Execute the move
        try:
            # Place stone using rules engine
            captured_stones = self.go_rules.place_stone(color, row, col)

            # Increment move counter
            self.move_counter += 1

            # Update game history
            self.game_history.append(("B" if color == 1 else "W", row, col))

            # Publish stone placed event
            EventPublisher.publish_event(GameEventType.STONE_PLACED, {
                'row': row,
                'col': col,
                'color': color,
                'move_number': self.move_counter,
                'captured_stones': captured_stones
            })

            # Publish captures
            for stone_pos in captured_stones:
                EventPublisher.publish_event(GameEventType.STONE_CAPTURED, {
                    'row': stone_pos[0],
                    'col': stone_pos[1]
                })

            # Update state machine
            if current_player == "black":
                self.state_machine.handle_event("black_move")
                self.state_machine.handle_event("move_valid")
                self.state_machine.handle_event("stone_placed")
                self.state_machine.handle_event("captures_processed")
                self.state_machine.handle_event("ko_passed_black")
                self.current_player = "white"
            else:
                self.state_machine.handle_event("white_move")
                self.state_machine.handle_event("move_valid")
                self.state_machine.handle_event("stone_placed")
                self.state_machine.handle_event("captures_processed")
                self.state_machine.handle_event("ko_passed_white")
                self.current_player = "black"

            # Publish player changed event
            EventPublisher.publish_event(GameEventType.PLAYER_CHANGED, {
                'current_player': self.current_player
            })

        except Exception as e:
            print(f"Error placing stone: {e}")

    def handle_pass(self):
        """Handle pass action."""
        if not self.state_machine:
            return

        current_state = self.state_machine.current_state.__class__.__name__

        if "black_turn" in current_state.lower():
            self.state_machine.handle_event("black_pass")
            self.current_player = "white"
        elif "white_turn" in current_state.lower():
            self.state_machine.handle_event("white_pass")
            self.current_player = "black"

        EventPublisher.publish_event(GameEventType.PLAYER_CHANGED, {
            'current_player': self.current_player
        })

    def handle_resign(self):
        """Handle resign action."""
        if not self.state_machine:
            return

        current_state = self.state_machine.current_state.__class__.__name__

        if "black_turn" in current_state.lower():
            self.state_machine.handle_event("black_resign")
        elif "white_turn" in current_state.lower():
            self.state_machine.handle_event("white_resign")

        EventPublisher.publish_event(GameEventType.GAME_ENDED, {
            'result': f"{self.current_player.title()} resigned"
        })

    def load_sgf_file(self, filename: str) -> bool:
        """Load SGF file."""
        if not self.sgf_parser:
            return False

        try:
            if self.sgf_parser.parse_file(filename):
                # Get moves and properties
                self.loaded_sgf_moves = self.sgf_parser.get_moves()
                properties = self.sgf_parser.get_properties()

                # Start at first move
                self.current_move_index = 1 if self.loaded_sgf_moves else 0

                # Immediately display first move after loading
                if self.loaded_sgf_moves:
                    self._display_current_position()

                # Publish SGF loaded event
                EventPublisher.publish_event(GameEventType.SGF_LOADED, {
                    'properties': properties,
                    'moves': self.loaded_sgf_moves
                })

                return True
            else:
                return False

        except Exception as e:
            print(f"Error loading SGF: {e}")
            return False

    def navigate_sgf(self, action: str):
        """Navigate through loaded SGF moves with proper capture handling."""
        if not self.loaded_sgf_moves:
            return

        if action == "first":
            self.current_move_index = 1  # Show first move
        elif action == "prev" and self.current_move_index > 0:
            self.current_move_index -= 1
        elif action == "next" and self.current_move_index < len(self.loaded_sgf_moves):
            self.current_move_index += 1
        elif action == "last":
            self.current_move_index = len(self.loaded_sgf_moves)

        # Display the current position
        self._display_current_position()

    def save_game(self, filename: str, properties: dict = None) -> bool:
        """Save current game as SGF."""
        if not self.sgf_parser or not self.game_history:
            return False

        try:
            if properties is None:
                properties = {
                    'PB': 'Black Player',
                    'PW': 'White Player',
                    'RE': 'B+Resign',
                    'DT': '2024',
                }

            sgf_content = self.sgf_parser.create_sgf(self.game_history, properties)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(sgf_content)

            EventPublisher.publish_event(GameEventType.SGF_SAVED, {
                'filename': filename
            })

            return True

        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def _display_current_position(self):
        """Display the current SGF position based on current_move_index."""
        # Clear board
        EventPublisher.publish_event(GameEventType.BOARD_CLEARED)
        if self.go_rules:
            self.go_rules.clear_board()

        # Replay moves up to current index
        for i in range(self.current_move_index):
            color, row, col = self.loaded_sgf_moves[i]
            stone_color = 1 if color == "B" else 2
            move_number = i + 1

            if self.go_rules:
                # Use replay_stone for SGF replay (bypasses validation since moves are already valid)
                captured_stones = self.go_rules.replay_stone(stone_color, row, col)

                # Publish stone placed event
                EventPublisher.publish_event(GameEventType.STONE_PLACED, {
                    'row': row,
                    'col': col,
                    'color': stone_color,
                    'move_number': move_number
                })

                # Publish capture events for any stones that were captured
                for stone_pos in captured_stones:
                    EventPublisher.publish_event(GameEventType.STONE_CAPTURED, {
                        'row': stone_pos[0],
                        'col': stone_pos[1]
                    })

    def _on_stone_placed(self, event):
        """Handle stone placed event (for internal tracking)."""
        # This method can be used for additional game logic
        pass