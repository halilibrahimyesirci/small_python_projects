"""
Transition effects for game state changes.
Handles smooth transitions between game states.
"""

import pygame
import time

# Transition types
TRANSITION_FADE = "fade"
TRANSITION_SLIDE_LEFT = "slide_left"
TRANSITION_SLIDE_RIGHT = "slide_right"
TRANSITION_ZOOM = "zoom"

class TransitionManager:
    """Manages transitions between game states"""
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.transitioning = False
        self.transition_start_time = 0
        self.transition_progress = 0
        self.transition_from_state = None
        self.transition_to_state = None
        self.transition_duration = 0.3  # Default duration in seconds
        self.transition_type = TRANSITION_FADE
        self.transition_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.snapshot_surface = None
        
    def start_transition(self, from_state, to_state, screen, duration=None, transition_type=None):
        """Start a transition from one state to another"""
        self.transitioning = True
        self.transition_start_time = time.time()
        self.transition_from_state = from_state
        self.transition_to_state = to_state
        self.transition_progress = 0
        
        if duration is not None:
            self.transition_duration = duration
            
        if transition_type is not None:
            self.transition_type = transition_type
            
        # Take a snapshot of the current state to transition from
        self.snapshot_surface = pygame.Surface((self.width, self.height))
        self.snapshot_surface.blit(screen, (0, 0))
        
        return self.transition_to_state
        
    def update(self):
        """Update transition progress"""
        if not self.transitioning:
            return False
            
        # Calculate progress (0 to 1)
        elapsed = time.time() - self.transition_start_time
        self.transition_progress = min(1.0, elapsed / self.transition_duration)
        
        # Check if transition is complete
        if self.transition_progress >= 1.0:
            self.transitioning = False
            return False
            
        return True
        
    def render(self, screen):
        """Render the current transition effect"""
        if not self.transitioning or not self.snapshot_surface:
            return
            
        # Apply the appropriate transition effect
        if self.transition_type == TRANSITION_FADE:
            self._render_fade(screen)
        elif self.transition_type == TRANSITION_SLIDE_LEFT:
            self._render_slide_left(screen)
        elif self.transition_type == TRANSITION_SLIDE_RIGHT:
            self._render_slide_right(screen)
        elif self.transition_type == TRANSITION_ZOOM:
            self._render_zoom(screen)
            
    def _render_fade(self, screen):
        """Render a fade transition effect"""
        # Create a fade effect using alpha
        alpha = int(255 * (1.0 - self.transition_progress))
        self.snapshot_surface.set_alpha(alpha)
        screen.blit(self.snapshot_surface, (0, 0))
        
    def _render_slide_left(self, screen):
        """Render a slide left transition effect"""
        # Calculate the x position for sliding left
        x_offset = int(self.width * self.transition_progress)
        screen.blit(self.snapshot_surface, (-x_offset, 0))
        
    def _render_slide_right(self, screen):
        """Render a slide right transition effect"""
        # Calculate the x position for sliding right
        x_offset = int(self.width * self.transition_progress)
        screen.blit(self.snapshot_surface, (x_offset, 0))
        
    def _render_zoom(self, screen):
        """Render a zoom transition effect"""
        # Calculate zoom factor
        zoom_factor = 1.0 + self.transition_progress
        
        # Calculate new dimensions with zoom
        new_width = int(self.width * zoom_factor)
        new_height = int(self.height * zoom_factor)
        
        # Calculate center offset
        offset_x = (new_width - self.width) // 2
        offset_y = (new_height - self.height) // 2
        
        # Create zoomed surface
        try:
            zoomed_surface = pygame.transform.scale(self.snapshot_surface, (new_width, new_height))
            screen.blit(zoomed_surface, (-offset_x, -offset_y))
        except pygame.error:
            # Fallback to fade if scaling fails
            self._render_fade(screen)