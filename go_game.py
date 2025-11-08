#!/usr/bin/env python3
"""
Go Game with PyQt6 GUI - Fixed Version
Complete Go game implementation with state machine and GUI
Fixed signal handling issues
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QMessageBox,
                            QGridLayout, QFrame, QSizePolicy, QFileDialog)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont

from gogameenhanced_corrected import StateMachine
from sgf_parser import SGFParser
from go_rules import GoRules


class GoBoardWidget(QWidget):
    """Go board widget for displaying and interacting with the game board."""

    # Define signal for stone clicks
    stone_clicked = pyqtSignal(int, int)  # row, col

    def __init__(self, board_size=19):
        super().__init__()
        self.board_size = board_size
        self.cell_size = 40  # Increased by 1/3 (from 30 to 40)
        self.margin = 53  # Increased by 1/3 (from 40 to 53)
        self.stones = {}  # (row, col) -> (color, move_number)
        self.setMinimumSize(800, 800)  # Increased minimum size
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        """Paint the Go board and stones."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw board background
        painter.fillRect(self.rect(), QColor(220, 179, 92))  # Wood color

        # Draw grid lines
        painter.setPen(QPen(Qt.GlobalColor.black, 2))

        for i in range(self.board_size):
            # Horizontal lines
            y = self.margin + i * self.cell_size
            painter.drawLine(self.margin, y,
                           self.margin + (self.board_size-1) * self.cell_size, y)
            # Vertical lines
            x = self.margin + i * self.cell_size
            painter.drawLine(x, self.margin,
                           x, self.margin + (self.board_size-1) * self.cell_size)

        # Draw star points for 19x19 board
        if self.board_size == 19:
            star_points = [3, 9, 15]
            painter.setBrush(QBrush(Qt.GlobalColor.black))
            for i in star_points:
                for j in star_points:
                    x = self.margin + i * self.cell_size
                    y = self.margin + j * self.cell_size
                    painter.drawEllipse(x-3, y-3, 6, 6)

        # Draw stones with move numbers
        for (row, col), (color, move_number) in self.stones.items():
            x = self.margin + col * self.cell_size
            y = self.margin + row * self.cell_size

            # Stone size increased by 1/3 (from 26 to 35)
            stone_size = 35
            stone_radius = stone_size // 2

            if color == 1:  # Black
                painter.setBrush(QBrush(Qt.GlobalColor.black))
                painter.setPen(QPen(Qt.GlobalColor.black))
                text_color = Qt.GlobalColor.white  # White text on black stones
            else:  # White
                painter.setBrush(QBrush(Qt.GlobalColor.white))
                painter.setPen(QPen(Qt.GlobalColor.black))
                text_color = Qt.GlobalColor.black  # Black text on white stones

            painter.drawEllipse(x-stone_radius, y-stone_radius, stone_size, stone_size)

            # Draw move number
            if move_number > 0:
                painter.setPen(QPen(text_color))
                painter.setFont(QFont("Arial", 15, QFont.Weight.Bold))  # Font size reduced by 1/4 (from 20 to 15)
                text_rect = painter.fontMetrics().boundingRect(str(move_number))
                # Perfect centering: center both horizontally and vertically
                painter.drawText(x - text_rect.width()//2, y + text_rect.height()//3, str(move_number))

    def mousePressEvent(self, event):
        """Handle mouse clicks to place stones."""
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.position().x()
            y = event.position().y()

            # Convert to board coordinates
            col = round((x - self.margin) / self.cell_size)
            row = round((y - self.margin) / self.cell_size)

            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                # Emit signal for stone placement - FIXED: using proper signal
                self.stone_clicked.emit(row, col)

    def place_stone(self, row, col, color, move_number=0):
        """Place a stone on the board with move number."""
        self.stones[(row, col)] = (color, move_number)
        self.update()

    def clear_board(self):
        """Clear all stones from the board."""
        self.stones.clear()
        self.update()


class GoGameWindow(QMainWindow):
    """Main Go game window with GUI."""

    def __init__(self):
        super().__init__()
        self.state_machine = StateMachine()
        self.current_player = "black"
        self.board_size = 19
        self.game_history = []  # Track moves for SGF saving
        self.move_counter = 0  # Track move numbers starting from 1
        self.sgf_parser = SGFParser()
        self.go_rules = GoRules(self.board_size)

        # SGF navigation variables
        self.loaded_sgf_moves = []  # All moves from loaded SGF
        self.current_move_index = 0  # Current move being displayed (0 = first move)
        # Trigger initial state transitions
        self.state_machine.handle_event('gui_ready')
        self.state_machine.handle_event('new_game')
        self.state_machine.handle_event('setup_complete')

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Go Game - Fixed Version")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel - Board
        self.board_widget = GoBoardWidget(self.board_size)
        main_layout.addWidget(self.board_widget, 3)

        # Right panel - Controls
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)
        main_layout.addWidget(control_panel, 1)

        # Game info
        self.status_label = QLabel("Game Status: Initializing...")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        control_layout.addWidget(self.status_label)

        # SGF status display (silent, no popup)
        self.sgf_status_label = QLabel("")
        self.sgf_status_label.setFont(QFont("Arial", 9))
        self.sgf_status_label.setStyleSheet("color: gray;")
        control_layout.addWidget(self.sgf_status_label)

        control_layout.addSpacing(20)

        # Game controls
        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.clicked.connect(self.new_game)
        control_layout.addWidget(self.new_game_btn)

        self.pass_btn = QPushButton("Pass")
        self.pass_btn.clicked.connect(self.pass_turn)
        control_layout.addWidget(self.pass_btn)

        self.resign_btn = QPushButton("Resign")
        self.resign_btn.clicked.connect(self.resign)
        control_layout.addWidget(self.resign_btn)

        control_layout.addSpacing(20)

        # SGF controls
        self.load_sgf_btn = QPushButton("Load SGF")
        self.load_sgf_btn.clicked.connect(self.load_sgf)
        control_layout.addWidget(self.load_sgf_btn)

        self.save_sgf_btn = QPushButton("Save Game")
        self.save_sgf_btn.clicked.connect(self.save_game)
        control_layout.addWidget(self.save_sgf_btn)

        control_layout.addSpacing(20)

        # SGF navigation controls
        nav_layout = QHBoxLayout()

        self.first_move_btn = QPushButton("First")
        self.first_move_btn.clicked.connect(self.show_first_move)
        self.first_move_btn.setEnabled(False)
        nav_layout.addWidget(self.first_move_btn)

        self.prev_move_btn = QPushButton("Previous")
        self.prev_move_btn.clicked.connect(self.show_previous_move)
        self.prev_move_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_move_btn)

        self.next_move_btn = QPushButton("Next")
        self.next_move_btn.clicked.connect(self.show_next_move)
        self.next_move_btn.setEnabled(False)
        nav_layout.addWidget(self.next_move_btn)

        self.last_move_btn = QPushButton("Last")
        self.last_move_btn.clicked.connect(self.show_last_move)
        self.last_move_btn.setEnabled(False)
        nav_layout.addWidget(self.last_move_btn)

        control_layout.addLayout(nav_layout)

        control_layout.addStretch()

        # Connect board clicks - FIXED: using proper signal connection
        self.board_widget.stone_clicked.connect(self.handle_stone_click)

        # Update initial state
        self.update_display()

    def update_display(self):
        """Update the display based on current state."""
        current_state = self.state_machine.current_state.__class__.__name__

        # Convert technical state names to user-friendly display
        if "black_turn" in current_state.lower():
            self.status_label.setText("Game Status: Black")
            self.current_player = "black"
        elif "white_turn" in current_state.lower():
            self.status_label.setText("Game Status: White")
            self.current_player = "white"
        elif "game_over" in current_state.lower():
            self.status_label.setText("Game Status: Game Over")
        elif "score_calculation" in current_state.lower():
            self.status_label.setText("Game Status: Scoring")
        elif "main_menu" in current_state.lower():
            self.status_label.setText("Game Status: Main Menu")
        elif "game_setup" in current_state.lower():
            self.status_label.setText("Game Status: Setting Up")
        else:
            # For other states, show simplified name
            simplified_name = current_state.replace("State", "")
            self.status_label.setText(f"Game Status: {simplified_name}")

    def handle_stone_click(self, row, col):
        """Handle stone placement on the board with full Go rules validation."""
        current_state = self.state_machine.current_state.__class__.__name__

        # Determine current player color
        if "black_turn" in current_state.lower():
            color = 1  # Black
            current_player = "black"
        elif "white_turn" in current_state.lower():
            color = 2  # White
            current_player = "white"
        else:
            QMessageBox.warning(self, "Invalid Move", "Not your turn!")
            return

        # Validate move using Go rules
        is_valid, error_msg = self.go_rules.is_valid_move(color, row, col)

        if not is_valid:
            QMessageBox.warning(self, "Invalid Move", error_msg)
            return

        # Execute the move
        try:
            # Place stone using rules engine
            captured_stones = self.go_rules.place_stone(color, row, col)

            # Increment move counter and place stone with move number
            self.move_counter += 1
            self.board_widget.place_stone(row, col, color, self.move_counter)

            # Remove captured stones from GUI
            for stone_pos in captured_stones:
                if stone_pos in self.board_widget.stones:
                    del self.board_widget.stones[stone_pos]

            # Update game history
            self.game_history.append(("B" if color == 1 else "W", row, col))

            # Update state machine
            if current_player == "black":
                self.state_machine.handle_event("black_move")
                self.state_machine.handle_event("move_valid")
                self.state_machine.handle_event("stone_placed")
                self.state_machine.handle_event("captures_processed")
                self.state_machine.handle_event("ko_passed_black")
            else:
                self.state_machine.handle_event("white_move")
                self.state_machine.handle_event("move_valid")
                self.state_machine.handle_event("stone_placed")
                self.state_machine.handle_event("captures_processed")
                self.state_machine.handle_event("ko_passed_white")

            # Update display
            self.update_display()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error placing stone: {str(e)}")
            return

    def new_game(self):
        """Start a new game."""
        self.board_widget.clear_board()
        self.go_rules.clear_board()  # Clear rules engine state
        self.move_counter = 0  # Reset move counter
        self.game_history = []  # Clear game history

        # Reset SGF status display
        self.sgf_status_label.setText("")
        self.sgf_status_label.setStyleSheet("color: gray;")

        # Completely reset the state machine by creating a new instance
        self.state_machine = StateMachine()

        # Trigger initial state transitions to start fresh game
        self.state_machine.handle_event('gui_ready')
        self.state_machine.handle_event('new_game')
        self.state_machine.handle_event('setup_complete')

        self.update_display()

    def pass_turn(self):
        """Pass the current turn."""
        current_state = self.state_machine.current_state.__class__.__name__

        if "black_turn" in current_state.lower():
            self.state_machine.handle_event("black_pass")
        elif "white_turn" in current_state.lower():
            self.state_machine.handle_event("white_pass")

        self.update_display()

    def resign(self):
        """Resign the current game."""
        current_state = self.state_machine.current_state.__class__.__name__

        if "black_turn" in current_state.lower():
            self.state_machine.handle_event("black_resign")
        elif "white_turn" in current_state.lower():
            self.state_machine.handle_event("white_resign")

        self.update_display()

    def load_sgf(self):
        """Load SGF file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load SGF File", "", "SGF Files (*.sgf);;All Files (*)")

        if filename:
            try:
                # Parse SGF file
                if self.sgf_parser.parse_file(filename):
                    # Clear current board
                    self.board_widget.clear_board()
                    self.go_rules.clear_board()
                    self.game_history = []
                    self.move_counter = 0  # Reset move counter

                    # Get moves from SGF
                    self.loaded_sgf_moves = self.sgf_parser.get_moves()

                    # Start at first move (show only first move initially)
                    self.current_move_index = 1 if self.loaded_sgf_moves else 0

                    # Update display to show first move
                    self.update_sgf_display()

                    # Update game info silently
                    properties = self.sgf_parser.get_properties()
                    info_text = f"Loaded: {properties.get('PB', 'Black')} vs {properties.get('PW', 'White')}"
                    if 'RE' in properties:
                        info_text += f" - {properties['RE']}"
                    info_text += f" - {len(self.loaded_sgf_moves)} moves"

                    # Update status label silently (no popup)
                    self.sgf_status_label.setText(info_text)
                    self.sgf_status_label.setStyleSheet("color: green;")
                else:
                    # Failed to parse - update status silently
                    self.sgf_status_label.setText("Failed to parse SGF file")
                    self.sgf_status_label.setStyleSheet("color: red;")

            except Exception as e:
                # Exception occurred - update status silently
                self.sgf_status_label.setText(f"Error loading SGF: {str(e)}")
                self.sgf_status_label.setStyleSheet("color: red;")

    def save_game(self):
        """Save current game as SGF."""
        if not self.game_history:
            QMessageBox.warning(self, "Warning", "No game to save!")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Game as SGF", "", "SGF Files (*.sgf);;All Files (*)")

        if filename:
            try:
                # Create SGF content
                properties = {
                    'PB': 'Black Player',
                    'PW': 'White Player',
                    'RE': 'B+Resign',  # Default result
                    'DT': '2024',  # Date
                }

                sgf_content = self.sgf_parser.create_sgf(self.game_history, properties)

                # Save to file
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(sgf_content)

                QMessageBox.information(self, "Game Saved", f"Game saved to {filename}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving game: {str(e)}")

    def show_first_move(self):
        """Show the first move of loaded SGF."""
        if self.loaded_sgf_moves:
            self.current_move_index = 0
            self.update_sgf_display()

    def show_previous_move(self):
        """Show the previous move."""
        if self.current_move_index > 0:
            self.current_move_index -= 1
            self.update_sgf_display()

    def show_next_move(self):
        """Show the next move."""
        if self.current_move_index < len(self.loaded_sgf_moves):
            self.current_move_index += 1
            self.update_sgf_display()

    def show_last_move(self):
        """Show the last move of loaded SGF."""
        if self.loaded_sgf_moves:
            self.current_move_index = len(self.loaded_sgf_moves)
            self.update_sgf_display()

    def update_sgf_display(self):
        """Update the board display based on current move index."""
        # Clear the board
        self.board_widget.clear_board()
        self.go_rules.clear_board()

        # Place stones up to current move index
        for i in range(self.current_move_index):
            color, row, col = self.loaded_sgf_moves[i]
            stone_color = 1 if color == "B" else 2
            move_number = i + 1  # Move numbers start from 1
            self.board_widget.place_stone(row, col, stone_color, move_number)
            self.go_rules.place_stone(stone_color, row, col)

        # Update navigation buttons
        self.update_navigation_buttons()

        # Update display
        self.update_display()

    def update_navigation_buttons(self):
        """Update navigation buttons state based on current position."""
        has_moves = len(self.loaded_sgf_moves) > 0

        self.first_move_btn.setEnabled(has_moves and self.current_move_index > 0)
        self.prev_move_btn.setEnabled(has_moves and self.current_move_index > 0)
        self.next_move_btn.setEnabled(has_moves and self.current_move_index < len(self.loaded_sgf_moves))
        self.last_move_btn.setEnabled(has_moves and self.current_move_index < len(self.loaded_sgf_moves))


def main():
    """Main function to run the Go game."""
    app = QApplication(sys.argv)

    # Create and show the main window
    window = GoGameWindow()
    window.show()

    # Start the game
    sys.exit(app.exec())


if __name__ == "__main__":
    main()