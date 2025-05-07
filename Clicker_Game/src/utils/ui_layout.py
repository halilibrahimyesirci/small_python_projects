"""
UI Layout utilities for RPG Clicker Game
Helps with consistent UI element positioning and layout
"""

import pygame
import logging

logger = logging.getLogger(__name__)

class UILayout:
    """
    Helper class for UI layout management
    Simplifies calculating positions for UI elements
    """
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.margin = 20  # Default margin
        
    def center_rect(self, width, height, y_offset=0):
        """Get a centered rectangle with the given dimensions"""
        return pygame.Rect(
            self.width // 2 - width // 2,
            self.height // 2 - height // 2 + y_offset,
            width,
            height
        )
    
    def vertical_stack(self, start_y, item_height, spacing, count):
        """
        Generate a list of y positions for vertically stacked elements
        Returns a list of y positions
        """
        return [start_y + i * (item_height + spacing) for i in range(count)]
    
    def horizontal_stack(self, start_x, item_width, spacing, count):
        """
        Generate a list of x positions for horizontally stacked elements
        Returns a list of x positions
        """
        return [start_x + i * (item_width + spacing) for i in range(count)]
    
    def grid(self, start_x, start_y, item_width, item_height, 
             h_spacing, v_spacing, columns, rows):
        """
        Generate a grid of rectangles
        Returns a 2D list of pygame.Rect objects
        """
        grid = []
        for row in range(rows):
            grid_row = []
            for col in range(columns):
                x = start_x + col * (item_width + h_spacing)
                y = start_y + row * (item_height + v_spacing)
                rect = pygame.Rect(x, y, item_width, item_height)
                grid_row.append(rect)
            grid.append(grid_row)
        return grid
    
    def top_bar(self, height, margin=None):
        """Get a rectangle for a top bar"""
        if margin is None:
            margin = self.margin
        return pygame.Rect(margin, margin, self.width - 2 * margin, height)
    
    def bottom_bar(self, height, margin=None):
        """Get a rectangle for a bottom bar"""
        if margin is None:
            margin = self.margin
        return pygame.Rect(
            margin, 
            self.height - height - margin, 
            self.width - 2 * margin, 
            height
        )
    
    def left_panel(self, width, margin=None):
        """Get a rectangle for a left panel"""
        if margin is None:
            margin = self.margin
        return pygame.Rect(
            margin, 
            margin, 
            width, 
            self.height - 2 * margin
        )
    
    def right_panel(self, width, margin=None):
        """Get a rectangle for a right panel"""
        if margin is None:
            margin = self.margin
        return pygame.Rect(
            self.width - width - margin, 
            margin, 
            width, 
            self.height - 2 * margin
        )
    
    def center_panel(self, width, height, margin=None):
        """Get a rectangle for a centered panel"""
        if margin is None:
            margin = self.margin
        return pygame.Rect(
            self.width // 2 - width // 2,
            self.height // 2 - height // 2,
            width,
            height
        )


def safe_label(screen, font, text, color, x, y, center=True, shadow=True, shadow_color=(0, 0, 0)):
    """
    Safely render text with optional centering and shadow
    Returns the rect of the rendered text
    """
    try:
        # Create shadow if enabled
        if shadow:
            shadow_surf = font.render(text, True, shadow_color)
            shadow_rect = shadow_surf.get_rect()
            
            if center:
                shadow_rect.center = (x + 2, y + 2)
            else:
                shadow_rect.topleft = (x + 2, y + 2)
                
            screen.blit(shadow_surf, shadow_rect)
        
        # Render main text
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
            
        screen.blit(text_surf, text_rect)
        return text_rect
        
    except Exception as e:
        logger.error(f"Error rendering text {text}: {e}")
        return pygame.Rect(x, y, 0, 0)
        

def safe_button_layout(buttons, horizontal=True, start_x=100, start_y=100, 
                       spacing=10, uniform_size=True):
    """
    Position a list of buttons in a horizontal or vertical layout
    Buttons should be a list of pygame.Rect objects
    
    Returns the total width/height of the layout
    """
    if not buttons:
        return 0
        
    # Find largest button dimensions if uniform_size is True
    if uniform_size:
        max_width = max(btn.width for btn in buttons)
        max_height = max(btn.height for btn in buttons)
        
        for btn in buttons:
            btn.width = max_width
            btn.height = max_height
    
    # Position buttons
    if horizontal:
        x = start_x
        for btn in buttons:
            btn.x = x
            btn.y = start_y
            x += btn.width + spacing
        return x - start_x - spacing
    else:
        y = start_y
        for btn in buttons:
            btn.x = start_x
            btn.y = y
            y += btn.height + spacing
        return y - start_y - spacing