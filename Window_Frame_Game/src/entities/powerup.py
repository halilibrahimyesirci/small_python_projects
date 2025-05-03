import random
import math
from typing import Dict, Tuple, Optional, List, Any
import sys

from .base_entity import GameEntity

sys.path.append("../../config")
try:
    from config.game_config import *
except ImportError:
    try:
        from Window_Frame_Game.config.game_config import *
    except ImportError:
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
    
    def __init__(self, 
                 powerup_type: str = None,
                 level: int = 1,
                 difficulty: str = "medium",
                 parent: Optional[Any] = None):
        if powerup_type is None:
            powerup_type = random.choice(list(POWERUP_WINDOW_COLORS.keys()))
            
        self.powerup_type = powerup_type
        
        color = POWERUP_WINDOW_COLORS.get(powerup_type, "white")
        
        self.config = POWERUP_EFFECTS.get(powerup_type, {})
        
        difficulty_factor = 1.0
        if difficulty == "easy":
            difficulty_factor = 1.2
        elif difficulty == "hard":
            difficulty_factor = 0.8
        elif difficulty == "expert":
            difficulty_factor = 0.6
        
        self.duration = self.config.get("duration", 5.0) * difficulty_factor
        
        shape_type = "circle"
        if powerup_type == "speed":
            shape_type = "triangle"
        elif powerup_type == "magnet":
            shape_type = "circle"
        elif powerup_type == "shield":
            shape_type = "star"
        elif powerup_type == "time":
            shape_type = "rectangle"
        
        super().__init__(
            title=POWERUP_WINDOW_TITLE,
            size=POWERUP_WINDOW_SIZE,
            color=color,
            shape_type=shape_type,
            is_player=False,
            parent=parent
        )
        
        self._set_animation()
        
        self._setup_floating_movement()
        
    def _set_animation(self):
        if self.powerup_type == "speed":
            self.animation_frames = 20
            self.start_animation('rotate')
            
        elif self.powerup_type == "magnet":
            self.start_animation('pulse')
            
        elif self.powerup_type == "shield":
            self.start_animation('color_shift')
            
        elif self.powerup_type == "time":
            self.animation_frames = 40
            self.start_animation('pulse')
        
    def _setup_floating_movement(self):
        self.initial_x, self.initial_y = self.get_position()
        
        self.float_amplitude_x = random.uniform(10, 30)
        self.float_amplitude_y = random.uniform(10, 30)
        self.float_speed_x = random.uniform(0.5, 1.5)
        self.float_speed_y = random.uniform(0.5, 1.5)
        self.float_phase_x = random.uniform(0, 2 * math.pi)
        self.float_phase_y = random.uniform(0, 2 * math.pi)
        self.float_time = 0
        
    def update(self, delta_time: float):
        super().update(delta_time)
        
        self._update_floating_movement(delta_time)
        
    def _update_floating_movement(self, delta_time: float):
        self.float_time += delta_time
        
        new_x = self.initial_x + self.float_amplitude_x * math.sin(
            self.float_speed_x * self.float_time + self.float_phase_x
        )
        new_y = self.initial_y + self.float_amplitude_y * math.sin(
            self.float_speed_y * self.float_time + self.float_phase_y
        )
        
        self.set_position(int(new_x), int(new_y))
        
    def get_type(self) -> str:
        return self.powerup_type
        
    def get_duration(self) -> float:
        return self.duration
        
    def get_multiplier(self) -> float:
        return self.config.get("multiplier", 2.0)
        
    def get_radius(self) -> float:
        return self.config.get("radius", 300)
        
    def get_slowdown(self) -> float:
        return self.config.get("slowdown", 0.5)