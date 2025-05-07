"""
Debug utilities for the game.
Provides debugging tools, performance monitoring, and error handling.
"""

import pygame
import time
import sys
import logging
import traceback
from collections import deque

logger = logging.getLogger(__name__)

class DebugManager:
    """Manages debugging tools and monitoring"""
    
    def __init__(self, enable_debug=False):
        self.debug_mode = enable_debug
        self.fps_values = deque(maxlen=60)  # Store last 60 FPS values for averaging
        self.frame_times = deque(maxlen=60)  # Store last 60 frame times
        self.last_time = time.time()
        self.debug_font = None
        self.debug_overlay_active = False
        self.memory_usage = 0
        self.debug_sections = {
            "fps": True,
            "memory": True,
            "objects": True,
            "input": False,
            "render": False
        }
        
        # Performance counters
        self.performance_data = {
            "update": 0,
            "render": 0,
            "ui": 0,
            "physics": 0,
            "input": 0
        }
        
        # Error tracking
        self.error_log = deque(maxlen=10)  # Store last 10 errors
        
        try:
            # Initialize debug font if pygame is initialized
            if pygame.font.get_init():
                self.debug_font = pygame.font.SysFont("monospace", 16)
            else:
                logger.warning("Pygame font module not initialized, debug text will be unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize debug font: {e}")
            
    def start_timer(self, section_name):
        """Start a performance timer for a section of code"""
        if not self.debug_mode:
            return None
            
        return time.time()
        
    def end_timer(self, section_name, start_time):
        """End a performance timer and record the elapsed time"""
        if not self.debug_mode or start_time is None:
            return
            
        elapsed = time.time() - start_time
        if section_name in self.performance_data:
            self.performance_data[section_name] = elapsed
            
    def log_error(self, error, context=None):
        """Log an error to the debug manager"""
        error_info = {
            "error": str(error),
            "traceback": traceback.format_exc(),
            "time": time.time(),
            "context": context or {}
        }
        self.error_log.append(error_info)
        logger.error(f"Error: {error}", exc_info=True)
        
    def toggle_debug_overlay(self):
        """Toggle the debug overlay display"""
        self.debug_overlay_active = not self.debug_overlay_active
        logger.debug(f"Debug overlay {'enabled' if self.debug_overlay_active else 'disabled'}")
        
    def toggle_debug_section(self, section_name):
        """Toggle visibility of a debug section"""
        if section_name in self.debug_sections:
            self.debug_sections[section_name] = not self.debug_sections[section_name]
            
    def update(self, dt):
        """Update debug information"""
        if not self.debug_mode:
            return
            
        # Calculate FPS
        current_time = time.time()
        frame_time = current_time - self.last_time
        self.last_time = current_time
        
        # Avoid division by zero
        fps = 1.0 / frame_time if frame_time > 0 else 0
        
        self.fps_values.append(fps)
        self.frame_times.append(frame_time * 1000)  # Convert to milliseconds
        
        # Update memory usage (only in debug mode)
        try:
            import psutil
            process = psutil.Process()
            self.memory_usage = process.memory_info().rss / (1024 * 1024)  # MB
        except ImportError:
            self.memory_usage = 0
            
    def render(self, screen):
        """Render debug information overlay"""
        if not self.debug_mode or not self.debug_overlay_active or not self.debug_font:
            return
            
        text_y = 10
        line_height = 20
        
        # Calculate average FPS and frame time
        avg_fps = sum(self.fps_values) / len(self.fps_values) if self.fps_values else 0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0
        
        # Draw FPS information
        if self.debug_sections["fps"]:
            fps_text = f"FPS: {avg_fps:.1f} ({avg_frame_time:.1f} ms)"
            fps_surface = self.debug_font.render(fps_text, True, (255, 255, 0))
            screen.blit(fps_surface, (10, text_y))
            text_y += line_height
            
        # Draw memory usage
        if self.debug_sections["memory"]:
            memory_text = f"Memory: {self.memory_usage:.1f} MB"
            memory_surface = self.debug_font.render(memory_text, True, (255, 255, 0))
            screen.blit(memory_surface, (10, text_y))
            text_y += line_height
            
        # Draw performance timers
        for section, time_ms in self.performance_data.items():
            if not self.debug_sections.get("render", False):
                continue
                
            perf_text = f"{section}: {time_ms*1000:.1f} ms"
            perf_surface = self.debug_font.render(perf_text, True, (255, 255, 0))
            screen.blit(perf_surface, (10, text_y))
            text_y += line_height
            
        # Draw recent error if any
        if self.error_log:
            latest_error = self.error_log[-1]
            error_text = f"Error: {latest_error['error']}"
            error_surface = self.debug_font.render(error_text, True, (255, 0, 0))
            screen.blit(error_surface, (10, text_y))
            
    def handle_key_event(self, event):
        """Handle debug keyboard events"""
        if not self.debug_mode:
            return False
            
        if event.type == pygame.KEYDOWN:
            # F3 to toggle debug overlay
            if event.key == pygame.K_F3:
                self.toggle_debug_overlay()
                return True
                
            # F4 to cycle through debug sections
            elif event.key == pygame.K_F4 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                # Cycle through available sections
                sections = list(self.debug_sections.keys())
                for i, section in enumerate(sections):
                    if i < len(sections) - 1:
                        self.debug_sections[section] = False
                    else:
                        self.debug_sections[section] = True
                return True
                
        return False