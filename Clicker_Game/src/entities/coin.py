"""
Coin entity for the RPG Clicker Game
"""
import pygame
import random
import math

class Coin:
    """A falling coin that can be collected by the player"""
    
    def __init__(self, x, y, value=1, size=15):
        self.x = x
        self.y = y
        self.value = value
        self.size = size
        self.speed = random.uniform(1, 3)
        self.alive = True
        self.color = (255, 215, 0)  # Gold color
        
    def update(self, mouse_pos, mouse_clicked):
        """Update coin position and check for collection"""
        self.y += self.speed
        
        # Check if coin is clicked (collected)
        mx, my = mouse_pos
        distance = math.sqrt((mx - self.x)**2 + (my - self.y)**2)
        
        if mouse_clicked and distance < self.size * 1.5:
            return True  # Coin collected
            
        # Check if coin is off-screen
        if self.y > 600:
            self.alive = False
            
        return False
        
    def draw(self, surface):
        """Draw the coin"""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(
            surface, 
            (255, 255, 200),  # Light gold inside
            (int(self.x), int(self.y)), 
            self.size - 3
        )