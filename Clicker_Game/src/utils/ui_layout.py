"""
UI Layout utilities for RPG Clicker Game
Helps with consistent UI element positioning and layout
"""

import pygame
from typing import Dict, List, Tuple, Optional, Union, Callable
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


class Text:
    """Text element with tkinter-inspired layout properties"""
    
    def __init__(self, text, font, color=(255, 255, 255), antialias=True):
        self.text = text
        self.font = font
        self.color = color
        self.antialias = antialias
        self.surface = None
        self.rect = None
        self.render()
        
    def render(self):
        """Render the text to a surface"""
        try:
            self.surface = self.font.render(self.text, self.antialias, self.color)
            self.rect = self.surface.get_rect()
        except pygame.error as e:
            logger.error(f"Failed to render text: {e}")
            
    def set_text(self, text):
        """Update the text and re-render"""
        if self.text != text:
            self.text = text
            self.render()
            
    def draw(self, surface, pos=None):
        """Draw the text at the specified position or use its rect position"""
        if not self.surface:
            return
            
        if pos:
            surface.blit(self.surface, pos)
        elif self.rect:
            surface.blit(self.surface, self.rect)
            
class Button:
    """Button element with tkinter-inspired layout properties"""
    
    def __init__(self, rect, text=None, image=None, callback=None, font=None, text_color=(255, 255, 255),
                 bg_color=(100, 100, 100), hover_color=(150, 150, 150), active_color=(200, 200, 200)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.image = image
        self.callback = callback
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.current_color = bg_color
        self.text_surface = None
        self.text_rect = None
        self.hovered = False
        self.active = False
        
        self._update_text()
        
    def _update_text(self):
        """Update the text surface if text and font are available"""
        if self.text and self.font:
            try:
                self.text_surface = self.font.render(self.text, True, self.text_color)
                self.text_rect = self.text_surface.get_rect(center=self.rect.center)
            except pygame.error as e:
                logger.error(f"Failed to render button text: {e}")
                
    def set_text(self, text):
        """Update the button text"""
        self.text = text
        self._update_text()
        
    def set_position(self, pos):
        """Update the button position"""
        old_center = self.rect.center
        self.rect.x, self.rect.y = pos
        self.rect.center = old_center
        if self.text_rect:
            self.text_rect.center = self.rect.center
            
    def set_dimensions(self, width, height):
        """Update the button dimensions"""
        old_center = self.rect.center
        self.rect.width = width
        self.rect.height = height
        self.rect.center = old_center
        if self.text_rect:
            self.text_rect.center = self.rect.center
            
    def handle_event(self, event):
        """Handle events for the button"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                self.active = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.active and self.hovered:
                if self.callback:
                    self.callback()
            self.active = False
            
    def update(self):
        """Update button state"""
        if self.active:
            self.current_color = self.active_color
        elif self.hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.bg_color
            
    def draw(self, surface):
        """Draw the button on the given surface"""
        # Draw button background
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2)  # Border
        
        # Draw image if available
        if self.image:
            image_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, image_rect)
            
        # Draw text if available
        if self.text_surface and self.text_rect:
            surface.blit(self.text_surface, self.text_rect)
            
class Container:
    """Container for grouping UI elements with layout capabilities"""
    
    def __init__(self, rect, padding=5, bg_color=None, border_color=None):
        self.rect = pygame.Rect(rect)
        self.padding = padding
        self.bg_color = bg_color
        self.border_color = border_color
        self.elements = []
        self.layout_type = "grid"  # or "pack"
        self.rows = 1
        self.cols = 1
        self.cells = {}
        self._init_grid()
        
    def _init_grid(self):
        """Initialize the grid cells"""
        cell_width = self.rect.width // self.cols
        cell_height = self.rect.height // self.rows
        
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.rect.x + col * cell_width
                y = self.rect.y + row * cell_height
                cell_rect = pygame.Rect(x, y, cell_width, cell_height)
                self.cells[(row, col)] = {
                    "rect": cell_rect,
                    "element": None
                }
                
    def set_grid(self, rows, cols):
        """Set up a grid layout with specified rows and columns"""
        self.layout_type = "grid"
        self.rows = max(1, rows)
        self.cols = max(1, cols)
        self.cells = {}
        self._init_grid()
        
    def place(self, element, row, col, rowspan=1, colspan=1, anchor="center"):
        """Place an element in the grid at specified position"""
        if self.layout_type != "grid":
            self.layout_type = "grid"
            self._init_grid()
            
        if (row, col) not in self.cells:
            logger.warning(f"Invalid grid position: {row}, {col}")
            return
            
        # Calculate combined rectangle for rowspan/colspan
        combined_rect = None
        for r in range(row, min(row + rowspan, self.rows)):
            for c in range(col, min(col + colspan, self.cols)):
                if (r, c) not in self.cells:
                    continue
                    
                cell_rect = self.cells[(r, c)]["rect"]
                if combined_rect is None:
                    combined_rect = cell_rect.copy()
                else:
                    combined_rect = combined_rect.union(cell_rect)
                    
        if not combined_rect:
            logger.warning(f"Could not calculate combined rect for: {row}, {col}, {rowspan}, {colspan}")
            return
            
        # Apply padding
        combined_rect.inflate_ip(-2 * self.padding, -2 * self.padding)
        
        # Position the element based on the anchor
        if hasattr(element, "rect"):
            if anchor == "center":
                element.rect.center = combined_rect.center
            elif anchor == "topleft":
                element.rect.topleft = combined_rect.topleft
            elif anchor == "topright":
                element.rect.topright = combined_rect.topright
            elif anchor == "bottomleft":
                element.rect.bottomleft = combined_rect.bottomleft
            elif anchor == "bottomright":
                element.rect.bottomright = combined_rect.bottomright
            elif anchor == "fill":
                element.rect = combined_rect.copy()
                
        # Store the element
        self.cells[(row, col)]["element"] = element
        if element not in self.elements:
            self.elements.append(element)
            
    def pack(self, element, side="top", fill=None, expand=False, padding=None):
        """Pack an element to a side, similar to tkinter's pack"""
        if self.layout_type != "pack":
            self.layout_type = "pack"
            self.elements = []
            
        if padding is None:
            padding = self.padding
            
        # Calculate the position based on already packed elements and side
        content_rect = self.rect.inflate(-2 * padding, -2 * padding)
        
        if not hasattr(element, "rect"):
            logger.warning("Cannot pack element without rect attribute")
            return
            
        if side == "top":
            # Pack to the top
            element.rect.top = content_rect.top
            element.rect.centerx = content_rect.centerx
            
            # Adjust content_rect for next element
            content_rect.top += element.rect.height + padding
            
        elif side == "bottom":
            # Pack to the bottom
            element.rect.bottom = content_rect.bottom
            element.rect.centerx = content_rect.centerx
            
            # Adjust content_rect for next element
            content_rect.bottom -= element.rect.height + padding
            
        elif side == "left":
            # Pack to the left
            element.rect.left = content_rect.left
            element.rect.centery = content_rect.centery
            
            # Adjust content_rect for next element
            content_rect.left += element.rect.width + padding
            
        elif side == "right":
            # Pack to the right
            element.rect.right = content_rect.right
            element.rect.centery = content_rect.centery
            
            # Adjust content_rect for next element
            content_rect.right -= element.rect.width + padding
            
        # Apply fill if specified
        if fill == "x" or fill == "both":
            element.rect.width = content_rect.width
            
        if fill == "y" or fill == "both":
            element.rect.height = content_rect.height
            
        # Store the element
        if element not in self.elements:
            self.elements.append(element)
            
    def draw(self, surface):
        """Draw the container and all its elements"""
        # Draw container background if specified
        if self.bg_color:
            pygame.draw.rect(surface, self.bg_color, self.rect)
            
        # Draw container border if specified
        if self.border_color:
            pygame.draw.rect(surface, self.border_color, self.rect, 1)
            
        # Draw all elements
        for element in self.elements:
            if hasattr(element, "draw"):
                element.draw(surface)
                
    def handle_event(self, event):
        """Handle events for all elements in the container"""
        for element in self.elements:
            if hasattr(element, "handle_event"):
                element.handle_event(event)
                
    def update(self):
        """Update all elements in the container"""
        for element in self.elements:
            if hasattr(element, "update"):
                element.update()
                
class UIFactory:
    """Factory class for creating UI elements with consistent styling"""
    
    def __init__(self, resource_manager=None):
        self.resource_manager = resource_manager
        self.default_font = None
        self.default_font_size = 24
        self.default_text_color = (255, 255, 255)
        self.default_button_bg = (80, 80, 100)
        self.default_button_hover = (100, 100, 120)
        self.default_button_active = (120, 120, 140)
        
        # Try to set up default font
        try:
            pygame.font.init()
            self.default_font = pygame.font.SysFont("Arial", self.default_font_size)
        except pygame.error as e:
            logger.error(f"Failed to initialize default font: {e}")
            
    def create_text(self, text, font=None, color=None, size=None):
        """Create a Text element with current style defaults"""
        # Use provided font or default
        actual_font = font
        if not actual_font:
            if size and self.default_font:
                try:
                    font_name = self.default_font.get_name()
                    actual_font = pygame.font.SysFont(font_name, size)
                except:
                    actual_font = self.default_font
            else:
                actual_font = self.default_font
                
        # Use provided color or default
        actual_color = color if color else self.default_text_color
        
        return Text(text, actual_font, actual_color)
        
    def create_button(self, rect, text, callback=None, font=None, text_color=None,
                     bg_color=None, hover_color=None, active_color=None, image=None):
        """Create a Button element with current style defaults"""
        # Use provided values or defaults
        actual_font = font if font else self.default_font
        actual_text_color = text_color if text_color else self.default_text_color
        actual_bg = bg_color if bg_color else self.default_button_bg
        actual_hover = hover_color if hover_color else self.default_button_hover
        actual_active = active_color if active_color else self.default_button_active
        
        # Create and return button
        return Button(
            rect=rect,
            text=text,
            image=image,
            callback=callback,
            font=actual_font,
            text_color=actual_text_color,
            bg_color=actual_bg,
            hover_color=actual_hover,
            active_color=actual_active
        )
        
    def create_container(self, rect, padding=5, bg_color=None, border_color=None):
        """Create a Container element with current style defaults"""
        return Container(rect, padding, bg_color, border_color)