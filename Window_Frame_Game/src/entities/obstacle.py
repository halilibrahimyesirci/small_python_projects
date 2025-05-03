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
        OBSTACLE_WINDOW_TITLE = "Obstacle"
        OBSTACLE_WINDOW_SIZE = (150, 150)
        OBSTACLE_WINDOW_COLOR = "gray"
        OBSTACLE_TYPES = {
            "barrier": {"effect": "block", "duration": 0},
            "trap": {"effect": "freeze", "duration": 3},
            "decoy": {"effect": "none", "duration": 0}
        }

class ObstacleEntity(GameEntity):
    
    def __init__(self, 
                 obstacle_type: str = "barrier",
                 level: int = 1,
                 difficulty: str = "medium",
                 parent: Optional[Any] = None):
        self.obstacle_type = obstacle_type
        self.config = OBSTACLE_TYPES.get(obstacle_type, OBSTACLE_TYPES["barrier"])
        
        if obstacle_type == "barrier":
            color = "gray"
            shape = "rectangle"
        elif obstacle_type == "trap":
            color = "orange"
            shape = "star"
        elif obstacle_type == "decoy":
            color = random.choice(TARGET_WINDOW_COLORS)
            shape = random.choice(SHAPE_TYPES)
        else:
            color = OBSTACLE_WINDOW_COLOR
            shape = "rectangle"
        
        self.effect_duration = self.config["duration"]
        if difficulty == "easy":
            self.effect_duration *= 0.8
        elif difficulty == "hard":
            self.effect_duration *= 1.2
        elif difficulty == "expert":
            self.effect_duration *= 1.5
            
        level_scale = 1.0 + (level - 1) * 0.05
        self.effect_duration *= level_scale
        
        super().__init__(
            title=OBSTACLE_WINDOW_TITLE,
            size=OBSTACLE_WINDOW_SIZE,
            color=color,
            shape_type=shape,
            is_player=False,
            parent=parent
        )
        
        self._set_behavior_and_animation()
        
    def _set_behavior_and_animation(self):
        if self.obstacle_type == "barrier":
            self.start_animation('none')
            
        elif self.obstacle_type == "trap":
            self.start_animation('pulse')
            
            self.window.after(100, self._rotate_trap)
            
        elif self.obstacle_type == "decoy":
            if random.random() < 0.5:
                self.start_animation('pulse')
            else:
                self.start_animation('rotate')
                
    def _rotate_trap(self):
        if self.obstacle_type != "trap" or not self.window:
            return
            
        self.rotation_angle = (self.rotation_angle + 5) % 360
        self._redraw_shape()
        
        self.window.after(100, self._rotate_trap)
        
    def get_type(self) -> str:
        return self.obstacle_type
        
    def get_effect(self) -> str:
        return self.config["effect"]
        
    def get_effect_duration(self) -> float:
        return self.effect_duration
        
    def apply_effect(self, player_entity):
        effect = self.get_effect()
        
        if effect == "block":
            return False
            
        elif effect == "freeze":
            duration = self.get_effect_duration()
            player_entity.apply_status_effect("freeze", duration)
            return True
            
        elif effect == "none":
            return False
            
        return False