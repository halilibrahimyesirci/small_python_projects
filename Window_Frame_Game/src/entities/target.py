import random
import math
from typing import Dict, Tuple, Optional, List, Any
import sys

from .base_entity import BaseEntity

sys.path.append("../../config")
try:
    from config.game_config import *
except ImportError:
    try:
        from Window_Frame_Game.config.game_config import *
    except ImportError:
        TARGET_WINDOW_TITLE = "Target"
        TARGET_WINDOW_SIZE = (200, 150)
        TARGET_WINDOW_COLORS = ["red", "blue", "green", "yellow", "purple"]
        TARGET_TYPES = {
            "standard": {"speed": 0, "points": 10, "behavior": "static"},
            "moving": {"speed": 3, "points": 20, "behavior": "random_movement"},
            "evasive": {"speed": 4, "points": 30, "behavior": "evade_player"},
            "boss": {"speed": 2, "points": 50, "behavior": "chase_player", "health": 3}
        }

class TargetEntity(BaseEntity):
    
    def __init__(self, 
                 target_type: str = "standard",
                 level: int = 1,
                 difficulty: str = "medium",
                 parent: Optional[Any] = None):
        self.target_type = target_type
        self.config = TARGET_TYPES.get(target_type, TARGET_TYPES["standard"])
        
        color = random.choice(TARGET_WINDOW_COLORS)
        shape = random.choice(SHAPE_TYPES)
        
        speed_multiplier = DIFFICULTY_LEVELS[difficulty]["target_speed_multiplier"]
        self.base_speed = self.config["speed"] * speed_multiplier * (1 + (level - 1) * 0.1)
        
        self.points = int(self.config["points"] * DIFFICULTY_LEVELS[difficulty]["score_multiplier"] * (1 + (level - 1) * 0.05))
        
        super().__init__(
            entity_type="target",
            title=TARGET_WINDOW_TITLE,
            size=TARGET_WINDOW_SIZE,
            color=color,
            shape=shape,
            parent=parent
        )
        
        self.behavior = self.config["behavior"]
        
        if target_type == "boss":
            self.health = self.config.get("health", 1)
            self.size = (TARGET_WINDOW_SIZE[0] * 1.5, TARGET_WINDOW_SIZE[1] * 1.5)
            self.window.geometry(f"{int(self.size[0])}x{int(self.size[1])}")
            self.canvas.config(width=self.size[0], height=self.size[1])
            self.draw_shape()  # Changed from create_shape to draw_shape
        else:
            self.health = 1
            
        self._set_movement_properties()
        
        self._set_animations()
        
    def _set_movement_properties(self):
        if self.behavior == "random_movement":
            angle = random.uniform(0, 2 * math.pi)
            vx = self.base_speed * math.cos(angle)
            vy = self.base_speed * math.sin(angle)
            self.set_velocity(vx, vy)
            
            self.direction_change_interval = random.uniform(2.0, 5.0)
            self.time_to_direction_change = self.direction_change_interval
            
        elif self.behavior == "evade_player" or self.behavior == "chase_player":
            self.detection_radius = 300
            self.set_velocity(0, 0)
            
    def _set_animations(self):
        # Animation parameters for the BaseEntity class
        frames = 2  # Number of animation frames
        speed = 0.3  # Animation speed in seconds
        loop = True  # Whether to loop the animation
        
        if self.target_type == "standard":
            # Simple pulse animation
            frames = 2
            speed = 0.5
            
        elif self.target_type == "moving":
            # Rotation animation
            frames = 4
            speed = 0.2
            
        elif self.target_type == "evasive":
            # Faster pulse animation
            frames = 2
            speed = 0.15
            
        elif self.target_type == "boss":
            # Color shifting animation
            frames = 3
            speed = 0.3
            
        # Start the animation with proper numeric parameters
        self.start_animation(frames, speed, loop)
            
    def update(self, delta_time: float, player_pos: Optional[Tuple[float, float]] = None):
        super().update(delta_time)
        
        if self.behavior == "random_movement":
            self._update_random_movement(delta_time)
            
        elif self.behavior == "evade_player" and player_pos:
            self._update_evade_behavior(delta_time, player_pos)
            
        elif self.behavior == "chase_player" and player_pos:
            self._update_chase_behavior(delta_time, player_pos)
            
    def _update_random_movement(self, delta_time: float):
        self.time_to_direction_change -= delta_time
        
        if self.time_to_direction_change <= 0:
            angle = random.uniform(0, 2 * math.pi)
            vx = self.base_speed * math.cos(angle)
            vy = self.base_speed * math.sin(angle)
            self.set_velocity(vx, vy)
            
            self.time_to_direction_change = self.direction_change_interval
            
        pos = self.get_position()
        size = self.get_size()
        vx, vy = self.velocity_x, self.velocity_y
        
        if pos[0] <= 0 and vx < 0:
            self.set_velocity(-vx, vy)
        elif pos[0] + size[0] >= SCREEN_WIDTH and vx > 0:
            self.set_velocity(-vx, vy)
            
        if pos[1] <= 0 and vy < 0:
            self.set_velocity(vx, -vy)
        elif pos[1] + size[1] >= SCREEN_HEIGHT and vy > 0:
            self.set_velocity(vx, -vy)
            
    def _update_evade_behavior(self, delta_time: float, player_pos: Tuple[float, float]):
        my_pos = self.get_center()
        
        dx = player_pos[0] - my_pos[0]
        dy = player_pos[1] - my_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.detection_radius:
            if distance > 0:
                dx /= distance
                dy /= distance
            
            vx = -dx * self.base_speed
            vy = -dy * self.base_speed
            self.set_velocity(vx, vy)
        else:
            self._update_random_movement(delta_time)
            
    def _update_chase_behavior(self, delta_time: float, player_pos: Tuple[float, float]):
        my_pos = self.get_center()
        
        dx = player_pos[0] - my_pos[0]
        dy = player_pos[1] - my_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.detection_radius * 1.5:
            if distance > 0:
                dx /= distance
                dy /= distance
            
            vx = dx * self.base_speed
            vy = dy * self.base_speed
            self.set_velocity(vx, vy)
        else:
            self._update_random_movement(delta_time)
            
    def take_damage(self) -> bool:
        self.health -= 1
        
        self._flash_damage()
        
        return self.health <= 0
        
    def _flash_damage(self):
        original_color = self.color  # Use self.color instead of self.current_color
        
        # Use the BaseEntity's flash effect method instead
        self.start_flash_effect(0.1, 3, "white")
        
    def _reset_color(self, color):
        self.color = color
        self.update_appearance()
            
    def get_points(self) -> int:
        return self.points
        
    def get_type(self) -> str:
        return self.target_type