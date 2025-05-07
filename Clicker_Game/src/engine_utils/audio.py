"""
Audio management for the game.
Handles sound effects and music playback with advanced features.
"""

import pygame
import os
import logging

logger = logging.getLogger(__name__)

class AudioManager:
    """Manages audio, including sound effects and music"""
    
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.sound_volume = 1.0
        self.music_volume = 0.5
        self.current_music = None
        self.sounds = {}
        self.music_tracks = {}
        self.music_fading = False
        self.initialized = False
        
        # Try to initialize audio
        try:
            pygame.mixer.init()
            self.initialized = True
            logger.info("Audio system initialized successfully")
        except pygame.error as e:
            logger.error(f"Failed to initialize audio system: {e}")
            self.initialized = False
            
    def load_sound(self, name, path):
        """Load a sound effect"""
        if not self.initialized:
            return None
            
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                self.sounds[name] = sound
                sound.set_volume(self.sound_volume)
                logger.debug(f"Loaded sound: {name}")
                return sound
            else:
                logger.warning(f"Sound file not found: {path}")
                return None
        except pygame.error as e:
            logger.error(f"Failed to load sound {name}: {e}")
            return None
            
    def load_music(self, name, path):
        """Register a music track"""
        if not self.initialized:
            return
            
        if os.path.exists(path):
            self.music_tracks[name] = path
            logger.debug(f"Registered music track: {name}")
        else:
            logger.warning(f"Music file not found: {path}")
            
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if not self.initialized:
            return
            
        sound = self.sounds.get(sound_name)
        if sound:
            sound.set_volume(self.sound_volume)
            sound.play()
        else:
            logger.warning(f"Attempted to play unknown sound: {sound_name}")
            
    def play_music(self, music_name, loops=-1, fade_ms=500):
        """Play a music track with optional fade-in"""
        if not self.initialized:
            return
            
        if music_name == self.current_music:
            return  # Already playing this track
            
        music_path = self.music_tracks.get(music_name)
        if not music_path:
            logger.warning(f"Attempted to play unknown music: {music_name}")
            return
            
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.music_volume)
            if fade_ms > 0:
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
            else:
                pygame.mixer.music.play(loops)
                
            self.current_music = music_name
            logger.debug(f"Playing music: {music_name}")
        except pygame.error as e:
            logger.error(f"Failed to play music {music_name}: {e}")
            
    def stop_music(self, fade_ms=500):
        """Stop the currently playing music with optional fade-out"""
        if not self.initialized:
            return
            
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
            
        self.current_music = None
        
    def pause_music(self):
        """Pause the currently playing music"""
        if not self.initialized:
            return
            
        pygame.mixer.music.pause()
        
    def unpause_music(self):
        """Resume the paused music"""
        if not self.initialized:
            return
            
        pygame.mixer.music.unpause()
        
    def set_sound_volume(self, volume):
        """Set the volume for sound effects (0.0 to 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        
        # Update volume of all loaded sounds
        if self.initialized:
            for sound in self.sounds.values():
                sound.set_volume(self.sound_volume)
                
    def set_music_volume(self, volume):
        """Set the volume for music (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        
        # Update volume of currently playing music
        if self.initialized:
            pygame.mixer.music.set_volume(self.music_volume)
            
    def load_all_sounds(self, sounds_dir):
        """Load all sound files from a directory"""
        if not os.path.exists(sounds_dir):
            logger.warning(f"Sounds directory not found: {sounds_dir}")
            return
            
        for filename in os.listdir(sounds_dir):
            if filename.endswith(('.wav', '.ogg', '.mp3')):
                path = os.path.join(sounds_dir, filename)
                name = os.path.splitext(filename)[0]
                self.load_sound(name, path)
                
    def load_all_music(self, music_dir):
        """Load all music files from a directory"""
        if not os.path.exists(music_dir):
            logger.warning(f"Music directory not found: {music_dir}")
            return
            
        for filename in os.listdir(music_dir):
            if filename.endswith(('.wav', '.ogg', '.mp3')):
                path = os.path.join(music_dir, filename)
                name = os.path.splitext(filename)[0]
                self.load_music(name, path)