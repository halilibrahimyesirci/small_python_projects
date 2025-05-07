"""
Game state management module for RPG Clicker Game
"""
import pygame
import random
import logging
import math
import os
from src.ui import Button, display_text, TextParticle
from src.entities.coin import Coin

logger = logging.getLogger(__name__)

# Game states
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER_WIN = "GAME_OVER_WIN"
STATE_GAME_OVER_LOSE = "GAME_OVER_LOSE"
STATE_UPGRADE = "UPGRADE"
STATE_PAUSE = "PAUSE"
STATE_SETTINGS = "SETTINGS"
STATE_ABILITY_SELECT = "ABILITY_SELECT"
STATE_ESC_MENU = "ESC_MENU"

# Game constants
CLICK_DELAY = 0.45  # Delay between clicks in seconds (match with engine.py)

# Utility functions for game states

def update_menu(game_engine, time_delta):
    """Update menu state"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Update play button
    play_button = game_engine.ui_elements[STATE_MENU]["play_button"]
    if play_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        game_engine._start_transition(STATE_PLAYING)
        game_engine.clicks = 0
        game_engine.start_ticks = pygame.time.get_ticks()
        
        # Play appropriate music
        if game_engine.current_level.is_boss:
            game_engine.resource_manager.play_music("boss")
        else:
            game_engine.resource_manager.play_music("gameplay")
            
        logger.info(f"Starting level {game_engine.current_level.level_number}")
    
    # Update settings button
    settings_button = game_engine.ui_elements[STATE_MENU]["settings_button"]
    if settings_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        game_engine._start_transition(STATE_SETTINGS)
        logger.info("Opening settings menu")

def render_menu(game_engine):
    """Render menu state"""
    # Game title with simple animation
    title_y_offset = math.sin(game_engine.current_time * 2) * 5  # Gentle float effect
    display_text(
        game_engine.screen,
        "RPG Clicker",
        game_engine.fonts["large"],
        game_engine.colors["white"],
        game_engine.width // 2,
        game_engine.height // 3 + title_y_offset,
        center=True
    )
    
    # Level info
    if game_engine.current_level:
        display_text(
            game_engine.screen,
            game_engine.current_level.get_description(),
            game_engine.fonts["medium"],
            game_engine.colors["white"],
            game_engine.width // 2,
            game_engine.height // 2 - 50,
            center=True
        )
        
        display_text(
            game_engine.screen,
            game_engine.current_level.get_objective_text(),
            game_engine.fonts["medium"],
            game_engine.colors["white"],
            game_engine.width // 2,
            game_engine.height // 2 - 20,
            center=True
        )
    
    # Draw play button
    game_engine.ui_elements[STATE_MENU]["play_button"].draw(game_engine.screen)
    
    # Draw settings button
    game_engine.ui_elements[STATE_MENU]["settings_button"].draw(game_engine.screen)
    
    # Player stats
    stats_y = game_engine.height - 80
    display_text(
        game_engine.screen,
        f"Highest Level: {game_engine.player.highest_level}",
        game_engine.fonts["small"],
        game_engine.colors["white"],
        game_engine.width // 2,
        stats_y,
        center=True
    )
    
    display_text(
        game_engine.screen,
        f"Click Power: {game_engine.player.stats['click_power']['value']}",
        game_engine.fonts["small"],
        game_engine.colors["white"],
        game_engine.width // 4,
        stats_y + 20,
        center=True
    )
    
    display_text(
        game_engine.screen,
        f"Crit Chance: {int(game_engine.player.stats['critical_chance']['value'] * 100)}%",
        game_engine.fonts["small"],
        game_engine.colors["white"],
        game_engine.width // 2,
        stats_y + 20,
        center=True
    )
    
    display_text(
        game_engine.screen,
        f"Crit Multiplier: {game_engine.player.stats['critical_multiplier']['value']}x",
        game_engine.fonts["small"],
        game_engine.colors["white"],
        3 * game_engine.width // 4,
        stats_y + 20,
        center=True
    )

def update_playing(game_engine, time_delta):
    """Update playing state"""
    from src.ui import ClickParticle
    
    # Get mouse state
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]  # Left button
    
    # Check for spacebar press to open upgrade menu
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        game_engine._start_transition(STATE_UPGRADE)
        logger.info("Opening upgrade menu via spacebar")
        return
    
    # Update falling coins
    for coin in game_engine.coins[:]:
        if coin.update(mouse_pos, mouse_pressed):
            # Coin collected
            coin_value = coin.value
            if game_engine.player_abilities["double_coins"]["active"]:
                coin_value *= 2
            
            game_engine.coin_counter += coin_value
            game_engine.resource_manager.play_sound("level_up")  # Use level_up sound for coin collection
            
            # Create coin text particle
            text_particle = TextParticle(
                coin.x,
                coin.y - 20,
                f"+{coin_value} Coin",
                game_engine.fonts["small"],
                game_engine.colors["gold"],
                speed=1.5,
                life=0.8
            )
            game_engine.ui_elements[STATE_PLAYING]["particles"].add_particle(text_particle)
            
            game_engine.coins.remove(coin)
        elif not coin.alive:
            game_engine.coins.remove(coin)
            
    # Spawn new coins based on clicks
    coin_spawn_threshold = max(10, 50 - game_engine.player.coin_upgrade_level * 5)  # Reduce threshold with upgrades
    if game_engine.clicks > 0 and game_engine.clicks % coin_spawn_threshold == 0 and random.random() < 0.3:
        coin_x = random.randint(50, game_engine.width - 50)
        coin_y = -20  # Start above the screen
        new_coin = Coin(coin_x, coin_y, value=1 + game_engine.player.coin_upgrade_level // 2)
        game_engine.coins.append(new_coin)
    
    # Update click button
    click_button = game_engine.ui_elements[STATE_PLAYING]["click_button"]
    
    # Handle boss abilities
    if game_engine.current_level and game_engine.current_level.is_boss and game_engine.current_level.ability_active:
        if game_engine.current_level.boss_ability == "move_button":
            # Randomly move button if ability is active
            if random.random() < 0.05:  # 5% chance per frame
                click_button.rect.x = random.randint(50, game_engine.width - 250)
                click_button.rect.y = random.randint(100, game_engine.height - 150)
                
        elif game_engine.current_level.boss_ability == "click_block":
            # Block some clicks (implemented in the button click handling below)
            pass
    
    # Check if button was clicked
    button_clicked = click_button.update(mouse_pos, mouse_pressed, game_engine.current_time)
    
    # Implement click delay unless rapid clicking ability is active
    can_click = (game_engine.current_time - game_engine.last_click_time >= CLICK_DELAY) or game_engine.player_abilities["rapid_clicking"]["active"]
    
    if button_clicked and can_click:
        game_engine.last_click_time = game_engine.current_time  # Update last click time
        
        # Process boss ability that blocks clicks
        if (game_engine.current_level and game_engine.current_level.is_boss and 
            game_engine.current_level.ability_active and 
            game_engine.current_level.boss_ability == "click_block" and
            random.random() < 0.5):  # 50% chance to block
            
            # Click blocked
            logger.info("Click blocked by boss ability")
            
            # Show blocked text
            text_particle = TextParticle(
                mouse_pos[0],
                mouse_pos[1] - 20,
                "BLOCKED!",
                game_engine.fonts["medium"],
                game_engine.colors["red"],
                speed=1,
                life=0.8
            )
            game_engine.ui_elements[STATE_PLAYING]["particles"].add_particle(text_particle)
        else:
            # Regular click processing
            combo_meter = game_engine.ui_elements[STATE_PLAYING]["combo_meter"]
            combo_meter.add_click(game_engine.current_time)
            combo_bonus = combo_meter.get_combo_bonus()
            
            # Determine if this is a critical click
            crit_chance = game_engine.player.stats["critical_chance"]["value"]
            # Apply crit master ability if active
            if game_engine.player_abilities["crit_master"]["active"]:
                crit_chance *= 1.5
            
            is_critical = random.random() < crit_chance
            
            # Calculate click value
            click_power = game_engine.player.stats["click_power"]["value"]
            crit_multiplier = game_engine.player.stats["critical_multiplier"]["value"] if is_critical else 1
            combo_multiplier = 1 + combo_bonus
            
            click_value = int(click_power * crit_multiplier * combo_multiplier)
            
            # Apply boss weakener ability if active against boss
            if game_engine.current_level and game_engine.current_level.is_boss and game_engine.player_abilities["boss_weakener"]["active"]:
                click_value = int(click_value * 1.5)
            
            # Update clicks
            game_engine.clicks += click_value
            game_engine.player.total_clicks += click_value
            
            # Play sound
            if is_critical:
                game_engine.resource_manager.play_sound("critical")
            else:
                game_engine.resource_manager.play_sound("click")
            
            # Add visual feedback
            # Text particle for click value
            text_color = game_engine.colors["yellow"] if is_critical else game_engine.colors["white"]
            text_particle = TextParticle(
                mouse_pos[0],
                mouse_pos[1] - 20,
                f"+{click_value}",
                game_engine.fonts["medium"] if is_critical else game_engine.fonts["small"],
                text_color,
                speed=1.5 if is_critical else 1,
                life=1.0
            )
            game_engine.ui_elements[STATE_PLAYING]["particles"].add_particle(text_particle)
            
            # Add click particles - more diverse particles with V0.3.2
            particle_colors = [(255, 255, 0)] if is_critical else [
                (150, 150, 255), 
                (100, 100, 255), 
                (200, 200, 255)
            ]
            
            for _ in range(5 if is_critical else 3):
                particle_color = random.choice(particle_colors)
                particle = ClickParticle(
                    mouse_pos[0],
                    mouse_pos[1],
                    particle_color,
                    size=3 + random.randint(0, 3),
                    speed=2 + random.random() * 2,
                    life=0.5 + random.random() * 0.5
                )
                game_engine.ui_elements[STATE_PLAYING]["particles"].add_particle(particle)
            
            # Update boss health if this is a boss level
            if game_engine.current_level and game_engine.current_level.is_boss:
                boss_defeated = game_engine.current_level.damage_boss(click_value)
                if boss_defeated:
                    game_engine._setup_ability_selection()  # Set up ability selection after defeating boss
                    game_engine._start_transition(STATE_ABILITY_SELECT)
                    game_engine.resource_manager.play_sound("level_up")
                    logger.info(f"Boss defeated! Level {game_engine.current_level.level_number} completed.")
    
    # Auto clicker ability if active
    if game_engine.player_abilities["auto_clicker"]["active"]:
        game_engine.auto_click_timer = getattr(game_engine, 'auto_click_timer', 0) + time_delta
        if game_engine.auto_click_timer >= 0.5:  # Click every 0.5 seconds
            game_engine.auto_click_timer = 0
            _process_auto_click(game_engine)
            
    # Update player abilities
    for ability_name, ability in game_engine.player_abilities.items():
        if ability["active"]:
            ability["duration"] -= time_delta
            if ability["duration"] <= 0:
                ability["active"] = False
                ability["cooldown"] = 60  # 60 second cooldown
                logger.info(f"Ability ended: {ability_name}")
    
    # Update combo meter
    combo_meter = game_engine.ui_elements[STATE_PLAYING]["combo_meter"]
    combo_meter.update(game_engine.current_time)
    
    # Update particles
    game_engine.ui_elements[STATE_PLAYING]["particles"].update()
    
    # Update progress bar
    progress_bar = game_engine.ui_elements[STATE_PLAYING]["progress_bar"]
    if game_engine.current_level:
        if game_engine.current_level.is_boss:
            # For boss levels, show boss health
            progress_bar.set_progress(1 - game_engine.current_level.get_health_percent())
        else:
            # For regular levels, show progress toward click target
            progress_percent = min(1.0, game_engine.clicks / game_engine.current_level.click_target)
            progress_bar.set_progress(progress_percent)
            
            # Check if level is complete (enough clicks)
            if game_engine.clicks >= game_engine.current_level.click_target:
                game_engine._start_transition(STATE_GAME_OVER_WIN)
                game_engine.resource_manager.play_sound("level_up")
                logger.info(f"Level {game_engine.current_level.level_number} completed!")

def _process_auto_click(game_engine):
    """Process an automatic click from the auto-clicker ability"""
    if not game_engine.current_level:
        return
        
    # Similar logic to regular clicks but simpler
    click_power = game_engine.player.stats["click_power"]["value"]
    game_engine.clicks += click_power
    game_engine.player.total_clicks += click_power
    
    # Update boss health if this is a boss level
    if game_engine.current_level.is_boss:
        boss_defeated = game_engine.current_level.damage_boss(click_power)
        if boss_defeated:
            game_engine._setup_ability_selection()
            game_engine._start_transition(STATE_ABILITY_SELECT)
            game_engine.resource_manager.play_sound("level_up")
            logger.info(f"Boss defeated by auto-clicker! Level {game_engine.current_level.level_number} completed.")

def render_playing(game_engine):
    """Render playing state"""
    # Draw click button
    game_engine.ui_elements[STATE_PLAYING]["click_button"].draw(game_engine.screen)
    
    # Draw falling coins
    for coin in game_engine.coins:
        coin.draw(game_engine.screen)
    
    # Draw progress bar
    game_engine.ui_elements[STATE_PLAYING]["progress_bar"].draw(game_engine.screen)
    
    # Draw combo meter if active
    combo_meter = game_engine.ui_elements[STATE_PLAYING]["combo_meter"]
    if combo_meter.active:
        combo_meter.draw(game_engine.screen)
        
    # Draw particles
    game_engine.ui_elements[STATE_PLAYING]["particles"].draw(game_engine.screen)
    
    # Display active abilities
    active_count = 0
    for ability_name, ability in game_engine.player_abilities.items():
        if ability["active"]:
            display_text(
                game_engine.screen,
                f"{ability_name.replace('_', ' ').title()}: {int(ability['duration'])}s",
                game_engine.fonts["small"],
                game_engine.colors["green"],
                10,
                10 + active_count * 20,
                center=False
            )
            active_count += 1
    
    # Display coin counter
    if game_engine.coin_counter > 0:
        display_text(
            game_engine.screen,
            f"Coins: {game_engine.coin_counter}",
            game_engine.fonts["medium"],
            game_engine.colors["gold"],
            game_engine.width - 80,
            10,
            center=False
        )

def update_settings(game_engine, time_delta):
    """Update settings menu state"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Handle sound volume slider
    sound_slider = game_engine.ui_elements[STATE_SETTINGS]["sound_slider"]
    if sound_slider.update(mouse_pos, mouse_clicked):
        game_engine.audio_settings["sound_volume"] = sound_slider.value
        # Apply setting immediately
        for sound in game_engine.resource_manager.sounds.values():
            sound.set_volume(game_engine.audio_settings["sound_volume"])
    
    # Handle music volume slider
    music_slider = game_engine.ui_elements[STATE_SETTINGS]["music_slider"]
    if music_slider.update(mouse_pos, mouse_clicked):
        game_engine.audio_settings["music_volume"] = music_slider.value
        # Apply setting immediately
        pygame.mixer.music.set_volume(game_engine.audio_settings["music_volume"])
    
    # Handle music selection buttons
    for music_file, button in game_engine.ui_elements[STATE_SETTINGS]["music_buttons"]:
        if button.update(mouse_pos, mouse_clicked, game_engine.current_time):
            game_engine.audio_settings["current_music"] = music_file
            # Play selected music
            music_path = os.path.join("assets", "music", music_file)
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                pygame.mixer.music.set_volume(game_engine.audio_settings["music_volume"])
                logger.info(f"Playing music: {music_file}")
            except Exception as e:
                logger.error(f"Error playing music '{music_file}': {e}")
    
    # Handle back button
    back_button = game_engine.ui_elements[STATE_SETTINGS]["back_button"]
    if back_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        # Return to previous state
        game_engine.game_state = game_engine.previous_state or STATE_MENU

