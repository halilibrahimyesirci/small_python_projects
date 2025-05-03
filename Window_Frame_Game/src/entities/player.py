"""
Player Entity Module
Defines the player entity class with player-specific functionality
"""

import tkinter as tk
import random
import time
import sys
import os
from typing import Dict, List, Tuple, Any, Optional, Callable

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import game configuration
try:
    from config.game_config import *
except ImportError:
    try:
        from Window_Frame_Game.config.game_config import *
    except ImportError:
        print("Error: Could not import game configuration")
        sys.exit(1)

# Import base entity class
try:
    from entities.base_entity import BaseEntity
except ImportError:
    try:
        from Window_Frame_Game.src.entities.base_entity import BaseEntity
    except ImportError:
        print("Error: Could not import BaseEntity class")
        sys.exit(1)

class PlayerEntity(BaseEntity):
    """
    Player entity class
    
    Extends the base entity with player-specific functionality:
    - Keyboard input handling
    - Special abilities
    - Player statistics
    """
    
    def __init__(self, health: int = 3, parent: Optional[tk.Tk] = None):
        """
        Initialize the player entity
        
        Args:
            health: Initial health
            parent: Parent Tkinter window
        """
        # Call base entity constructor
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
        
        # Player-specific properties
        self.health = health
        self.max_health = health
        self.speed = PLAYER_SPEED
        self.score = 0
        
        # Input state
        self.keys_pressed = set()
        self.mouse_position = (0, 0)
        self.mouse_buttons = [False, False, False]  # Left, Middle, Right
        
        # Cooldowns
        self.dash_cooldown = 0
        self.dash_ready = True
        self.dash_duration = 0.2
        self.dash_active = False
        self.dash_start_time = 0
        self.dash_direction = (0, 0)
        
        # Bind input events
        self.bind_events()
        
        # Set initial position
        self.set_position(
            (SCREEN_WIDTH - self.size[0]) // 2,
            (SCREEN_HEIGHT - self.size[1]) // 2
        )
        
        # Draw initial player appearance
        self.update_appearance()
        
    def bind_events(self):
        """Bind input events to the player window"""
        try:
            # Keyboard events
            self.window.bind("<KeyPress>", self.on_key_press)
            self.window.bind("<KeyRelease>", self.on_key_release)
            
            # Mouse events
            self.window.bind("<Motion>", self.on_mouse_move)
            self.window.bind("<Button-1>", lambda e: self.on_mouse_button(0, True))
            self.window.bind("<ButtonRelease-1>", lambda e: self.on_mouse_button(0, False))
            self.window.bind("<Button-2>", lambda e: self.on_mouse_button(1, True))
            self.window.bind("<ButtonRelease-2>", lambda e: self.on_mouse_button(1, False))
            self.window.bind("<Button-3>", lambda e: self.on_mouse_button(2, True))
            self.window.bind("<ButtonRelease-3>", lambda e: self.on_mouse_button(2, False))
            
            # Focus events
            self.window.bind("<FocusIn>", self.on_focus)
            
            # Ensure player window has focus to receive input
            self.window.focus_force()
            
        except Exception as e:
            self.logger.exception("Error binding player events", e)
            
    def on_key_press(self, event):
        """
        Handle key press event
        
        Args:
            event: Key event
        """
        # Add key to pressed set
        self.keys_pressed.add(event.keysym.lower())
        
        # Handle special keys
        if event.keysym.lower() == "space" and self.dash_ready:
            self.activate_dash()
            
    def on_key_release(self, event):
        """
        Handle key release event
        
        Args:
            event: Key event
        """
        # Remove key from pressed set
        if event.keysym.lower() in self.keys_pressed:
            self.keys_pressed.remove(event.keysym.lower())
            
    def on_mouse_move(self, event):
        """
        Handle mouse move event
        
        Args:
            event: Mouse event
        """
        # Update mouse position
        self.mouse_position = (event.x_root, event.y_root)
        
    def on_mouse_button(self, button: int, pressed: bool):
        """
        Handle mouse button event
        
        Args:
            button: Button index (0=left, 1=middle, 2=right)
            pressed: True if pressed, False if released
        """
        self.mouse_buttons[button] = pressed
        
    def on_focus(self, event):
        """
        Handle focus event
        
        Args:
            event: Focus event
        """
        # Clear input state when gaining focus
        self.keys_pressed.clear()
        self.mouse_buttons = [False, False, False]
        
    def update(self, delta_time: float):
        """
        Update player state
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.active:
            return
            
        # Handle dash
        if self.dash_active:
            # Check if dash has ended
            if time.time() - self.dash_start_time >= self.dash_duration:
                self.dash_active = False
                self.dash_ready = False
                self.dash_cooldown = DASH_COOLDOWN
            else:
                # Apply dash movement
                dash_speed = DASH_SPEED * self.speed_multiplier
                self.x += self.dash_direction[0] * dash_speed * delta_time
                self.y += self.dash_direction[1] * dash_speed * delta_time
                
                # Keep in bounds
                self.keep_in_bounds()
                
                # Update position
                self.update_position()
                
                # Skip normal movement during dash
                super().update(delta_time)
                return
        elif not self.dash_ready:
            # Update dash cooldown
            self.dash_cooldown -= delta_time
            if self.dash_cooldown <= 0:
                self.dash_ready = True
            
        # Get movement direction from keys
        dx, dy = 0, 0
        
        if "w" in self.keys_pressed or "up" in self.keys_pressed:
            dy -= 1
        if "s" in self.keys_pressed or "down" in self.keys_pressed:
            dy += 1
        if "a" in self.keys_pressed or "left" in self.keys_pressed:
            dx -= 1
        if "d" in self.keys_pressed or "right" in self.keys_pressed:
            dx += 1
            
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            mag = (dx*dx + dy*dy) ** 0.5
            dx /= mag
            dy /= mag
            
        # Set velocity
        self.set_velocity(dx, dy)
        
        # Update base entity
        super().update(delta_time)
        
        # Keep player in bounds
        self.keep_in_bounds()
        
    def activate_dash(self):
        """Activate the dash ability"""
        if not self.dash_ready or self.dash_active:
            return
            
        # Get dash direction from current velocity or keys
        if self.velocity_x != 0 or self.velocity_y != 0:
            # Use current movement direction
            dx, dy = self.velocity_x, self.velocity_y
        else:
            # Use key inputs
            dx, dy = 0, 0
            
            if "w" in self.keys_pressed or "up" in self.keys_pressed:
                dy -= 1
            if "s" in self.keys_pressed or "down" in self.keys_pressed:
                dy += 1
            if "a" in self.keys_pressed or "left" in self.keys_pressed:
                dx -= 1
            if "d" in self.keys_pressed or "right" in self.keys_pressed:
                dx += 1
                
        # Don't dash if no direction
        if dx == 0 and dy == 0:
            return
            
        # Normalize direction
        mag = (dx*dx + dy*dy) ** 0.5
        dx /= mag
        dy /= mag
        
        # Start dash
        self.dash_active = True
        self.dash_start_time = time.time()
        self.dash_direction = (dx, dy)
        
        # Visual feedback
        self.start_flash_effect(0.05, 4, DASH_COLOR)
        
        self.logger.debug("Player dash activated", {
            "direction": self.dash_direction
        })
        
    def keep_in_bounds(self):
        """Keep the player within screen bounds"""
        # Constrain X position
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.size[0]:
            self.x = SCREEN_WIDTH - self.size[0]
            
        # Constrain Y position
        if self.y < 0:
            self.y = 0
        elif self.y > SCREEN_HEIGHT - self.size[1]:
            self.y = SCREEN_HEIGHT - self.size[1]
            
    def take_damage(self, amount: int = 1) -> bool:
        """
        Apply damage to the player
        
        Args:
            amount: Amount of damage to apply
            
        Returns:
            True if player was destroyed, False otherwise
        """
        # Skip if invulnerable during dash
        if self.dash_active:
            return False
            
        # Apply damage via base entity method
        result = super().take_damage(amount)
        
        self.logger.info(f"Player took damage", {
            "amount": amount,
            "health_remaining": self.health,
        })
        
        return result
        
    def add_score(self, points: int):
        """
        Add points to the player's score
        
        Args:
            points: Number of points to add
        """
        self.score += points
        
    def get_score(self) -> int:
        """
        Get the player's score
        
        Returns:
            Current score
        """
        return self.score
        
    def is_dash_ready(self) -> bool:
        """
        Check if dash ability is ready
        
        Returns:
            True if dash is ready, False otherwise
        """
        return self.dash_ready
        
    def get_dash_cooldown(self) -> float:
        """
        Get the remaining dash cooldown
        
        Returns:
            Cooldown time in seconds
        """
        return max(0, self.dash_cooldown)
        
    def update_appearance(self):
        """Update the player appearance"""
        try:
            # Update canvas background
            self.canvas.config(bg=self.color)
            
            # Clear canvas
            self.canvas.delete("all")
            
            # Get dimensions
            width, height = self.size
            
            # Draw player shape
            if self.shape == "rectangle":
                # Player rectangle with border
                self.canvas.create_rectangle(
                    2, 2, width-2, height-2,
                    fill=self.color,
                    outline=PLAYER_OUTLINE_COLOR,
                    width=2,
                    tags=("shape",)
                )
                
            elif self.shape == "circle":
                # Player circle with border
                self.canvas.create_oval(
                    2, 2, width-2, height-2,
                    fill=self.color,
                    outline=PLAYER_OUTLINE_COLOR,
                    width=2,
                    tags=("shape",)
                )
                
            # Add health indicator
            health_width = width - 10
            health_height = 5
            health_x = 5
            health_y = 5
            
            # Health background
            self.canvas.create_rectangle(
                health_x, health_y,
                health_x + health_width, health_y + health_height,
                fill="gray30",
                outline="gray50",
                tags=("health_bg",)
            )
            
            # Health bar
            health_percent = max(0, self.health / self.max_health)
            current_health_width = int(health_width * health_percent)
            
            self.canvas.create_rectangle(
                health_x, health_y,
                health_x + current_health_width, health_y + health_height,
                fill=self.get_health_color(),
                outline="",
                tags=("health_bar",)
            )
            
            # Dash indicator
            if self.dash_ready:
                dash_color = DASH_READY_COLOR
            else:
                cooldown_percent = max(0, min(1, self.dash_cooldown / DASH_COOLDOWN))
                # Blend from red to yellow as cooldown decreases
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
        """
        Get the color for the health bar based on current health percentage
        
        Returns:
            Color string
        """
        health_percent = self.health / self.max_health
        
        if health_percent > 0.7:
            return "green3"
        elif health_percent > 0.3:
            return "yellow2"
        else:
            return "red3"
            
    @staticmethod
    def blend_color(color1: str, color2: str, blend_factor: float) -> str:
        """
        Blend between two colors
        
        Args:
            color1: First color (hex or name)
            color2: Second color (hex or name)
            blend_factor: Blend factor (0.0 = color1, 1.0 = color2)
            
        Returns:
            Blended color as hex string
        """
        # Convert color names to hex if needed
        if not color1.startswith("#"):
            temp_label = tk.Label(bg=color1)
            color1 = temp_label.cget("bg")
            temp_label.destroy()
            
        if not color2.startswith("#"):
            temp_label = tk.Label(bg=color2)
            color2 = temp_label.cget("bg")
            temp_label.destroy()
            
        # Parse hex colors
        r1 = int(color1[1:3], 16)
        g1 = int(color1[3:5], 16)
        b1 = int(color1[5:7], 16)
        
        r2 = int(color2[1:3], 16)
        g2 = int(color2[3:5], 16)
        b2 = int(color2[5:7], 16)
        
        # Blend colors
        r = int(r1 + (r2 - r1) * blend_factor)
        g = int(g1 + (g2 - g1) * blend_factor)
        b = int(b1 + (b2 - b1) * blend_factor)
        
        # Return as hex
        return f"#{r:02x}{g:02x}{b:02x}"