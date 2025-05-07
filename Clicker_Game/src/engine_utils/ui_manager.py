"""
UI Manager for handling rendering and interactions with UI elements.
Uses the tkinter-inspired layout system to manage UI components.
"""

import pygame
import logging
from src.utils.ui_layout import Container, UIFactory, Text, Button

logger = logging.getLogger(__name__)

class UIElement:
    """
    Base class for UI elements with common properties and methods.
    Used for handling UI element registration and interaction.
    """
    
    def __init__(self, rect, name=None, z_index=0):
        self.rect = rect
        self.name = name
        self.z_index = z_index
        self.visible = True
        self.enabled = True
        self.parent = None
        self.hover = False
        self.clicked = False
        
    def update(self, mouse_pos, mouse_clicked, current_time):
        """
        Update the element state based on mouse interaction.
        Returns True if the element was clicked.
        """
        # Check if mouse is over this element
        self.hover = self.rect.collidepoint(mouse_pos) if self.visible and self.enabled else False
        
        # Check if element was clicked
        was_clicked = self.hover and mouse_clicked
        if was_clicked and self.enabled:
            self.clicked = True
        else:
            self.clicked = False
            
        return self.clicked
        
    def draw(self, surface):
        """Base draw method to be overridden by subclasses"""
        if not self.visible:
            return
            
        # Default implementation just draws a rect
        color = (150, 150, 150) if self.enabled else (100, 100, 100)
        pygame.draw.rect(surface, color, self.rect)
        
    def set_position(self, x, y):
        """Set the position of this element"""
        self.rect.x = x
        self.rect.y = y
        
    def set_size(self, width, height):
        """Set the size of this element"""
        self.rect.width = width
        self.rect.height = height
        
    def resize(self, width, height):
        """Resize the element (alias for set_size)"""
        self.set_size(width, height)
        
    def set_visible(self, visible):
        """Set visibility of the element"""
        self.visible = visible
        
    def set_enabled(self, enabled):
        """Set whether the element is enabled (can be interacted with)"""
        self.enabled = enabled
        
    def get_position(self):
        """Get the element's position as (x, y)"""
        return (self.rect.x, self.rect.y)
        
    def get_size(self):
        """Get the element's size as (width, height)"""
        return (self.rect.width, self.rect.height)
        
    def get_center(self):
        """Get the element's center position"""
        return self.rect.center
        
    def set_center(self, center_x, center_y):
        """Set the element's center position"""
        self.rect.center = (center_x, center_y)

