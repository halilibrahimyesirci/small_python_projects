"""
Core game engine handling main loop and game state.
Uses modular components from engine_utils for better organization.
"""

import pygame
import sys
import time
import random
import logging
import os

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

# Import modules from engine_utils
from src.engine_utils.resource_manager import ResourceManager
from src.engine_utils.audio import AudioManager
from src.engine_utils.debug import DebugManager
from src.engine_utils.layout_manager import LayoutManager
from src.engine_utils.game_state_manager import GameStateManager
from src.engine_utils.transitions import TransitionManager

# Click delay in seconds
CLICK_DELAY = 0.45  # Increased for V0.3.3 (was 0.15)

logger = logging.getLogger(__name__)

class GameEngine:
    """Core game engine handling main loop and game state"""
    
    def __init__(self, resource_manager, player, level_manager, shop_manager=None):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Use the provided resource manager
        self.resource_manager = resource_manager
        
        # Get screen dimensions from config
        self.width = self.resource_manager.get_config_value("screen", "width") or 800
        self.height = self.resource_manager.get_config_value("screen", "height") or 600
        self.fps = self.resource_manager.get_config_value("screen", "fps") or 60
        
        # Create screen and clock
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("RPG Clicker V0.3.5")
        self.clock = pygame.time.Clock()
        
        # Initialize additional managers
        self.audio_manager = AudioManager(self.resource_manager)
        self.debug_manager = DebugManager(self.resource_manager.get_config_value("debug", "enabled", False))
        self.layout_manager = LayoutManager(self.width, self.height)
        self.state_manager = GameStateManager(self.width, self.height)
        self.transition_manager = TransitionManager(self.width, self.height)
        
        # Register state handlers
        self._register_state_handlers()
        
        # Store game references
        self.player = player
        self.level_manager = level_manager
        self.shop_manager = shop_manager
        
        # ESC key tracking
        self.last_esc_press = 0  # Initialize the last_esc_press attribute to track ESC key timing
        
        # Create UI manager for collision detection
        from src.ui import UIManager
        self.ui_manager = UIManager(self.width, self.height)
        
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
        
        # Load resources
        self._load_resources()
        
        # Create level
        self.current_level = None
        if self.level_manager:
            self.current_level = self.level_manager.create_level(self.player.level)
        
        # UI initialization will be done in the respective state functions
        self.ui_elements = {}
        self._init_ui()
        
        # Apply initial audio settings
        self._apply_audio_settings()
        
        logger.info("Game engine initialized")
        
    def _register_state_handlers(self):
        """Register state handlers with the state manager"""
        self.state_manager.register_state_handlers(STATE_MENU, update_menu, render_menu)
        self.state_manager.register_state_handlers(STATE_PLAYING, update_playing, render_playing)
        self.state_manager.register_state_handlers(STATE_GAME_OVER_WIN, self._update_game_over_win, self._render_game_over_win)    
        self.state_manager.register_state_handlers(STATE_GAME_OVER_LOSE, self._update_game_over_lose, self._render_game_over_lose)
        self.state_manager.register_state_handlers(STATE_UPGRADE, update_upgrade, render_upgrade)
        self.state_manager.register_state_handlers(STATE_PAUSE, self._update_pause, self._render_pause)
        self.state_manager.register_state_handlers(STATE_SETTINGS, update_settings, render_settings)
        self.state_manager.register_state_handlers(STATE_ABILITY_SELECT, update_ability_select, render_ability_select)
        self.state_manager.register_state_handlers(STATE_ESC_MENU, update_esc_menu, render_esc_menu)
        self.state_manager.register_state_handlers(STATE_SHOP, update_shop, render_shop)
        
    def _load_resources(self):
        """Load game resources using the resource manager"""
        # Load images
        bg_path = os.path.join("assets", "images", "background.png")
        self.resource_manager.load_image("background", bg_path, (self.width, self.height))
        
        button_path = os.path.join("assets", "images", "button.png")
        self.resource_manager.load_image("button", button_path, (200, 100))
        
        # Load sounds
        click_sound_path = os.path.join("assets", "sounds", "click.wav")
        self.resource_manager.load_sound("click", click_sound_path)
        
        critical_sound_path = os.path.join("assets", "sounds", "critical.wav")
        self.resource_manager.load_sound("critical", critical_sound_path)
        
        level_up_path = os.path.join("assets", "sounds", "level_up.wav")
        self.resource_manager.load_sound("level_up", level_up_path)
        
        # Load music
        menu_music_path = os.path.join("assets", "music", "best_one.mp3")
        self.resource_manager.load_music("menu", menu_music_path)
        
        gameplay_music_path = os.path.join("assets", "music", "mid.mp3")
        self.resource_manager.load_music("gameplay", gameplay_music_path)
        
        boss_music_path = os.path.join("assets", "music", "mhysteric_type.mp3")
        self.resource_manager.load_music("boss", boss_music_path)
        
    def _init_ui(self):
        """Initialize UI elements using the layout manager"""
        from src.ui import Button, ProgressBar, ComboMeter, ParticleSystem, Slider, UIElement
        
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
        
        # Create main layout containers for each game state
        for state in self.ui_elements.keys():
            self.layout_manager.create_container(state)
            
        # Menu UI - Using grid layout
        menu_container = self.layout_manager.get_container(STATE_MENU)
        self.layout_manager.grid_configure(STATE_MENU, 5, 3)  # 5 rows, 3 columns
        
        play_button = Button(
            pygame.Rect(0, 0, 200, 50),  # Placeholder rect, will be positioned by grid
            "Play",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        self.layout_manager.grid_place(STATE_MENU, play_button, 1, 1)  # Row 1, Col 1
        self.ui_elements[STATE_MENU]["play_button"] = play_button
        
        settings_button = Button(
            pygame.Rect(0, 0, 200, 50),  # Placeholder rect
            "Settings",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        self.layout_manager.grid_place(STATE_MENU, settings_button, 2, 1)  # Row 2, Col 1
        self.ui_elements[STATE_MENU]["settings_button"] = settings_button
        
        # Playing UI - Using both grid and pack layouts
        playing_container = self.layout_manager.get_container(STATE_PLAYING)
        self.layout_manager.grid_configure(STATE_PLAYING, 7, 3)  # 7 rows, 3 columns
        
        # Centered click button with increased size for better usability
        click_button = Button(
            pygame.Rect(0, 0, 240, 120),  # Bigger button size
            "Click Me!",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        self.layout_manager.grid_place(STATE_PLAYING, click_button, 3, 1, sticky="nsew")  # Center with stretching
        self.ui_elements[STATE_PLAYING]["click_button"] = click_button
        
        # Progress bar at bottom
        progress_bar = ProgressBar(
            pygame.Rect(0, 0, self.width - 100, 20),  # Placeholder rect
            (50, 50, 50),
            self.colors["green"],
            border_color=self.colors["white"],
            border_width=2
        )
        self.layout_manager.grid_place(STATE_PLAYING, progress_bar, 6, 0, 1, 3, "we")  # Bottom row, span all columns
        self.ui_elements[STATE_PLAYING]["progress_bar"] = progress_bar
        
        # Money counter (left bottom corner)
        money_counter = Button(
            pygame.Rect(0, 0, 160, 40),
            "Coins: 0",
            self.fonts["medium"],
            {"normal": (50, 50, 60), "hover": (60, 60, 70), "clicked": (70, 70, 80)},
            border_width=2,
            border_color=self.colors["gold"]
        )
        self.layout_manager.grid_place(STATE_PLAYING, money_counter, 5, 0, sticky="w")  # Bottom left
        self.ui_elements[STATE_PLAYING]["money_counter"] = money_counter
        
        # Level progress indicator (right bottom corner)
        level_indicator = Button(
            pygame.Rect(0, 0, 160, 40),
            "Level: 1",
            self.fonts["medium"],
            {"normal": (50, 50, 60), "hover": (60, 60, 70), "clicked": (70, 70, 80)},
            border_width=2,
            border_color=self.colors["blue"]
        )
        self.layout_manager.grid_place(STATE_PLAYING, level_indicator, 5, 2, sticky="e")  # Bottom right
        self.ui_elements[STATE_PLAYING]["level_indicator"] = level_indicator
        
        # Combo meter at top
        combo_meter = ComboMeter(
            pygame.Rect(0, 0, 200, 30),  # Placeholder rect
            self.colors["combo"],
            self.fonts["medium"],
            decay_rate=0.5
        )
        self.layout_manager.grid_place(STATE_PLAYING, combo_meter, 0, 1)  # Top middle
        self.ui_elements[STATE_PLAYING]["combo_meter"] = combo_meter
        
        # Particle system
        self.ui_elements[STATE_PLAYING]["particles"] = ParticleSystem()
        
        # Game over (win) UI - Using grid layout
        win_container = self.layout_manager.get_container(STATE_GAME_OVER_WIN)
        self.layout_manager.grid_configure(STATE_GAME_OVER_WIN, 7, 3)
        
        continue_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Continue",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["green"]
        )
        self.layout_manager.grid_place(STATE_GAME_OVER_WIN, continue_button, 5, 1)  # Row 5, Col 1
        self.ui_elements[STATE_GAME_OVER_WIN]["continue_button"] = continue_button
        
        # Game over (lose) UI - Using grid layout
        lose_container = self.layout_manager.get_container(STATE_GAME_OVER_LOSE)
        self.layout_manager.grid_configure(STATE_GAME_OVER_LOSE, 7, 3)
        
        restart_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Restart",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["red"]
        )
        self.layout_manager.grid_place(STATE_GAME_OVER_LOSE, restart_button, 5, 1)  # Row 5, Col 1
        self.ui_elements[STATE_GAME_OVER_LOSE]["restart_button"] = restart_button
        
        # Upgrade UI - Using grid layout with 5 rows and 5 columns for more layout control
        upgrade_container = self.layout_manager.get_container(STATE_UPGRADE)
        self.layout_manager.grid_configure(STATE_UPGRADE, 5, 5)
        
        # Click power upgrade - Top left
        click_power_button = Button(
            pygame.Rect(0, 0, 180, 50),
            "Click Power",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["blue"]
        )
        self.layout_manager.grid_place(STATE_UPGRADE, click_power_button, 1, 1)
        self.ui_elements[STATE_UPGRADE]["click_power_button"] = click_power_button
        
        # Critical chance - Top right
        crit_chance_button = Button(
            pygame.Rect(0, 0, 180, 50),
            "Crit Chance",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["blue"]
        )
        self.layout_manager.grid_place(STATE_UPGRADE, crit_chance_button, 1, 3)
        self.ui_elements[STATE_UPGRADE]["crit_chance_button"] = crit_chance_button
        
        # Critical multiplier - Bottom left
        crit_mult_button = Button(
            pygame.Rect(0, 0, 180, 50),
            "Crit Multiplier",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["blue"]
        )
        self.layout_manager.grid_place(STATE_UPGRADE, crit_mult_button, 2, 1)
        self.ui_elements[STATE_UPGRADE]["crit_mult_button"] = crit_mult_button
        
        # Coin upgrade - Bottom right
        coin_upgrade_button = Button(
            pygame.Rect(0, 0, 180, 50),
            "Coin Drop",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["gold"]
        )
        self.layout_manager.grid_place(STATE_UPGRADE, coin_upgrade_button, 2, 3)
        self.ui_elements[STATE_UPGRADE]["coin_upgrade_button"] = coin_upgrade_button
        
        # Continue button
        upgrade_continue_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Continue",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["green"]
        )
        self.layout_manager.grid_place(STATE_UPGRADE, upgrade_continue_button, 3, 2)
        self.ui_elements[STATE_UPGRADE]["continue_button"] = upgrade_continue_button
        
        # ESC Menu UI - Using grid layout
        esc_container = self.layout_manager.get_container(STATE_ESC_MENU)
        self.layout_manager.grid_configure(STATE_ESC_MENU, 7, 3)
        
        # Resume button
        resume_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Resume",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["green"]
        )
        self.layout_manager.grid_place(STATE_ESC_MENU, resume_button, 2, 1)
        self.ui_elements[STATE_ESC_MENU]["resume_button"] = resume_button
        
        # Settings button
        esc_settings_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Settings",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["blue"]
        )
        self.layout_manager.grid_place(STATE_ESC_MENU, esc_settings_button, 3, 1)
        self.ui_elements[STATE_ESC_MENU]["settings_button"] = esc_settings_button
        
        # Shop button
        shop_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Shop",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["gold"]
        )
        self.layout_manager.grid_place(STATE_ESC_MENU, shop_button, 4, 1)
        self.ui_elements[STATE_ESC_MENU]["shop_button"] = shop_button
        
        # Main menu button
        main_menu_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Main Menu",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["red"]
        )
        self.layout_manager.grid_place(STATE_ESC_MENU, main_menu_button, 5, 1)
        self.ui_elements[STATE_ESC_MENU]["main_menu_button"] = main_menu_button
        
        # Settings UI - Using grid layout
        settings_container = self.layout_manager.get_container(STATE_SETTINGS)
        self.layout_manager.grid_configure(STATE_SETTINGS, 10, 5)  # More rows and columns for better spacing
        
        # Sound volume slider
        sound_slider = Slider(
            pygame.Rect(0, 0, 300, 30),
            self.audio_settings["sound_volume"],  # initial value
            0.0, 1.0,  # min and max values
            self.colors["white"],  # bg_color
            self.colors["blue"],   # handle_color
            self.fonts["small"],   # font
            label="Sound Volume"   # label
        )
        self.layout_manager.grid_place(STATE_SETTINGS, sound_slider, 2, 2)
        self.ui_elements[STATE_SETTINGS]["sound_slider"] = sound_slider
        
        # Music volume slider
        music_slider = Slider(
            pygame.Rect(0, 0, 300, 30),
            self.audio_settings["music_volume"],  # initial value
            0.0, 1.0,  # min and max values
            self.colors["white"],  # bg_color
            self.colors["green"],  # handle_color
            self.fonts["small"],   # font
            label="Music Volume"   # label
        )
        self.layout_manager.grid_place(STATE_SETTINGS, music_slider, 4, 2)
        self.ui_elements[STATE_SETTINGS]["music_slider"] = music_slider
        
        # Music selection buttons
        music_files = [
            "best_one.mp3",
            "energitic_stuff.mp3",
            "mhysteric_type.mp3",
            "mid.mp3",
            "very_energitic_stuff.mp3"
        ]
        
        music_buttons = []
        for i, music_file in enumerate(music_files):
            # Calculate position in a two-row grid
            row = 6 + (i // 3)  # Start at row 6, put 3 buttons per row
            col = 1 + (i % 3)   # Start at col 1, spread across 3 columns
            
            # Create a button for each music file
            music_name = music_file.replace(".mp3", "").replace("_", " ").title()
            music_button = Button(
                pygame.Rect(0, 0, 160, 40),
                music_name,
                self.fonts["small"],
                self.colors["button"],
                border_width=2,
                border_color=self.colors["purple"]
            )
            self.layout_manager.grid_place(STATE_SETTINGS, music_button, row, col)
            music_buttons.append((music_file, music_button))
        
        self.ui_elements[STATE_SETTINGS]["music_buttons"] = music_buttons
        
        # Back button for settings
        settings_back_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Back",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["red"]
        )
        self.layout_manager.grid_place(STATE_SETTINGS, settings_back_button, 9, 2)
        self.ui_elements[STATE_SETTINGS]["back_button"] = settings_back_button
        
        # Shop UI initialization - Using a grid layout for shop items
        shop_container = self.layout_manager.get_container(STATE_SHOP)
        # Use more rows to accommodate more shop items without overflow
        self.layout_manager.grid_configure(STATE_SHOP, 12, 3)
        
        # Initialize shop item buttons list
        self.ui_elements[STATE_SHOP]["item_buttons"] = []
        
        # Coin display at top of shop
        coin_display = Button(
            pygame.Rect(0, 0, 200, 40),
            "Coins: 0",
            self.fonts["medium"],
            {"normal": (60, 60, 40), "hover": (60, 60, 40), "clicked": (60, 60, 40)},
            border_width=2,
            border_color=self.colors["gold"]
        )
        self.layout_manager.grid_place(STATE_SHOP, coin_display, 1, 1)
        self.ui_elements[STATE_SHOP]["coin_display"] = coin_display
        
        # Back button for shop
        shop_back_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Back",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["red"]
        )
        self.layout_manager.grid_place(STATE_SHOP, shop_back_button, 11, 1)  # Last row
        self.ui_elements[STATE_SHOP]["back_button"] = shop_back_button
        
        # Pause menu UI - Using grid layout
        pause_container = self.layout_manager.get_container(STATE_PAUSE)
        self.layout_manager.grid_configure(STATE_PAUSE, 7, 3)
        
        # Resume button for pause menu
        pause_resume_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Resume",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["green"]
        )
        self.layout_manager.grid_place(STATE_PAUSE, pause_resume_button, 3, 1)
        self.ui_elements[STATE_PAUSE]["resume_button"] = pause_resume_button
        
        # Settings button for pause menu
        pause_settings_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Settings",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["blue"]
        )
        self.layout_manager.grid_place(STATE_PAUSE, pause_settings_button, 4, 1)
        self.ui_elements[STATE_PAUSE]["settings_button"] = pause_settings_button
        
        # Quit button for pause menu
        pause_quit_button = Button(
            pygame.Rect(0, 0, 200, 50),
            "Quit",
            self.fonts["medium"],
            self.colors["button"],
            border_width=2,
            border_color=self.colors["red"]
        )
        self.layout_manager.grid_place(STATE_PAUSE, pause_quit_button, 5, 1)
        self.ui_elements[STATE_PAUSE]["quit_button"] = pause_quit_button
        
        # Ability select state UI will be initialized in the ability_select_state module
        
        # Register all UI elements with the UI manager for collision detection
        self._register_ui_elements_with_manager()
        
    def _apply_audio_settings(self):
        """Apply audio settings to the audio manager"""
        self.audio_manager.set_music_volume(self.audio_settings["music_volume"])
        self.audio_manager.set_sound_volume(self.audio_settings["sound_volume"])
        
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
            
            # Update transitions
            self.transition_manager.update()
            
            # Update game state
            self.state_manager.update(time_delta, self)
            
            # Update layout system
            self.layout_manager.update_layouts()
            
            # Render
            self._render()
            
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
                        
                        if self.state_manager.is_state(STATE_PLAYING):
                            self.state_manager.change_state(STATE_ESC_MENU)
                            logger.info("Game paused with ESC key")
                        elif self.state_manager.is_state(STATE_ESC_MENU):
                            self.state_manager.change_state(STATE_PLAYING)
                            logger.info("Game resumed via ESC key")
                        elif self.state_manager.is_state(STATE_SETTINGS) or \
                             self.state_manager.is_state(STATE_SHOP) or \
                             self.state_manager.is_state(STATE_UPGRADE):
                            # Return to previous state
                            previous_state = self.state_manager.previous_state or STATE_MENU
                            self.state_manager.change_state(previous_state)
                            logger.info(f"Returned to {previous_state} with ESC key")
                
    def _render(self):
        """Render the current game state"""
        # Clear screen
        self.screen.fill(self.colors["black"])
        
        # Draw background if available
        if "background" in self.resource_manager.images:
            self.screen.blit(self.resource_manager.images["background"], (0, 0))
        
        # Render the current state using the state manager
        self.state_manager.render(self.screen, self)
        
        # Render any active transitions
        self.transition_manager.render(self.screen)
        
        # Draw version info
        from src.ui import display_text
        display_text(
            self.screen,
            "V0.3.5",
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
            f"State: {self.state_manager.current_state}",
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
        
    def _update_game_over_win(self, engine, time_delta):
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
            
            # Only go to upgrade screen after boss levels
            if self.current_level and self.current_level.is_boss:
                self.state_manager.change_state(STATE_UPGRADE)
            else:
                self.state_manager.change_state(STATE_MENU)
                logger.info("Returning to menu after level completion")
            
    def _render_game_over_win(self, engine):
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
        
    def _update_game_over_lose(self, engine, time_delta):
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
            self.state_manager.change_state(STATE_PLAYING)
            logger.info(f"Restarting level {self.player.level}")
            
    def _render_game_over_lose(self, engine):
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
        
    def _update_pause(self, engine, time_delta):
        """Update pause state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
        
        # Check for ESC key to resume
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.state_manager.change_state(STATE_PLAYING)
            logger.info("Game resumed via ESC key")
            return
        
        # Update resume button
        resume_button = self.ui_elements[STATE_PAUSE]["resume_button"]
        if resume_button.update(mouse_pos, mouse_clicked, self.current_time):
            self.state_manager.change_state(STATE_PLAYING)
            logger.info("Game resumed via button")
            
        # Update settings button
        settings_button = self.ui_elements[STATE_PAUSE]["settings_button"]
        if settings_button.update(mouse_pos, mouse_clicked, self.current_time):
            self.state_manager.change_state(STATE_SETTINGS)
            logger.info("Opening settings from pause menu")
            
        # Update quit button
        quit_button = self.ui_elements[STATE_PAUSE]["quit_button"]
        if quit_button.update(mouse_pos, mouse_clicked, self.current_time):
            self.state_manager.change_state(STATE_MENU)
            logger.info("Quitting to main menu")
            
    def _render_pause(self, engine):
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
        
    def _register_ui_elements_with_manager(self):
        """Register all UI elements with the UI manager for collision detection"""
        # Clear existing elements
        self.ui_manager.elements = []
        
        # Register UI elements from each state
        for state, elements in self.ui_elements.items():
            for key, element in elements.items():
                # Skip particle systems and other non-UI elements
                if key == "particles" or not hasattr(element, "rect"):
                    continue
                
                # Handle collections of UI elements (like buttons in lists of tuples)
                if isinstance(element, list):
                    for item in element:
                        if isinstance(item, tuple) and len(item) == 2 and hasattr(item[1], "rect"):
                            ui_element = self.ui_manager.convert_to_ui_element(item[1], f"{state}_{key}")
                            self.ui_manager.add_element(ui_element)
                else:
                    # Register individual UI element
                    ui_element = self.ui_manager.convert_to_ui_element(element, f"{state}_{key}")
                    self.ui_manager.add_element(ui_element)
        
        # Adjust all positions to prevent collisions and stay within screen boundaries
        self.ui_manager.adjust_all_positions()
        
    def _start_transition(self, to_state, duration=None, transition_type=None):
        """Start a transition to a new state"""
        from_state = self.state_manager.current_state
        next_state = to_state
        # If transition manager is available, use it
        if hasattr(self, 'transition_manager'):
            next_state = self.transition_manager.start_transition(
                from_state, 
                to_state, 
                self.screen, 
                duration, 
                transition_type
            )
        self.state_manager.change_state(next_state)
        return next_state

    @property
    def previous_state(self):
        """Get the previous state from the state manager"""
        return self.state_manager.previous_state