import json
import os
import pygame
import logging

# Set up logging
logging.basicConfig(
    filename='rpg_clicker.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResourceManager:
    """Manages loading and accessing game resources like images and sounds"""
    
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.music = {}
        self._load_config()
        
    def _load_config(self):
        """Load game configuration from JSON file"""
        config_path = os.path.join("config", "game_config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info("Configuration loaded successfully")
            else:
                self.config = self._create_default_config()
                logger.warning("Config file not found, using default configuration")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = self._create_default_config()
    
    def _create_default_config(self):
        """Create and save default configuration"""
        default_config = {
            "screen": {
                "width": 800,
                "height": 600,
                "fps": 60
            },
            "gameplay": {
                "initial_click_target": 50,
                "target_increment": 10,
                "timer_duration": 30,
                "critical_click_chance": 0.1,
                "critical_click_value": 2
            },
            "upgrade_costs": {
                "click_power": [50, 100, 200, 400, 800],
                "critical_chance": [75, 150, 300, 600, 1200],
                "critical_multiplier": [100, 200, 400, 800, 1600]
            },
            "boss_levels": [5, 10, 15, 20, 25]
        }
        
        # Ensure config directory exists
        os.makedirs("config", exist_ok=True)
        
        # Save default config
        config_path = os.path.join("config", "game_config.json")
        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            logger.info("Default configuration created")
        except Exception as e:
            logger.error(f"Error creating default configuration: {e}")
            
        return default_config
    
    def load_image(self, name, filepath, scale=None):
        """Load an image and store it in the resources dictionary"""
        try:
            if os.path.exists(filepath):
                image = pygame.image.load(filepath).convert_alpha()
                if scale:
                    image = pygame.transform.scale(image, scale)
                self.images[name] = image
                logger.info(f"Image '{name}' loaded successfully")
                return image
            else:
                logger.warning(f"Image file not found: {filepath}")
                return None
        except Exception as e:
            logger.error(f"Error loading image '{name}': {e}")
            return None
    
    def load_sound(self, name, filepath):
        """Load a sound effect and store it in the resources dictionary"""
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                self.sounds[name] = sound
                logger.info(f"Sound '{name}' loaded successfully")
                return sound
            else:
                logger.warning(f"Sound file not found: {filepath}")
                return None
        except Exception as e:
            logger.error(f"Error loading sound '{name}': {e}")
            return None
    
    def load_music(self, name, filepath):
        """Register a music file path"""
        if os.path.exists(filepath):
            self.music[name] = filepath
            logger.info(f"Music '{name}' registered successfully")
            return True
        else:
            logger.warning(f"Music file not found: {filepath}")
            return False
    
    def play_sound(self, name):
        """Play a sound effect by name"""
        if name in self.sounds:
            self.sounds[name].play()
            return True
        logger.warning(f"Sound '{name}' not found")
        return False
    
    def play_music(self, name, loops=-1):
        """Play a music track by name"""
        if name in self.music:
            try:
                pygame.mixer.music.load(self.music[name])
                pygame.mixer.music.play(loops)
                logger.info(f"Playing music: {name}")
                return True
            except Exception as e:
                logger.error(f"Error playing music '{name}': {e}")
                return False
        logger.warning(f"Music '{name}' not found")
        return False
    
    def stop_music(self):
        """Stop currently playing music"""
        pygame.mixer.music.stop()
        
    def get_config_value(self, *keys):
        """Get a configuration value using a chain of keys"""
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logger.warning(f"Config key not found: {keys}")
            return None