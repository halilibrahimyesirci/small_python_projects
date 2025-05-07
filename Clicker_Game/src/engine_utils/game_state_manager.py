"""
Game state manager for handling different game states and transitions.
Manages state switching, transitions, and state-specific logic.
"""

import pygame
import logging
import time

logger = logging.getLogger(__name__)

# State constants (can be imported from game_states.py)
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER_WIN = "game_over_win"
STATE_GAME_OVER_LOSE = "game_over_lose"
STATE_UPGRADE = "upgrade"
STATE_PAUSE = "pause"
STATE_SETTINGS = "settings"
STATE_ABILITY_SELECT = "ability_select"
STATE_ESC_MENU = "esc_menu"
STATE_SHOP = "shop"

class GameStateManager:
    """Manages game states and transitions between them"""
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.current_state = STATE_MENU
        self.previous_state = None
        self.state_handlers = {}
        
        # Transition settings
        self.transitioning = False
        self.transition_start_time = 0
        self.transition_progress = 0
        self.transition_duration = 0.3  # Default duration in seconds
        self.transition_from_state = None
        self.transition_to_state = None
        self.transition_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Additional state data
        self.state_data = {}
        
    def register_state_handlers(self, state, update_func, render_func):
        """Register update and render functions for a specific state"""
        self.state_handlers[state] = {
            'update': update_func,
            'render': render_func
        }
        
    def change_state(self, new_state, transition=True):
        """Change to a new state, optionally with transition effect"""
        if new_state not in self.state_handlers:
            logger.warning(f"Attempted to change to unregistered state: {new_state}")
            return False
            
        logger.info(f"Changing state from {self.current_state} to {new_state}")
        
        if transition:
            self._start_transition(new_state)
        else:
            self.previous_state = self.current_state
            self.current_state = new_state
            
        return True
        
    def _start_transition(self, to_state):
        """Start a transition to a new state"""
        self.transitioning = True
        self.transition_start_time = time.time()
        self.transition_from_state = self.current_state
        self.transition_to_state = to_state
        self.transition_progress = 0
        
        # Create a screenshot of the current state to fade from
        if hasattr(pygame, 'display') and pygame.display.get_surface():
            self.transition_surface.fill((0, 0, 0, 0))
            self.transition_surface.blit(pygame.display.get_surface(), (0, 0))
        
        # Actually change the state
        self.previous_state = self.current_state
        self.current_state = to_state
        
        logger.info(f"Transitioning from {self.transition_from_state} to {self.transition_to_state}")
        
    def update(self, time_delta, engine):
        """Update the current state"""
        # Update transition if active
        if self.transitioning:
            self._update_transition(time_delta)
        
        # Update the current state
        if self.current_state in self.state_handlers:
            self.state_handlers[self.current_state]['update'](engine, time_delta)
        else:
            logger.warning(f"No update handler for state: {self.current_state}")
            
    def render(self, surface, engine):
        """Render the current state"""
        # Render the current state
        if self.current_state in self.state_handlers:
            self.state_handlers[self.current_state]['render'](engine)
        else:
            logger.warning(f"No render handler for state: {self.current_state}")
            
        # Render transition effect if active
        if self.transitioning:
            self._render_transition(surface)
            
    def _update_transition(self, time_delta):
        """Update transition progress"""
        if not self.transitioning:
            return
            
        # Calculate progress (0 to 1)
        elapsed = time.time() - self.transition_start_time
        self.transition_progress = min(1.0, elapsed / self.transition_duration)
        
        # Check if transition is complete
        if self.transition_progress >= 1.0:
            self.transitioning = False
            
    def _render_transition(self, surface):
        """Render the transition effect"""
        if not self.transitioning:
            return
            
        # Create a fade effect
        alpha = int(255 * (1.0 - self.transition_progress))
        self.transition_surface.set_alpha(alpha)
        surface.blit(self.transition_surface, (0, 0))
        
    def get_state_data(self, key, default=None):
        """Get state-specific data"""
        return self.state_data.get(key, default)
        
    def set_state_data(self, key, value):
        """Set state-specific data"""
        self.state_data[key] = value
        
    def clear_state_data(self, key=None):
        """Clear state-specific data"""
        if key is None:
            self.state_data.clear()
        elif key in self.state_data:
            del self.state_data[key]
            
    def is_state(self, state):
        """Check if the current state matches the given state"""
        return self.current_state == state
        
    def was_state(self, state):
        """Check if the previous state matches the given state"""
        return self.previous_state == state