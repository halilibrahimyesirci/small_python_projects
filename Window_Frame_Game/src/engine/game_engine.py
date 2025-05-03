import tkinter as tk
import random
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable

sys.path.append("../../config")
try:
    from config.game_config import *
except ImportError:
    try:
        from Window_Frame_Game.config.game_config import *
    except ImportError:
        print("Warning: Could not import game_config, using fallback values")
        
from ..utils.logger import Logger

class GameEngine:
    
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_LEVEL_COMPLETE = "level_complete"
    STATE_GAME_OVER = "game_over"
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.logger = Logger("GameEngine", log_level=Logger.INFO)
        self.logger.info("Initializing Game Engine")
        
        self.state = self.STATE_MENU
        self.prev_state = None
        self.paused = False
        
        self.score = 0
        self.level = 1
        self.targets_captured = 0
        self.levels_completed = 0
        self.game_time = 0
        self.difficulty = "medium"
        
        self.ui_manager = None
        
        self.player = None
        self.targets = []
        self.obstacles = []
        self.powerups = []
        self.active_effects = {}
        
        self.keys_pressed = set()
        
        self.running = False
        self.last_update_time = 0
        self.update_after_id = None
        
        self.last_target_spawn = 0
        self.last_obstacle_spawn = 0
        self.last_powerup_spawn = 0
        
    def set_ui_manager(self, ui_manager):
        self.ui_manager = ui_manager
        self.logger.info("UI Manager reference set")
        
        self._register_ui_callbacks()
        
    def _register_ui_callbacks(self):
        if not self.ui_manager:
            return
            
        self.ui_manager.register_callback("menu_play", lambda _: self.start_game())
        self.ui_manager.register_callback("menu_settings", lambda _: self.show_settings())
        self.ui_manager.register_callback("menu_help", lambda _: self.show_help())
        self.ui_manager.register_callback("menu_quit", lambda _: self.root.quit())
        
        self.ui_manager.register_callback("settings_saved", self._on_settings_saved)
        
        self.ui_manager.register_callback("pause_resume", lambda _: self.resume_game())
        self.ui_manager.register_callback("pause_settings", lambda _: self.show_settings())
        self.ui_manager.register_callback("pause_quit", lambda _: self.quit_to_menu())
        
        self.ui_manager.register_callback("level_continue", lambda _: self.start_next_level())
        
        self.ui_manager.register_callback("gameover_retry", lambda _: self.start_game())
        self.ui_manager.register_callback("gameover_menu", lambda _: self.quit_to_menu())
        
    def show_main_menu(self):
        self.state = self.STATE_MENU
        
        if self.ui_manager and "main_menu" not in self.ui_manager.windows:
            self.ui_manager.create_main_menu()
            self.ui_manager.create_settings_menu()
            self.ui_manager.create_help_menu()
        else:
            self.ui_manager.show_window("main_menu")
            
        self.logger.info("Main menu displayed")
        
    def show_settings(self):
        if self.ui_manager and "settings_menu" not in self.ui_manager.windows:
            self.ui_manager.create_settings_menu()
            
        self.ui_manager.show_window("settings_menu")
        
    def show_help(self):
        if self.ui_manager and "help_menu" not in self.ui_manager.windows:
            self.ui_manager.create_help_menu()
            
        self.ui_manager.show_window("help_menu")
        
    def _on_settings_saved(self, settings):
        self.logger.info("Settings saved", settings)
        
        self.difficulty = settings.get("difficulty", "medium")
        
        try:
            save_settings(settings)
        except Exception as e:
            self.logger.exception("Error saving settings", e)
            
    def start_game(self):
        self.logger.info("Starting new game")
        
        self.score = 0
        self.level = 1
        self.targets_captured = 0
        self.levels_completed = 0
        self.game_time = 0
        self.active_effects = {}
        
        if self.ui_manager:
            for name in list(self.ui_manager.windows.keys()):
                self.ui_manager.close_window(name)
                
        self.state = self.STATE_PLAYING
        self.paused = False
        
        self._initialize_game_elements()
        
        self.running = True
        self.last_update_time = time.time()
        self._game_loop()
        
    def _initialize_game_elements(self):
        self.hud_elements = self.ui_manager.create_game_hud(self.root)
        
        self.pause_elements = self.ui_manager.create_pause_menu(self.root)
        self.ui_manager.hide_pause_menu(self.pause_elements)
        
        self.level_complete_elements = self.ui_manager.create_level_complete_screen(self.root)
        
        self.game_over_elements = self.ui_manager.create_game_over_screen(self.root)
        
        self.targets = []
        self.obstacles = []
        self.powerups = []
        
        from ..entities.player import PlayerEntity
        
        player_health = DIFFICULTY_LEVELS[self.difficulty]["player_health"]
        self.player = PlayerEntity(health=player_health, parent=self.root)
        
        self.last_target_spawn = 0
        self.last_obstacle_spawn = 0
        self.last_powerup_spawn = 0
        
    def pause_game(self):
        if self.state != self.STATE_PLAYING or self.paused:
            return
            
        self.logger.info("Game paused")
        self.paused = True
        self.prev_state = self.state
        self.state = self.STATE_PAUSED
        
        self.ui_manager.show_pause_menu(self.pause_elements)
        
    def resume_game(self):
        if self.state != self.STATE_PAUSED:
            return
            
        self.logger.info("Game resumed")
        self.paused = False
        self.state = self.prev_state
        self.prev_state = None
        
        self.ui_manager.hide_pause_menu(self.pause_elements)
        
        self.last_update_time = time.time()
        
    def quit_to_menu(self):
        self.logger.info("Quitting to main menu")
        
        self.running = False
        if self.update_after_id:
            self.root.after_cancel(self.update_after_id)
            self.update_after_id = None
            
        if self.ui_manager:
            for name in list(self.ui_manager.windows.keys()):
                self.ui_manager.close_window(name)
                
        self.show_main_menu()
        
    def complete_level(self):
        self.logger.info(f"Level {self.level} completed")
        
        self.prev_state = self.state
        self.state = self.STATE_LEVEL_COMPLETE
        
        self.levels_completed += 1
        
        self.ui_manager.show_level_complete(
            self.level_complete_elements,
            self.level,
            self.score,
            self.targets_captured
        )
        
    def start_next_level(self):
        self.level += 1
        self.logger.info(f"Starting level {self.level}")
        
        self.targets_captured = 0
        
        self.ui_manager.hide_level_complete(self.level_complete_elements)
        
        self.state = self.STATE_PLAYING
        
        self.targets = []
        self.obstacles = []
        self.powerups = []
        self.last_target_spawn = 0
        self.last_obstacle_spawn = 0
        self.last_powerup_spawn = 0
        
        self.last_update_time = time.time()
        
    def game_over(self):
        self.logger.info("Game over")
        
        self.prev_state = self.state
        self.state = self.STATE_GAME_OVER
        
        self.ui_manager.show_game_over(
            self.game_over_elements,
            self.score,
            self.levels_completed
        )
        
    def _game_loop(self):
        if not self.running:
            return
            
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        if not self.paused and self.state == self.STATE_PLAYING:
            self._update(delta_time)
            
        self.update_after_id = self.root.after(16, self._game_loop)
        
    def _update(self, delta_time):
        self.logger.debug(f"Game update", {"delta_time": f"{delta_time:.4f}"})
        
        self.game_time += delta_time
        
        self._update_entities(delta_time)
        
        self._check_spawns()
        
        self._check_collisions()
        
        self._update_effects(delta_time)
        
        self._update_hud()
        
        self._check_level_completion()
        
    def _update_entities(self, delta_time):
        if self.player:
            self.player.update(delta_time)
            
        for target in self.targets[:]:
            target.update(delta_time)
            
        for obstacle in self.obstacles[:]:
            obstacle.update(delta_time)
            
        for powerup in self.powerups[:]:
            powerup.update(delta_time)
            
    def _check_spawns(self):
        current_time = time.time()
        
        if (current_time - self.last_target_spawn >= TARGET_SPAWN_INTERVAL and
                len(self.targets) < MAX_TARGETS):
            self._spawn_target()
            self.last_target_spawn = current_time
            
        if (self.level > 1 and
                current_time - self.last_obstacle_spawn >= OBSTACLE_SPAWN_INTERVAL and
                len(self.obstacles) < MAX_OBSTACLES):
            self._spawn_obstacle()
            self.last_obstacle_spawn = current_time
            
        if (current_time - self.last_powerup_spawn >= POWERUP_SPAWN_INTERVAL and
                len(self.powerups) < MAX_POWERUPS and
                random.random() < POWERUP_SPAWN_CHANCE):
            self._spawn_powerup()
            self.last_powerup_spawn = current_time
            
    def _spawn_target(self):
        try:
            from ..entities.target import TargetEntity
            
            spawn_chances = get_spawn_chances(self.level)
            target_chances = spawn_chances["targets"]
            
            target_types = ["standard", "moving", "evasive", "boss"]
            
            r = random.random()
            cumulative_prob = 0
            selected_type = "standard"
            
            for i, prob in enumerate(target_chances):
                cumulative_prob += prob
                if r <= cumulative_prob:
                    selected_type = target_types[i]
                    break
            
            player_pos = self.player.get_position() if self.player else (0, 0)
            player_size = self.player.get_size() if self.player else (0, 0)
            
            safe_distance = 200
            
            max_attempts = 10
            for _ in range(max_attempts):
                x = random.randint(0, SCREEN_WIDTH - TARGET_WINDOW_SIZE[0])
                y = random.randint(0, SCREEN_HEIGHT - TARGET_WINDOW_SIZE[1])
                
                dx = x - player_pos[0]
                dy = y - player_pos[1]
                distance = (dx*dx + dy*dy) ** 0.5
                
                if distance >= safe_distance:
                    break
            
            target = TargetEntity(
                target_type=selected_type,
                level=self.level,
                difficulty=self.difficulty,
                parent=self.root
            )
            
            target.set_position(x, y)
            
            self.targets.append(target)
            
            self.logger.debug(f"Target spawned", {
                "type": selected_type,
                "position": (x, y)
            })
            
        except Exception as e:
            self.logger.exception("Error spawning target", e)
            from ..entities.base_entity import BaseEntity
            
            target = BaseEntity(
                entity_type="target",
                title="Target",
                size=TARGET_WINDOW_SIZE,
                color=random.choice(TARGET_WINDOW_COLORS),
                shape="rectangle",
                parent=self.root
            )
            
            x = random.randint(0, SCREEN_WIDTH - TARGET_WINDOW_SIZE[0])
            y = random.randint(0, SCREEN_HEIGHT - TARGET_WINDOW_SIZE[1])
            target.set_position(x, y)
            
            self.targets.append(target)
            
            self.logger.debug("Created fallback target")
        
    def _spawn_obstacle(self):
        self.logger.debug("Spawning obstacle")
        
    def _spawn_powerup(self):
        self.logger.debug("Spawning powerup")
        
    def _check_collisions(self):
        if not self.player:
            return
            
        for target in self.targets[:]:
            if self._check_collision(self.player, target):
                self._handle_target_collision(target)
                
        for obstacle in self.obstacles[:]:
            if self._check_collision(self.player, obstacle):
                self._handle_obstacle_collision(obstacle)
                
        for powerup in self.powerups[:]:
            if self._check_collision(self.player, powerup):
                self._handle_powerup_collision(powerup)
                
    def _check_collision(self, entity1, entity2):
        pos1 = entity1.get_position()
        size1 = entity1.get_size()
        pos2 = entity2.get_position()
        size2 = entity2.get_size()
        
        rect1 = (pos1[0], pos1[1], pos1[0] + size1[0], pos1[1] + size1[1])
        rect2 = (pos2[0], pos2[1], pos2[0] + size2[0], pos2[1] + size2[1])
        
        if (rect1[0] < rect2[2] and rect1[2] > rect2[0] and
            rect1[1] < rect2[3] and rect1[3] > rect2[1]):
            return True
            
        return False
        
    def _handle_target_collision(self, target):
        points = 10
        
        self.score += points
        
        self.targets_captured += 1
        
        self.targets.remove(target)
        
        self.logger.debug(f"Target hit", {"points": points, "score": self.score})
        
    def _handle_obstacle_collision(self, obstacle):
        effect = "none"
        
        if effect == "block":
            pass
        elif effect == "freeze":
            pass
            
        self.logger.debug(f"Obstacle hit", {"effect": effect})
        
    def _handle_powerup_collision(self, powerup):
        powerup_type = "speed"
        duration = 5.0
        
        self.active_effects[powerup_type] = {
            "remaining": duration,
            "params": {}
        }
        
        self.powerups.remove(powerup)
        
        self.logger.debug(f"Powerup collected", {"type": powerup_type, "duration": duration})
        
    def _update_effects(self, delta_time):
        for effect_type in list(self.active_effects.keys()):
            effect = self.active_effects[effect_type]
            effect["remaining"] -= delta_time
            
            if effect["remaining"] <= 0:
                del self.active_effects[effect_type]
                self.logger.debug(f"Effect expired", {"type": effect_type})
                
    def _update_hud(self):
        if not hasattr(self, 'hud_elements'):
            return
            
        active_effect_names = list(self.active_effects.keys())
        
        self.ui_manager.update_hud(
            self.hud_elements,
            self.score,
            self.level,
            active_effect_names
        )
        
    def _check_level_completion(self):
        target_score = get_level_target_score(self.level, self.difficulty)
        
        if self.score >= target_score:
            self.complete_level()
            
    def handle_key_press(self, event):
        key = event.keysym.lower()
        self.keys_pressed.add(key)
        
        if key == "escape":
            if self.state == self.STATE_PLAYING and not self.paused:
                self.pause_game()
            elif self.state == self.STATE_PAUSED:
                self.resume_game()
                
        elif key == "space":
            pass
            
    def handle_key_release(self, event):
        key = event.keysym.lower()
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
            
    def shutdown(self):
        self.logger.info("Shutting down game engine")
        
        self.running = False
        if self.update_after_id:
            self.root.after_cancel(self.update_after_id)
            self.update_after_id = None