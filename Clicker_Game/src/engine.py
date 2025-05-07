import pygame
import sys
import time
import random
import logging
import os
import math
from src.entities.coin import Coin
from src.utils.ui_layout import UILayout, safe_label, safe_button_layout
from src.game_states import (
    STATE_MENU, STATE_PLAYING, STATE_GAME_OVER_WIN, STATE_GAME_OVER_LOSE, 
    STATE_UPGRADE, STATE_PAUSE, STATE_SETTINGS, STATE_ABILITY_SELECT,
    STATE_ESC_MENU, STATE_SHOP,
    update_menu, render_menu,
    update_playing, render_playing,
    update_settings, render_settings,
    update_upgrade, render_upgrade,
    update_ability_select, render_ability_select,
    update_esc_menu, render_esc_menu,
    update_shop, render_shop
)

# State transition duration in seconds
TRANSITION_DURATION = 0.3

# Click delay in seconds
CLICK_DELAY = 0.45  # Increased for V0.3.3 (was 0.15)

logger = logging.getLogger(__name__)

class GameEngine:
    """Core game engine handling main loop and game state"""
    
    def __init__(self, resource_manager, player, level_manager, shop_manager=None):
        self.resource_manager = resource_manager
        self.player = player
        self.level_manager = level_manager
        self.shop_manager = shop_manager
        
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Get screen dimensions from config
        self.width = self.resource_manager.get_config_value("screen", "width") or 800
        self.height = self.resource_manager.get_config_value("screen", "height") or 600
        self.fps = self.resource_manager.get_config_value("screen", "fps") or 60
        
        # Create screen and clock
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("RPG Clicker V0.3.4")
        self.clock = pygame.time.Clock()
        
        # ESC key tracking
        self.last_esc_press = 0  # Initialize the last_esc_press attribute to track ESC key timing
        
        # Create fonts
        self.fonts = {
            "large": pygame.font.SysFont(None, 50),
            "medium": pygame.font.SysFont(None, 30),
            "small": pygame.font.SysFont(None, 20)
        }
        
        # Colors
        self.colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 100, 255),
            "yellow": (255, 255, 0),  # Make sure yellow is defined for critical hits
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "gold": (255, 215, 0),
            "button": {
                "normal": (100, 100, 255),
                "hover": (150, 150, 255),
                "clicked": (200, 200, 255)
            },
            "boss": (255, 50, 50),
            "combo": [(100, 100, 255), (150, 150, 255), (200, 200, 255), (255, 255, 100)]
        }
        
        # Game variables
        self.running = True
        self.game_state = STATE_MENU
        self.previous_state = None
        self.clicks = 0
        self.start_ticks = 0
        self.current_time = 0
        self.debug_mode = False
        self.last_click_time = 0  # Track time of last click for click delay
        self.coins = []  # Store falling coins
        self.coin_spawn_timer = 0
        self.coin_spawn_rate = 3  # Coins per second
        self.coin_counter = 0  # Money earned from coins
        
        
        
        # Player ability variables
        self.player_abilities = {
            "rapid_clicking": {"active": False, "duration": 0, "cooldown": 0, "description": "Click rapidly without delay"},
            "auto_clicker": {"active": False, "duration": 0, "cooldown": 0, "description": "Automatic clicking for a duration"},
            "double_coins": {"active": False, "duration": 0, "cooldown": 0, "description": "Coins give double value"},
            "coin_magnet": {"active": False, "duration": 0, "cooldown": 0, "description": "Attract coins from longer distance"},
            "crit_master": {"active": False, "duration": 0, "cooldown": 0, "description": "Increased critical chance"},
            "boss_weakener": {"active": False, "duration": 0, "cooldown": 0, "description": "Boss takes more damage"}
        }
        self.active_abilities = []  # List of currently active special abilities
        
        # Audio settings
        self.audio_settings = {
            "sound_volume": 0.7,  # 0.0 to 1.0
            "music_volume": 0.5,  # 0.0 to 1.0
            "current_music": "mid.mp3"  # default track
        }
        
        # FPS monitoring
        self.fps_history = []
        self.fps_history_max_size = 60  # Track FPS over 60 frames
        
        # State transition variables
        self.transitioning = False
        self.transition_start_time = 0
        self.transition_progress = 0
        self.transition_from_state = None
        self.transition_to_state = None
        self.transition_surface = None
        
        # Load resources
        self._load_resources()
        
        # Create level
        self.current_level = None
        if self.level_manager:
            self.current_level = self.level_manager.create_level(self.player.level)
        
        # UI initialization will be done in the respective state functions
        self.ui_elements = {}
        self._init_ui()
        
        # Create transition surface
        self.transition_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Apply initial audio settings
        self._apply_audio_settings()
        
        logger.info("Game engine initialized")
        
    def _load_resources(self):
        """Load game resources"""
        # Try to load background
        bg_path = os.path.join("assets", "images", "background.png")
        self.resource_manager.load_image("background", bg_path, (self.width, self.height))
        
        # Try to load button
        button_path = os.path.join("assets", "images", "button.png")
        self.resource_manager.load_image("button", button_path, (200, 100))
        
        # Try to load sounds
        click_sound_path = os.path.join("assets", "sounds", "click.wav")
        self.resource_manager.load_sound("click", click_sound_path)
        
        critical_sound_path = os.path.join("assets", "sounds", "critical.wav")
        self.resource_manager.load_sound("critical", critical_sound_path)
        
        level_up_path = os.path.join("assets", "sounds", "level_up.wav")
        self.resource_manager.load_sound("level_up", level_up_path)
        
        # Try to load music - using existing music files instead of missing ones
        menu_music_path = os.path.join("assets", "music", "best_one.mp3")  # Use best_one.mp3 for menu
        self.resource_manager.load_music("menu", menu_music_path)
        
        gameplay_music_path = os.path.join("assets", "music", "mid.mp3")  # Use mid.mp3 for gameplay
        self.resource_manager.load_music("gameplay", gameplay_music_path)
        
        boss_music_path = os.path.join("assets", "music", "mhysteric_type.mp3")  # Use mhysteric_type.mp3 for boss
        self.resource_manager.load_music("boss", boss_music_path)
        
    def _init_ui(self):
        """Initialize UI elements"""
        from src.ui import Button, ProgressBar, ComboMeter, ParticleSystem, Slider
        
        # Create UI containers for each state
        self.ui_elements = {
            STATE_MENU: {},
            STATE_PLAYING: {},
            STATE_GAME_OVER_WIN: {},
            STATE_GAME_OVER_LOSE: {},
            STATE_UPGRADE: {},
            STATE_PAUSE: {},
            STATE_SETTINGS: {},
            STATE_ABILITY_SELECT: {},
            STATE_ESC_MENU: {},
            STATE_SHOP: {}
        }
        
        # Menu UI - Adjusted for better layout
        play_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 - 30, 200, 50)
        self.ui_elements[STATE_MENU]["play_button"] = Button(
            play_button_rect,
            "Play",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        
        # Add settings button to menu
        settings_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 + 40, 200, 50)
        self.ui_elements[STATE_MENU]["settings_button"] = Button(
            settings_button_rect,
            "Settings",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        
        # Playing UI
        click_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 - 50, 200, 100)
        self.ui_elements[STATE_PLAYING]["click_button"] = Button(
            click_button_rect,
            "Click Me!",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        
        # Progress bar for clicks
        progress_rect = pygame.Rect(50, self.height - 40, self.width - 100, 20)
        self.ui_elements[STATE_PLAYING]["progress_bar"] = ProgressBar(
            progress_rect,
            (50, 50, 50),
            self.colors["green"],
            border_color=self.colors["white"],
            border_width=2
        )
        
        # Combo meter
        combo_rect = pygame.Rect(self.width // 2 - 100, 80, 200, 30)
        self.ui_elements[STATE_PLAYING]["combo_meter"] = ComboMeter(
            combo_rect,
            self.colors["combo"],
            self.fonts["medium"],
            decay_rate=0.5
        )
        
        # Particle system
        self.ui_elements[STATE_PLAYING]["particles"] = ParticleSystem()
        
        # Game over (win) UI
        continue_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 + 150, 200, 50)
        self.ui_elements[STATE_GAME_OVER_WIN]["continue_button"] = Button(
            continue_button_rect,
            "Continue",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["green"]
        )
        
        # Game over (lose) UI
        restart_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 + 150, 200, 50)
        self.ui_elements[STATE_GAME_OVER_LOSE]["restart_button"] = Button(
            restart_button_rect,
            "Restart",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["red"]
        )
        
        # Upgrade UI - Improved layout with larger buttons
        btn_width, btn_height = 180, 50
        padding = 40
        start_y = self.height // 2 - 100
        
        # Click power upgrade button - Top left
        click_power_rect = pygame.Rect(
            self.width // 2 - btn_width - padding,
            start_y,
            btn_width,
            btn_height
        )
        self.ui_elements[STATE_UPGRADE]["click_power_button"] = Button(
            click_power_rect,
            "Click Power",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["blue"]
        )
        
        # Critical chance upgrade button - Top right
        crit_chance_rect = pygame.Rect(
            self.width // 2 + padding,
            start_y,
            btn_width,
            btn_height
        )
        self.ui_elements[STATE_UPGRADE]["crit_chance_button"] = Button(
            crit_chance_rect,
            "Crit Chance",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["blue"]
        )
        
        # Critical multiplier upgrade button - Bottom left
        crit_mult_rect = pygame.Rect(
            self.width // 2 - btn_width - padding,
            start_y + btn_height + padding,
            btn_width,
            btn_height
        )
        self.ui_elements[STATE_UPGRADE]["crit_mult_button"] = Button(
            crit_mult_rect,
            "Crit Multiplier",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["blue"]
        )
        
        # Coin upgrade button - Bottom right
        coin_upgrade_rect = pygame.Rect(
            self.width // 2 + padding,
            start_y + btn_height + padding,
            btn_width,
            btn_height
        )
        self.ui_elements[STATE_UPGRADE]["coin_upgrade_button"] = Button(
            coin_upgrade_rect,
            "Coin Drop",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["gold"]
        )
        
        # Continue button (after upgrades) - Moved lower to avoid overlap
        upgrade_continue_rect = pygame.Rect(
            self.width // 2 - 100,
            start_y + (btn_height + padding) * 3,
            200,
            btn_height
        )
        self.ui_elements[STATE_UPGRADE]["continue_button"] = Button(
            upgrade_continue_rect,
            "Continue",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["green"]
        )
        
        # Pause UI
        resume_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 - 80, 200, 50)
        self.ui_elements[STATE_PAUSE]["resume_button"] = Button(
            resume_button_rect,
            "Resume",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        
        settings_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2, 200, 50)
        self.ui_elements[STATE_PAUSE]["settings_button"] = Button(
            settings_button_rect,
            "Settings",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        
        quit_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 + 80, 200, 50)
        self.ui_elements[STATE_PAUSE]["quit_button"] = Button(
            quit_button_rect,
            "Quit",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["red"]
        )
        
        # Settings UI
        slider_width = 300
        slider_height = 30
        slider_x = self.width // 2 - slider_width // 2
        
        # Sound volume slider
        sound_slider_rect = pygame.Rect(slider_x, self.height // 3, slider_width, slider_height)
        self.ui_elements[STATE_SETTINGS]["sound_slider"] = Slider(
            sound_slider_rect,
            self.audio_settings["sound_volume"],
            0.0, 1.0,
            self.colors["button"]["normal"],
            self.colors["button"]["hover"],
            self.fonts["medium"],
            "Sound Volume"
        )
        
        # Music volume slider
        music_slider_rect = pygame.Rect(slider_x, self.height // 3 + 80, slider_width, slider_height)
        self.ui_elements[STATE_SETTINGS]["music_slider"] = Slider(
            music_slider_rect,
            self.audio_settings["music_volume"],
            0.0, 1.0,
            self.colors["button"]["normal"],
            self.colors["button"]["hover"],
            self.fonts["medium"],
            "Music Volume"
        )
        
        # Music selection buttons
        music_btn_width = 180
        music_btn_height = 40
        music_btn_x = self.width // 2 - music_btn_width // 2
        
        # Create music selection buttons with better spacing
        music_files = ["mid.mp3", "best_one.mp3", "energitic_stuff.mp3", 
                       "mhysteric_type.mp3", "very_energitic_stuff.mp3"]
        
        self.ui_elements[STATE_SETTINGS]["music_buttons"] = []
        
        for i, music_file in enumerate(music_files):
            music_btn_rect = pygame.Rect(
                music_btn_x,
                self.height // 3 + 150 + i * (music_btn_height + 15),
                music_btn_width,
                music_btn_height
            )
            
            # Remove .mp3 extension for display
            display_name = music_file.replace(".mp3", "")
            
            music_btn = Button(
                music_btn_rect,
                display_name,
                self.fonts["medium"],
                self.colors["button"],
                border_width=2,
                border_color=self.colors["purple"]
            )
            
            self.ui_elements[STATE_SETTINGS]["music_buttons"].append((music_file, music_btn))
        
        # Back button
        back_button_rect = pygame.Rect(
            self.width // 2 - 100,
            self.height - 80,
            200,
            50
        )
        self.ui_elements[STATE_SETTINGS]["back_button"] = Button(
            back_button_rect,
            "Back",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        
        # Ability Selection UI
        self.ui_elements[STATE_ABILITY_SELECT]["ability_buttons"] = []
        self.ui_elements[STATE_ABILITY_SELECT]["selected_abilities"] = []
        
        # ESC Menu UI - Improved layout and spacing
        btn_width, btn_height = 200, 50
        btn_spacing = 35  # Increased spacing
        start_y = self.height // 3
        
        # Resume button
        resume_rect = pygame.Rect(
            self.width // 2 - btn_width // 2,
            start_y,
            btn_width,
            btn_height
        )
        self.ui_elements[STATE_ESC_MENU]["resume_button"] = Button(
            resume_rect,
            "Resume Game",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["green"]
        )
        
        # Settings button
        settings_rect = pygame.Rect(
            self.width // 2 - btn_width // 2,
            start_y + btn_height + btn_spacing,
            btn_width,
            btn_height
        )
        self.ui_elements[STATE_ESC_MENU]["settings_button"] = Button(
            settings_rect,
            "Settings",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        
        # Shop button
        shop_rect = pygame.Rect(
            self.width // 2 - btn_width // 2,
            start_y + (btn_height + btn_spacing) * 2,
            btn_width,
            btn_height
        )
        self.ui_elements[STATE_ESC_MENU]["shop_button"] = Button(
            shop_rect,
            "Shop",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["gold"]
        )
        
        # Main menu button
        menu_rect = pygame.Rect(
            self.width // 2 - btn_width // 2,
            start_y + (btn_height + btn_spacing) * 3,
            btn_width,
            btn_height
        )
        self.ui_elements[STATE_ESC_MENU]["main_menu_button"] = Button(
            menu_rect,
            "Main Menu",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["red"]
        )
        
        # Shop UI - Improved layout
        item_width, item_height = 350, 70  # Increased height for better visibility
        item_spacing = 30
        item_start_y = self.height // 4
        item_start_x = self.width // 2 - item_width // 2
        
        self.ui_elements[STATE_SHOP]["item_buttons"] = []
        
        # Back button
        back_button_rect = pygame.Rect(
            self.width // 2 - 100,
            self.height - 80,
            200,
            50
        )
        self.ui_elements[STATE_SHOP]["back_button"] = Button(
            back_button_rect,
            "Back",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        
    def _apply_audio_settings(self):
        """Apply audio settings"""
        pygame.mixer.music.set_volume(self.audio_settings["music_volume"])
        for sound in self.resource_manager.sounds.values():
            sound.set_volume(self.audio_settings["sound_volume"])
        
    def _start_transition(self, to_state):
        """Start a transition to a new state"""
        self.transitioning = True
        self.transition_start_time = self.current_time
        self.transition_from_state = self.game_state
        self.transition_to_state = to_state
        self.transition_progress = 0
        
        # Create a screenshot of the current state to fade from
        self.transition_surface.fill((0, 0, 0, 0))
        self.transition_surface.blit(self.screen, (0, 0))
        
        # Actually change the state
        self.previous_state = self.game_state
        self.game_state = to_state
        
        logger.info(f"Transitioning from {self.transition_from_state} to {self.transition_to_state}")
        
    def _update_transition(self):
        """Update the state transition progress"""
        if not self.transitioning:
            return
            
        # Calculate progress (0 to 1)
        elapsed = self.current_time - self.transition_start_time
        self.transition_progress = min(1.0, elapsed / TRANSITION_DURATION)
        
        # Check if transition is complete
        if self.transition_progress >= 1.0:
            self.transitioning = False
            
    def _render_transition(self):
        """Render the state transition effect"""
        if not self.transitioning:
            return
            
        # Create a fade effect
        alpha = int(255 * (1.0 - self.transition_progress))
        self.transition_surface.set_alpha(alpha)
        self.screen.blit(self.transition_surface, (0, 0))
        
    def run(self):
        """Run the main game loop"""
        logger.info("Starting game loop")
        
        while self.running:
            # Get time delta
            time_delta = self.clock.tick(self.fps) / 1000.0
            self.current_time = pygame.time.get_ticks() / 1000.0
            
            # Track FPS history for performance monitoring
            current_fps = self.clock.get_fps()
            self.fps_history.append(current_fps)
            if len(self.fps_history) > self.fps_history_max_size:
                self.fps_history = self.fps_history[-self.fps_history_max_size:]
            
            # Process events
            self._process_events()
            
            # Update transition if active
            self._update_transition()
            
            # Update game state
            self._update(time_delta)
            
            # Render
            self._render()
            
            # Add transition effect if active
            self._render_transition()
            
            # Update display
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()
        
    def _process_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                # Toggle debug mode with F3
                if event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                    logger.info(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}")
                    
                if event.key == pygame.K_ESCAPE:
                    current_time = pygame.time.get_ticks()
                    
                    # Add delay check to prevent immediate toggle
                    if current_time - self.last_esc_press > 300:  # 300ms delay
                        self.last_esc_press = current_time
                        
                        if self.game_state == STATE_PLAYING:
                            self._start_transition(STATE_ESC_MENU)
                            logger.info("Game paused with ESC key")
                        elif self.game_state == STATE_ESC_MENU:
                            self._start_transition(STATE_PLAYING)
                            logger.info("Game resumed via ESC key")
                        elif self.game_state in [STATE_SETTINGS, STATE_SHOP, STATE_UPGRADE]:
                            # Return to previous state
                            previous_state = self.previous_state if self.previous_state else STATE_MENU
                            self._start_transition(previous_state)
                            logger.info(f"Returned to {previous_state} with ESC key")
                
            # Handle mouse events in state-specific update methods
                
    def _update(self, time_delta):
        """Update game logic based on current state"""
        if self.game_state == STATE_MENU:
            update_menu(self, time_delta)
        elif self.game_state == STATE_PLAYING:
            update_playing(self, time_delta)
        elif self.game_state == STATE_GAME_OVER_WIN:
            self._update_game_over_win(time_delta)
        elif self.game_state == STATE_GAME_OVER_LOSE:
            self._update_game_over_lose(time_delta)
        elif self.game_state == STATE_UPGRADE:
            update_upgrade(self, time_delta)
        elif self.game_state == STATE_PAUSE:
            self._update_pause(time_delta)
        elif self.game_state == STATE_SETTINGS:
            update_settings(self, time_delta)
        elif self.game_state == STATE_ABILITY_SELECT:
            update_ability_select(self, time_delta)
        elif self.game_state == STATE_ESC_MENU:
            update_esc_menu(self, time_delta)
        elif self.game_state == STATE_SHOP:
            update_shop(self, time_delta)
            
    def _render(self):
        """Render the current game state"""
        # Clear screen
        self.screen.fill(self.colors["black"])
        
        # Draw background if available
        if "background" in self.resource_manager.images:
            self.screen.blit(self.resource_manager.images["background"], (0, 0))
        
        # Render based on current state
        if self.game_state == STATE_MENU:
            render_menu(self)
        elif self.game_state == STATE_PLAYING:
            render_playing(self)
        elif self.game_state == STATE_GAME_OVER_WIN:
            self._render_game_over_win()
        elif self.game_state == STATE_GAME_OVER_LOSE:
            self._render_game_over_lose()
        elif self.game_state == STATE_UPGRADE:
            render_upgrade(self)
        elif self.game_state == STATE_PAUSE:
            self._render_pause()
        elif self.game_state == STATE_SETTINGS:
            render_settings(self)
        elif self.game_state == STATE_ABILITY_SELECT:
            render_ability_select(self)
        elif self.game_state == STATE_ESC_MENU:
            render_esc_menu(self)
        elif self.game_state == STATE_SHOP:
            render_shop(self)
            
        # Draw version info
        from src.ui import display_text
        display_text(
            self.screen,
            "V0.3.4",
            self.fonts["small"],
            self.colors["white"],
            self.width - 40,
            self.height - 20,
            center=False
        )
        
        # Debug info if enabled
        if self.debug_mode:
            self._render_debug_info()
            
    def _render_debug_info(self):
        """Render debug information"""
        from src.ui import display_text
        
        # Calculate average and min FPS
        avg_fps = sum(self.fps_history) / max(1, len(self.fps_history))
        min_fps = min(self.fps_history) if self.fps_history else 0
        
        debug_info = [
            f"FPS: {int(self.clock.get_fps())} (Avg: {int(avg_fps)}, Min: {int(min_fps)})",
            f"State: {self.game_state}",
            f"Level: {self.player.level}",
            f"Clicks: {self.clicks}",
            f"Target: {self.current_level.click_target if self.current_level else 'N/A'}",
            f"Click Power: {self.player.stats['click_power']['value']}",
            f"Crit Chance: {int(self.player.stats['critical_chance']['value'] * 100)}%",
            f"Crit Mult: {self.player.stats['critical_multiplier']['value']}x",
            f"Upgrade Points: {self.player.upgrade_points}",
            f"Total Clicks: {self.player.total_clicks}",
            f"Highest Level: {self.player.highest_level}",
            f"Memory: {pygame.display.get_surface().get_width() * pygame.display.get_surface().get_height() * 4 / (1024*1024):.2f} MB"
        ]
        
        # Create debug panel background
        debug_panel = pygame.Surface((300, len(debug_info) * 20 + 10), pygame.SRCALPHA)
        debug_panel.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(debug_panel, (5, 5))
        
        y = 10
        for info in debug_info:
            display_text(
                self.screen,
                info,
                self.fonts["small"],
                (255, 255, 100),
                10,
                y,
                center=False
            )
            y += 20
        
    def _update_game_over_win(self, time_delta):
        """Update game over (win) state"""
        from src.ui import display_text
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
        
        # Update player stats based on completion
        if not hasattr(self, 'win_stats_updated') or not self.win_stats_updated:
            # Update player level
            self.player.level += 1
            
            # Update highest level if needed
            if self.player.level > self.player.highest_level:
                self.player.highest_level = self.player.level
            
            # Grant upgrade points
            if self.current_level.is_boss:
                self.player.upgrade_points += 3  # More points for boss levels
            else:
                self.player.upgrade_points += 1
            
            # Save progress
            self.player.save_progress()
            
            # Flag that stats were updated
            self.win_stats_updated = True
            
            logger.info(f"Win rewards granted. Player now level {self.player.level} with {self.player.upgrade_points} upgrade points")
            
        # Update continue button
        continue_button = self.ui_elements[STATE_GAME_OVER_WIN]["continue_button"]
        if continue_button.update(mouse_pos, mouse_clicked, self.current_time):
            # Create new level for next round
            self.current_level = self.level_manager.create_level(self.player.level)
            
            # Reset win stats flag
            self.win_stats_updated = False
            
            # Transition to upgrade
            self._start_transition(STATE_UPGRADE)
            
    def _render_game_over_win(self):
        """Render game over (win) state"""
        from src.ui import display_text
        
        # Display win title
        display_text(
            self.screen,
            "Level Complete!",
            self.fonts["large"],
            self.colors["green"],
            self.width // 2,
            self.height // 3,
            center=True
        )
        
        # Display level stats
        display_text(
            self.screen,
            f"Level {self.current_level.level_number} completed with {self.clicks} clicks",
            self.fonts["medium"],
            self.colors["white"],
            self.width // 2,
            self.height // 3 + 50,
            center=True
        )
        
        # Display rewards
        display_text(
            self.screen,
            f"You earned {3 if self.current_level.is_boss else 1} upgrade point{'s' if self.current_level.is_boss else ''}!",
            self.fonts["medium"],
            self.colors["gold"],
            self.width // 2,
            self.height // 3 + 80,
            center=True
        )
        
        # Display information about upgrades
        display_text(
            self.screen,
            "You can spend your points to upgrade your character.",
            self.fonts["small"],
            self.colors["white"],
            self.width // 2,
            self.height // 3 + 110,
            center=True
        )
        
        # Draw continue button
        self.ui_elements[STATE_GAME_OVER_WIN]["continue_button"].draw(self.screen)
        
    def _update_game_over_lose(self, time_delta):
        """Update game over (lose) state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
        
        # Update restart button
        restart_button = self.ui_elements[STATE_GAME_OVER_LOSE]["restart_button"]
        if restart_button.update(mouse_pos, mouse_clicked, self.current_time):
            # Reset level (same level number)
            self.current_level = self.level_manager.create_level(self.player.level)
            
            # Reset clicks
            self.clicks = 0
            
            # Transition back to game
            self._start_transition(STATE_PLAYING)
            logger.info(f"Restarting level {self.player.level}")
            
    def _render_game_over_lose(self):
        """Render game over (lose) state"""
        from src.ui import display_text
        
        # Display lose title
        display_text(
            self.screen,
            "Level Failed!",
            self.fonts["large"],
            self.colors["red"],
            self.width // 2,
            self.height // 3,
            center=True
        )
        
        # Display failure message
        display_text(
            self.screen,
            "You were not able to complete the objective.",
            self.fonts["medium"],
            self.colors["white"],
            self.width // 2,
            self.height // 3 + 50,
            center=True
        )
        
        # Display tip
        display_text(
            self.screen,
            "Try upgrading your character before trying again.",
            self.fonts["small"],
            self.colors["white"],
            self.width // 2,
            self.height // 3 + 80,
            center=True
        )
        
        # Draw restart button
        self.ui_elements[STATE_GAME_OVER_LOSE]["restart_button"].draw(self.screen)
        
    def _update_pause(self, time_delta):
        """Update pause state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
        
        # Check for ESC key to resume
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self._start_transition(STATE_PLAYING)
            logger.info("Game resumed via ESC key")
            return
        
        # Update resume button
        resume_button = self.ui_elements[STATE_PAUSE]["resume_button"]
        if resume_button.update(mouse_pos, mouse_clicked, self.current_time):
            self._start_transition(STATE_PLAYING)
            logger.info("Game resumed via button")
            
        # Update settings button
        settings_button = self.ui_elements[STATE_PAUSE]["settings_button"]
        if settings_button.update(mouse_pos, mouse_clicked, self.current_time):
            self._start_transition(STATE_SETTINGS)
            logger.info("Opening settings from pause menu")
            
        # Update quit button
        quit_button = self.ui_elements[STATE_PAUSE]["quit_button"]
        if quit_button.update(mouse_pos, mouse_clicked, self.current_time):
            self._start_transition(STATE_MENU)
            logger.info("Quitting to main menu")
            
    def _render_pause(self):
        """Render pause state"""
        from src.ui import display_text
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Display pause title
        display_text(
            self.screen,
            "Paused",
            self.fonts["large"],
            self.colors["white"],
            self.width // 2,
            self.height // 3,
            center=True
        )
        
        # Draw buttons
        self.ui_elements[STATE_PAUSE]["resume_button"].draw(self.screen)
        self.ui_elements[STATE_PAUSE]["settings_button"].draw(self.screen)
        self.ui_elements[STATE_PAUSE]["quit_button"].draw(self.screen)
        
    def _setup_ability_selection(self):
        """Set up the ability selection screen after defeating a boss"""
        from src.ui import Button
        
        # Clear previous buttons
        self.ui_elements[STATE_ABILITY_SELECT]["ability_buttons"] = []
        self.ui_elements[STATE_ABILITY_SELECT]["selected_abilities"] = []
        
        # Get three random abilities
        available_abilities = list(self.player_abilities.keys())
        random.shuffle(available_abilities)
        selected_abilities = available_abilities[:3]
        
        # Create buttons for each ability
        btn_width, btn_height = 200, 80
        padding = 30
        start_y = self.height // 2 - 50
        
        for i, ability_name in enumerate(selected_abilities):
            ability = self.player_abilities[ability_name]
            
            # Create readable name and description
            readable_name = ability_name.replace("_", " ").title()
            
            # Create button
            ability_rect = pygame.Rect(
                self.width // 2 - btn_width // 2,
                start_y + i * (btn_height + padding),
                btn_width,
                btn_height
            )
            
            ability_button = Button(
                ability_rect,
                readable_name,
                self.fonts["medium"],
                self.colors["button"],
                border_width=2,
                border_color=self.colors["purple"]
            )
            
            self.ui_elements[STATE_ABILITY_SELECT]["ability_buttons"].append((ability_name, ability_button))
            
        # Continue button
        continue_rect = pygame.Rect(
            self.width // 2 - 100,
            self.height - 100,
            200,
            50
        )
        
        continue_button = Button(
            continue_rect,
            "Continue",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["green"]
        )
        
        self.ui_elements[STATE_ABILITY_SELECT]["continue_button"] = continue_button