import tkinter as tk
from tkinter import Canvas
import random
import time
from conf import *

class GameWindow:
    def __init__(self, title, size, color, is_player=False):
        try:
            self.window = tk.Tk() if is_player else tk.Toplevel()
            self.window.title(title)
            self.size = size
            self.color = color
            
            # Make only target windows transparent
            if not is_player:
                self.window.attributes('-alpha', WINDOW_ALPHA)
                self.window.attributes('-transparentcolor', 'white')
            
            # Remove window decorations for all windows
            self.window.overrideredirect(True)
            
            # Create canvas with appropriate background
            bg_color = 'white' if not is_player else color
            self.canvas = Canvas(self.window, width=size[0], height=size[1],
                               bg=bg_color, highlightthickness=0)
            self.canvas.pack()
            
            # Create shape
            self.shape_type = "rectangle" if is_player else random.choice(SHAPE_TYPES)
            self.create_shape()
            
            # Window setup
            self.window.resizable(False, False)
            
            # Position window safely within screen bounds
            self.reposition()
            
            if is_player:
                self.fps_label = tk.Label(self.window, text="FPS: 0", fg="white", bg=color)
                self.fps_label.pack()
                self.last_time = time.time()
                self.frame_count = 0
                self.fps = 0
                self.update_fps()

            # Add window state tracking
            self.is_visible = True
            self.window.bind('<Unmap>', self._on_minimize)
            self.window.bind('<Map>', self._on_restore)
            
            # Add window protocol handler
            self.window.protocol("WM_DELETE_WINDOW", self.destroy)
            
        except Exception as e:
            print(f"Error creating window: {e}")
            raise

    def create_shape(self):
        self.canvas.delete("all")  # Clear canvas
        if self.shape_type == "triangle":
            # Create triangle
            points = [
                0, self.size[1],  # Bottom left
                self.size[0]/2, 0,  # Top middle
                self.size[0], self.size[1]  # Bottom right
            ]
            self.canvas.create_polygon(points, fill=self.color)
        else:
            # Create rectangle
            self.canvas.create_rectangle(0, 0, self.size[0], self.size[1], 
                                      fill=self.color)

    def reposition(self):
        # Ensure window stays within screen bounds
        x = random.randint(0, SCREEN_WIDTH - self.size[0])
        y = random.randint(0, SCREEN_HEIGHT - self.size[1])
        self.window.geometry(f"{self.size[0]}x{self.size[1]}+{x}+{y}")

    def _on_minimize(self, event):
        self.is_visible = False

    def _on_restore(self, event):
        self.is_visible = True

    def is_window_visible(self):
        return self.is_visible and self.window.winfo_exists()

    def update_fps(self):
        self.frame_count += 1
        current_time = time.time()
        delta_time = current_time - self.last_time
        
        if (delta_time >= 1.0):
            self.fps = self.frame_count
            self.fps_label.config(text=f"FPS: {self.fps}")
            self.frame_count = 0
            self.last_time = current_time
        
        self.window.after(1, self.update_fps)

    def move(self, dx, dy):
        current_x = self.window.winfo_x()
        current_y = self.window.winfo_y()
        
        # Calculate new position with strict boundary checking
        new_x = max(0, min(current_x + dx, SCREEN_WIDTH - self.size[0]))
        new_y = max(0, min(current_y + dy, SCREEN_HEIGHT - self.size[1]))
        
        self.window.geometry(f"+{new_x}+{new_y}")

    def get_position(self):
        return (self.window.winfo_x(), self.window.winfo_y())

    def get_size(self):
        return (self.window.winfo_width(), self.window.winfo_height())

    def destroy(self):
        try:
            if self.window.winfo_exists():
                self.window.destroy()
        except Exception as e:
            print(f"Error destroying window: {e}")
