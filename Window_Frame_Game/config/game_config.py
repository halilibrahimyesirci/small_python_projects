"""
Game Configuration Module
Contains all settings and constants for the Window Frame Game
"""

import os
import json
from typing import Dict, List, Any

# Screen dimensions (use system resolution)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Game title
GAME_TITLE = "Window Hunter"

# Game settings
DEFAULT_SETTINGS = {
    "difficulty": "medium",
    "sound_enabled": True,
    "music_volume": 0.7,
    "sfx_volume": 1.0,
    "show_fps": True,
    "show_hitboxes": False
}

# Difficulty levels and their modifiers
DIFFICULTY_LEVELS = {
    "easy": {
        "player_health": 5,
        "target_spawn_rate": 0.8,
        "obstacle_spawn_rate": 0.5,
        "powerup_spawn_rate": 1.2,
        "target_speed_multiplier": 0.8,
        "score_multiplier": 0.8,
        "level_score_requirement": 200
    },
    "medium": {
        "player_health": 3,
        "target_spawn_rate": 1.0,
        "obstacle_spawn_rate": 1.0,
        "powerup_spawn_rate": 1.0,
        "target_speed_multiplier": 1.0,
        "score_multiplier": 1.0,
        "level_score_requirement": 300
    },
    "hard": {
        "player_health": 2,
        "target_spawn_rate": 1.2,
        "obstacle_spawn_rate": 1.5,
        "powerup_spawn_rate": 0.8,
        "target_speed_multiplier": 1.2,
        "score_multiplier": 1.2,
        "level_score_requirement": 400
    },
    "expert": {
        "player_health": 1,
        "target_spawn_rate": 1.5,
        "obstacle_spawn_rate": 2.0,
        "powerup_spawn_rate": 0.5,
        "target_speed_multiplier": 1.5,
        "score_multiplier": 1.5,
        "level_score_requirement": 500
    }
}

# Window transparency
WINDOW_ALPHA = 0.8

# Player settings
PLAYER_WINDOW_TITLE = "Hunter"
PLAYER_WINDOW_SIZE = (100, 100)
PLAYER_COLOR = "black"
PLAYER_SHAPE = "rectangle"
PLAYER_SPEED = 300  # Increased from 5 to 300 for faster movement
PLAYER_OUTLINE_COLOR = "white"
PLAYER_MAX_HEALTH = 3  # This will be overridden by difficulty setting
PLAYER_INVINCIBILITY_TIME = 2.0

# Player dash ability settings
DASH_COOLDOWN = 2.0      # Seconds before dash can be used again
DASH_SPEED = 20          # Speed multiplier for dash
DASH_COLOR = "cyan"      # Flash color during dash
DASH_READY_COLOR = "lime" # Indicator color when dash is ready
DASH_COOLDOWN_COLOR = "red" # Indicator color when dash is on cooldown

# Target settings
TARGET_WINDOW_TITLE = "Target"
TARGET_WINDOW_SIZE = (200, 150)
TARGET_WINDOW_COLORS = ["red", "blue", "green", "yellow", "purple"]
TARGET_TYPES = {
    "standard": {"speed": 0, "points": 10, "behavior": "static"},
    "moving": {"speed": 3, "points": 20, "behavior": "random_movement"},
    "evasive": {"speed": 4, "points": 30, "behavior": "evade_player"},
    "boss": {"speed": 2, "points": 50, "behavior": "chase_player", "health": 3}
}

# Target spawn chances per level
# Format: [standard, moving, evasive, boss]
TARGET_SPAWN_CHANCES = [
    [1.0, 0.0, 0.0, 0.0],  # Level 1: 100% standard
    [0.7, 0.3, 0.0, 0.0],  # Level 2: 70% standard, 30% moving
    [0.5, 0.4, 0.1, 0.0],  # Level 3: 50% standard, 40% moving, 10% evasive
    [0.4, 0.4, 0.2, 0.0],  # Level 4: 40% standard, 40% moving, 20% evasive
    [0.3, 0.4, 0.2, 0.1],  # Level 5: 30% standard, 40% moving, 20% evasive, 10% boss
    [0.2, 0.3, 0.4, 0.1],  # Level 6: 20% standard, 30% moving, 40% evasive, 10% boss
    [0.1, 0.3, 0.4, 0.2],  # Level 7: 10% standard, 30% moving, 40% evasive, 20% boss
    [0.1, 0.2, 0.4, 0.3],  # Level 8: 10% standard, 20% moving, 40% evasive, 30% boss
    [0.0, 0.2, 0.5, 0.3],  # Level 9: 0% standard, 20% moving, 50% evasive, 30% boss
    [0.0, 0.1, 0.4, 0.5]   # Level 10+: 0% standard, 10% moving, 40% evasive, 50% boss
]

# Powerup settings
POWERUP_WINDOW_TITLE = "Power-Up"
POWERUP_WINDOW_SIZE = (75, 75)
POWERUP_WINDOW_COLORS = {
    "speed": "cyan",
    "magnet": "magenta",
    "shield": "gold",
    "time": "silver"
}
POWERUP_EFFECTS = {
    "speed": {"multiplier": 2.0, "duration": 5.0},
    "magnet": {"radius": 300, "duration": 7.0},
    "shield": {"duration": 10.0},
    "time": {"slowdown": 0.5, "duration": 5.0}
}

# Powerup spawn chances
POWERUP_SPAWN_CHANCE = 0.1  # 10% chance per spawn cycle
POWERUP_TYPES_CHANCES = {
    "speed": 0.3,   # 30% chance of speed powerup
    "magnet": 0.3,  # 30% chance of magnet powerup
    "shield": 0.2,  # 20% chance of shield powerup
    "time": 0.2     # 20% chance of time powerup
}

