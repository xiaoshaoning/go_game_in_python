#!/usr/bin/env python3
"""
Go game rules validation
Implements complete Go rules including:
- Position validation (intersections only)
- Occupied position check
- Suicide rule
- Ko rule
- Liberty checking

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

from typing import List, Tuple, Set, Dict


class GoRules:
    """Go game rules validator."""

    def __init__(self, board_size: int = 19):
        self.board_size = board_size
        self.board = {}  # (row, col) -> color (1=black, 2=white)
        self.last_move = None  # For ko rule

    def is_valid_move(self, color: int, row: int, col: int) -> Tuple[bool, str]:
        """
        Check if a move is valid according to Go rules.

        Args:
            color: 1 for black, 2 for white
            row: Row coordinate (0-indexed)
            col: Column coordinate (0-indexed)

        Returns:
            Tuple of (is_valid, error_message)
        """

        # Rule 1: Must be on board intersection
        if not self._is_on_board(row, col):
            return False, "Move must be on board intersection"

        # Rule 2: Position must be empty
        if (row, col) in self.board:
            return False, "Position already occupied"

        # Rule 3: Suicide rule - move must not be suicide
        if self._is_suicide(color, row, col):
            return False, "Suicide move not allowed"

        # Rule 4: Ko rule - cannot repeat previous board position
        if self._violates_ko(color, row, col):
            return False, "Ko violation - cannot repeat board position"

        return True, ""

    def _is_on_board(self, row: int, col: int) -> bool:
        """Check if coordinates are valid board intersections."""
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def _is_suicide(self, color: int, row: int, col: int) -> bool:
        """
        Check if move is suicide (would have no liberties after placement).

        Args:
            color: Stone color
            row, col: Move coordinates

        Returns:
            True if move is suicide
        """
        # Temporarily place stone
        self.board[(row, col)] = color

        # Check if the placed stone has liberties
        has_liberties = self._has_liberties(row, col, set())

        # Remove temporary stone
        del self.board[(row, col)]

        return not has_liberties

    def _has_liberties(self, row: int, col: int, visited: Set[Tuple[int, int]]) -> bool:
        """
        Check if a stone or group has liberties.

        Args:
            row, col: Starting position
            visited: Set of visited positions

        Returns:
            True if the stone/group has at least one liberty
        """
        if (row, col) in visited:
            return False
        visited.add((row, col))

        color = self.board.get((row, col))
        if color is None:
            return False

        # Check adjacent positions
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_row, new_col = row + dr, col + dc

            # Check if adjacent position is on board
            if not self._is_on_board(new_row, new_col):
                continue

            # If adjacent position is empty, we have a liberty
            if (new_row, new_col) not in self.board:
                return True

            # If adjacent position has same color, check its liberties
            if self.board.get((new_row, new_col)) == color:
                if self._has_liberties(new_row, new_col, visited):
                    return True

        return False

    def _violates_ko(self, color: int, row: int, col: int) -> bool:
        """
        Check if move violates ko rule.
        For simplicity, we only check immediate ko (single stone capture).

        Args:
            color: Stone color
            row, col: Move coordinates

        Returns:
            True if move violates ko rule
        """
        if self.last_move is None:
            return False

        # Check if this move would capture exactly one stone
        # and that stone was placed in the last move
        captured_stones = self._get_captured_stones(color, row, col)

        if len(captured_stones) == 1:
            captured_stone = next(iter(captured_stones))
            if captured_stone == self.last_move:
                return True

        return False

    def _get_captured_stones(self, color: int, row: int, col: int) -> Set[Tuple[int, int]]:
        """
        Get stones that would be captured by this move.

        Args:
            color: Stone color
            row, col: Move coordinates

        Returns:
            Set of captured stone positions
        """
        captured = set()
        opponent_color = 2 if color == 1 else 1

        # Save current board state
        original_board = self.board.copy()

        # Temporarily place stone
        self.board[(row, col)] = color

        # Check adjacent opponent stones
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_row, new_col = row + dr, col + dc

            if not self._is_on_board(new_row, new_col):
                continue

            if self.board.get((new_row, new_col)) == opponent_color:
                if not self._has_liberties(new_row, new_col, set()):
                    # Find all stones in the group
                    group = self._get_stone_group(new_row, new_col)
                    captured.update(group)

        # Restore original board state
        self.board = original_board

        return captured

    def _get_stone_group(self, row: int, col: int) -> Set[Tuple[int, int]]:
        """
        Get all stones in the same connected group.

        Args:
            row, col: Starting position

        Returns:
            Set of all positions in the stone group
        """
        if (row, col) not in self.board:
            return set()

        color = self.board.get((row, col))
        if color is None:
            return set()

        group = set()
        stack = [(row, col)]

        while stack:
            r, c = stack.pop()
            if (r, c) in group:
                continue
            group.add((r, c))

            # Check adjacent positions
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_r, new_c = r + dr, c + dc
                if (self._is_on_board(new_r, new_c) and
                    self.board.get((new_r, new_c)) == color):
                    stack.append((new_r, new_c))

        return group

    def place_stone(self, color: int, row: int, col: int) -> Set[Tuple[int, int]]:
        """
        Place a stone on the board and handle captures.

        Args:
            color: Stone color
            row, col: Move coordinates

        Returns:
            Set of captured stone positions
        """
        # Validate move
        is_valid, error_msg = self.is_valid_move(color, row, col)
        if not is_valid:
            raise ValueError(f"Invalid move: {error_msg}")

        # Place stone
        self.board[(row, col)] = color

        # Handle captures
        captured_stones = self._execute_captures(color, row, col)

        # Update last move for ko rule
        self.last_move = (row, col)

        return captured_stones

    def _execute_captures(self, color: int, row: int, col: int) -> Set[Tuple[int, int]]:
        """
        Execute captures after placing a stone.

        Args:
            color: Stone color
            row, col: Move coordinates

        Returns:
            Set of captured stone positions
        """
        captured = set()
        opponent_color = 2 if color == 1 else 1

        # Check adjacent opponent stones
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_row, new_col = row + dr, col + dc

            if not self._is_on_board(new_row, new_col):
                continue

            if self.board.get((new_row, new_col)) == opponent_color:
                if not self._has_liberties(new_row, new_col, set()):
                    # Find all stones in the group
                    group = self._get_stone_group(new_row, new_col)
                    captured.update(group)

        # Remove captured stones from board
        for stone_pos in captured:
            if stone_pos in self.board:
                del self.board[stone_pos]

        return captured

    def get_board_state(self) -> Dict[Tuple[int, int], int]:
        """Get current board state."""
        return self.board.copy()

    def replay_stone(self, color: int, row: int, col: int) -> Set[Tuple[int, int]]:
        """
        Place a stone during SGF replay without validation checks.
        This is used for replaying recorded games where moves are already known to be valid.

        Args:
            color: Stone color
            row, col: Move coordinates

        Returns:
            Set of captured stone positions
        """
        # Place stone without validation
        self.board[(row, col)] = color

        # Handle captures
        captured_stones = self._execute_captures(color, row, col)

        # Update last move for ko rule
        self.last_move = (row, col)

        return captured_stones

    def clear_board(self):
        """Clear the board."""
        self.board.clear()
        self.last_move = None