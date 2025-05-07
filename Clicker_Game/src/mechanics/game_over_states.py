"""
Game over states implementation (win and lose)
"""
from src.mechanics.common import *

def update_game_over_win(game_engine, time_delta):
    """Update game over (win) state"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Update player stats based on completion
    if not hasattr(game_engine, 'win_stats_updated') or not game_engine.win_stats_updated:
        # Update player level
        game_engine.player.level += 1
        
        # Update highest level if needed
        if game_engine.player.level > game_engine.player.highest_level:
            game_engine.player.highest_level = game_engine.player.level
        
        # Grant upgrade points
        if game_engine.current_level.is_boss:
            game_engine.player.upgrade_points += 3  # More points for boss levels
        else:
            game_engine.player.upgrade_points += 1
        
        # Save progress
        game_engine.player.save_progress()
        
        # Flag that stats were updated
        game_engine.win_stats_updated = True
        
        logger.info(f"Win rewards granted. Player now level {game_engine.player.level} with {game_engine.player.upgrade_points} upgrade points")
        
    # Update continue button
    continue_button = game_engine.ui_elements[STATE_GAME_OVER_WIN]["continue_button"]
    if continue_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        # Create new level for next round
        game_engine.current_level = game_engine.level_manager.create_level(game_engine.player.level)
        
        # Reset win stats flag
        game_engine.win_stats_updated = False
        
        # Only go to upgrade screen after boss levels
        if game_engine.current_level and game_engine.current_level.is_boss:
            game_engine._start_transition(STATE_UPGRADE)
            logger.info("Showing upgrade screen after defeating boss level")
        else:
            game_engine._start_transition(STATE_MENU)
            logger.info("Returning to menu after level completion")

def render_game_over_win(game_engine):
    """Render game over (win) state"""
    # Display victory message
    title_y_offset = math.sin(game_engine.current_time * 2) * 5  # Gentle float effect
    display_text(
        game_engine.screen,
        "Level Complete!",
        game_engine.fonts["large"],
        game_engine.colors["green"],
        game_engine.width // 2,
        game_engine.height // 3 + title_y_offset,
        center=True
    )
    
    # Display stats
    stats_y = game_engine.height // 2
    display_text(
        game_engine.screen,
        f"Level: {game_engine.player.level}",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 2,
        stats_y,
        center=True
    )
    
    display_text(
        game_engine.screen,
        f"Upgrade Points: {game_engine.player.upgrade_points}",
        game_engine.fonts["medium"],
        game_engine.colors["yellow"],
        game_engine.width // 2,
        stats_y + 40,
        center=True
    )
    
    # Show coin count
    if game_engine.coin_counter > 0:
        display_text(
            game_engine.screen,
            f"Coins: {game_engine.coin_counter}",
            game_engine.fonts["medium"],
            game_engine.colors["gold"],
            game_engine.width // 2,
            stats_y + 80,
            center=True
        )
    
    # Draw continue button
    game_engine.ui_elements[STATE_GAME_OVER_WIN]["continue_button"].draw(game_engine.screen)

def update_game_over_lose(game_engine, time_delta):
    """Update game over (lose) state"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Update retry button
    retry_button = game_engine.ui_elements[STATE_GAME_OVER_LOSE]["retry_button"]
    if retry_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        # Reset the current level
        game_engine.clicks = 0
        game_engine.start_ticks = pygame.time.get_ticks()
        
        # If it's a boss level, reset the boss health
        if game_engine.current_level and game_engine.current_level.is_boss:
            game_engine.current_level.reset_boss_health()
        
        game_engine._start_transition(STATE_PLAYING)
        logger.info(f"Retrying level {game_engine.current_level.level_number}")
    
    # Update menu button
    menu_button = game_engine.ui_elements[STATE_GAME_OVER_LOSE]["menu_button"]
    if menu_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        game_engine._start_transition(STATE_MENU)
        logger.info("Returning to menu after defeat")

def render_game_over_lose(game_engine):
    """Render game over (lose) state"""
    # Display defeat message
    display_text(
        game_engine.screen,
        "Level Failed!",
        game_engine.fonts["large"],
        game_engine.colors["red"],
        game_engine.width // 2,
        game_engine.height // 3,
        center=True
    )
    
    # Display stats
    stats_y = game_engine.height // 2
    if game_engine.current_level:
        if game_engine.current_level.is_boss:
            health_percent = game_engine.current_level.get_health_percent() * 100
            display_text(
                game_engine.screen,
                f"Boss Health: {int(health_percent)}%",
                game_engine.fonts["medium"],
                game_engine.colors["white"],
                game_engine.width // 2,
                stats_y,
                center=True
            )
        else:
            progress_percent = min(100, (game_engine.clicks / game_engine.current_level.click_target) * 100)
            display_text(
                game_engine.screen,
                f"Progress: {int(progress_percent)}%",
                game_engine.fonts["medium"],
                game_engine.colors["white"],
                game_engine.width // 2,
                stats_y,
                center=True
            )
    
    # Draw buttons
    game_engine.ui_elements[STATE_GAME_OVER_LOSE]["retry_button"].draw(game_engine.screen)
    game_engine.ui_elements[STATE_GAME_OVER_LOSE]["menu_button"].draw(game_engine.screen)