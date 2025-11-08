# Generated State Machine: GoGameEnhanced
# Version: 2.1

from abc import ABC, abstractmethod


class State(ABC):
    """Base state class."""

    @abstractmethod
    def handle_event(self, event):
        """Handle an event and return next state."""
        pass

    def enter(self):
        """Called when entering the state."""
        pass

    def exit(self):
        """Called when exiting the state."""
        pass


class StateMachine:
    """State machine container."""

    def __init__(self):
        self.current_state = None
        self._states = {}
        self._initialize_states()
        self.set_initial_state('gui_initialization')

    def _initialize_states(self):
        """Initialize all states."""
        self._states['gui_initialization'] = gui_initializationState()
        self._states['main_menu'] = main_menuState()
        self._states['game_setup'] = game_setupState()
        self._states['black_turn'] = black_turnState()
        self._states['white_turn'] = white_turnState()
        self._states['move_validation'] = move_validationState()
        self._states['stone_placement'] = stone_placementState()
        self._states['liberty_check'] = liberty_checkState()
        self._states['ko_check'] = ko_checkState()
        self._states['sgf_loading'] = sgf_loadingState()
        self._states['sgf_playback_initial'] = sgf_playback_initialState()
        self._states['sgf_playback'] = sgf_playbackState()
        self._states['game_recording'] = game_recordingState()
        self._states['score_calculation'] = score_calculationState()
        self._states['game_over'] = game_overState()

    def set_initial_state(self, state_name):
        """Set the initial state."""
        if state_name in self._states:
            self.current_state = self._states[state_name]
            self.current_state.enter()

    def handle_event(self, event):
        """Handle an event and transition states."""
        if self.current_state:
            old_state = self.current_state
            new_state = self.current_state.handle_event(event)

            if new_state != old_state:
                old_state.exit()
                self.current_state = new_state
                self.current_state.enter()

class gui_initializationState(State):
    """gui_initialization state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'gui_ready':
            return main_menuState()
        return self

class main_menuState(State):
    """main_menu state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'new_game':
            return game_setupState()
        if event == 'load_sgf':
            return sgf_loadingState()
        return self

class game_setupState(State):
    """game_setup state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'setup_complete':
            return black_turnState()
        return self

class black_turnState(State):
    """black_turn state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'black_move':
            return move_validationState()
        if event == 'black_pass':
            return white_turnState()
        if event == 'both_pass':
            return score_calculationState()
        if event == 'black_resign':
            return score_calculationState()
        if event == 'save_game':
            return game_recordingState()
        return self

class white_turnState(State):
    """white_turn state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'white_move':
            return move_validationState()
        if event == 'white_pass':
            return black_turnState()
        if event == 'both_pass':
            return score_calculationState()
        if event == 'white_resign':
            return score_calculationState()
        if event == 'save_game':
            return game_recordingState()
        return self

class move_validationState(State):
    """move_validation state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'move_valid':
            return stone_placementState()
        if event == 'move_invalid_black':
            return black_turnState()
        if event == 'move_invalid_white':
            return white_turnState()
        return self

class stone_placementState(State):
    """stone_placement state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'stone_placed':
            return liberty_checkState()
        return self

class liberty_checkState(State):
    """liberty_check state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'captures_processed':
            return ko_checkState()
        return self

class ko_checkState(State):
    """ko_check state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'ko_passed_black':
            return white_turnState()
        if event == 'ko_passed_white':
            return black_turnState()
        if event == 'ko_violation':
            return move_validationState()
        return self

class sgf_loadingState(State):
    """sgf_loading state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'sgf_loaded':
            return sgf_playback_initialState()
        return self

class sgf_playback_initialState(State):
    """sgf_playback_initial state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'playback_start':
            return sgf_playbackState()
        return self

class sgf_playbackState(State):
    """sgf_playback state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'sgf_next':
            return sgf_playbackState()
        if event == 'sgf_prev':
            return sgf_playbackState()
        if event == 'sgf_first':
            return sgf_playbackState()
        if event == 'sgf_last':
            return sgf_playbackState()
        if event == 'exit_playback':
            return main_menuState()
        return self

class game_recordingState(State):
    """game_recording state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'game_saved_black':
            return black_turnState()
        if event == 'game_saved_white':
            return white_turnState()
        return self

class score_calculationState(State):
    """score_calculation state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'score_calculated':
            return game_overState()
        return self

class game_overState(State):
    """game_over state."""

    def handle_event(self, event):
        """Handle events for this state."""
        if event == 'return_to_menu':
            return main_menuState()
        return self

