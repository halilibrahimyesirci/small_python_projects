"""
Ability selection state implementation
"""
from src.mechanics.common import *

def update_ability_select(game_engine, time_delta):
    """Update ability selection state"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Update ability buttons
    for ability_name, button in game_engine.ui_elements[STATE_ABILITY_SELECT]["ability_buttons"]:
        if button.update(mouse_pos, mouse_clicked, game_engine.current_time):
            # Activate ability
            ability = game_engine.player_abilities[ability_name]
            ability["active"] = True
            ability["duration"] = 30  # 30 seconds duration
            ability["cooldown"] = 0
            
            game_engine.resource_manager.play_sound("skill_up")
            logger.info(f"Activated ability: {ability_name}")
            
            # Move to game over win state 
            game_engine._start_transition(STATE_GAME_OVER_WIN)
    
    # Skip button
    skip_button = game_engine.ui_elements[STATE_ABILITY_SELECT]["skip_button"]
    if skip_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        game_engine._start_transition(STATE_GAME_OVER_WIN)
        logger.info("Skipped ability selection")

def render_ability_select(game_engine):
    """Render ability selection state"""
    # Draw background overlay
    overlay = pygame.Surface((game_engine.width, game_engine.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    game_engine.screen.blit(overlay, (0, 0))
    
    # Display title
    display_text(
        game_engine.screen,
        "Select an Ability",
        game_engine.fonts["large"],
        game_engine.colors["white"],
        game_engine.width // 2,
        80,
        center=True
    )
    
    # Display explanation
    display_text(
        game_engine.screen,
        "Choose one ability to activate for 30 seconds:",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 2,
        130,
        center=True
    )
    
    # Draw ability buttons
    for ability_name, button in game_engine.ui_elements[STATE_ABILITY_SELECT]["ability_buttons"]:
        button.draw(game_engine.screen)
        
        # Draw ability description
        ability = game_engine.player_abilities[ability_name]
        description_y = button.rect.bottom + 5
        
        display_text(
            game_engine.screen,
            ability["description"],
            game_engine.fonts["small"],
            game_engine.colors["white"],
            button.rect.centerx,
            description_y,
            center=True
        )
    
    # Draw skip button
    game_engine.ui_elements[STATE_ABILITY_SELECT]["skip_button"].draw(game_engine.screen)