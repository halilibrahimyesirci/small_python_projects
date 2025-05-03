import tkinter as tk
import random
import time
import sys
import os
from typing import Dict, List, Tuple, Any, Optional, Callable

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from config.game_config import *
except ImportError:
    try:
        from Window_Frame_Game.config.game_config import *
    except ImportError:
        print("Error: Could not import game configuration")
        sys.exit(1)

try:
    from utils.logger import Logger
except ImportError:
    try:
        from Window_Frame_Game.src.utils.logger import Logger
    except ImportError:
        print("Error: Could not import Logger module")
        sys.exit(1)

class BaseEntity:
    
    def __init__(self, entity_type: str, title: str, size: Tuple[int, int], color: str, 
                 shape: str = "rectangle", parent: Optional[tk.Tk] = None,
                 always_on_top: bool = True, alpha: float = WINDOW_ALPHA):
        self.logger = Logger(f"{entity_type.capitalize()}Entity", log_level=Logger.INFO)
        
        self.entity_type = entity_type
        self.title = title
        self.size = size
        self.color = color
        self.shape = shape
        self.parent = parent
        self.always_on_top = always_on_top
        self.alpha = alpha
        
        self.x = 0
        self.y = 0
        
        self.speed = 0
        self.speed_multiplier = 1.0
        self.velocity_x = 0
        self.velocity_y = 0
        
        self.active = True
        self.visible = True
        self.health = 1
        
        self.animation_frame = 0
        self.animation_frames = 1
        self.animation_speed = 0.1
        self.last_animation_update = 0
        self.animation_loop = True
        self.animation_callback = None
        
        self.flash_active = False
        self.flash_duration = 0.1
        self.flash_count = 0
        self.flash_max_count = 3
        self.flash_last_update = 0
        self.original_color = color
        self.flash_color = "white"
        
        self.create_window()
        
        self.logger.debug(f"{entity_type.capitalize()} entity created", {
            "title": title,
            "size": size,
            "color": color,
            "shape": shape
        })
        
    def create_window(self):
        try:
            self.window = tk.Toplevel(self.parent)
            self.window.title(self.title)
            
            self.window.geometry(f"{self.size[0]}x{self.size[1]}+{self.x}+{self.y}")
            self.window.overrideredirect(True)
            self.window.attributes("-topmost", self.always_on_top)
            self.window.attributes("-alpha", self.alpha)
            
            self.canvas = tk.Canvas(
                self.window,
                width=self.size[0],
                height=self.size[1],
                bg=self.color,
                highlightthickness=0
            )
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            self.draw_shape()
            
            self.window.bind("<Map>", self.on_map)
            self.window.bind("<Unmap>", self.on_unmap)
            
        except Exception as e:
            self.logger.exception("Error creating entity window", e)
            
    def draw_shape(self):
        self.canvas.delete("all")
        
        width, height = self.size
        
        if self.shape == "rectangle":
            self.canvas.create_rectangle(
                0, 0, width, height,
                fill=self.color,
                outline="",
                tags=("shape",)
            )
            
        elif self.shape == "circle":
            self.canvas.create_oval(
                0, 0, width, height,
                fill=self.color,
                outline="",
                tags=("shape",)
            )
            
        elif self.shape == "triangle":
            self.canvas.create_polygon(
                width/2, 0,
                0, height,
                width, height,
                fill=self.color,
                outline="",
                tags=("shape",)
            )
            
        elif self.shape == "star":
            points = []
            cx, cy = width/2, height/2
            r_outer = min(width, height) / 2
            r_inner = r_outer * 0.4
            
            for i in range(10):
                if i % 2 == 0:
                    angle = (i * 36) * (3.14159 / 180)
                    points.append(cx + r_outer * (cos(angle)))
                    points.append(cy - r_outer * (sin(angle)))
                else:
                    angle = (i * 36) * (3.14159 / 180)
                    points.append(cx + r_inner * (cos(angle)))
                    points.append(cy - r_inner * (sin(angle)))
                    
            self.canvas.create_polygon(
                *points,
                fill=self.color,
                outline="",
                tags=("shape",)
            )
        
    def update(self, delta_time: float):
        if not self.active:
            return
            
        if self.velocity_x != 0 or self.velocity_y != 0:
            effective_speed = self.speed * self.speed_multiplier
            
            self.x += self.velocity_x * effective_speed * delta_time
            self.y += self.velocity_y * effective_speed * delta_time
            
            self.update_position()
            
        current_time = time.time()
        
        if self.animation_frames > 1:
            if current_time - self.last_animation_update >= self.animation_speed:
                self.animation_frame = (self.animation_frame + 1) % self.animation_frames
                
                if self.animation_frame == 0 and not self.animation_loop and self.animation_callback:
                    self.animation_callback()
                    
                self.last_animation_update = current_time
                self.update_appearance()
                
        if self.flash_active:
            if current_time - self.flash_last_update >= self.flash_duration:
                self.flash_count += 1
                
                if self.color == self.original_color:
                    self.color = self.flash_color
                else:
                    self.color = self.original_color
                    
                self.update_appearance()
                self.flash_last_update = current_time
                
                if self.flash_count >= self.flash_max_count * 2:
                    self.flash_active = False
                    self.color = self.original_color
                    self.update_appearance()
                    
    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y
        self.update_position()
        
    def set_velocity(self, vx: float, vy: float):
        self.velocity_x = vx
        self.velocity_y = vy
        
    def set_speed(self, speed: float):
        self.speed = speed
        
    def set_color(self, color: str):
        self.color = color
        self.original_color = color
        self.update_appearance()
        
    def update_position(self):
        try:
            self.window.geometry(f"{self.size[0]}x{self.size[1]}+{int(self.x)}+{int(self.y)}")
        except:
            pass
            
    def update_appearance(self):
        try:
            self.canvas.config(bg=self.color)
            
            self.draw_shape()
        except:
            pass
            
    def get_position(self) -> Tuple[int, int]:
        return (self.x, self.y)
        
    def get_center(self) -> Tuple[int, int]:
        return (self.x + self.size[0] / 2, self.y + self.size[1] / 2)
        
    def get_size(self) -> Tuple[int, int]:
        return self.size
        
    def get_type(self) -> str:
        return self.entity_type
        
    def start_flash_effect(self, duration: float = 0.1, count: int = 3, color: str = "white"):
        self.flash_active = True
        self.flash_duration = duration
        self.flash_max_count = count
        self.flash_count = 0
        self.flash_last_update = time.time()
        self.flash_color = color
        
    def start_animation(self, frames: int, speed: float, loop: bool = True, callback: Optional[Callable] = None):
        self.animation_frames = frames
        self.animation_speed = speed
        self.animation_loop = loop
        self.animation_callback = callback
        self.animation_frame = 0
        self.last_animation_update = time.time()
        
    def stop_animation(self):
        self.animation_frames = 1
        self.animation_frame = 0
        
    def take_damage(self, amount: int = 1) -> bool:
        if not self.active:
            return False
            
        self.health -= amount
        
        self.start_flash_effect(0.1, 3, "red")
        
        if self.health <= 0:
            self.active = False
            return True
            
        return False
        
    def heal(self, amount: int = 1):
        self.health += amount
        
        self.start_flash_effect(0.1, 2, "green")
        
    def show(self):
        if not self.visible:
            try:
                self.window.deiconify()
                self.visible = True
            except:
                pass
                
    def hide(self):
        if self.visible:
            try:
                self.window.withdraw()
                self.visible = False
            except:
                pass
                
    def destroy(self):
        try:
            self.window.destroy()
            self.active = False
            self.visible = False
        except:
            pass
            
    def on_map(self, event):
        self.visible = True
        
    def on_unmap(self, event):
        self.visible = False
        
    def is_active(self) -> bool:
        return self.active
        
    def is_visible(self) -> bool:
        return self.visible
        
    def get_health(self) -> int:
        return self.health
        
    def set_health(self, health: int):
        self.health = health

from math import sin, cos