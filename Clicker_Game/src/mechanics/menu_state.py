"""
Menu state implementation
"""
from src.mechanics.common import *

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