"""
Base Entity Module
Defines the base entity class for all game objects
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

# Import utility modules
try:
    from utils.logger import Logger
except ImportError:
    try:
        from Window_Frame_Game.src.utils.logger import Logger
    except ImportError:
        print("Error: Could not import Logger module")
        sys.exit(1)

class BaseEntity:
    """
    Base class for all game entities
    
    This class provides common functionality for all entities including:
    - Window creation and management
    - Position and movement
    - Animations and effects
    - Collision detection
    """
    
    def __init__(self, entity_type: str, title: str, size: Tuple[int, int], color: str, 
                 shape: str = "rectangle", parent: Optional[tk.Tk] = None,
                 always_on_top: bool = True, alpha: float = WINDOW_ALPHA):
        """
        Initialize the base entity
        
        Args:
            entity_type: Type of entity (player, target, powerup, obstacle)
            title: Window title
            size: Window size (width, height)
            color: Window color
            shape: Window shape (rectangle, circle, triangle, star)
            parent: Parent Tkinter window
            always_on_top: Whether the window should always be on top
            alpha: Window transparency (0.0-1.0)
        """
        self.logger = Logger(f"{entity_type.capitalize()}Entity", log_level=Logger.INFO)
        
        self.entity_type = entity_type
        self.title = title
        self.size = size
        self.color = color
        self.shape = shape
        self.parent = parent
        self.always_on_top = always_on_top
        self.alpha = alpha
        
        # Position
        self.x = 0
        self.y = 0
        
        # Movement
        self.speed = 0
        self.speed_multiplier = 1.0
        self.velocity_x = 0
        self.velocity_y = 0
        
        # State
        self.active = True
        self.visible = True
        self.health = 1
        
        # Animation
        self.animation_frame = 0
        self.animation_frames = 1
        self.animation_speed = 0.1
        self.last_animation_update = 0
        self.animation_loop = True
        self.animation_callback = None
        
        # Visual effects
        self.flash_active = False
        self.flash_duration = 0.1
        self.flash_count = 0
        self.flash_max_count = 3
        self.flash_last_update = 0
        self.original_color = color
        self.flash_color = "white"
        
        # Create the entity window
        self.create_window()
        
        self.logger.debug(f"{entity_type.capitalize()} entity created", {
            "title": title,
            "size": size,
            "color": color,
            "shape": shape
        })
        
    def create_window(self):
        """Create the entity window"""
        try:
            # Create a new Toplevel window
            self.window = tk.Toplevel(self.parent)
            self.window.title(self.title)
            
            # Set window properties
            self.window.geometry(f"{self.size[0]}x{self.size[1]}+{self.x}+{self.y}")
            self.window.overrideredirect(True)  # Remove window decorations
            self.window.attributes("-topmost", self.always_on_top)
            self.window.attributes("-alpha", self.alpha)
            
            # Create canvas for custom drawing
            self.canvas = tk.Canvas(
                self.window,
                width=self.size[0],
                height=self.size[1],
                bg=self.color,
                highlightthickness=0
            )
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Draw shape based on type
            self.draw_shape()
            
            # Bind events
            self.window.bind("<Map>", self.on_map)
            self.window.bind("<Unmap>", self.on_unmap)
            
        except Exception as e:
            self.logger.exception("Error creating entity window", e)
            
    def draw_shape(self):
        """Draw the entity shape on the canvas"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Get dimensions
        width, height = self.size
        
        # Draw based on shape type
        if self.shape == "rectangle":
            # Rectangle (default)
            self.canvas.create_rectangle(
                0, 0, width, height,
                fill=self.color,
                outline="",
                tags=("shape",)
            )
            
        elif self.shape == "circle":
            # Circle
            self.canvas.create_oval(
                0, 0, width, height,
                fill=self.color,
                outline="",
                tags=("shape",)
            )
            
        elif self.shape == "triangle":
            # Triangle
            self.canvas.create_polygon(
                width/2, 0,
                0, height,
                width, height,
                fill=self.color,
                outline="",
                tags=("shape",)
            )
            
        elif self.shape == "star":
            # Star (5-pointed)
            points = []
            cx, cy = width/2, height/2
            r_outer = min(width, height) / 2
            r_inner = r_outer * 0.4
            
            for i in range(10):
                if i % 2 == 0:
                    # Outer point
                    angle = (i * 36) * (3.14159 / 180)
                    points.append(cx + r_outer * (cos(angle)))
                    points.append(cy - r_outer * (sin(angle)))
                else:
                    # Inner point
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
        """
        Update the entity state
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.active:
            return
            
        # Update position based on velocity
        if self.velocity_x != 0 or self.velocity_y != 0:
            effective_speed = self.speed * self.speed_multiplier
            
            self.x += self.velocity_x * effective_speed * delta_time
            self.y += self.velocity_y * effective_speed * delta_time
            
            # Update window position
            self.update_position()
            
        # Update animations
        current_time = time.time()
        
        # Handle animation frames
        if self.animation_frames > 1:
            if current_time - self.last_animation_update >= self.animation_speed:
                self.animation_frame = (self.animation_frame + 1) % self.animation_frames
                
                # If animation completed and not looping, call callback
                if self.animation_frame == 0 and not self.animation_loop and self.animation_callback:
                    self.animation_callback()
                    
                self.last_animation_update = current_time
                self.update_appearance()
                
        # Handle flash effect
        if self.flash_active:
            if current_time - self.flash_last_update >= self.flash_duration:
                self.flash_count += 1
                
                # Toggle color
                if self.color == self.original_color:
                    self.color = self.flash_color
                else:
                    self.color = self.original_color
                    
                self.update_appearance()
                self.flash_last_update = current_time
                
                # End flash effect if max count reached
                if self.flash_count >= self.flash_max_count * 2:
                    self.flash_active = False
                    self.color = self.original_color
                    self.update_appearance()
                    
    def set_position(self, x: int, y: int):
        """
        Set the entity position
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y
        self.update_position()
        
    def set_velocity(self, vx: float, vy: float):
        """
        Set the entity velocity
        
        Args:
            vx: X velocity component
            vy: Y velocity component
        """
        self.velocity_x = vx
        self.velocity_y = vy
        
    def set_speed(self, speed: float):
        """
        Set the entity speed
        
        Args:
            speed: Movement speed
        """
        self.speed = speed
        
    def set_color(self, color: str):
        """
        Set the entity color
        
        Args:
            color: Color string
        """
        self.color = color
        self.original_color = color
        self.update_appearance()
        
    def update_position(self):
        """Update the window position"""
        try:
            self.window.geometry(f"{self.size[0]}x{self.size[1]}+{int(self.x)}+{int(self.y)}")
        except:
            pass
            
    def update_appearance(self):
        """Update the entity appearance"""
        try:
            # Update canvas background
            self.canvas.config(bg=self.color)
            
            # Redraw shape
            self.draw_shape()
        except:
            pass
            
    def get_position(self) -> Tuple[int, int]:
        """
        Get the entity position
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)
        
    def get_center(self) -> Tuple[int, int]:
        """
        Get the entity center position
        
        Returns:
            Tuple of (x, y) coordinates at the center of the entity
        """
        return (self.x + self.size[0] / 2, self.y + self.size[1] / 2)
        
    def get_size(self) -> Tuple[int, int]:
        """
        Get the entity size
        
        Returns:
            Tuple of (width, height)
        """
        return self.size
        
    def get_type(self) -> str:
        """
        Get the entity type
        
        Returns:
            Entity type string
        """
        return self.entity_type
        
    def start_flash_effect(self, duration: float = 0.1, count: int = 3, color: str = "white"):
        """
        Start a flashing effect
        
        Args:
            duration: Duration of each flash in seconds
            count: Number of flashes
            color: Flash color
        """
        self.flash_active = True
        self.flash_duration = duration
        self.flash_max_count = count
        self.flash_count = 0
        self.flash_last_update = time.time()
        self.flash_color = color
        
    def start_animation(self, frames: int, speed: float, loop: bool = True, callback: Optional[Callable] = None):
        """
        Start an animation sequence
        
        Args:
            frames: Number of animation frames
            speed: Time between frames in seconds
            loop: Whether the animation should loop
            callback: Function to call when animation completes (if not looping)
        """
        self.animation_frames = frames
        self.animation_speed = speed
        self.animation_loop = loop
        self.animation_callback = callback
        self.animation_frame = 0
        self.last_animation_update = time.time()
        
    def stop_animation(self):
        """Stop the current animation"""
        self.animation_frames = 1
        self.animation_frame = 0
        
    def take_damage(self, amount: int = 1) -> bool:
        """
        Apply damage to the entity
        
        Args:
            amount: Amount of damage to apply
            
        Returns:
            True if the entity was destroyed, False otherwise
        """
        # Skip if already inactive
        if not self.active:
            return False
            
        # Reduce health
        self.health -= amount
        
        # Start flash effect for visual feedback
        self.start_flash_effect(0.1, 3, "red")
        
        # Check if destroyed
        if self.health <= 0:
            self.active = False
            return True
            
        return False
        
    def heal(self, amount: int = 1):
        """
        Heal the entity
        
        Args:
            amount: Amount of health to restore
        """
        self.health += amount
        
        # Visual feedback
        self.start_flash_effect(0.1, 2, "green")
        
    def show(self):
        """Show the entity"""
        if not self.visible:
            try:
                self.window.deiconify()
                self.visible = True
            except:
                pass
                
    def hide(self):
        """Hide the entity"""
        if self.visible:
            try:
                self.window.withdraw()
                self.visible = False
            except:
                pass
                
    def destroy(self):
        """Destroy the entity window"""
        try:
            self.window.destroy()
            self.active = False
            self.visible = False
        except:
            pass
            
    def on_map(self, event):
        """Handle window map event"""
        self.visible = True
        
    def on_unmap(self, event):
        """Handle window unmap event"""
        self.visible = False
        
    def is_active(self) -> bool:
        """
        Check if the entity is active
        
        Returns:
            True if active, False otherwise
        """
        return self.active
        
    def is_visible(self) -> bool:
        """
        Check if the entity is visible
        
        Returns:
            True if visible, False otherwise
        """
        return self.visible
        
    def get_health(self) -> int:
        """
        Get the entity health
        
        Returns:
            Current health
        """
        return self.health
        
    def set_health(self, health: int):
        """
        Set the entity health
        
        Args:
            health: New health value
        """
        self.health = health

# Import math functions now to avoid issues with the star shape drawing
from math import sin, cos