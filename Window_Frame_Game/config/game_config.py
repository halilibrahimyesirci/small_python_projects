import os
import json
from typing import Dict, List, Any

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

GAME_TITLE = "Window Hunter"

DEFAULT_SETTINGS = {
    "difficulty": "medium",
    "sound_enabled": True,
    "music_volume": 0.7,
    "sfx_volume": 1.0,
    "show_fps": True,
    "show_hitboxes": False
}

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

WINDOW_ALPHA = 0.8

PLAYER_WINDOW_TITLE = "Hunter"
PLAYER_WINDOW_SIZE = (100, 100)
PLAYER_COLOR = "black"
PLAYER_SHAPE = "rectangle"
PLAYER_SPEED = 300
PLAYER_OUTLINE_COLOR = "white"
PLAYER_MAX_HEALTH = 3
PLAYER_INVINCIBILITY_TIME = 2.0

DASH_COOLDOWN = 2.0
DASH_SPEED = 20
DASH_COLOR = "cyan"
DASH_READY_COLOR = "lime"
DASH_COOLDOWN_COLOR = "red"

TARGET_WINDOW_TITLE = "Target"
TARGET_WINDOW_SIZE = (200, 150)
TARGET_WINDOW_COLORS = ["red", "blue", "green", "yellow", "purple"]
TARGET_TYPES = {
    "standard": {"speed": 0, "points": 10, "behavior": "static"},
    "moving": {"speed": 3, "points": 20, "behavior": "random_movement"},
    "evasive": {"speed": 4, "points": 30, "behavior": "evade_player"},
    "boss": {"speed": 2, "points": 50, "behavior": "chase_player", "health": 3}
}

TARGET_SPAWN_CHANCES = [
    [1.0, 0.0, 0.0, 0.0],
    [0.7, 0.3, 0.0, 0.0],
    [0.5, 0.4, 0.1, 0.0],
    [0.4, 0.4, 0.2, 0.0],
    [0.3, 0.4, 0.2, 0.1],
    [0.2, 0.3, 0.4, 0.1],
    [0.1, 0.3, 0.4, 0.2],
    [0.1, 0.2, 0.4, 0.3],
    [0.0, 0.2, 0.5, 0.3],
    [0.0, 0.1, 0.4, 0.5]
]

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

POWERUP_SPAWN_CHANCE = 0.1
POWERUP_TYPES_CHANCES = {
    "speed": 0.3,
    "magnet": 0.3,
    "shield": 0.2,
    "time": 0.2
}

OBSTACLE_WINDOW_TITLE = "Obstacle"
OBSTACLE_WINDOW_SIZE = (150, 150)
OBSTACLE_WINDOW_COLOR = "gray"
OBSTACLE_TYPES = {
    "barrier": {"effect": "block", "duration": 0},
    "trap": {"effect": "freeze", "duration": 3},
    "decoy": {"effect": "none", "duration": 0}
}

OBSTACLE_SPAWN_CHANCES = [
    [0.0, 0.0, 0.0],
    [0.7, 0.0, 0.3],
    [0.6, 0.1, 0.3],
    [0.5, 0.2, 0.3],
    [0.4, 0.3, 0.3],
    [0.4, 0.4, 0.2],
    [0.3, 0.5, 0.2],
    [0.3, 0.6, 0.1],
    [0.2, 0.7, 0.1],
    [0.2, 0.8, 0.0]
]

MAX_TARGETS = 10
MAX_OBSTACLES = 5
MAX_POWERUPS = 2

TARGET_SPAWN_INTERVAL = 2.0
OBSTACLE_SPAWN_INTERVAL = 4.0
POWERUP_SPAWN_INTERVAL = 8.0
GAME_UPDATE_INTERVAL = 1/60

LEVEL_SCORE_REQUIREMENT = 300
MAX_LEVEL = 10

COLLISION_THRESHOLD = 20
MAGNET_FORCE = 200

SHOW_FPS = True
SHOW_HITBOXES = False

SHAPE_TYPES = ["rectangle", "triangle", "circle", "star"]

SOUND_ENABLED = True
MUSIC_VOLUME = 0.7
SFX_VOLUME = 1.0

SAVE_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "save_data.json")
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

def load_settings():
    if os.path.exists(SAVE_FILE_PATH):
        try:
            with open(SAVE_FILE_PATH, 'r') as f:
                settings = json.load(f)
                
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
    try:
        os.makedirs(os.path.dirname(SAVE_FILE_PATH), exist_ok=True)
        
        with open(SAVE_FILE_PATH, 'w') as f:
            json.dump(settings, f)
            
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
    base_requirement = DIFFICULTY_LEVELS[difficulty]["level_score_requirement"]
    return int(base_requirement * (1 + (level - 1) * 0.2))

def get_spawn_chances(level):
    level_index = min(level - 1, len(TARGET_SPAWN_CHANCES) - 1)
    obstacle_index = min(level - 1, len(OBSTACLE_SPAWN_CHANCES) - 1)
    
    return {
        "targets": TARGET_SPAWN_CHANCES[level_index],
        "obstacles": OBSTACLE_SPAWN_CHANCES[obstacle_index]
    }

settings = load_settings()