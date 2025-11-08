#!/usr/bin/env python3
"""
Main Window Module - Refactored Go Game Window

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

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                            QMessageBox, QFileDialog)

from board_widget import GoBoardWidget
from control_panel import ControlPanel
from game_manager import GameManager
from event_system import EventPublisher, GameEventType
from dependency_injection import ServiceProvider, DependencyContainer


class GoGameWindow(QMainWindow):
    """Main Go game window using new modular architecture."""

    def __init__(self):
        super().__init__()

        # Initialize dependency injection and event system
        self._initialize_dependencies()

        # Create game manager
        self.game_manager = GameManager()
        self.game_manager.initialize_services()

        self.init_ui()
        self._setup_connections()

        # Start new game
        self.game_manager.start_new_game()

    def _initialize_dependencies(self):
        """Initialize dependency injection container."""
        container = DependencyContainer()

        # Register services
        from go_state_machine import StateMachine
        from go_rules import GoRules
        from sgf_parser import SGFParser
        from event_system import EventBus

        container.register_singleton("state_machine", lambda c: StateMachine())
        container.register_singleton("go_rules", lambda c: GoRules())
        container.register_singleton("sgf_parser", lambda c: SGFParser())
        container.register_singleton("event_bus", lambda c: EventBus())

        ServiceProvider.set_container(container)

        # Initialize event bus
        event_bus = ServiceProvider.get_service("event_bus")
        EventPublisher.set_event_bus(event_bus)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Go Game - Modular Architecture")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Board widget
        self.board_widget = GoBoardWidget()
        main_layout.addWidget(self.board_widget, 3)

        # Control panel
        self.control_panel = ControlPanel()
        self.control_panel.set_sgf_parser(ServiceProvider.get_service("sgf_parser"))
        main_layout.addWidget(self.control_panel, 1)

    def _setup_connections(self):
        """Setup connections between components."""
        # Connect board clicks to game manager
        self.board_widget.stone_clicked.connect(self.game_manager.handle_stone_placement)

        # Connect control panel actions
        self.control_panel.new_game_requested.connect(self._on_new_game)
        self.control_panel.pass_requested.connect(self._on_pass)
        self.control_panel.resign_requested.connect(self._on_resign)
        self.control_panel.load_sgf_requested.connect(self._on_load_sgf)
        self.control_panel.save_sgf_requested.connect(self._on_save_sgf)
        self.control_panel.sgf_navigation_requested.connect(self._on_sgf_navigation)

        # Setup event listeners for UI updates
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Setup event listeners for UI updates."""
        EventPublisher.subscribe_to_event(GameEventType.MOVE_VALIDATED, self._on_move_validated)
        EventPublisher.subscribe_to_event(GameEventType.SGF_SAVED, self._on_sgf_saved)

    def _on_new_game(self):
        """Handle new game request."""
        self.game_manager.start_new_game()

    def _on_pass(self):
        """Handle pass request."""
        self.game_manager.handle_pass()

    def _on_resign(self):
        """Handle resign request."""
        self.game_manager.handle_resign()

    def _on_load_sgf(self):
        """Handle load SGF request."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load SGF File", "", "SGF Files (*.sgf);;All Files (*)")

        if filename:
            success = self.game_manager.load_sgf_file(filename)
            if not success:
                # Update status silently on failure
                self.control_panel.sgf_status_label.setText("Failed to load SGF file")
                self.control_panel.sgf_status_label.setStyleSheet("color: red;")

    def _on_save_sgf(self):
        """Handle save SGF request."""
        if not self.game_manager.game_history:
            QMessageBox.warning(self, "Warning", "No game to save!")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Game as SGF", "", "SGF Files (*.sgf);;All Files (*)")

        if filename:
            success = self.game_manager.save_game(filename)
            if success:
                QMessageBox.information(self, "Game Saved", f"Game saved to {filename}")
            else:
                QMessageBox.critical(self, "Error", "Error saving game")

    def _on_sgf_navigation(self, action):
        """Handle SGF navigation request."""
        self.game_manager.navigate_sgf(action)

        # Update navigation buttons state
        total_moves = len(self.game_manager.loaded_sgf_moves)
        current_index = self.game_manager.current_move_index
        self.control_panel.update_sgf_navigation_state(current_index, total_moves)

    def _on_move_validated(self, event):
        """Handle move validation result."""
        data = event.data
        if not data.get('valid', False):
            QMessageBox.warning(self, "Invalid Move", data.get('error', 'Invalid move'))

    def _on_sgf_saved(self, event):
        """Handle SGF saved event."""
        # This could be used for additional UI updates
        pass


def main():
    """Main function to run the Go game with new architecture."""
    app = QApplication(sys.argv)

    # Create and show the main window
    window = GoGameWindow()
    window.show()

    # Start the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()