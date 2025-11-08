#!/usr/bin/env python3
"""
Go Board Widget Module

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

from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont

from event_system import EventPublisher, GameEventType


class GoBoardWidget(QWidget):
    """Go board widget for displaying and interacting with the game board."""

    # Define signal for stone clicks
    stone_clicked = pyqtSignal(int, int)  # row, col

    def __init__(self, board_size=19):
        super().__init__()
        self.board_size = board_size
        self.cell_size = 40
        self.margin = 53
        self.stones = {}  # (row, col) -> (color, move_number)
        self.setMinimumSize(800, 800)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Connect to event system
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Setup event listeners for board updates."""
        EventPublisher.subscribe_to_event(GameEventType.STONE_PLACED, self._on_stone_placed)
        EventPublisher.subscribe_to_event(GameEventType.BOARD_CLEARED, self._on_board_cleared)
        EventPublisher.subscribe_to_event(GameEventType.STONE_CAPTURED, self._on_stone_captured)

    def _on_stone_placed(self, event):
        """Handle stone placement event."""
        data = event.data
        if 'row' in data and 'col' in data and 'color' in data:
            move_number = data.get('move_number', 0)
            self.place_stone(data['row'], data['col'], data['color'], move_number)

    def _on_board_cleared(self, event):
        """Handle board cleared event."""
        self.clear_board()

    def _on_stone_captured(self, event):
        """Handle stone captured event."""
        data = event.data
        if 'row' in data and 'col' in data:
            self.remove_stone(data['row'], data['col'])

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

            stone_size = 35
            stone_radius = stone_size // 2

            if color == 1:  # Black
                painter.setBrush(QBrush(Qt.GlobalColor.black))
                painter.setPen(QPen(Qt.GlobalColor.black))
                text_color = Qt.GlobalColor.white
            else:  # White
                painter.setBrush(QBrush(Qt.GlobalColor.white))
                painter.setPen(QPen(Qt.GlobalColor.black))
                text_color = Qt.GlobalColor.black

            painter.drawEllipse(x-stone_radius, y-stone_radius, stone_size, stone_size)

            # Draw move number
            if move_number > 0:
                painter.setPen(QPen(text_color))
                painter.setFont(QFont("Arial", 15, QFont.Weight.Bold))
                text_rect = painter.fontMetrics().boundingRect(str(move_number))
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
                # Emit signal for stone placement
                self.stone_clicked.emit(row, col)

    def place_stone(self, row, col, color, move_number=0):
        """Place a stone on the board with move number."""
        self.stones[(row, col)] = (color, move_number)
        self.update()

    def clear_board(self):
        """Clear all stones from the board."""
        self.stones.clear()
        self.update()

    def get_stone_at(self, row, col):
        """Get stone at position, or None if empty."""
        return self.stones.get((row, col))

    def remove_stone(self, row, col):
        """Remove stone from position."""
        if (row, col) in self.stones:
            del self.stones[(row, col)]
            self.update()

    def get_board_state(self):
        """Get current board state."""
        return dict(self.stones)