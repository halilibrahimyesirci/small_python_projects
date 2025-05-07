"""
Settings state implementation
"""
from src.mechanics.common import *

def update_settings(game_engine, time_delta):
    """Update settings state"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]  # Left button
    
    # Update sound volume slider
    sound_slider = game_engine.ui_elements[STATE_SETTINGS]["sound_slider"]
    if sound_slider.update(mouse_pos, mouse_clicked):
        game_engine.audio_settings["sound_volume"] = sound_slider.value
        
        # Apply sound volume to all sounds
        for sound in game_engine.resource_manager.sounds.values():
            sound.set_volume(game_engine.audio_settings["sound_volume"])
    
    # Update music volume slider
    music_slider = game_engine.ui_elements[STATE_SETTINGS]["music_slider"]
    if music_slider.update(mouse_pos, mouse_clicked):
        game_engine.audio_settings["music_volume"] = music_slider.value
        pygame.mixer.music.set_volume(game_engine.audio_settings["music_volume"])
    
    # Update music selection buttons
    current_music = game_engine.audio_settings["current_music"]
    for music_file, button in game_engine.ui_elements[STATE_SETTINGS]["music_buttons"]:
        # Highlight current selection
        if music_file == current_music:
            button.border_color = game_engine.colors["yellow"]
            button.border_width = 3
        else:
            button.border_color = game_engine.colors["purple"]
            button.border_width = 2
            
        if button.update(mouse_pos, mouse_clicked, game_engine.current_time):
            # Change music
            game_engine.audio_settings["current_music"] = music_file
            music_path = os.path.join("assets", "music", music_file)
            
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(game_engine.audio_settings["music_volume"])
            pygame.mixer.music.play(-1)  # Loop indefinitely
            
            logger.info(f"Changed music to {music_file}")
    
    # Back button
    back_button = game_engine.ui_elements[STATE_SETTINGS]["back_button"]
    if back_button.update(mouse_pos, mouse_clicked, game_engine.current_time):
        # Return to previous state
        previous_state = game_engine.previous_state if game_engine.previous_state else STATE_MENU
        game_engine._start_transition(previous_state)
        logger.info(f"Returning to {previous_state} from settings")

def render_settings(game_engine):
    """Render settings state"""
    # Draw settings title
    display_text(
        game_engine.screen,
        "Settings",
        game_engine.fonts["large"],
        game_engine.colors["white"],
        game_engine.width // 2,
        80,
        center=True
    )
    
    # Draw "Sound Volume" label
    display_text(
        game_engine.screen,
        "Sound Volume:",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 2,
        game_engine.height // 3 - 30,
        center=True
    )
    
    # Draw sound volume slider
    game_engine.ui_elements[STATE_SETTINGS]["sound_slider"].draw(game_engine.screen)
    
    # Draw "Music Volume" label
    display_text(
        game_engine.screen,
        "Music Volume:",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 2,
        game_engine.height // 3 + 50,
        center=True
    )
    
    # Draw music volume slider
    game_engine.ui_elements[STATE_SETTINGS]["music_slider"].draw(game_engine.screen)
    
    # Draw "Select Music" label
    display_text(
        game_engine.screen,
        "Select Music:",
        game_engine.fonts["medium"],
        game_engine.colors["white"],
        game_engine.width // 2,
        game_engine.height // 3 + 120,
        center=True
    )
    
    # Draw music selection buttons
    for music_file, button in game_engine.ui_elements[STATE_SETTINGS]["music_buttons"]:
        button.draw(game_engine.screen)
    
    # Draw back button
    game_engine.ui_elements[STATE_SETTINGS]["back_button"].draw(game_engine.screen)