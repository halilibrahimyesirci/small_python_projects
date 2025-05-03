"""
Powerup Entity Module
Implements various types of powerup windows that provide special abilities
"""

import random
import math
from typing import Dict, Tuple, Optional, List, Any
import sys

# Import base entity
from .base_entity import GameEntity

# Import game configuration
sys.path.append("../../config")
try:
    from config.game_config import *
except ImportError:
    try:
        from Window_Frame_Game.config.game_config import *
    except ImportError:
        # Fallback values
        POWERUP_WINDOW_TITLE = "Power-Up"
        POWERUP_WINDOW_SIZE = (75, 75)
        POWERUP_WINDOW_COLORS = {
            "speed": "cyan",
            "magnet": "magenta",
            "shield": "gold",
            "time": "silver"
        }
        POWERUP_EFFECTS = {
            "speed": {"multiplier": 2.0, "duration": 5.0},
            "magnet": {"radius": 300, "duration": 7.0},
            "shield": {"duration": 10.0},
            "time": {"slowdown": 0.5, "duration": 5.0}
        }

class PowerupEntity(GameEntity):
    """
    Powerup entity that provides special abilities when collected by the player
    """
    
    def __init__(self, 
                 powerup_type: str = None,
                 level: int = 1,
                 difficulty: str = "medium",
                 parent: Optional[Any] = None):
        """
        Initialize a powerup entity
        
        Args:
            powerup_type: Type of powerup ('speed', 'magnet', 'shield', 'time')
            level: Current game level (affects duration)
            difficulty: Game difficulty setting
            parent: Parent window
        """
        # Choose powerup type if not specified
        if powerup_type is None:
            powerup_type = random.choice(list(POWERUP_WINDOW_COLORS.keys()))
            
        self.powerup_type = powerup_type
        
        # Get color for this powerup type
        color = POWERUP_WINDOW_COLORS.get(powerup_type, "white")
        
        # Get effect data
        self.config = POWERUP_EFFECTS.get(powerup_type, {})
        
        # Scale duration based on difficulty (harder = shorter duration)
        difficulty_factor = 1.0
        if difficulty == "easy":
            difficulty_factor = 1.2
        elif difficulty == "hard":
            difficulty_factor = 0.8
        elif difficulty == "expert":
            difficulty_factor = 0.6
        
        self.duration = self.config.get("duration", 5.0) * difficulty_factor
        
        # Initialize base entity with different shape for each powerup type
        shape_type = "circle"  # Default
        if powerup_type == "speed":
            shape_type = "triangle"  # Triangle for speed boost
        elif powerup_type == "magnet":
            shape_type = "circle"    # Circle for magnet
        elif powerup_type == "shield":
            shape_type = "star"      # Star for shield
        elif powerup_type == "time":
            shape_type = "rectangle" # Rectangle for time slowdown
        
        super().__init__(
            title=POWERUP_WINDOW_TITLE,
            size=POWERUP_WINDOW_SIZE,
            color=color,
            shape_type=shape_type,
            is_player=False,
            parent=parent
        )
        
        # Set powerup-specific animation
        self._set_animation()
        
        # Add floating movement
        self._setup_floating_movement()
        
    def _set_animation(self):
        """Set animation based on powerup type"""
        if self.powerup_type == "speed":
            # Speed powerups rotate quickly
            self.animation_frames = 20  # Faster rotation
            self.start_animation('rotate')
            
        elif self.powerup_type == "magnet":
            # Magnet powerups pulse
            self.start_animation('pulse')
            
        elif self.powerup_type == "shield":
            # Shield powerups glow with color shift
            self.start_animation('color_shift')
            
        elif self.powerup_type == "time":
            # Time powerups pulse slowly
            self.animation_frames = 40  # Slower pulse
            self.start_animation('pulse')
        
    def _setup_floating_movement(self):
        """Set up gentle floating movement for powerups"""
        # Store initial position
        self.initial_x, self.initial_y = self.get_position()
        
        # Random float parameters
        self.float_amplitude_x = random.uniform(10, 30)
        self.float_amplitude_y = random.uniform(10, 30)
        self.float_speed_x = random.uniform(0.5, 1.5)
        self.float_speed_y = random.uniform(0.5, 1.5)
        self.float_phase_x = random.uniform(0, 2 * math.pi)
        self.float_phase_y = random.uniform(0, 2 * math.pi)
        self.float_time = 0
        
    def update(self, delta_time: float):
        """
        Update powerup state for the current frame
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Call parent update for animations
        super().update(delta_time)
        
        # Update floating movement
        self._update_floating_movement(delta_time)
        
    def _update_floating_movement(self, delta_time: float):
        """Update floating movement animation"""
        # Increment float time
        self.float_time += delta_time
        
        # Calculate new position with sinusoidal movement
        new_x = self.initial_x + self.float_amplitude_x * math.sin(
            self.float_speed_x * self.float_time + self.float_phase_x
        )
        new_y = self.initial_y + self.float_amplitude_y * math.sin(
            self.float_speed_y * self.float_time + self.float_phase_y
        )
        
        # Set new position
        self.set_position(int(new_x), int(new_y))
        
    def get_type(self) -> str:
        """Get the powerup type"""
        return self.powerup_type
        
    def get_duration(self) -> float:
        """Get effect duration in seconds"""
        return self.duration
        
    def get_multiplier(self) -> float:
        """Get speed multiplier (for speed powerups)"""
        return self.config.get("multiplier", 2.0)
        
    def get_radius(self) -> float:
        """Get magnet radius (for magnet powerups)"""
        return self.config.get("radius", 300)
        
    def get_slowdown(self) -> float:
        """Get time slowdown factor (for time powerups)"""
        return self.config.get("slowdown", 0.5)