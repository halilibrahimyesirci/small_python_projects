"""
Target Entity Module
Implements various types of target windows with different behaviors
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
        TARGET_WINDOW_TITLE = "Target"
        TARGET_WINDOW_SIZE = (200, 150)
        TARGET_WINDOW_COLORS = ["red", "blue", "green", "yellow", "purple"]
        TARGET_TYPES = {
            "standard": {"speed": 0, "points": 10, "behavior": "static"},
            "moving": {"speed": 3, "points": 20, "behavior": "random_movement"},
            "evasive": {"speed": 4, "points": 30, "behavior": "evade_player"},
            "boss": {"speed": 2, "points": 50, "behavior": "chase_player", "health": 3}
        }

class TargetEntity(GameEntity):
    """
    Target entity that the player tries to capture
    Features different behaviors, points values, and visual styles
    """
    
    def __init__(self, 
                 target_type: str = "standard",
                 level: int = 1,
                 difficulty: str = "medium",
                 parent: Optional[Any] = None):
        """
        Initialize a target entity
        
        Args:
            target_type: Type of target ('standard', 'moving', 'evasive', 'boss')
            level: Current game level (affects difficulty)
            difficulty: Game difficulty setting
            parent: Parent window
        """
        # Get target properties from configuration
        self.target_type = target_type
        self.config = TARGET_TYPES.get(target_type, TARGET_TYPES["standard"])
        
        # Choose a random color and shape
        color = random.choice(TARGET_WINDOW_COLORS)
        shape = random.choice(SHAPE_TYPES)
        
        # Apply difficulty multiplier to speed
        speed_multiplier = DIFFICULTY_LEVELS[difficulty]["target_speed_multiplier"]
        self.base_speed = self.config["speed"] * speed_multiplier * (1 + (level - 1) * 0.1)
        
        # Points value with difficulty and level scaling
        self.points = int(self.config["points"] * DIFFICULTY_LEVELS[difficulty]["score_multiplier"] * (1 + (level - 1) * 0.05))
        
        # Initialize base entity
        super().__init__(
            title=TARGET_WINDOW_TITLE,
            size=TARGET_WINDOW_SIZE,
            color=color,
            shape_type=shape,
            is_player=False,
            parent=parent
        )
        
        # Set behavior based on type
        self.behavior = self.config["behavior"]
        
        # Special properties for boss targets
        if target_type == "boss":
            self.health = self.config.get("health", 1)
            # Make boss targets larger
            self.size = (TARGET_WINDOW_SIZE[0] * 1.5, TARGET_WINDOW_SIZE[1] * 1.5)
            self.window.geometry(f"{int(self.size[0])}x{int(self.size[1])}")
            self.canvas.config(width=self.size[0], height=self.size[1])
            self.create_shape()  # Redraw with new size
        else:
            self.health = 1
            
        # Movement properties
        self._set_movement_properties()
        
        # Start animation based on type
        self._set_animations()
        
    def _set_movement_properties(self):
        """Set movement properties based on target type"""
        # Set initial velocity if it's a moving target
        if self.behavior == "random_movement":
            angle = random.uniform(0, 2 * math.pi)
            vx = self.base_speed * math.cos(angle)
            vy = self.base_speed * math.sin(angle)
            self.set_velocity(vx, vy)
            
            # Set random direction change interval
            self.direction_change_interval = random.uniform(2.0, 5.0)
            self.time_to_direction_change = self.direction_change_interval
            
        elif self.behavior == "evade_player" or self.behavior == "chase_player":
            # These targets will set velocity dynamically based on player position
            self.detection_radius = 300  # How far they can detect the player
            self.set_velocity(0, 0)  # Start stationary
            
    def _set_animations(self):
        """Set up animations based on target type"""
        if self.target_type == "standard":
            # Standard targets pulse slowly
            self.start_animation('pulse')
            
        elif self.target_type == "moving":
            # Moving targets rotate
            self.start_animation('rotate')
            
        elif self.target_type == "evasive":
            # Evasive targets pulse quickly
            self.animation_frames = 15  # Faster animation cycle
            self.start_animation('pulse')
            
        elif self.target_type == "boss":
            # Boss targets shift colors
            self.start_animation('color_shift')
            
    def update(self, delta_time: float, player_pos: Optional[Tuple[float, float]] = None):
        """
        Update target state for the current frame
        
        Args:
            delta_time: Time elapsed since last update in seconds
            player_pos: Current player position for reactive behaviors
        """
        # Call parent update for basic movement and animation
        super().update(delta_time)
        
        # Update behavior based on type
        if self.behavior == "random_movement":
            self._update_random_movement(delta_time)
            
        elif self.behavior == "evade_player" and player_pos:
            self._update_evade_behavior(delta_time, player_pos)
            
        elif self.behavior == "chase_player" and player_pos:
            self._update_chase_behavior(delta_time, player_pos)
            
    def _update_random_movement(self, delta_time: float):
        """Update movement for random movement behavior"""
        # Decrease time to next direction change
        self.time_to_direction_change -= delta_time
        
        # Check if it's time to change direction
        if self.time_to_direction_change <= 0:
            # Choose new random direction
            angle = random.uniform(0, 2 * math.pi)
            vx = self.base_speed * math.cos(angle)
            vy = self.base_speed * math.sin(angle)
            self.set_velocity(vx, vy)
            
            # Reset timer
            self.time_to_direction_change = self.direction_change_interval
            
        # Check if we hit screen edge and bounce
        pos = self.get_position()
        size = self.get_size()
        vx, vy = self.velocity
        
        if pos[0] <= 0 and vx < 0:
            # Hit left edge, reverse x velocity
            self.set_velocity(-vx, vy)
        elif pos[0] + size[0] >= SCREEN_WIDTH and vx > 0:
            # Hit right edge, reverse x velocity
            self.set_velocity(-vx, vy)
            
        if pos[1] <= 0 and vy < 0:
            # Hit top edge, reverse y velocity
            self.set_velocity(vx, -vy)
        elif pos[1] + size[1] >= SCREEN_HEIGHT and vy > 0:
            # Hit bottom edge, reverse y velocity
            self.set_velocity(vx, -vy)
            
    def _update_evade_behavior(self, delta_time: float, player_pos: Tuple[float, float]):
        """Update movement to evade player"""
        my_pos = self.get_center()
        
        # Calculate distance to player
        dx = player_pos[0] - my_pos[0]
        dy = player_pos[1] - my_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Only evade if player is within detection radius
        if distance <= self.detection_radius:
            # Normalize direction vector
            if distance > 0:
                dx /= distance
                dy /= distance
            
            # Move in opposite direction from player
            vx = -dx * self.base_speed
            vy = -dy * self.base_speed
            self.set_velocity(vx, vy)
        else:
            # Player not detected, move randomly
            self._update_random_movement(delta_time)
            
    def _update_chase_behavior(self, delta_time: float, player_pos: Tuple[float, float]):
        """Update movement to chase player"""
        my_pos = self.get_center()
        
        # Calculate distance to player
        dx = player_pos[0] - my_pos[0]
        dy = player_pos[1] - my_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Only chase if player is within detection radius
        if distance <= self.detection_radius * 1.5:  # Longer detection for chase
            # Normalize direction vector
            if distance > 0:
                dx /= distance
                dy /= distance
            
            # Move toward player
            vx = dx * self.base_speed
            vy = dy * self.base_speed
            self.set_velocity(vx, vy)
        else:
            # Player not detected, move randomly
            self._update_random_movement(delta_time)
            
    def take_damage(self) -> bool:
        """
        Apply damage to the target
        
        Returns:
            bool: True if target is destroyed, False otherwise
        """
        self.health -= 1
        
        # Visual feedback for damage
        self._flash_damage()
        
        return self.health <= 0
        
    def _flash_damage(self):
        """Flash the target to indicate damage"""
        original_color = self.current_color
        
        # Flash white briefly
        self.current_color = "white"
        if self.shape_id:
            self.canvas.itemconfig(self.shape_id, fill=self.current_color)
        self.window.update()
        
        # Schedule return to original color
        self.window.after(100, lambda: self._reset_color(original_color))
        
    def _reset_color(self, color):
        """Reset to original color after damage flash"""
        self.current_color = color
        if self.shape_id:
            self.canvas.itemconfig(self.shape_id, fill=self.current_color)
            
    def get_points(self) -> int:
        """Get points value of this target"""
        return self.points
        
    def get_type(self) -> str:
        """Get the target type"""
        return self.target_type