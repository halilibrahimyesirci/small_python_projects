"""
Obstacle Entity Module
Implements various types of obstacle windows that hinder the player
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
        OBSTACLE_WINDOW_TITLE = "Obstacle"
        OBSTACLE_WINDOW_SIZE = (150, 150)
        OBSTACLE_WINDOW_COLOR = "gray"
        OBSTACLE_TYPES = {
            "barrier": {"effect": "block", "duration": 0},
            "trap": {"effect": "freeze", "duration": 3},
            "decoy": {"effect": "none", "duration": 0}
        }

class ObstacleEntity(GameEntity):
    """
    Obstacle entity that hinders the player's progress
    Features different types with various effects
    """
    
    def __init__(self, 
                 obstacle_type: str = "barrier",
                 level: int = 1,
                 difficulty: str = "medium",
                 parent: Optional[Any] = None):
        """
        Initialize an obstacle entity
        
        Args:
            obstacle_type: Type of obstacle ('barrier', 'trap', 'decoy')
            level: Current game level (affects difficulty)
            difficulty: Game difficulty setting
            parent: Parent window
        """
        # Get obstacle properties from configuration
        self.obstacle_type = obstacle_type
        self.config = OBSTACLE_TYPES.get(obstacle_type, OBSTACLE_TYPES["barrier"])
        
        # Choose color based on type
        if obstacle_type == "barrier":
            color = "gray"
            shape = "rectangle"
        elif obstacle_type == "trap":
            color = "orange"
            shape = "star"
        elif obstacle_type == "decoy":
            # Decoys look like targets to confuse the player
            color = random.choice(TARGET_WINDOW_COLORS)
            shape = random.choice(SHAPE_TYPES)
        else:
            color = OBSTACLE_WINDOW_COLOR
            shape = "rectangle"
        
        # Effect duration adjustment based on difficulty and level
        self.effect_duration = self.config["duration"]
        if difficulty == "easy":
            self.effect_duration *= 0.8
        elif difficulty == "hard":
            self.effect_duration *= 1.2
        elif difficulty == "expert":
            self.effect_duration *= 1.5
            
        # Additional scaling based on level (effects get stronger)
        level_scale = 1.0 + (level - 1) * 0.05  # 5% increase per level
        self.effect_duration *= level_scale
        
        # Initialize base entity
        super().__init__(
            title=OBSTACLE_WINDOW_TITLE,
            size=OBSTACLE_WINDOW_SIZE,
            color=color,
            shape_type=shape,
            is_player=False,
            parent=parent
        )
        
        # Set behavior based on type
        self._set_behavior_and_animation()
        
    def _set_behavior_and_animation(self):
        """Set behavior and animation based on obstacle type"""
        if self.obstacle_type == "barrier":
            # Barriers are static obstacles that block movement
            self.start_animation('none')  # No animation
            
        elif self.obstacle_type == "trap":
            # Traps freeze the player
            self.start_animation('pulse')  # Pulsing animation
            
            # Add rotation for visual effect
            self.window.after(100, self._rotate_trap)
            
        elif self.obstacle_type == "decoy":
            # Decoys look like targets
            if random.random() < 0.5:
                self.start_animation('pulse')
            else:
                self.start_animation('rotate')
                
    def _rotate_trap(self):
        """Rotate trap obstacle for visual effect"""
        # Only for trap obstacles
        if self.obstacle_type != "trap" or not self.window:
            return
            
        # Change rotation angle
        self.rotation_angle = (self.rotation_angle + 5) % 360
        self._redraw_shape()
        
        # Schedule next rotation
        self.window.after(100, self._rotate_trap)
        
    def get_type(self) -> str:
        """Get obstacle type"""
        return self.obstacle_type
        
    def get_effect(self) -> str:
        """Get obstacle effect"""
        return self.config["effect"]
        
    def get_effect_duration(self) -> float:
        """Get effect duration in seconds"""
        return self.effect_duration
        
    def apply_effect(self, player_entity):
        """
        Apply obstacle effect to player
        
        Args:
            player_entity: The player entity to affect
        
        Returns:
            bool: Whether the effect was applied
        """
        effect = self.get_effect()
        
        if effect == "block":
            # Barriers physically block the player
            # This is handled by collision detection
            return False
            
        elif effect == "freeze":
            # Freeze the player temporarily
            duration = self.get_effect_duration()
            player_entity.apply_status_effect("freeze", duration)
            return True
            
        elif effect == "none":
            # Decoys have no effect
            return False
            
        # Unknown effect
        return False