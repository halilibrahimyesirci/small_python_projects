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
    from entities.base_entity import BaseEntity
except ImportError:
    try:
        from Window_Frame_Game.src.entities.base_entity import BaseEntity
    except ImportError:
        print("Error: Could not import BaseEntity class")
        sys.exit(1)

class PlayerEntity(BaseEntity):
    
    def __init__(self, health: int = 3, parent: Optional[tk.Tk] = None):
        super().__init__(
            entity_type="player",
            title="Player",
            size=PLAYER_WINDOW_SIZE,
            color=PLAYER_COLOR,
            shape=PLAYER_SHAPE,
            parent=parent,
            always_on_top=True,
            alpha=WINDOW_ALPHA
        )
        
        self.health = health
        self.max_health = health
        self.speed = PLAYER_SPEED
        self.score = 0
        self.speed_multiplier = 1.0
        
        self.keys_pressed = set()
        self.mouse_position = (0, 0)
        self.mouse_buttons = [False, False, False]
        
        self.dash_cooldown = 0
        self.dash_ready = True
        self.dash_duration = 0.2
        self.dash_active = False
        self.dash_start_time = 0
        self.dash_direction = (0, 0)
        
        self.bind_events()
        
        self.set_position(
            (SCREEN_WIDTH - self.size[0]) // 2,
            (SCREEN_HEIGHT - self.size[1]) // 2
        )
        
        self.update_appearance()
        
    def bind_events(self):
        try:
            self.window.bind("<KeyPress>", self.on_key_press)
            self.window.bind("<KeyRelease>", self.on_key_release)
            
            self.window.bind("<Motion>", self.on_mouse_move)
            self.window.bind("<Button-1>", lambda e: self.on_mouse_button(0, True))
            self.window.bind("<ButtonRelease-1>", lambda e: self.on_mouse_button(0, False))
            self.window.bind("<Button-2>", lambda e: self.on_mouse_button(1, True))
            self.window.bind("<ButtonRelease-2>", lambda e: self.on_mouse_button(1, False))
            self.window.bind("<Button-3>", lambda e: self.on_mouse_button(2, True))
            self.window.bind("<ButtonRelease-3>", lambda e: self.on_mouse_button(2, False))
            
            self.window.bind("<FocusIn>", self.on_focus)
            
            self.window.focus_force()
            
        except Exception as e:
            self.logger.exception("Error binding player events", e)
            
    def on_key_press(self, event):
        self.keys_pressed.add(event.keysym.lower())
        
        if event.keysym.lower() == "space" and self.dash_ready:
            self.activate_dash()
            
    def on_key_release(self, event):
        if event.keysym.lower() in self.keys_pressed:
            self.keys_pressed.remove(event.keysym.lower())
            
    def on_mouse_move(self, event):
        self.mouse_position = (event.x_root, event.y_root)
        
    def on_mouse_button(self, button: int, pressed: bool):
        self.mouse_buttons[button] = pressed
        
    def on_focus(self, event):
        self.keys_pressed.clear()
        self.mouse_buttons = [False, False, False]
        
    def update(self, delta_time: float):
        if not self.active:
            return
            
        if self.dash_active:
            if time.time() - self.dash_start_time >= self.dash_duration:
                self.dash_active = False
                self.dash_ready = False
                self.dash_cooldown = DASH_COOLDOWN
            else:
                dash_speed = DASH_SPEED * self.speed_multiplier
                self.x += self.dash_direction[0] * dash_speed * delta_time
                self.y += self.dash_direction[1] * dash_speed * delta_time
                
                self.keep_in_bounds()
                
                self.update_position()
                
                super().update(delta_time)
                return
        elif not self.dash_ready:
            self.dash_cooldown -= delta_time
            if self.dash_cooldown <= 0:
                self.dash_ready = True
            
        dx, dy = 0, 0
        
        if "w" in self.keys_pressed or "up" in self.keys_pressed:
            dy -= 1
        if "s" in self.keys_pressed or "down" in self.keys_pressed:
            dy += 1
        if "a" in self.keys_pressed or "left" in self.keys_pressed:
            dx -= 1
        if "d" in self.keys_pressed or "right" in self.keys_pressed:
            dx += 1
            
        if dx != 0 and dy != 0:
            mag = (dx*dx + dy*dy) ** 0.5
            dx /= mag
            dy /= mag
            
        self.set_velocity(dx, dy)
        
        super().update(delta_time)
        
        self.keep_in_bounds()
        
    def activate_dash(self):
        if not self.dash_ready or self.dash_active:
            return
            
        if self.velocity_x != 0 or self.velocity_y != 0:
            dx, dy = self.velocity_x, self.velocity_y
        else:
            dx, dy = 0, 0
            
            if "w" in self.keys_pressed or "up" in self.keys_pressed:
                dy -= 1
            if "s" in self.keys_pressed or "down" in self.keys_pressed:
                dy += 1
            if "a" in self.keys_pressed or "left" in self.keys_pressed:
                dx -= 1
            if "d" in self.keys_pressed or "right" in self.keys_pressed:
                dx += 1
                
        if dx == 0 and dy == 0:
            return
            
        mag = (dx*dx + dy*dy) ** 0.5
        dx /= mag
        dy /= mag
        
        self.dash_active = True
        self.dash_start_time = time.time()
        self.dash_direction = (dx, dy)
        
        self.start_flash_effect(0.05, 4, DASH_COLOR)
        
        self.logger.debug("Player dash activated", {
            "direction": self.dash_direction
        })
        
    def keep_in_bounds(self):
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.size[0]:
            self.x = SCREEN_WIDTH - self.size[0]
            
        if self.y < 0:
            self.y = 0
        elif self.y > SCREEN_HEIGHT - self.size[1]:
            self.y = SCREEN_HEIGHT - self.size[1]
            
    def take_damage(self, amount: int = 1) -> bool:
        if self.dash_active:
            return False
            
        result = super().take_damage(amount)
        
        self.logger.info(f"Player took damage", {
            "amount": amount,
            "health_remaining": self.health,
        })
        
        return result
        
    def add_score(self, points: int):
        self.score += points
        
    def get_score(self) -> int:
        return self.score
        
    def is_dash_ready(self) -> bool:
        return self.dash_ready
        
    def get_dash_cooldown(self) -> float:
        return max(0, self.dash_cooldown)
        
    def update_appearance(self):
        try:
            self.canvas.config(bg=self.color)
            
            self.canvas.delete("all")
            
            width, height = self.size
            
            if self.shape == "rectangle":
                self.canvas.create_rectangle(
                    2, 2, width-2, height-2,
                    fill=self.color,
                    outline=PLAYER_OUTLINE_COLOR,
                    width=2,
                    tags=("shape",)
                )
                
            elif self.shape == "circle":
                self.canvas.create_oval(
                    2, 2, width-2, height-2,
                    fill=self.color,
                    outline=PLAYER_OUTLINE_COLOR,
                    width=2,
                    tags=("shape",)
                )
                
            health_width = width - 10
            health_height = 5
            health_x = 5
            health_y = 5
            
            self.canvas.create_rectangle(
                health_x, health_y,
                health_x + health_width, health_y + health_height,
                fill="gray30",
                outline="gray50",
                tags=("health_bg",)
            )
            
            health_percent = max(0, self.health / self.max_health)
            current_health_width = int(health_width * health_percent)
            
            self.canvas.create_rectangle(
                health_x, health_y,
                health_x + current_health_width, health_y + health_height,
                fill=self.get_health_color(),
                outline="",
                tags=("health_bar",)
            )
            
            if self.dash_ready:
                dash_color = DASH_READY_COLOR
            else:
                cooldown_percent = max(0, min(1, self.dash_cooldown / DASH_COOLDOWN))
                dash_color = self.blend_color(DASH_COOLDOWN_COLOR, DASH_READY_COLOR, 1 - cooldown_percent)
                
            dash_size = 6
            dash_x = width - dash_size - 5
            dash_y = 5
            
            self.canvas.create_oval(
                dash_x, dash_y,
                dash_x + dash_size, dash_y + dash_size,
                fill=dash_color,
                outline="white",
                width=1,
                tags=("dash_indicator",)
            )
            
        except Exception as e:
            self.logger.exception("Error updating player appearance", e)
            
    def get_health_color(self) -> str:
        health_percent = self.health / self.max_health
        
        if health_percent > 0.7:
            return "green3"
        elif health_percent > 0.3:
            return "yellow2"
        else:
            return "red3"
            
    @staticmethod
    def blend_color(color1: str, color2: str, blend_factor: float) -> str:
        try:
            root = tk.Tk()
            root.withdraw()
            
            if not color1.startswith("#"):
                try:
                    color1 = root.winfo_rgb(color1)
                    r1, g1, b1 = [int(c / 256) for c in color1]
                except:
                    r1, g1, b1 = 255, 0, 0
            else:
                r1 = int(color1[1:3], 16)
                g1 = int(color1[3:5], 16)
                b1 = int(color1[5:7], 16)
            
            if not color2.startswith("#"):
                try:
                    color2 = root.winfo_rgb(color2)
                    r2, g2, b2 = [int(c / 256) for c in color2]
                except:
                    r2, g2, b2 = 0, 255, 0
            else:
                r2 = int(color2[1:3], 16)
                g2 = int(color2[3:5], 16)
                b2 = int(color2[5:7], 16)
            
            root.destroy()
            
            r = int(r1 + (r2 - r1) * blend_factor)
            g = int(g1 + (g2 - g1) * blend_factor)
            b = int(b1 + (b2 - b1) * blend_factor)
            
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except Exception as e:
            return "#FF00FF"