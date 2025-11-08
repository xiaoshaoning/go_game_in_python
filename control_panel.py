#!/usr/bin/env python3
"""
Control Panel Module

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

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QFileDialog, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

from event_system import EventPublisher, GameEventType


class ControlPanel(QWidget):
    """Control panel for game controls and status display."""

    # Signals for user actions
    new_game_requested = pyqtSignal()
    pass_requested = pyqtSignal()
    resign_requested = pyqtSignal()
    load_sgf_requested = pyqtSignal()
    save_sgf_requested = pyqtSignal()
    sgf_navigation_requested = pyqtSignal(str)  # first, prev, next, last

    def __init__(self):
        super().__init__()
        self.sgf_parser = None
        self.loaded_sgf_moves = []
        self.current_move_index = 0

        self.init_ui()
        self._setup_event_listeners()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Game info
        self.status_label = QLabel("Game Status: Initializing...")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.status_label)

        # SGF status display
        self.sgf_status_label = QLabel("")
        self.sgf_status_label.setFont(QFont("Arial", 9))
        self.sgf_status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.sgf_status_label)

        layout.addSpacing(20)

        # Game controls
        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.clicked.connect(self._on_new_game)
        layout.addWidget(self.new_game_btn)

        self.pass_btn = QPushButton("Pass")
        self.pass_btn.clicked.connect(self._on_pass)
        layout.addWidget(self.pass_btn)

        self.resign_btn = QPushButton("Resign")
        self.resign_btn.clicked.connect(self._on_resign)
        layout.addWidget(self.resign_btn)

        layout.addSpacing(20)

        # SGF controls
        self.load_sgf_btn = QPushButton("Load SGF")
        self.load_sgf_btn.clicked.connect(self._on_load_sgf)
        layout.addWidget(self.load_sgf_btn)

        self.save_sgf_btn = QPushButton("Save Game")
        self.save_sgf_btn.clicked.connect(self._on_save_sgf)
        layout.addWidget(self.save_sgf_btn)

        layout.addSpacing(20)

        # SGF navigation controls
        nav_layout = QHBoxLayout()

        self.first_move_btn = QPushButton("First")
        self.first_move_btn.clicked.connect(lambda: self._on_sgf_navigation("first"))
        self.first_move_btn.setEnabled(False)
        nav_layout.addWidget(self.first_move_btn)

        self.prev_move_btn = QPushButton("Previous")
        self.prev_move_btn.clicked.connect(lambda: self._on_sgf_navigation("prev"))
        self.prev_move_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_move_btn)

        self.next_move_btn = QPushButton("Next")
        self.next_move_btn.clicked.connect(lambda: self._on_sgf_navigation("next"))
        self.next_move_btn.setEnabled(False)
        nav_layout.addWidget(self.next_move_btn)

        self.last_move_btn = QPushButton("Last")
        self.last_move_btn.clicked.connect(lambda: self._on_sgf_navigation("last"))
        self.last_move_btn.setEnabled(False)
        nav_layout.addWidget(self.last_move_btn)

        layout.addLayout(nav_layout)
        layout.addStretch()

    def _setup_event_listeners(self):
        """Setup event listeners."""
        EventPublisher.subscribe_to_event(GameEventType.PLAYER_CHANGED, self._on_player_changed)
        EventPublisher.subscribe_to_event(GameEventType.GAME_STARTED, self._on_game_started)
        EventPublisher.subscribe_to_event(GameEventType.GAME_ENDED, self._on_game_ended)
        EventPublisher.subscribe_to_event(GameEventType.SGF_LOADED, self._on_sgf_loaded)

    def _on_player_changed(self, event):
        """Handle player change event."""
        data = event.data
        if 'current_player' in data:
            self.status_label.setText(f"Game Status: {data['current_player'].title()}")

    def _on_game_started(self, event):
        """Handle game started event."""
        self.status_label.setText("Game Status: Black")

    def _on_game_ended(self, event):
        """Handle game ended event."""
        data = event.data
        if 'result' in data:
            self.status_label.setText(f"Game Status: Game Over - {data['result']}")
        else:
            self.status_label.setText("Game Status: Game Over")

    def _on_sgf_loaded(self, event):
        """Handle SGF loaded event."""
        data = event.data
        if 'properties' in data and 'moves' in data:
            properties = data['properties']
            moves = data['moves']

            info_text = f"Loaded: {properties.get('PB', 'Black')} vs {properties.get('PW', 'White')}"
            if 'RE' in properties:
                info_text += f" - {properties['RE']}"
            info_text += f" - {len(moves)} moves"

            self.sgf_status_label.setText(info_text)
            self.sgf_status_label.setStyleSheet("color: green;")

            self.loaded_sgf_moves = moves
            self.current_move_index = 0
            self._update_navigation_buttons()

    def _on_new_game(self):
        """Handle new game button click."""
        self.new_game_requested.emit()

    def _on_pass(self):
        """Handle pass button click."""
        self.pass_requested.emit()

    def _on_resign(self):
        """Handle resign button click."""
        self.resign_requested.emit()

    def _on_load_sgf(self):
        """Handle load SGF button click."""
        self.load_sgf_requested.emit()

    def _on_save_sgf(self):
        """Handle save SGF button click."""
        self.save_sgf_requested.emit()

    def _on_sgf_navigation(self, action):
        """Handle SGF navigation button clicks."""
        self.sgf_navigation_requested.emit(action)

    def _update_navigation_buttons(self):
        """Update navigation buttons state."""
        has_moves = len(self.loaded_sgf_moves) > 0

        self.first_move_btn.setEnabled(has_moves)
        self.prev_move_btn.setEnabled(has_moves and self.current_move_index > 0)
        self.next_move_btn.setEnabled(has_moves and self.current_move_index < len(self.loaded_sgf_moves))
        self.last_move_btn.setEnabled(has_moves and self.current_move_index < len(self.loaded_sgf_moves))

    def set_sgf_parser(self, sgf_parser):
        """Set SGF parser instance."""
        self.sgf_parser = sgf_parser

    def update_sgf_navigation_state(self, current_index, total_moves):
        """Update SGF navigation state."""
        self.current_move_index = current_index
        self._update_navigation_buttons()