def render_settings(game_engine):
    """Render settings menu state"""
    # Display settings title
    display_text(
        game_engine.screen,
        "Settings",
        game_engine.fonts["large"],
        game_engine.colors["white"],
        game_engine.width // 2,
        50,
        center=True
    )
    
    # Draw sound volume slider
    game_engine.ui_elements[STATE_SETTINGS]["sound_slider"].draw(game_engine.screen)
    
    # Draw music volume slider
    game_engine.ui_elements[STATE_SETTINGS]["music_slider"].draw(game_engine.screen)
    
    # Draw music selection title
    display_text(
        game_engine.screen,
        "Select Music Track:",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 2,
        game_engine.height // 3 + 100,
        center=True
    )
    
    # Draw music selection buttons
    for music_file, button in game_engine.ui_elements[STATE_SETTINGS]["music_buttons"]:
        # Highlight current selection
        if music_file == game_engine.audio_settings["current_music"]:
            button.border_color = game_engine.colors["green"]
            button.border_width = 3
        else:
            button.border_color = game_engine.colors["purple"]
            button.border_width = 2
            
        button.draw(game_engine.screen)
    
    # Draw back button
    game_engine.ui_elements[STATE_SETTINGS]["back_button"].draw(game_engine.screen)

def update_upgrade(game_engine, time_delta):
    """Update upgrade state"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Update click power button
    click_power_button = game_engine.ui_elements[STATE_UPGRADE]["click_power_button"]
    if click_power_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        if game_engine.player.upgrade_stat("click_power"):
            game_engine.player.save_progress()
            logger.info("Upgraded click power")
    
    # Update critical chance button
    crit_chance_button = game_engine.ui_elements[STATE_UPGRADE]["crit_chance_button"]
    if crit_chance_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        if game_engine.player.upgrade_stat("critical_chance"):
            game_engine.player.save_progress()
            logger.info("Upgraded critical chance")
    
    # Update critical multiplier button
    crit_mult_button = game_engine.ui_elements[STATE_UPGRADE]["crit_mult_button"]
    if crit_mult_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        if game_engine.player.upgrade_stat("critical_multiplier"):
            game_engine.player.save_progress()
            logger.info("Upgraded critical multiplier")
    
    # Update coin upgrade button
    coin_upgrade_button = game_engine.ui_elements[STATE_UPGRADE]["coin_upgrade_button"]
    if coin_upgrade_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        if game_engine.player.upgrade_coin_rate():
            game_engine.player.save_progress()
            logger.info("Upgraded coin drop rate")
    
    # Update continue button
    continue_button = game_engine.ui_elements[STATE_UPGRADE]["continue_button"]
    if continue_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        # Create new level and go back to menu
        game_engine.current_level = game_engine.level_manager.create_level(game_engine.player.level)
        game_engine.game_state = STATE_MENU
        logger.info(f"Continuing to level {game_engine.player.level}")

def render_upgrade(game_engine):
    """Render upgrade state"""
    # Display upgrade screen title
    display_text(
        game_engine.screen,
        "Upgrade Your Character",
        game_engine.fonts["large"],
        game_engine.colors["white"],
        game_engine.width // 2,
        game_engine.height // 3 - 50,
        center=True
    )
    
    # Display available upgrade points
    display_text(
        game_engine.screen,
        f"Available Upgrade Points: {game_engine.player.upgrade_points}",
        game_engine.fonts["medium"],
        game_engine.colors["green"],
        game_engine.width // 2,
        game_engine.height // 3,
        center=True
    )
    
    # Display coin count
    display_text(
        game_engine.screen,
        f"Coins: {game_engine.coin_counter}",
        game_engine.fonts["medium"],
        game_engine.colors["gold"],
        game_engine.width // 2,
        game_engine.height // 3 + 30,
        center=True
    )
    
    # Draw upgrade buttons
    click_power_button = game_engine.ui_elements[STATE_UPGRADE]["click_power_button"]
    click_power_button.draw(game_engine.screen)
    
    crit_chance_button = game_engine.ui_elements[STATE_UPGRADE]["crit_chance_button"]
    crit_chance_button.draw(game_engine.screen)
    
    crit_mult_button = game_engine.ui_elements[STATE_UPGRADE]["crit_mult_button"]
    crit_mult_button.draw(game_engine.screen)
    
    coin_upgrade_button = game_engine.ui_elements[STATE_UPGRADE]["coin_upgrade_button"]
    coin_upgrade_button.draw(game_engine.screen)
    
    # Draw continue button
    continue_button = game_engine.ui_elements[STATE_UPGRADE]["continue_button"]
    continue_button.draw(game_engine.screen)
    
    # Display current stats
    y_offset = game_engine.height // 2 + 100
    display_text(
        game_engine.screen,
        "Current Stats:",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 2,
        y_offset,
        center=True
    )
    
    # Click power stat
    can_upgrade = game_engine.player.can_upgrade("click_power")
    stat_color = game_engine.colors["green"] if can_upgrade else game_engine.colors["white"]
    level = game_engine.player.stats["click_power"]["level"]
    max_level = game_engine.player.stats["click_power"]["max_level"]
    value = game_engine.player.stats["click_power"]["value"]
    
    display_text(
        game_engine.screen,
        f"Click Power: {value} ({level}/{max_level})",
        game_engine.fonts["small"],
        stat_color,
        game_engine.width // 4,
        y_offset + 30,
        center=True
    )
    
    # Critical chance stat
    can_upgrade = game_engine.player.can_upgrade("critical_chance")
    stat_color = game_engine.colors["green"] if can_upgrade else game_engine.colors["white"]
    level = game_engine.player.stats["critical_chance"]["level"]
    max_level = game_engine.player.stats["critical_chance"]["max_level"]
    value = int(game_engine.player.stats["critical_chance"]["value"] * 100)
    
    display_text(
        game_engine.screen,
        f"Critical Chance: {value}% ({level}/{max_level})",
        game_engine.fonts["small"],
        stat_color,
        game_engine.width // 2,
        y_offset + 30,
        center=True
    )
    
    # Critical multiplier stat
    can_upgrade = game_engine.player.can_upgrade("critical_multiplier")
    stat_color = game_engine.colors["green"] if can_upgrade else game_engine.colors["white"]
    level = game_engine.player.stats["critical_multiplier"]["level"]
    max_level = game_engine.player.stats["critical_multiplier"]["max_level"]
    value = game_engine.player.stats["critical_multiplier"]["value"]
    
    display_text(
        game_engine.screen,
        f"Critical Multiplier: {value}x ({level}/{max_level})",
        game_engine.fonts["small"],
        stat_color,
        3 * game_engine.width // 4,
        y_offset + 30,
        center=True
    )
    
    # Coin upgrade stat
    coin_level = game_engine.player.coin_upgrade_level
    coin_max_level = game_engine.player.coin_upgrade_max_level
    
    display_text(
        game_engine.screen,
        f"Coin Drop Rate: ({coin_level}/{coin_max_level})",
        game_engine.fonts["small"],
        game_engine.colors["gold"],
        game_engine.width // 2,
        y_offset + 60,
        center=True
    )
    
    # Next level info
    display_text(
        game_engine.screen,
        f"Next Level: {game_engine.player.level}",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 2,
        y_offset + 90,
        center=True
    )

def update_ability_select(game_engine, time_delta):
    """Update ability selection screen"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Check if any ability is clicked
    for ability_name, button in game_engine.ui_elements[STATE_ABILITY_SELECT]["ability_buttons"]:
        if button.update(mouse_pos, mouse_clicked, game_engine.current_time):
            # Activate the selected ability
            ability = game_engine.player_abilities[ability_name]
            ability["active"] = True
            ability["duration"] = 30  # 30 seconds duration
            ability["cooldown"] = 0
            
            logger.info(f"Activated ability: {ability_name}")
            
            # Move to win screen
            game_engine._start_transition(STATE_GAME_OVER_WIN)
            
    # Handle continue button
    continue_button = game_engine.ui_elements[STATE_ABILITY_SELECT]["continue_button"]
    if continue_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        # Skip ability selection and go to win screen
        game_engine._start_transition(STATE_GAME_OVER_WIN)

def render_ability_select(game_engine):
    """Render ability selection screen"""
    # Display selection title
    display_text(
        game_engine.screen,
        "Select Special Ability",
        game_engine.fonts["large"],
        game_engine.colors["white"],
        game_engine.width // 2,
        50,
        center=True
    )
    
    display_text(
        game_engine.screen,
        "Choose a special ability to activate:",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 2,
        100,
        center=True
    )
    
    # Draw ability buttons
    for ability_name, button in game_engine.ui_elements[STATE_ABILITY_SELECT]["ability_buttons"]:
        button.draw(game_engine.screen)
        
        # Draw ability description below button
        description = game_engine.player_abilities[ability_name]["description"]
        description_y = button.rect.bottom + 5
        
        display_text(
            game_engine.screen,
            description,
            game_engine.fonts["small"],
            game_engine.colors["white"],
            game_engine.width // 2,
            description_y,
            center=True
        )
        
    # Draw continue button
    game_engine.ui_elements[STATE_ABILITY_SELECT]["continue_button"].draw(game_engine.screen)