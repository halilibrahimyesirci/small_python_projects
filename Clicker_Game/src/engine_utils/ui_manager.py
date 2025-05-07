"""
UI Manager for handling rendering and interactions with UI elements.
Uses the tkinter-inspired layout system to manage UI components.
"""

import pygame
import logging
from src.utils.ui_layout import Container, UIFactory, Text, Button

logger = logging.getLogger(__name__)

class UIManager:
    """
    Manages UI elements and their interactions using a tkinter-inspired layout system.
    """
    
    def __init__(self, resource_manager, screen_size):
        self.resource_manager = resource_manager
        self.screen_size = screen_size
        self.ui_factory = UIFactory(resource_manager)
        self.containers = {}
        self.active_elements = []
        
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
        """Handle events for all containers"""
        for container in self.containers.values():
            container.handle_event(event)
    
    def update(self):
        """Update all containers"""
        for container in self.containers.values():
            container.update()
    
    def draw(self, surface):
        """Draw all containers to the surface"""
        for container in self.containers.values():
            container.draw(surface)
    
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