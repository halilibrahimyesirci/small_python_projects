"""
Playing state implementation
"""
from src.mechanics.common import *
from src.ui import ClickParticle

def update_playing(game_engine, time_delta):
    """Update playing state"""
    # Get mouse state
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]  # Left button
    
    # Check for spacebar press to open shop instead of upgrade menu
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        # Initialize the shop if needed
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
        logger.info("Opening shop via spacebar")
        return
    
    # Update falling coins
    update_coins(game_engine, mouse_pos, mouse_pressed)
            
    # Spawn new coins based on clicks
    spawn_coins(game_engine)
    
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
        process_click(game_engine, mouse_pos)
    
    # Auto clicker ability if active
    if game_engine.player_abilities["auto_clicker"]["active"]:
        game_engine.auto_click_timer = getattr(game_engine, 'auto_click_timer', 0) + time_delta
        if game_engine.auto_click_timer >= 0.5:  # Click every 0.5 seconds
            game_engine.auto_click_timer = 0
            process_auto_click(game_engine)
            
    # Update player abilities
    update_abilities(game_engine, time_delta)
    
    # Update combo meter
    combo_meter = game_engine.ui_elements[STATE_PLAYING]["combo_meter"]
    combo_meter.update(game_engine.current_time)
    
    # Update particles
    game_engine.ui_elements[STATE_PLAYING]["particles"].update()
    
    # Update progress bar
    update_progress(game_engine)

def update_coins(game_engine, mouse_pos, mouse_pressed):
    """Update all falling coins"""
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

def spawn_coins(game_engine):
    """Spawn new coins based on gameplay criteria"""
    coin_spawn_threshold = max(10, 50 - game_engine.player.coin_upgrade_level * 5)  # Reduce threshold with upgrades
    if game_engine.clicks > 0 and game_engine.clicks % coin_spawn_threshold == 0 and random.random() < 0.3:
        coin_x = random.randint(50, game_engine.width - 50)
        coin_y = -20  # Start above the screen
        new_coin = game_engine.coin_class(coin_x, coin_y, value=1 + game_engine.player.coin_upgrade_level // 2)
        game_engine.coins.append(new_coin)

def process_click(game_engine, mouse_pos):
    """Process a click on the click button"""
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

def process_auto_click(game_engine):
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

def update_abilities(game_engine, time_delta):
    """Update active player abilities"""
    for ability_name, ability in game_engine.player_abilities.items():
        if ability["active"]:
            ability["duration"] -= time_delta
            if ability["duration"] <= 0:
                ability["active"] = False
                ability["cooldown"] = 60  # 60 second cooldown
                logger.info(f"Ability ended: {ability_name}")

def update_progress(game_engine):
    """Update progress bar based on level type"""
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

def render_playing(game_engine):
    """Render playing state"""
    # Sort UI elements by z-index for proper layering
    ui_elements = {}
    for key, element in game_engine.ui_elements[STATE_PLAYING].items():
        if hasattr(element, 'z_index'):
            ui_elements[key] = element
    
    # Explicitly define z-indices for key elements if not already set
    if "click_button" in ui_elements:
        # The main game_click_area should have a lower z-index than other UI
        game_engine.ui_elements[STATE_PLAYING]["click_button"].z_index = 5
    
    if "progress_bar" in ui_elements:
        game_engine.ui_elements[STATE_PLAYING]["progress_bar"].z_index = 10
    
    if "combo_meter" in ui_elements:
        game_engine.ui_elements[STATE_PLAYING]["combo_meter"].z_index = 15
    
    # Sort elements by z-index (lower values drawn first)
    sorted_elements = sorted(
        [(key, element) for key, element in game_engine.ui_elements[STATE_PLAYING].items() 
         if hasattr(element, 'z_index')],
        key=lambda x: x[1].z_index
    )
    
    # Draw background elements (game_click_area)
    game_engine.ui_elements[STATE_PLAYING]["click_button"].draw(game_engine.screen)
    
    # Draw falling coins (between game_click_area and UI elements)
    for coin in game_engine.coins:
        coin.draw(game_engine.screen)
    
    # Draw UI elements in order of z-index
    for key, element in sorted_elements:
        if key != "click_button" and key != "particles":  # We handle these separately
            element.draw(game_engine.screen)
    
    # Draw particles (always on top)
    game_engine.ui_elements[STATE_PLAYING]["particles"].draw(game_engine.screen)
    
    # Display active abilities (top layer)
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
    
    # Display coin counter (top layer)
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