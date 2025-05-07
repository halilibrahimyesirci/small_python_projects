"""
Shop state implementation
"""
from src.mechanics.common import *

def update_shop(game_engine, time_delta):
    """Update shop state"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Back button
    back_button = game_engine.ui_elements[STATE_SHOP]["back_button"]
    if back_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        # Return to previous state
        previous_state = game_engine.previous_state if game_engine.previous_state else STATE_PLAYING
        game_engine._start_transition(previous_state)
        logger.info(f"Returning to {previous_state} from shop")
    
    # Update shop item buttons
    for item, button in game_engine.ui_elements[STATE_SHOP]["item_buttons"]:
        # Update button appearance based on affordability
        can_afford = game_engine.coin_counter >= item.cost
        if not can_afford:
            button.colors = {
                "normal": (100, 100, 100),  # Grayed out
                "hover": (120, 120, 120),
                "clicked": (150, 150, 150)
            }
        else:
            button.colors = game_engine.colors["button"].copy()
            
        if button.update(mouse_pos, mouse_clicked, game_engine.current_time):
            # Try to purchase item
            if can_afford:
                game_engine.coin_counter -= item.cost
                item.apply_effect(game_engine.player)
                game_engine.resource_manager.play_sound("skill_up")  # Play skill up sound for purchases
                
                # Create text particle for purchase
                text_particle = TextParticle(
                    mouse_pos[0],
                    mouse_pos[1] - 30,
                    f"Purchased: {item.name}",
                    game_engine.fonts["medium"],
                    game_engine.colors["green"],
                    speed=1.5,
                    life=1.5
                )
                
                # Add to playing state particles if they exist
                if "particles" in game_engine.ui_elements[STATE_PLAYING]:
                    game_engine.ui_elements[STATE_PLAYING]["particles"].add_particle(text_particle)
                
                logger.info(f"Purchased item: {item.name} for {item.cost} coins")
            else:
                # Show cannot afford message
                game_engine.resource_manager.play_sound("nothing_happend")  # Play error sound
                
                # Create text particle for cannot afford
                text_particle = TextParticle(
                    mouse_pos[0],
                    mouse_pos[1] - 30,
                    f"Cannot afford: {item.cost} coins required",
                    game_engine.fonts["medium"],
                    game_engine.colors["red"],
                    speed=1.5,
                    life=1.5
                )
                
                # Add to playing state particles if they exist
                if "particles" in game_engine.ui_elements[STATE_PLAYING]:
                    game_engine.ui_elements[STATE_PLAYING]["particles"].add_particle(text_particle)
                
                logger.info(f"Cannot afford item: {item.name} (cost: {item.cost}, coins: {game_engine.coin_counter})")

def render_shop(game_engine):
    """Render shop state"""
    # Draw background overlay
    overlay = pygame.Surface((game_engine.width, game_engine.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    game_engine.screen.blit(overlay, (0, 0))
    
    # Draw shop title
    display_text(
        game_engine.screen,
        "Shop",
        game_engine.fonts["large"],
        game_engine.colors["white"],
        game_engine.width // 2,
        80,
        center=True
    )
    
    # Display coin counter
    display_text(
        game_engine.screen,
        f"Coins: {game_engine.coin_counter}",
        game_engine.fonts["medium"],
        game_engine.colors["gold"],
        game_engine.width // 2,
        130,
        center=True
    )
    
    # Draw item buttons
    for item, button in game_engine.ui_elements[STATE_SHOP]["item_buttons"]:
        button.draw(game_engine.screen)
        
        # Draw item description
        description_y = button.rect.bottom + 5
        desc_lines = item.description.split(". ")
        for i, line in enumerate(desc_lines):
            display_text(
                game_engine.screen,
                line + ("." if i < len(desc_lines) - 1 else ""),
                game_engine.fonts["small"],
                game_engine.colors["white"],
                button.rect.centerx,
                description_y + i * 20,
                center=True
            )
    
    # Draw back button
    game_engine.ui_elements[STATE_SHOP]["back_button"].draw(game_engine.screen)