import pygame
import sys
import time
import random
import logging
import os

# Game states
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER_WIN = "GAME_OVER_WIN"
STATE_GAME_OVER_LOSE = "GAME_OVER_LOSE"
STATE_UPGRADE = "UPGRADE"
STATE_PAUSE = "PAUSE"

logger = logging.getLogger(__name__)

class GameEngine:
    """Core game engine handling main loop and game state"""
    
    def __init__(self, resource_manager, player, level_manager):
        self.resource_manager = resource_manager
        self.player = player
        self.level_manager = level_manager
        
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Get screen dimensions from config
        self.width = self.resource_manager.get_config_value("screen", "width") or 800
        self.height = self.resource_manager.get_config_value("screen", "height") or 600
        self.fps = self.resource_manager.get_config_value("screen", "fps") or 60
        
        # Create screen and clock
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("RPG Clicker V0.3")
        self.clock = pygame.time.Clock()
        
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
        self.clicks = 0
        self.start_ticks = 0
        self.current_time = 0
        self.debug_mode = False
        
        # Load resources
        self._load_resources()
        
        # Create level
        self.current_level = self.level_manager.create_level(self.player.level)
        
        # UI initialization will be done in the respective state functions
        self.ui_elements = {}
        self._init_ui()
        
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
        
        # Try to load music
        menu_music_path = os.path.join("assets", "music", "menu.mp3")
        self.resource_manager.load_music("menu", menu_music_path)
        
        gameplay_music_path = os.path.join("assets", "music", "gameplay.mp3")
        self.resource_manager.load_music("gameplay", gameplay_music_path)
        
        boss_music_path = os.path.join("assets", "music", "boss.mp3")
        self.resource_manager.load_music("boss", boss_music_path)
        
    def _init_ui(self):
        """Initialize UI elements"""
        from src.ui import Button, ProgressBar, ComboMeter, ParticleSystem
        
        # Create UI containers for each state
        self.ui_elements = {
            STATE_MENU: {},
            STATE_PLAYING: {},
            STATE_GAME_OVER_WIN: {},
            STATE_GAME_OVER_LOSE: {},
            STATE_UPGRADE: {},
            STATE_PAUSE: {}
        }
        
        # Menu UI
        play_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2, 200, 50)
        self.ui_elements[STATE_MENU]["play_button"] = Button(
            play_button_rect,
            "Play",
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
        continue_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 + 100, 200, 50)
        self.ui_elements[STATE_GAME_OVER_WIN]["continue_button"] = Button(
            continue_button_rect,
            "Continue",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["green"]
        )
        
        # Game over (lose) UI
        restart_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 + 100, 200, 50)
        self.ui_elements[STATE_GAME_OVER_LOSE]["restart_button"] = Button(
            restart_button_rect,
            "Restart",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["red"]
        )
        
        # Upgrade UI
        btn_width, btn_height = 150, 40
        padding = 20
        start_y = self.height // 2 - 50
        
        # Click power upgrade button
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
        
        # Critical chance upgrade button
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
        
        # Critical multiplier upgrade button
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
        
        # Continue button (after upgrades)
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
        resume_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 - 30, 200, 50)
        self.ui_elements[STATE_PAUSE]["resume_button"] = Button(
            resume_button_rect,
            "Resume",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["blue"]
        )
        
        quit_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 + 30, 200, 50)
        self.ui_elements[STATE_PAUSE]["quit_button"] = Button(
            quit_button_rect,
            "Quit",
            self.fonts["large"],
            self.colors["button"],
            border_width=3,
            border_color=self.colors["red"]
        )
        
    def run(self):
        """Run the main game loop"""
        logger.info("Starting game loop")
        
        while self.running:
            # Get time delta
            time_delta = self.clock.tick(self.fps) / 1000.0
            self.current_time = pygame.time.get_ticks() / 1000.0
            
            # Process events
            self._process_events()
            
            # Update game state
            self._update(time_delta)
            
            # Render
            self._render()
            
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
                
                # Pause game with ESC during gameplay
                if event.key == pygame.K_ESCAPE and self.game_state == STATE_PLAYING:
                    self.game_state = STATE_PAUSE
                    logger.info("Game paused")
                
            # Handle mouse events in state-specific update methods
                
    def _update(self, time_delta):
        """Update game logic based on current state"""
        if self.game_state == STATE_MENU:
            self._update_menu(time_delta)
        elif self.game_state == STATE_PLAYING:
            self._update_playing(time_delta)
        elif self.game_state == STATE_GAME_OVER_WIN:
            self._update_game_over_win(time_delta)
        elif self.game_state == STATE_GAME_OVER_LOSE:
            self._update_game_over_lose(time_delta)
        elif self.game_state == STATE_UPGRADE:
            self._update_upgrade(time_delta)
        elif self.game_state == STATE_PAUSE:
            self._update_pause(time_delta)
            
    def _render(self):
        """Render the current game state"""
        # Clear screen
        self.screen.fill(self.colors["black"])
        
        # Draw background if available
        if "background" in self.resource_manager.images:
            self.screen.blit(self.resource_manager.images["background"], (0, 0))
        
        # Render based on current state
        if self.game_state == STATE_MENU:
            self._render_menu()
        elif self.game_state == STATE_PLAYING:
            self._render_playing()
        elif self.game_state == STATE_GAME_OVER_WIN:
            self._render_game_over_win()
        elif self.game_state == STATE_GAME_OVER_LOSE:
            self._render_game_over_lose()
        elif self.game_state == STATE_UPGRADE:
            self._render_upgrade()
        elif self.game_state == STATE_PAUSE:
            self._render_pause()
            
        # Draw version info
        from src.ui import display_text
        display_text(
            self.screen,
            "V0.3",
            self.fonts["small"],
            self.colors["white"],
            self.width - 40,
            self.height - 20,
            center=False
        )
        
        # Debug info if enabled
        if self.debug_mode:
            self._render_debug_info()
            
        # Update display
        pygame.display.flip()
        
    def _render_debug_info(self):
        """Render debug information"""
        from src.ui import display_text
        
        debug_info = [
            f"FPS: {int(self.clock.get_fps())}",
            f"State: {self.game_state}",
            f"Level: {self.player.level}",
            f"Clicks: {self.clicks}",
            f"Target: {self.current_level.click_target if self.current_level else 'N/A'}",
            f"Click Power: {self.player.stats['click_power']['value']}",
            f"Crit Chance: {int(self.player.stats['critical_chance']['value'] * 100)}%",
            f"Crit Mult: {self.player.stats['critical_multiplier']['value']}x",
            f"Upgrade Points: {self.player.upgrade_points}"
        ]
        
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
            
    def _update_menu(self, time_delta):
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
        
        # Update play button
        play_button = self.ui_elements[STATE_MENU]["play_button"]
        if play_button.update(mouse_pos, mouse_clicked, self.current_time):
            self.game_state = STATE_PLAYING
            self.clicks = 0
            self.start_ticks = pygame.time.get_ticks()
            
            # Play appropriate music
            if self.current_level.is_boss:
                self.resource_manager.play_music("boss")
            else:
                self.resource_manager.play_music("gameplay")
                
            logger.info(f"Starting level {self.current_level.level_number}")
            
    def _render_menu(self):
        """Render menu state"""
        from src.ui import display_text
        
        # Game title
        display_text(
            self.screen,
            "RPG Clicker",
            self.fonts["large"],
            self.colors["white"],
            self.width // 2,
            self.height // 3,
            center=True
        )
        
        # Level info
        if self.current_level:
            display_text(
                self.screen,
                self.current_level.get_description(),
                self.fonts["medium"],
                self.colors["white"],
                self.width // 2,
                self.height // 2 - 50,
                center=True
            )
            
            display_text(
                self.screen,
                self.current_level.get_objective_text(),
                self.fonts["medium"],
                self.colors["white"],
                self.width // 2,
                self.height // 2 - 20,
                center=True
            )
        
        # Draw play button
        self.ui_elements[STATE_MENU]["play_button"].draw(self.screen)
        
        # Player stats
        stats_y = self.height - 80
        display_text(
            self.screen,
            f"Highest Level: {self.player.highest_level}",
            self.fonts["small"],
            self.colors["white"],
            self.width // 2,
            stats_y,
            center=True
        )
        
        display_text(
            self.screen,
            f"Click Power: {self.player.stats['click_power']['value']}",
            self.fonts["small"],
            self.colors["white"],
            self.width // 4,
            stats_y + 20,
            center=True
        )
        
        display_text(
            self.screen,
            f"Crit Chance: {int(self.player.stats['critical_chance']['value'] * 100)}%",
            self.fonts["small"],
            self.colors["white"],
            self.width // 2,
            stats_y + 20,
            center=True
        )
        
        display_text(
            self.screen,
            f"Crit Multiplier: {self.player.stats['critical_multiplier']['value']}x",
            self.fonts["small"],
            self.colors["white"],
            3 * self.width // 4,
            stats_y + 20,
            center=True
        )
    
    def _update_playing(self, time_delta):
        """Update playing state"""
        from src.ui import ClickParticle, TextParticle
        
        # Get mouse state
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Left button
        
        # Update click button
        click_button = self.ui_elements[STATE_PLAYING]["click_button"]
        if self.current_level.is_boss and self.current_level.ability_active:
            # Handle boss abilities
            if self.current_level.boss_ability == "move_button":
                # Randomly move button if ability is active
                if random.random() < 0.05:  # 5% chance per frame
                    click_button.rect.x = random.randint(50, self.width - 250)
                    click_button.rect.y = random.randint(100, self.height - 150)
                    
            elif self.current_level.boss_ability == "click_block":
                # Block some clicks (implemented in the button click handling below)
                pass
        
        # Check if button was clicked
        button_clicked = click_button.update(mouse_pos, mouse_pressed, self.current_time)
        if button_clicked:
            # Process boss ability that blocks clicks
            if (self.current_level.is_boss and 
                self.current_level.ability_active and 
                self.current_level.boss_ability == "click_block" and
                random.random() < 0.5):  # 50% chance to block
                
                # Click blocked
                logger.info("Click blocked by boss ability")
                
                # Show blocked text
                text_particle = TextParticle(
                    mouse_pos[0],
                    mouse_pos[1] - 20,
                    "BLOCKED!",
                    self.fonts["medium"],
                    self.colors["red"],
                    speed=1,
                    life=0.8
                )
                self.ui_elements[STATE_PLAYING]["particles"].add_particle(text_particle)
            else:
                # Regular click processing
                combo_meter = self.ui_elements[STATE_PLAYING]["combo_meter"]
                combo_meter.add_click(self.current_time)
                combo_bonus = combo_meter.get_combo_bonus()
                
                # Determine if this is a critical click
                crit_chance = self.player.stats["critical_chance"]["value"]
                is_critical = random.random() < crit_chance
                
                # Calculate click value
                click_power = self.player.stats["click_power"]["value"]
                crit_multiplier = self.player.stats["critical_multiplier"]["value"] if is_critical else 1
                combo_multiplier = 1 + combo_bonus
                
                click_value = int(click_power * crit_multiplier * combo_multiplier)
                
                # Update clicks
                self.clicks += click_value
                self.player.total_clicks += click_value
                
                # Play sound
                if is_critical:
                    self.resource_manager.play_sound("critical")
                else:
                    self.resource_manager.play_sound("click")
                
                # Add visual feedback
                # Text particle for click value
                text_color = self.colors["yellow"] if is_critical else self.colors["white"]
                text_particle = TextParticle(
                    mouse_pos[0],
                    mouse_pos[1] - 20,
                    f"+{click_value}",
                    self.fonts["medium"] if is_critical else self.fonts["small"],
                    text_color,
                    speed=1.5 if is_critical else 1,
                    life=1.0
                )
                self.ui_elements[STATE_PLAYING]["particles"].add_particle(text_particle)
                
                # Add click particles
                for _ in range(5 if is_critical else 3):
                    particle = ClickParticle(
                        mouse_pos[0],
                        mouse_pos[1],
                        (255, 255, 0) if is_critical else (150, 150, 255),
                        size=3 + random.randint(0, 3),
                        speed=2 + random.random() * 2,
                        life=0.5 + random.random() * 0.5
                    )
                    self.ui_elements[STATE_PLAYING]["particles"].add_particle(particle)
                
                # Update boss health if this is a boss level
                if self.current_level.is_boss:
                    boss_defeated = self.current_level.damage_boss(click_value)
                    if boss_defeated:
                        self.game_state = STATE_GAME_OVER_WIN
                        self.resource_manager.play_sound("level_up")
                        logger.info(f"Boss defeated! Level {self.current_level.level_number} completed.")
                
        # Update combo meter
        combo_meter = self.ui_elements[STATE_PLAYING]["combo_meter"]
        combo_meter.update(self.current_time)
        
        # Update particles
        self.ui_elements[STATE_PLAYING]["particles"].update()
        
        # Update progress bar
        progress_bar = self.ui_elements[STATE_PLAYING]["progress_bar"]
        if self.current_level.is_boss:
            # For boss levels, show boss health
            progress_bar.set_progress(1 - self.current_level.get_health_percent())
        else:
            # For regular levels, show progress toward click target
            progress_percent = min(1.0, self.clicks / self.current_level.click_target)
            progress_bar.set_progress(progress_percent)
        progress_bar.update()
        
        # Check if level is completed (for non-boss levels)
        if not self.current_level.is_boss:
            if self.current_level.check_completion(self.clicks, 0):
                self.game_state = STATE_GAME_OVER_WIN
                self.resource_manager.play_sound("level_up")
                logger.info(f"Level {self.current_level.level_number} completed!")
        
        # Check if timer has expired
        seconds_elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000
        if seconds_elapsed >= self.current_level.timer_duration:
            if self.current_level.check_completion(self.clicks, 0):
                self.game_state = STATE_GAME_OVER_WIN
                self.resource_manager.play_sound("level_up")
                logger.info(f"Level {self.current_level.level_number} completed just in time!")
            else:
                self.game_state = STATE_GAME_OVER_LOSE
                logger.info(f"Time's up! Failed level {self.current_level.level_number}.")
                
        # Update boss ability
        if self.current_level.is_boss:
            self.current_level.update_ability(seconds_elapsed, self.current_time)
            
    def _render_playing(self):
        """Render playing state"""
        from src.ui import display_text
        
        # Display level info
        level_text = self.current_level.get_description()
        if self.current_level.is_boss:
            display_text(
                self.screen,
                level_text,
                self.fonts["large"],
                self.colors["boss"],
                self.width // 2,
                20,
                center=True
            )
        else:
            display_text(
                self.screen,
                level_text,
                self.fonts["large"],
                self.colors["white"],
                self.width // 2,
                20,
                center=True
            )
        
        # Display clicks
        display_text(
            self.screen,
            f"Clicks: {self.clicks} / {self.current_level.click_target}",
            self.fonts["medium"],
            self.colors["white"],
            20,
            20,
            center=False
        )
        
        # Display timer
        seconds_elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000
        seconds_remaining = max(0, self.current_level.timer_duration - seconds_elapsed)
        
        # Make timer red if time is running out
        timer_color = self.colors["red"] if seconds_remaining < 5 else self.colors["white"]
        
        display_text(
            self.screen,
            f"Time: {seconds_remaining:.1f}s",
            self.fonts["medium"],
            timer_color,
            self.width - 150,
            20,
            center=False
        )
        
        # Display boss health if this is a boss level
        if self.current_level.is_boss:
            health_percent = self.current_level.get_health_percent()
            boss_health_text = f"Boss Health: {int(health_percent * 100)}%"
            
            display_text(
                self.screen,
                boss_health_text,
                self.fonts["medium"],
                self.colors["boss"],
                self.width // 2,
                50,
                center=True
            )
            
            # Display boss ability warning
            if self.current_level.ability_active:
                ability_name = self.current_level.boss_ability.replace("_", " ").upper()
                display_text(
                    self.screen,
                    f"BOSS ABILITY: {ability_name}",
                    self.fonts["medium"],
                    self.colors["red"],
                    self.width // 2,
                    80,
                    center=True
                )
        
        # Draw click button
        self.ui_elements[STATE_PLAYING]["click_button"].draw(self.screen)
        
        # Draw progress bar
        self.ui_elements[STATE_PLAYING]["progress_bar"].draw(self.screen)
        
        # Draw combo meter if active
        combo_meter = self.ui_elements[STATE_PLAYING]["combo_meter"]
        if combo_meter.active:
            combo_meter.draw(self.screen)
            
        # Draw particles
        self.ui_elements[STATE_PLAYING]["particles"].draw(self.screen)
        
    def _update_game_over_win(self, time_delta):
        """Update game over (win) state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
        
        # Update continue button
        continue_button = self.ui_elements[STATE_GAME_OVER_WIN]["continue_button"]
        if continue_button.update(mouse_pos, mouse_clicked, self.current_time):
            # Player completed the level
            self.player.complete_level(win=True)
            self.player.save_progress()
            
            # Go to upgrade screen
            self.game_state = STATE_UPGRADE
            logger.info("Proceeding to upgrade screen")
            
    def _render_game_over_win(self):
        """Render game over (win) state"""
        from src.ui import display_text
        
        # Display win message
        if self.current_level.is_boss:
            display_text(
                self.screen,
                f"Boss Defeated!",
                self.fonts["large"],
                self.colors["green"],
                self.width // 2,
                self.height // 3 - 50,
                center=True
            )
            
            display_text(
                self.screen,
                f"{self.current_level.boss_name} has been vanquished!",
                self.fonts["medium"],
                self.colors["white"],
                self.width // 2,
                self.height // 3,
                center=True
            )
        else:
            display_text(
                self.screen,
                "Level Complete!",
                self.fonts["large"],
                self.colors["green"],
                self.width // 2,
                self.height // 3 - 30,
                center=True
            )
        
        # Display stats
        display_text(
            self.screen,
            f"Total Clicks: {self.clicks} / {self.current_level.click_target}",
            self.fonts["medium"],
            self.colors["white"],
            self.width // 2,
            self.height // 2 - 40,
            center=True
        )
        
        seconds_elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000
        display_text(
            self.screen,
            f"Time: {seconds_elapsed:.1f}s / {self.current_level.timer_duration}s",
            self.fonts["medium"],
            self.colors["white"],
            self.width // 2,
            self.height // 2 - 10,
            center=True
        )
        
        # Display level info
        display_text(
            self.screen,
            f"Level {self.current_level.level_number} Completed!",
            self.fonts["medium"],
            self.colors["white"],
            self.width // 2,
            self.height // 2 + 20,
            center=True
        )
        
        # Display reward
        display_text(
            self.screen,
            "Reward: 1 Upgrade Point",
            self.fonts["medium"],
            self.colors["green"],
            self.width // 2,
            self.height // 2 + 50,
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
            # Player failed the level, reset to level 1
            self.player.complete_level(win=False)
            self.player.save_progress()
            
            # Create new level 1 and go back to menu
            self.current_level = self.level_manager.create_level(self.player.level)
            self.game_state = STATE_MENU
            logger.info("Restarting from level 1")
            
    def _render_game_over_lose(self):
        """Render game over (lose) state"""
        from src.ui import display_text
        
        # Display lose message
        display_text(
            self.screen,
            "Game Over!",
            self.fonts["large"],
            self.colors["red"],
            self.width // 2,
            self.height // 3 - 30,
            center=True
        )
        
        # Display stats
        display_text(
            self.screen,
            f"Clicks: {self.clicks} / {self.current_level.click_target}",
            self.fonts["medium"],
            self.colors["white"],
            self.width // 2,
            self.height // 2 - 40,
            center=True
        )
        
        # Display level info
        display_text(
            self.screen,
            f"You reached Level {self.current_level.level_number}",
            self.fonts["medium"],
            self.colors["white"],
            self.width // 2,
            self.height // 2 - 10,
            center=True
        )
        
        display_text(
            self.screen,
            "You must restart from Level 1",
            self.fonts["medium"],
            self.colors["white"],
            self.width // 2,
            self.height // 2 + 20,
            center=True
        )
        
        display_text(
            self.screen,
            "(But you keep your upgrades!)",
            self.fonts["small"],
            self.colors["green"],
            self.width // 2,
            self.height // 2 + 50,
            center=True
        )
        
        # Draw restart button
        self.ui_elements[STATE_GAME_OVER_LOSE]["restart_button"].draw(self.screen)
        
    def _update_upgrade(self, time_delta):
        """Update upgrade state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
        
        # Update click power button
        click_power_button = self.ui_elements[STATE_UPGRADE]["click_power_button"]
        if click_power_button.update(mouse_pos, mouse_clicked, self.current_time):
            if self.player.upgrade_stat("click_power"):
                self.player.save_progress()
                logger.info("Upgraded click power")
        
        # Update critical chance button
        crit_chance_button = self.ui_elements[STATE_UPGRADE]["crit_chance_button"]
        if crit_chance_button.update(mouse_pos, mouse_clicked, self.current_time):
            if self.player.upgrade_stat("critical_chance"):
                self.player.save_progress()
                logger.info("Upgraded critical chance")
        
        # Update critical multiplier button
        crit_mult_button = self.ui_elements[STATE_UPGRADE]["crit_mult_button"]
        if crit_mult_button.update(mouse_pos, mouse_clicked, self.current_time):
            if self.player.upgrade_stat("critical_multiplier"):
                self.player.save_progress()
                logger.info("Upgraded critical multiplier")
        
        # Update continue button
        continue_button = self.ui_elements[STATE_UPGRADE]["continue_button"]
        if continue_button.update(mouse_pos, mouse_clicked, self.current_time):
            # Create new level and go back to menu
            self.current_level = self.level_manager.create_level(self.player.level)
            self.game_state = STATE_MENU
            logger.info(f"Continuing to level {self.player.level}")
            
    def _render_upgrade(self):
        """Render upgrade state"""
        from src.ui import display_text
        
        # Display upgrade screen title
        display_text(
            self.screen,
            "Upgrade Your Character",
            self.fonts["large"],
            self.colors["white"],
            self.width // 2,
            self.height // 3 - 50,
            center=True
        )
        
        # Display available upgrade points
        display_text(
            self.screen,
            f"Available Upgrade Points: {self.player.upgrade_points}",
            self.fonts["medium"],
            self.colors["green"],
            self.width // 2,
            self.height // 3,
            center=True
        )
        
        # Draw upgrade buttons
        click_power_button = self.ui_elements[STATE_UPGRADE]["click_power_button"]
        click_power_button.draw(self.screen)
        
        crit_chance_button = self.ui_elements[STATE_UPGRADE]["crit_chance_button"]
        crit_chance_button.draw(self.screen)
        
        crit_mult_button = self.ui_elements[STATE_UPGRADE]["crit_mult_button"]
        crit_mult_button.draw(self.screen)
        
        # Draw continue button
        continue_button = self.ui_elements[STATE_UPGRADE]["continue_button"]
        continue_button.draw(self.screen)
        
        # Display current stats
        y_offset = self.height // 2 + 100
        display_text(
            self.screen,
            "Current Stats:",
            self.fonts["medium"],
            self.colors["white"],
            self.width // 2,
            y_offset,
            center=True
        )
        
        # Click power stat
        can_upgrade = self.player.can_upgrade("click_power")
        stat_color = self.colors["green"] if can_upgrade else self.colors["white"]
        level = self.player.stats["click_power"]["level"]
        max_level = self.player.stats["click_power"]["max_level"]
        value = self.player.stats["click_power"]["value"]
        
        display_text(
            self.screen,
            f"Click Power: {value} ({level}/{max_level})",
            self.fonts["small"],
            stat_color,
            self.width // 4,
            y_offset + 30,
            center=True
        )
        
        # Critical chance stat
        can_upgrade = self.player.can_upgrade("critical_chance")
        stat_color = self.colors["green"] if can_upgrade else self.colors["white"]
        level = self.player.stats["critical_chance"]["level"]
        max_level = self.player.stats["critical_chance"]["max_level"]
        value = int(self.player.stats["critical_chance"]["value"] * 100)
        
        display_text(
            self.screen,
            f"Critical Chance: {value}% ({level}/{max_level})",
            self.fonts["small"],
            stat_color,
            self.width // 2,
            y_offset + 30,
            center=True
        )
        
        # Critical multiplier stat
        can_upgrade = self.player.can_upgrade("critical_multiplier")
        stat_color = self.colors["green"] if can_upgrade else self.colors["white"]
        level = self.player.stats["critical_multiplier"]["level"]
        max_level = self.player.stats["critical_multiplier"]["max_level"]
        value = self.player.stats["critical_multiplier"]["value"]
        
        display_text(
            self.screen,
            f"Critical Multiplier: {value}x ({level}/{max_level})",
            self.fonts["small"],
            stat_color,
            3 * self.width // 4,
            y_offset + 30,
            center=True
        )
        
        # Next level info
        display_text(
            self.screen,
            f"Next Level: {self.player.level}",
            self.fonts["medium"],
            self.colors["white"],
            self.width // 2,
            y_offset + 70,
            center=True
        )
        
    def _update_pause(self, time_delta):
        """Update pause state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
        
        # Update resume button
        resume_button = self.ui_elements[STATE_PAUSE]["resume_button"]
        if resume_button.update(mouse_pos, mouse_clicked, self.current_time):
            self.game_state = STATE_PLAYING
            logger.info("Game resumed")
        
        # Update quit button
        quit_button = self.ui_elements[STATE_PAUSE]["quit_button"]
        if quit_button.update(mouse_pos, mouse_clicked, self.current_time):
            self.player.save_progress()
            self.game_state = STATE_MENU
            logger.info("Returned to menu from pause")
            
    def _render_pause(self):
        """Render pause state"""
        from src.ui import display_text
        
        # Display pause title
        display_text(
            self.screen,
            "Game Paused",
            self.fonts["large"],
            self.colors["white"],
            self.width // 2,
            self.height // 3,
            center=True
        )
        
        # Draw resume button
        self.ui_elements[STATE_PAUSE]["resume_button"].draw(self.screen)
        
        # Draw quit button
        self.ui_elements[STATE_PAUSE]["quit_button"].draw(self.screen)