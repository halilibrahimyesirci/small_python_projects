"""
Upgrade state implementation
"""
from src.mechanics.common import *

def update_upgrade(game_engine, time_delta):
    """Update upgrade state"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Handle upgrade buttons if player has upgrade points
    if game_engine.player.upgrade_points > 0:
        # Click power upgrade
        click_power_button = game_engine.ui_elements[STATE_UPGRADE]["click_power_button"]
        if click_power_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
            game_engine.player.upgrade_stat("click_power")
            game_engine.player.upgrade_points -= 1
            game_engine.player.save_progress()
            game_engine.resource_manager.play_sound("skill_up")
            logger.info(f"Upgraded click power to {game_engine.player.stats['click_power']['value']}")
        
        # Critical chance upgrade
        crit_chance_button = game_engine.ui_elements[STATE_UPGRADE]["crit_chance_button"]
        if crit_chance_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
            game_engine.player.upgrade_stat("critical_chance")
            game_engine.player.upgrade_points -= 1
            game_engine.player.save_progress()
            game_engine.resource_manager.play_sound("skill_up")
            logger.info(f"Upgraded critical chance to {game_engine.player.stats['critical_chance']['value']}")
        
        # Critical multiplier upgrade
        crit_mult_button = game_engine.ui_elements[STATE_UPGRADE]["crit_mult_button"]
        if crit_mult_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
            game_engine.player.upgrade_stat("critical_multiplier")
            game_engine.player.upgrade_points -= 1
            game_engine.player.save_progress()
            game_engine.resource_manager.play_sound("skill_up")
            logger.info(f"Upgraded critical multiplier to {game_engine.player.stats['critical_multiplier']['value']}")
        
        # Coin upgrade
        coin_upgrade_button = game_engine.ui_elements[STATE_UPGRADE]["coin_upgrade_button"]
        if coin_upgrade_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
            game_engine.player.upgrade_coin()
            game_engine.player.upgrade_points -= 1
            game_engine.player.save_progress()
            game_engine.resource_manager.play_sound("skill_up")
            logger.info(f"Upgraded coin drop to level {game_engine.player.coin_upgrade_level}")
    
    # Continue button
    continue_button = game_engine.ui_elements[STATE_UPGRADE]["continue_button"]
    if continue_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        if game_engine.current_level.is_boss:
            # If we just defeated a boss, move to the next level
            game_engine.current_level = game_engine.level_manager.create_level(game_engine.player.level)
        
        game_engine._start_transition(STATE_PLAYING)
        logger.info("Continuing to gameplay")

def render_upgrade(game_engine):
    """Render upgrade state"""
    # Draw title
    display_text(
        game_engine.screen,
        "Character Upgrades",
        game_engine.fonts["large"],
        game_engine.colors["white"],
        game_engine.width // 2,
        80,
        center=True
    )
    
    # Display upgrade points
    display_text(
        game_engine.screen,
        f"Upgrade Points: {game_engine.player.upgrade_points}",
        game_engine.fonts["medium"],
        game_engine.colors["yellow"],
        game_engine.width // 2,
        130,
        center=True
    )
    
    # Display current stats
    stats_y = game_engine.height // 2 - 180
    stats_spacing = 30
    
    display_text(
        game_engine.screen,
        f"Click Power: {game_engine.player.stats['click_power']['value']}",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 4,
        stats_y,
        center=True
    )
    
    display_text(
        game_engine.screen,
        f"Crit Chance: {int(game_engine.player.stats['critical_chance']['value'] * 100)}%",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        3 * game_engine.width // 4,
        stats_y,
        center=True
    )
    
    display_text(
        game_engine.screen,
        f"Crit Multiplier: {game_engine.player.stats['critical_multiplier']['value']}x",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 4,
        stats_y + stats_spacing,
        center=True
    )
    
    display_text(
        game_engine.screen,
        f"Coin Drop Level: {game_engine.player.coin_upgrade_level}",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        3 * game_engine.width // 4,
        stats_y + stats_spacing,
        center=True
    )
    
    # Draw buttons with appropriate coloring
    has_points = game_engine.player.upgrade_points > 0
    
    # Click power button
    click_power_button = game_engine.ui_elements[STATE_UPGRADE]["click_power_button"]
    if has_points:
        click_power_button.border_color = game_engine.colors["blue"]
    else:
        click_power_button.border_color = game_engine.colors["black"]
    click_power_button.draw(game_engine.screen)
    
    # Critical chance button
    crit_chance_button = game_engine.ui_elements[STATE_UPGRADE]["crit_chance_button"]
    if has_points:
        crit_chance_button.border_color = game_engine.colors["blue"]
    else:
        crit_chance_button.border_color = game_engine.colors["black"]
    crit_chance_button.draw(game_engine.screen)
    
    # Critical multiplier button
    crit_mult_button = game_engine.ui_elements[STATE_UPGRADE]["crit_mult_button"]
    if has_points:
        crit_mult_button.border_color = game_engine.colors["blue"]
    else:
        crit_mult_button.border_color = game_engine.colors["black"]
    crit_mult_button.draw(game_engine.screen)
    
    # Coin upgrade button
    coin_upgrade_button = game_engine.ui_elements[STATE_UPGRADE]["coin_upgrade_button"]
    if has_points:
        coin_upgrade_button.border_color = game_engine.colors["gold"]
    else:
        coin_upgrade_button.border_color = game_engine.colors["black"]
    coin_upgrade_button.draw(game_engine.screen)
    
    # Continue button
    game_engine.ui_elements[STATE_UPGRADE]["continue_button"].draw(game_engine.screen)
    
    # Show explanation if no points
    if not has_points:
        display_text(
            game_engine.screen,
            "You have no upgrade points. Complete levels to earn more!",
            game_engine.fonts["small"],
            game_engine.colors["yellow"],
            game_engine.width // 2,
            game_engine.height - 170,
            center=True
        )
    else:
        display_text(
            game_engine.screen,
            "Click on a button to upgrade that stat",
            game_engine.fonts["small"],
            game_engine.colors["white"],
            game_engine.width // 2,
            game_engine.height - 170,
            center=True
        )