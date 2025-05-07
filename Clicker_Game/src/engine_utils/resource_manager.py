"""
Resource manager for handling game assets.
Manages loading, caching, and accessing various game resources.
"""

import pygame
import os
import json
import logging

logger = logging.getLogger(__name__)

class ResourceManager:
    """Manages loading and caching of game resources"""
    
    def __init__(self, config_path=None):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.music = {}
        self.config = {}
        
        # Load config file if provided
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
            
    def load_config(self, config_path):
        """Load a JSON configuration file"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            # Create a default config
            self.config = {
                "screen": {
                    "width": 800,
                    "height": 600,
                    "fps": 60
                }
            }
            
    def save_config(self, config_path):
        """Save the current configuration to a file"""
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Saved configuration to {config_path}")
            return True
        except IOError as e:
            logger.error(f"Failed to save config to {config_path}: {e}")
            return False
            
    def get_config_value(self, section, key, default=None):
        """Get a value from the configuration"""
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default
        
    def set_config_value(self, section, key, value):
        """Set a value in the configuration"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        
    def load_image(self, name, file_path, scale=None, convert_alpha=True):
        """Load an image and store it by name"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Image file not found: {file_path}")
                return None
                
            image = pygame.image.load(file_path)
            
            if convert_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
                
            if scale:
                image = pygame.transform.scale(image, scale)
                
            self.images[name] = image
            logger.debug(f"Loaded image: {name} from {file_path}")
            return image
        except pygame.error as e:
            logger.error(f"Failed to load image {name} from {file_path}: {e}")
            return None
            
    def load_sound(self, name, file_path):
        """Load a sound effect and store it by name"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Sound file not found: {file_path}")
                return None
                
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
            logger.debug(f"Loaded sound: {name} from {file_path}")
            return sound
        except pygame.error as e:
            logger.error(f"Failed to load sound {name} from {file_path}: {e}")
            return None
            
    def load_music(self, name, file_path):
        """Register a music track by name"""
        if not os.path.exists(file_path):
            logger.warning(f"Music file not found: {file_path}")
            return False
            
        self.music[name] = file_path
        logger.debug(f"Registered music track: {name} from {file_path}")
        return True
        
    def load_font(self, name, font_name=None, size=24):
        """Load a font and store it by name"""
        try:
            if font_name is None:
                # Use default font
                font = pygame.font.SysFont(None, size)
            else:
                # Try to load the specified font
                font = pygame.font.SysFont(font_name, size)
                
            self.fonts[name] = font
            logger.debug(f"Loaded font: {name} (size: {size})")
            return font
        except pygame.error as e:
            logger.error(f"Failed to load font {name}: {e}")
            return None
            
    def get_image(self, name):
        """Get an image by name"""
        return self.images.get(name)
        
    def get_sound(self, name):
        """Get a sound by name"""
        return self.sounds.get(name)
        
    def get_music(self, name):
        """Get a music track file path by name"""
        return self.music.get(name)
        
    def get_font(self, name):
        """Get a font by name"""
        return self.fonts.get(name)
        
    def get_or_load_font(self, name, font_name=None, size=24):
        """Get a font by name, loading it if not available"""
        if name in self.fonts:
            return self.fonts[name]
        return self.load_font(name, font_name, size)
        
    def unload_resource(self, resource_type, name):
        """Unload a resource by type and name"""
        if resource_type == "image" and name in self.images:
            del self.images[name]
            return True
        elif resource_type == "sound" and name in self.sounds:
            self.sounds[name].stop()  # Ensure sound is stopped
            del self.sounds[name]
            return True
        elif resource_type == "music" and name in self.music:
            del self.music[name]
            return True
        elif resource_type == "font" and name in self.fonts:
            del self.fonts[name]
            return True
        return False
        
    def clear_resources(self, resource_type=None):
        """Clear resources of a specific type or all resources"""
        if resource_type == "image":
            self.images.clear()
        elif resource_type == "sound":
            # Stop all sounds first
            for sound in self.sounds.values():
                sound.stop()
            self.sounds.clear()
        elif resource_type == "music":
            pygame.mixer.music.stop()
            self.music.clear()
        elif resource_type == "font":
            self.fonts.clear()
        elif resource_type is None:
            # Clear all resources
            self.images.clear()
            for sound in self.sounds.values():
                sound.stop()
            self.sounds.clear()
            pygame.mixer.music.stop()
            self.music.clear()
            self.fonts.clear()
            
    def load_resources_from_directory(self, directory, resource_type):
        """
        Load all resources of a specific type from a directory
        resource_type can be 'image', 'sound', or 'music'
        """
        if not os.path.exists(directory):
            logger.warning(f"Directory not found: {directory}")
            return False
            
        count = 0
        if resource_type == "image":
            for filename in os.listdir(directory):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    name = os.path.splitext(filename)[0]
                    file_path = os.path.join(directory, filename)
                    if self.load_image(name, file_path):
                        count += 1
                        
        elif resource_type == "sound":
            for filename in os.listdir(directory):
                if filename.lower().endswith(('.wav', '.ogg')):
                    name = os.path.splitext(filename)[0]
                    file_path = os.path.join(directory, filename)
                    if self.load_sound(name, file_path):
                        count += 1
                        
        elif resource_type == "music":
            for filename in os.listdir(directory):
                if filename.lower().endswith(('.mp3', '.ogg', '.wav')):
                    name = os.path.splitext(filename)[0]
                    file_path = os.path.join(directory, filename)
                    if self.load_music(name, file_path):
                        count += 1
                        
        logger.info(f"Loaded {count} {resource_type} resources from {directory}")
        return count > 0