# Obstacle settings
OBSTACLE_WINDOW_TITLE = "Obstacle"
OBSTACLE_WINDOW_SIZE = (150, 150)
OBSTACLE_WINDOW_COLOR = "gray"
OBSTACLE_TYPES = {
    "barrier": {"effect": "block", "duration": 0},
    "trap": {"effect": "freeze", "duration": 3},
    "decoy": {"effect": "none", "duration": 0}
}

# Obstacle spawn chances per level
# Format: [barrier, trap, decoy]
OBSTACLE_SPAWN_CHANCES = [
    [0.0, 0.0, 0.0],  # Level 1: No obstacles
    [0.7, 0.0, 0.3],  # Level 2: 70% barrier, 0% trap, 30% decoy
    [0.6, 0.1, 0.3],  # Level 3: 60% barrier, 10% trap, 30% decoy
    [0.5, 0.2, 0.3],  # Level 4: 50% barrier, 20% trap, 30% decoy
    [0.4, 0.3, 0.3],  # Level 5: 40% barrier, 30% trap, 30% decoy
    [0.4, 0.4, 0.2],  # Level 6: 40% barrier, 40% trap, 20% decoy
    [0.3, 0.5, 0.2],  # Level 7: 30% barrier, 50% trap, 20% decoy
    [0.3, 0.6, 0.1],  # Level 8: 30% barrier, 60% trap, 10% decoy
    [0.2, 0.7, 0.1],  # Level 9: 20% barrier, 70% trap, 10% decoy
    [0.2, 0.8, 0.0]   # Level 10+: 20% barrier, 80% trap, 0% decoy
]

# Entity spawn settings
MAX_TARGETS = 10    # Maximum number of targets on screen at once
MAX_OBSTACLES = 5   # Maximum number of obstacles on screen at once
MAX_POWERUPS = 2    # Maximum number of powerups on screen at once

# Game timing
TARGET_SPAWN_INTERVAL = 2.0      # Seconds between target spawn attempts
OBSTACLE_SPAWN_INTERVAL = 4.0    # Seconds between obstacle spawn attempts
POWERUP_SPAWN_INTERVAL = 8.0     # Seconds between powerup spawn attempts
GAME_UPDATE_INTERVAL = 1/60      # Target 60 FPS (16.67ms)

# Level progression
LEVEL_SCORE_REQUIREMENT = 300  # Score needed to advance to next level (base value)
MAX_LEVEL = 10                 # Maximum level

# Game physics
COLLISION_THRESHOLD = 20  # Distance threshold for collision detection in pixels
MAGNET_FORCE = 200        # Force of the magnet powerup attraction

# Display settings
SHOW_FPS = True
SHOW_HITBOXES = False

# Entity shapes
SHAPE_TYPES = ["rectangle", "triangle", "circle", "star"]

# Sound settings
SOUND_ENABLED = True
MUSIC_VOLUME = 0.7
SFX_VOLUME = 1.0

# File paths
SAVE_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "save_data.json")
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

def load_settings():
    """Load saved settings if available, otherwise use defaults"""
    if os.path.exists(SAVE_FILE_PATH):
        try:
            with open(SAVE_FILE_PATH, 'r') as f:
                settings = json.load(f)
                
            # Apply loaded settings to globals
            global SHOW_FPS, SHOW_HITBOXES, SOUND_ENABLED, MUSIC_VOLUME, SFX_VOLUME
            
            SHOW_FPS = settings.get('show_fps', DEFAULT_SETTINGS['show_fps'])
            SHOW_HITBOXES = settings.get('show_hitboxes', DEFAULT_SETTINGS['show_hitboxes'])
            SOUND_ENABLED = settings.get('sound_enabled', DEFAULT_SETTINGS['sound_enabled'])
            MUSIC_VOLUME = settings.get('music_volume', DEFAULT_SETTINGS['music_volume'])
            SFX_VOLUME = settings.get('sfx_volume', DEFAULT_SETTINGS['sfx_volume'])
            
            return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS
    else:
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Save settings to file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(SAVE_FILE_PATH), exist_ok=True)
        
        with open(SAVE_FILE_PATH, 'w') as f:
            json.dump(settings, f)
            
        # Apply settings to globals
        global SHOW_FPS, SHOW_HITBOXES, SOUND_ENABLED, MUSIC_VOLUME, SFX_VOLUME
        
        SHOW_FPS = settings.get('show_fps', DEFAULT_SETTINGS['show_fps'])
        SHOW_HITBOXES = settings.get('show_hitboxes', DEFAULT_SETTINGS['show_hitboxes'])
        SOUND_ENABLED = settings.get('sound_enabled', DEFAULT_SETTINGS['sound_enabled'])
        MUSIC_VOLUME = settings.get('music_volume', DEFAULT_SETTINGS['music_volume'])
        SFX_VOLUME = settings.get('sfx_volume', DEFAULT_SETTINGS['sfx_volume'])
        
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def get_level_target_score(level, difficulty="medium"):
    """Get the score needed to complete a level based on level number and difficulty"""
    base_requirement = DIFFICULTY_LEVELS[difficulty]["level_score_requirement"]
    return int(base_requirement * (1 + (level - 1) * 0.2))

def get_spawn_chances(level):
    """Get spawn chances for the current level"""
    level_index = min(level - 1, len(TARGET_SPAWN_CHANCES) - 1)
    obstacle_index = min(level - 1, len(OBSTACLE_SPAWN_CHANCES) - 1)
    
    return {
        "targets": TARGET_SPAWN_CHANCES[level_index],
        "obstacles": OBSTACLE_SPAWN_CHANCES[obstacle_index]
    }

# Load settings at module initialization
settings = load_settings()