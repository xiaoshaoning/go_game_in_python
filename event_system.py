#!/usr/bin/env python3
"""
Event System for Go Game

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

from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal


class GameEventType(Enum):
    """Game event types."""
    STONE_PLACED = "stone_placed"
    STONE_CAPTURED = "stone_captured"
    GAME_STARTED = "game_started"
    GAME_ENDED = "game_ended"
    PLAYER_CHANGED = "player_changed"
    MOVE_VALIDATED = "move_validated"
    SGF_LOADED = "sgf_loaded"
    SGF_SAVED = "sgf_saved"
    BOARD_CLEARED = "board_cleared"


class GameEvent:
    """Game event data container."""

    def __init__(self, event_type: GameEventType, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = None  # Could be set to current time

    def __repr__(self):
        return f"GameEvent({self.event_type.value}, {self.data})"


class EventBus(QObject):
    """Event bus for game events."""

    # PyQt signals for UI events
    stone_placed = pyqtSignal(dict)
    game_state_changed = pyqtSignal(dict)
    sgf_loaded = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._listeners: Dict[GameEventType, List[Callable]] = {}

    def subscribe(self, event_type: GameEventType, callback: Callable):
        """Subscribe to an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: GameEventType, callback: Callable):
        """Unsubscribe from an event type."""
        if event_type in self._listeners:
            if callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)

    def publish(self, event: GameEvent):
        """Publish an event to all subscribers."""
        event_type = event.event_type

        # Emit PyQt signals for UI events
        if event_type == GameEventType.STONE_PLACED:
            self.stone_placed.emit(event.data)
        elif event_type == GameEventType.PLAYER_CHANGED:
            self.game_state_changed.emit(event.data)
        elif event_type == GameEventType.SGF_LOADED:
            self.sgf_loaded.emit(event.data)

        # Call registered listeners
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event listener for {event_type}: {e}")


class EventPublisher:
    """Event publisher for game components."""

    _event_bus: Optional[EventBus] = None

    @classmethod
    def set_event_bus(cls, event_bus: EventBus):
        """Set the global event bus."""
        cls._event_bus = event_bus

    @classmethod
    def publish_event(cls, event_type: GameEventType, data: Dict[str, Any] = None):
        """Publish an event."""
        if cls._event_bus:
            event = GameEvent(event_type, data)
            cls._event_bus.publish(event)

    @classmethod
    def subscribe_to_event(cls, event_type: GameEventType, callback: Callable):
        """Subscribe to an event type."""
        if cls._event_bus:
            cls._event_bus.subscribe(event_type, callback)

    @classmethod
    def unsubscribe_from_event(cls, event_type: GameEventType, callback: Callable):
        """Unsubscribe from an event type."""
        if cls._event_bus:
            cls._event_bus.unsubscribe(event_type, callback)