class UIManager:
    """
    Manages UI elements and their interactions using a tkinter-inspired layout system.
    """
    
    def __init__(self, width, height=None, resource_manager=None):
        # Support both (width, height) and (resource_manager, screen_size) initialization
        if height is None and isinstance(width, tuple):
            # Called with screen_size as first parameter
            self.screen_size = width
            self.width, self.height = width
            self.resource_manager = resource_manager
        elif isinstance(width, int) and isinstance(height, int):
            # Called with width, height as parameters
            self.width = width
            self.height = height
            self.screen_size = (width, height)
            self.resource_manager = resource_manager
        else:
            # Default case, likely called incorrectly
            logger.warning("UIManager initialized with incorrect parameters")
            self.width = 800
            self.height = 600
            self.screen_size = (800, 600)
            self.resource_manager = None
        
        # Initialize collections
        self.elements = []
        self.containers = {}
        
        # Initialize UI factory if resource manager is available
        if self.resource_manager:
            self.ui_factory = UIFactory(self.resource_manager)
            # Initialize basic containers
            self._init_containers()
        
    def _init_containers(self):
        """Initialize default containers for different screen regions"""
        # Main container covers the entire screen
        screen_rect = pygame.Rect(0, 0, *self.screen_size)
        self.containers["main"] = self.ui_factory.create_container(
            screen_rect, 
            padding=10
        )
        
        # Header container (top 10% of screen)
        header_height = int(self.screen_size[1] * 0.1)
        header_rect = pygame.Rect(0, 0, self.screen_size[0], header_height)
        self.containers["header"] = self.ui_factory.create_container(
            header_rect,
            padding=5,
            bg_color=(40, 40, 60, 150),
            border_color=(100, 100, 120)
        )
        
        # Footer container (bottom 10% of screen)
        footer_height = int(self.screen_size[1] * 0.1)
        footer_rect = pygame.Rect(0, self.screen_size[1] - footer_height, 
                                 self.screen_size[0], footer_height)
        self.containers["footer"] = self.ui_factory.create_container(
            footer_rect,
            padding=5,
            bg_color=(40, 40, 60, 150),
            border_color=(100, 100, 120)
        )
        
        # Left sidebar (20% of screen width)
        sidebar_width = int(self.screen_size[0] * 0.2)
        left_sidebar_rect = pygame.Rect(
            0, header_height, 
            sidebar_width, self.screen_size[1] - header_height - footer_height
        )
        self.containers["left_sidebar"] = self.ui_factory.create_container(
            left_sidebar_rect,
            padding=5,
            bg_color=(30, 30, 50, 150),
            border_color=(80, 80, 100)
        )
        
        # Right sidebar (20% of screen width)
        right_sidebar_rect = pygame.Rect(
            self.screen_size[0] - sidebar_width, header_height,
            sidebar_width, self.screen_size[1] - header_height - footer_height
        )
        self.containers["right_sidebar"] = self.ui_factory.create_container(
            right_sidebar_rect,
            padding=5,
            bg_color=(30, 30, 50, 150),
            border_color=(80, 80, 100)
        )
        
        # Content area (middle 60% of screen)
        content_rect = pygame.Rect(
            sidebar_width, header_height,
            self.screen_size[0] - (2 * sidebar_width), 
            self.screen_size[1] - header_height - footer_height
        )
        self.containers["content"] = self.ui_factory.create_container(
            content_rect,
            padding=10
        )
    
    def create_container(self, name, rect, padding=5, bg_color=None, border_color=None):
        """Create a new named container"""
        self.containers[name] = self.ui_factory.create_container(
            rect, padding, bg_color, border_color
        )
        return self.containers[name]
    
    def get_container(self, name):
        """Get a container by name"""
        return self.containers.get(name)
    
    def create_grid_layout(self, container_name, rows, cols):
        """Create a grid layout in the specified container"""
        if container_name in self.containers:
            self.containers[container_name].set_grid(rows, cols)
            return True
        return False
    
    def place_element(self, container_name, element, row, col, 
                     rowspan=1, colspan=1, anchor="center"):
        """Place an element in a grid container"""
        if container_name in self.containers:
            self.containers[container_name].place(
                element, row, col, rowspan, colspan, anchor
            )
            return True
        return False
    
    def pack_element(self, container_name, element, side="top", 
                    fill=None, expand=False, padding=None):
        """Pack an element in a container"""
        if container_name in self.containers:
            self.containers[container_name].pack(
                element, side, fill, expand, padding
            )
            return True
        return False
    
    def create_text(self, text, font=None, color=None, size=None):
        """Create a text element"""
        return self.ui_factory.create_text(text, font, color, size)
    
    def create_button(self, rect, text, callback=None, font=None, text_color=None,
                     bg_color=None, hover_color=None, active_color=None, image=None):
        """Create a button element"""
        return self.ui_factory.create_button(
            rect, text, callback, font, text_color,
            bg_color, hover_color, active_color, image
        )
    
    def handle_event(self, event):
        """Handle pygame events for all UI elements"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Check elements in reverse order (top elements first)
            for element in reversed(self.elements):
                if hasattr(element, 'rect') and element.rect.collidepoint(mouse_pos):
                    if hasattr(element, 'on_click') and callable(element.on_click):
                        element.on_click(event)
                    break  # Stop after first hit
                    
        for container in self.containers.values():
            container.handle_event(event)
    
    def update(self, mouse_pos=None, mouse_clicked=False, current_time=0):
        """Update all UI elements"""
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
            
        for element in self.elements:
            if hasattr(element, 'update') and callable(element.update):
                element.update(mouse_pos, mouse_clicked, current_time)
                
        for container in self.containers.values():
            container.update()
    
    def draw(self, surface):
        """Draw all UI elements"""
        for element in self.elements:
            if hasattr(element, 'draw') and callable(element.draw):
                element.draw(surface)
                
        for container in self.containers.values():
            container.draw(surface)
    
    def add_element(self, element):
        """Add a UI element to be managed"""
        self.elements.append(element)
        # Sort elements by z-index to ensure proper drawing order
        self.elements.sort(key=lambda e: getattr(e, 'z_index', 0))
        
    def remove_element(self, element):
        """Remove a UI element from management"""
        if element in self.elements:
            self.elements.remove(element)
            
    def convert_to_ui_element(self, element, name=None):
        """
        Convert a pygame rect or other UI component to a UIElement 
        if it's not already one
        """
        if isinstance(element, UIElement):
            if name and not element.name:
                element.name = name
            return element
            
        # If it's not a UIElement but has a rect, wrap it
        if hasattr(element, 'rect'):
            # Create a wrapper that delegates to the original object
            wrapper = UIElement(element.rect, name, getattr(element, 'z_index', 0))
            wrapper.update = element.update if hasattr(element, 'update') else wrapper.update
            wrapper.draw = element.draw if hasattr(element, 'draw') else wrapper.draw
            return wrapper
            
        # If it's just a rect, create a basic UIElement
        if isinstance(element, pygame.Rect):
            return UIElement(element, name)
            
        # Can't convert this
        logger.warning(f"Could not convert {element} to UIElement")
        return None
    
    def adjust_all_positions(self):
        """
        Adjust element positions to prevent collisions and 
        ensure all elements are within screen bounds
        """
        for element in self.elements:
            if not hasattr(element, 'rect'):
                continue
                
            # Keep element within screen bounds
            if element.rect.left < 0:
                element.rect.left = 0
            if element.rect.right > self.screen_size[0]:
                element.rect.right = self.screen_size[0]
            if element.rect.top < 0:
                element.rect.top = 0
            if element.rect.bottom > self.screen_size[1]:
                element.rect.bottom = self.screen_size[1]
                
    def update_element_position(self, ui_element):
        """Update the original element position based on the UI element wrapper"""
        # If the UI element is a wrapper and the original element has a rect
        if hasattr(ui_element, 'original_element') and hasattr(ui_element.original_element, 'rect'):
            # Update the original element's rect
            ui_element.original_element.rect = ui_element.rect
            
    def get_element_by_name(self, name):
        """Get an element by its name"""
        for element in self.elements:
            if hasattr(element, 'name') and element.name == name:
                return element
        return None
    
    def create_standard_layout(self):
        """Create a standard game UI layout with header, footer, sidebars and content"""
        # This is already handled in _init_containers, but can be extended here
        pass
    
    def create_text_and_place(self, container_name, text, row, col, 
                             font=None, color=None, size=None, 
                             rowspan=1, colspan=1, anchor="center"):
        """Create a text element and place it in a grid container"""
        text_element = self.create_text(text, font, color, size)
        self.place_element(container_name, text_element, row, col, 
                          rowspan, colspan, anchor)
        return text_element
    
    def create_button_and_place(self, container_name, text, row, col, 
                              callback=None, width=150, height=40,
                              font=None, text_color=None, bg_color=None,
                              rowspan=1, colspan=1, anchor="center"):
        """Create a button and place it in a grid container"""
        # Create a temporary rect - will be positioned by the grid system
        temp_rect = pygame.Rect(0, 0, width, height)
        
        button = self.create_button(
            temp_rect, text, callback, font, text_color, bg_color
        )
        
        self.place_element(container_name, button, row, col, 
                          rowspan, colspan, anchor)
        
        return button