"""
ESC menu state implementation
"""
from src.mechanics.common import *

def update_esc_menu(game_engine, time_delta):
    """Update ESC menu state"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Resume button
    resume_button = game_engine.ui_elements[STATE_ESC_MENU]["resume_button"]
    if resume_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        game_engine._start_transition(STATE_PLAYING)
        logger.info("Game resumed from ESC menu")
    
    # Settings button
    settings_button = game_engine.ui_elements[STATE_ESC_MENU]["settings_button"]
    if settings_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        game_engine._start_transition(STATE_SETTINGS)
        logger.info("Opening settings from ESC menu")
    
    # Shop button
    shop_button = game_engine.ui_elements[STATE_ESC_MENU]["shop_button"]
    if shop_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        # Initialize the shop items if not already done
        if not hasattr(game_engine, 'shop_manager'):
            from src.shop import ShopManager
            game_engine.shop_manager = ShopManager(game_engine.resource_manager)
            
        # Reset shop UI
        from src.ui import Button
        game_engine.ui_elements[STATE_SHOP]["item_buttons"] = []  # Clear existing buttons
        
        item_width, item_height = 350, 70  # Increased height for better visibility
        item_spacing = 30  # Increased spacing between items
        item_start_y = game_engine.height // 4
        
        # Create buttons for each shop item with improved layout
        for i, item in enumerate(game_engine.shop_manager.items):
            item_rect = pygame.Rect(
                game_engine.width // 2 - item_width // 2,
                item_start_y + i * (item_height + item_spacing),
                item_width,
                item_height
            )
            
            # Button colors based on affordability
            colors = game_engine.colors["button"].copy()
            
            # Create button for the item
            item_button = Button(
                item_rect,
                f"{item.name} - {item.cost} coins",
                game_engine.fonts["medium"],
                colors,
                border_width=2,
                border_color=game_engine.colors["blue"]
            )
            
            game_engine.ui_elements[STATE_SHOP]["item_buttons"].append((item, item_button))
        
        game_engine._start_transition(STATE_SHOP)
        logger.info("Opening shop from ESC menu")
    
    # Main menu button
    menu_button = game_engine.ui_elements[STATE_ESC_MENU]["main_menu_button"]
    if menu_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        game_engine._start_transition(STATE_MENU)
        logger.info("Returning to main menu from ESC menu")

def render_esc_menu(game_engine):
    """Render ESC menu state"""
    # Semi-transparent overlay
    overlay = pygame.Surface((game_engine.width, game_engine.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    game_engine.screen.blit(overlay, (0, 0))
    
    # Display title
    display_text(
        game_engine.screen,
        "Game Paused",
        game_engine.fonts["large"],
        game_engine.colors["white"],
        game_engine.width // 2,
        game_engine.height // 4.5,
        center=True
    )
    
    # Draw buttons with improved spacing
    game_engine.ui_elements[STATE_ESC_MENU]["resume_button"].draw(game_engine.screen)
    game_engine.ui_elements[STATE_ESC_MENU]["settings_button"].draw(game_engine.screen)
    game_engine.ui_elements[STATE_ESC_MENU]["shop_button"].draw(game_engine.screen)
    game_engine.ui_elements[STATE_ESC_MENU]["main_menu_button"].draw(game_engine.screen)
    
    # Display current level and progress
    if game_engine.current_level:
        level_text = f"Level {game_engine.current_level.level_number}"
        if game_engine.current_level.is_boss:
            level_text += " (Boss)"
            health_percent = game_engine.current_level.get_health_percent() * 100
            progress_text = f"Boss Health: {int(health_percent)}%"
        else:
            progress_percent = min(100, (game_engine.clicks / game_engine.current_level.click_target) * 100)
            progress_text = f"Progress: {int(progress_percent)}%"
            
        display_text(
            game_engine.screen,
            level_text,
            game_engine.fonts["medium"],
            game_engine.colors["white"],
            game_engine.width // 2,
            game_engine.height - 150,
            center=True
        )
        
        display_text(
            game_engine.screen,
            progress_text,
            game_engine.fonts["medium"],
            game_engine.colors["white"],
            game_engine.width // 2,
            game_engine.height - 120,
            center=True
        )
    
    # Display coin count
    if game_engine.coin_counter > 0:
        display_text(
            game_engine.screen,
            f"Coins: {game_engine.coin_counter}",
            game_engine.fonts["medium"],
            game_engine.colors["gold"],
            game_engine.width // 2,
            game_engine.height - 80,
            center=True
        )