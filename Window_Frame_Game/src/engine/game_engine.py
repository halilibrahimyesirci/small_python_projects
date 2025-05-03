"""
Game Engine Module
Central controller for game logic, state management, and entity interactions
"""

import tkinter as tk
import random
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable

# Import configuration
sys.path.append("../../config")
try:
    from config.game_config import *
except ImportError:
    try:
        from Window_Frame_Game.config.game_config import *
    except ImportError:
        # Fallback to prevent errors
        print("Warning: Could not import game_config, using fallback values")
        
# Import logger
from ..utils.logger import Logger

class GameEngine:
    """
    Main game engine that manages game state, entities, and interactions
    """
    
    # Game states
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_LEVEL_COMPLETE = "level_complete"
    STATE_GAME_OVER = "game_over"
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the game engine
        
        Args:
            root: Main Tkinter root window
        """
        self.root = root
        self.logger = Logger("GameEngine", log_level=Logger.INFO)
        self.logger.info("Initializing Game Engine")
        
        # Game state
        self.state = self.STATE_MENU
        self.prev_state = None
        self.paused = False
        
        # Game variables
        self.score = 0
        self.level = 1
        self.targets_captured = 0
        self.levels_completed = 0
        self.game_time = 0
        self.difficulty = "medium"
        
        # UI manager reference (will be set later)
        self.ui_manager = None
        
        # Entity containers
        self.player = None
        self.targets = []
        self.obstacles = []
        self.powerups = []
        self.active_effects = {}
        
        # Input state
        self.keys_pressed = set()
        
        # Game loop control
        self.running = False
        self.last_update_time = 0
        self.update_after_id = None
        
        # Spawn timers
        self.last_target_spawn = 0
        self.last_obstacle_spawn = 0
        self.last_powerup_spawn = 0
        
    def set_ui_manager(self, ui_manager):
        """
        Set the UI manager reference
        
        Args:
            ui_manager: UI manager instance
        """
        self.ui_manager = ui_manager
        self.logger.info("UI Manager reference set")
        
        # Register UI callbacks
        self._register_ui_callbacks()
        
    def _register_ui_callbacks(self):
        """Register callbacks for UI events"""
        if not self.ui_manager:
            return
            
        # Main menu events
        self.ui_manager.register_callback("menu_play", lambda _: self.start_game())
        self.ui_manager.register_callback("menu_settings", lambda _: self.show_settings())
        self.ui_manager.register_callback("menu_help", lambda _: self.show_help())
        self.ui_manager.register_callback("menu_quit", lambda _: self.root.quit())
        
        # Settings events
        self.ui_manager.register_callback("settings_saved", self._on_settings_saved)
        
        # Pause menu events
        self.ui_manager.register_callback("pause_resume", lambda _: self.resume_game())
        self.ui_manager.register_callback("pause_settings", lambda _: self.show_settings())
        self.ui_manager.register_callback("pause_quit", lambda _: self.quit_to_menu())
        
        # Level complete events
        self.ui_manager.register_callback("level_continue", lambda _: self.start_next_level())
        
        # Game over events
        self.ui_manager.register_callback("gameover_retry", lambda _: self.start_game())
        self.ui_manager.register_callback("gameover_menu", lambda _: self.quit_to_menu())
        
    def show_main_menu(self):
        """Show the main menu"""
        self.state = self.STATE_MENU
        
        # Create UI if not already created
        if self.ui_manager and "main_menu" not in self.ui_manager.windows:
            self.ui_manager.create_main_menu()
            self.ui_manager.create_settings_menu()
            self.ui_manager.create_help_menu()
        else:
            # Show existing menu
            self.ui_manager.show_window("main_menu")
            
        self.logger.info("Main menu displayed")
        
    def show_settings(self):
        """Show the settings menu"""
        # Create if not exists
        if self.ui_manager and "settings_menu" not in self.ui_manager.windows:
            self.ui_manager.create_settings_menu()
            
        # Show window
        self.ui_manager.show_window("settings_menu")
        
    def show_help(self):
        """Show the help menu"""
        # Create if not exists
        if self.ui_manager and "help_menu" not in self.ui_manager.windows:
            self.ui_manager.create_help_menu()
            
        # Show window
        self.ui_manager.show_window("help_menu")
        
    def _on_settings_saved(self, settings):
        """
        Handle settings saved event
        
        Args:
            settings: Dictionary of game settings
        """
        self.logger.info("Settings saved", settings)
        
        # Update game settings
        self.difficulty = settings.get("difficulty", "medium")
        
        # Save settings to config
        try:
            save_settings(settings)
        except Exception as e:
            self.logger.exception("Error saving settings", e)
            
    def start_game(self):
        """Start a new game"""
        self.logger.info("Starting new game")
        
        # Reset game state
        self.score = 0
        self.level = 1
        self.targets_captured = 0
        self.levels_completed = 0
        self.game_time = 0
        self.active_effects = {}
        
        # Close any open windows
        if self.ui_manager:
            for name in list(self.ui_manager.windows.keys()):
                self.ui_manager.close_window(name)
                
        # Set game state
        self.state = self.STATE_PLAYING
        self.paused = False
        
        # Initialize game elements
        # For now, just stub these out since we haven't implemented entity classes yet
        self._initialize_game_elements()
        
        # Start game loop
        self.running = True
        self.last_update_time = time.time()
        self._game_loop()
        
    def _initialize_game_elements(self):
        """Initialize game elements for a new game or level"""
        # Initialize HUD
        self.hud_elements = self.ui_manager.create_game_hud(self.root)
        
        # Initialize pause menu
        self.pause_elements = self.ui_manager.create_pause_menu(self.root)
        self.ui_manager.hide_pause_menu(self.pause_elements)
        
        # Initialize level complete screen
        self.level_complete_elements = self.ui_manager.create_level_complete_screen(self.root)
        
        # Initialize game over screen
        self.game_over_elements = self.ui_manager.create_game_over_screen(self.root)
        
        # Reset entity lists
        self.targets = []
        self.obstacles = []
        self.powerups = []
        
        # Create player (placeholder for now)
        # self.player = PlayerEntity()
        
        # Schedule first spawns
        self.last_target_spawn = 0
        self.last_obstacle_spawn = 0
        self.last_powerup_spawn = 0
        
    def pause_game(self):
        """Pause the game"""
        if self.state != self.STATE_PLAYING or self.paused:
            return
            
        self.logger.info("Game paused")
        self.paused = True
        self.prev_state = self.state
        self.state = self.STATE_PAUSED
        
        # Show pause menu
        self.ui_manager.show_pause_menu(self.pause_elements)
        
    def resume_game(self):
        """Resume the game from pause"""
        if self.state != self.STATE_PAUSED:
            return
            
        self.logger.info("Game resumed")
        self.paused = False
        self.state = self.prev_state
        self.prev_state = None
        
        # Hide pause menu
        self.ui_manager.hide_pause_menu(self.pause_elements)
        
        # Reset last update time to prevent big delta time
        self.last_update_time = time.time()
        
    def quit_to_menu(self):
        """Quit current game and return to main menu"""
        self.logger.info("Quitting to main menu")
        
        # Stop game loop
        self.running = False
        if self.update_after_id:
            self.root.after_cancel(self.update_after_id)
            self.update_after_id = None
            
        # Close any open windows
        if self.ui_manager:
            for name in list(self.ui_manager.windows.keys()):
                self.ui_manager.close_window(name)
                
        # Show main menu
        self.show_main_menu()
        
    def complete_level(self):
        """Complete the current level"""
        self.logger.info(f"Level {self.level} completed")
        
        # Update state
        self.prev_state = self.state
        self.state = self.STATE_LEVEL_COMPLETE
        
        # Increment levels completed
        self.levels_completed += 1
        
        # Show level complete screen
        self.ui_manager.show_level_complete(
            self.level_complete_elements,
            self.level,
            self.score,
            self.targets_captured
        )
        
    def start_next_level(self):
        """Start the next level"""
        # Increment level
        self.level += 1
        self.logger.info(f"Starting level {self.level}")
        
        # Reset level-specific counters
        self.targets_captured = 0
        
        # Hide level complete screen
        self.ui_manager.hide_level_complete(self.level_complete_elements)
        
        # Update state
        self.state = self.STATE_PLAYING
        
        # Reset entity lists and spawns
        self.targets = []
        self.obstacles = []
        self.powerups = []
        self.last_target_spawn = 0
        self.last_obstacle_spawn = 0
        self.last_powerup_spawn = 0
        
        # Reset last update time
        self.last_update_time = time.time()
        
    def game_over(self):
        """Handle game over"""
        self.logger.info("Game over")
        
        # Update state
        self.prev_state = self.state
        self.state = self.STATE_GAME_OVER
        
        # Show game over screen
        self.ui_manager.show_game_over(
            self.game_over_elements,
            self.score,
            self.levels_completed
        )
        
    def _game_loop(self):
        """Main game loop"""
        if not self.running:
            return
            
        # Get current time and calculate delta time
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update game
        if not self.paused and self.state == self.STATE_PLAYING:
            self._update(delta_time)
            
        # Schedule next update - target 60 FPS
        self.update_after_id = self.root.after(16, self._game_loop)
        
    def _update(self, delta_time):
        """
        Update game state
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        self.logger.debug(f"Game update", {"delta_time": f"{delta_time:.4f}"})
        
        # Update game time
        self.game_time += delta_time
        
        # Update entities
        self._update_entities(delta_time)
        
        # Check for spawns
        self._check_spawns()
        
        # Check collisions
        self._check_collisions()
        
        # Update effects
        self._update_effects(delta_time)
        
        # Update HUD
        self._update_hud()
        
        # Check for level completion
        self._check_level_completion()
        
    def _update_entities(self, delta_time):
        """
        Update all game entities
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Update player
        if self.player:
            self.player.update(delta_time)
            
        # Update targets
        for target in self.targets[:]:  # Use copy to allow safe removal
            target.update(delta_time)
            
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(delta_time)
            
        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update(delta_time)
            
    def _check_spawns(self):
        """Check and perform entity spawns"""
        current_time = time.time()
        
        # Check target spawn
        if (current_time - self.last_target_spawn >= TARGET_SPAWN_INTERVAL and
                len(self.targets) < MAX_TARGETS):
            self._spawn_target()
            self.last_target_spawn = current_time
            
        # Check obstacle spawn (not in first level)
        if (self.level > 1 and
                current_time - self.last_obstacle_spawn >= OBSTACLE_SPAWN_INTERVAL and
                len(self.obstacles) < MAX_OBSTACLES):
            self._spawn_obstacle()
            self.last_obstacle_spawn = current_time
            
        # Check powerup spawn (random chance)
        if (current_time - self.last_powerup_spawn >= POWERUP_SPAWN_INTERVAL and
                len(self.powerups) < MAX_POWERUPS and
                random.random() < POWERUP_SPAWN_CHANCE):
            self._spawn_powerup()
            self.last_powerup_spawn = current_time
            
    def _spawn_target(self):
        """Spawn a new target entity"""
        # Placeholder - this would actually create a new target entity
        self.logger.debug("Spawning target")
        # self.targets.append(TargetEntity())
        
    def _spawn_obstacle(self):
        """Spawn a new obstacle entity"""
        # Placeholder
        self.logger.debug("Spawning obstacle")
        # self.obstacles.append(ObstacleEntity())
        
    def _spawn_powerup(self):
        """Spawn a new powerup entity"""
        # Placeholder
        self.logger.debug("Spawning powerup")
        # self.powerups.append(PowerupEntity())
        
    def _check_collisions(self):
        """Check for collisions between entities"""
        if not self.player:
            return
            
        # Check collisions with targets
        for target in self.targets[:]:  # Use copy to allow safe removal
            if self._check_collision(self.player, target):
                self._handle_target_collision(target)
                
        # Check collisions with obstacles
        for obstacle in self.obstacles[:]:
            if self._check_collision(self.player, obstacle):
                self._handle_obstacle_collision(obstacle)
                
        # Check collisions with powerups
        for powerup in self.powerups[:]:
            if self._check_collision(self.player, powerup):
                self._handle_powerup_collision(powerup)
                
    def _check_collision(self, entity1, entity2):
        """
        Check if two entities are colliding
        
        Args:
            entity1: First entity
            entity2: Second entity
            
        Returns:
            True if entities are colliding, False otherwise
        """
        # Placeholder - would implement collision detection
        return False
        
    def _handle_target_collision(self, target):
        """
        Handle collision with a target
        
        Args:
            target: Target entity that was hit
        """
        # Get points for target
        points = 10  # Default, would get from target
        
        # Update score
        self.score += points
        
        # Update targets captured
        self.targets_captured += 1
        
        # Remove target
        self.targets.remove(target)
        
        self.logger.debug(f"Target hit", {"points": points, "score": self.score})
        
    def _handle_obstacle_collision(self, obstacle):
        """
        Handle collision with an obstacle
        
        Args:
            obstacle: Obstacle entity that was hit
        """
        # Apply obstacle effect
        effect = "none"  # Would get from obstacle
        
        if effect == "block":
            # Push player back
            pass
        elif effect == "freeze":
            # Freeze player temporarily
            pass
            
        self.logger.debug(f"Obstacle hit", {"effect": effect})
        
    def _handle_powerup_collision(self, powerup):
        """
        Handle collision with a powerup
        
        Args:
            powerup: Powerup entity that was hit
        """
        # Apply powerup effect
        powerup_type = "speed"  # Would get from powerup
        duration = 5.0  # Would get from powerup
        
        # Add to active effects
        self.active_effects[powerup_type] = {
            "remaining": duration,
            "params": {}  # Would get from powerup
        }
        
        # Remove powerup
        self.powerups.remove(powerup)
        
        self.logger.debug(f"Powerup collected", {"type": powerup_type, "duration": duration})
        
    def _update_effects(self, delta_time):
        """
        Update active effects and durations
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Update effect timers
        for effect_type in list(self.active_effects.keys()):
            effect = self.active_effects[effect_type]
            effect["remaining"] -= delta_time
            
            # Remove expired effects
            if effect["remaining"] <= 0:
                del self.active_effects[effect_type]
                self.logger.debug(f"Effect expired", {"type": effect_type})
                
    def _update_hud(self):
        """Update the HUD display"""
        if not hasattr(self, 'hud_elements'):
            return
            
        # Get active effect names
        active_effect_names = list(self.active_effects.keys())
        
        # Update HUD
        self.ui_manager.update_hud(
            self.hud_elements,
            self.score,
            self.level,
            active_effect_names
        )
        
    def _check_level_completion(self):
        """Check if the current level is completed"""
        # Get target score for this level
        target_score = get_level_target_score(self.level, self.difficulty)
        
        # Check if score meets or exceeds target
        if self.score >= target_score:
            self.complete_level()
            
    def handle_key_press(self, event):
        """
        Handle key press event
        
        Args:
            event: Tkinter event object
        """
        key = event.keysym.lower()
        self.keys_pressed.add(key)
        
        # Handle special keys
        if key == "escape":
            if self.state == self.STATE_PLAYING and not self.paused:
                self.pause_game()
            elif self.state == self.STATE_PAUSED:
                self.resume_game()
                
        elif key == "space":
            # Use special ability if available
            pass
            
    def handle_key_release(self, event):
        """
        Handle key release event
        
        Args:
            event: Tkinter event object
        """
        key = event.keysym.lower()
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
            
    def shutdown(self):
        """Shut down the game engine"""
        self.logger.info("Shutting down game engine")
        
        # Stop game loop
        self.running = False
        if self.update_after_id:
            self.root.after_cancel(self.update_after_id)
            self.update_after_id = None