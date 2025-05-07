"""
Layout manager that provides tkinter-inspired positioning systems for UI elements.
Supports both grid and pack layout methods for easier UI positioning.
"""

import pygame
import logging

logger = logging.getLogger(__name__)

class LayoutManager:
    """
    Manages the layout of UI elements using tkinter-inspired positioning systems.
    Supports both grid and pack layout methods.
    """
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.containers = {}
        
    def create_container(self, name, rect=None, parent=None, padding=5):
        """Create a new container for organizing UI elements"""
        if rect is None and parent is None:
            # Create root container with full screen dimensions
            rect = pygame.Rect(0, 0, self.width, self.height)
        elif rect is None and parent in self.containers:
            # Create child container within parent's bounds
            rect = self.containers[parent].rect.copy()
            
        container = Container(name, rect, padding)
        self.containers[name] = container
        return container
    
    def grid_configure(self, container_name, rows, cols, padding=(5, 5)):
        """Configure a container to use grid layout"""
        if container_name in self.containers:
            self.containers[container_name].setup_grid(rows, cols, padding)
            return True
        return False
    
    def grid_place(self, container_name, element, row, col, rowspan=1, colspan=1, sticky=None):
        """Place an element in a grid-configured container"""
        if container_name in self.containers and hasattr(element, 'rect'):
            return self.containers[container_name].grid_place(element, row, col, rowspan, colspan, sticky)
        return False
    
    def pack(self, container_name, element, side="top", fill=None, expand=False, padding=None):
        """Pack an element in a container"""
        if container_name in self.containers and hasattr(element, 'rect'):
            return self.containers[container_name].pack(element, side, fill, expand, padding)
        return False
    
    def update_layouts(self):
        """Update all container layouts"""
        for container in self.containers.values():
            container.update_layout()
    
    def get_container(self, name):
        """Get a container by name"""
        return self.containers.get(name)
    
    def clear_container(self, name):
        """Remove all elements from a container"""
        if name in self.containers:
            self.containers[name].clear()
            return True
        return False


class Container:
    """A container for organizing UI elements using grid or pack layout"""
    
    def __init__(self, name, rect, padding=5):
        self.name = name
        self.rect = rect
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)
        self.elements = []
        
        # Grid layout properties
        self.is_grid = False
        self.rows = 0
        self.cols = 0
        self.grid_cells = {}  # (row, col) -> rect
        self.grid_elements = {}  # (row, col) -> element
        self.grid_padding = (5, 5)
        
        # Pack layout properties
        self.pack_info = []  # [(element, side, fill, expand, padding)]
        
    def setup_grid(self, rows, cols, padding=(5, 5)):
        """Setup grid layout for this container"""
        self.is_grid = True
        self.rows = rows
        self.cols = cols
        self.grid_padding = padding
        self._calculate_grid_cells()
        
    def _calculate_grid_cells(self):
        """Calculate grid cell dimensions"""
        if not self.is_grid or self.rows == 0 or self.cols == 0:
            return
            
        # Calculate available space
        available_width = self.rect.width - (2 * self.padding[0])
        available_height = self.rect.height - (2 * self.padding[1])
        
        # Calculate cell dimensions
        cell_width = available_width / self.cols
        cell_height = available_height / self.rows
        
        # Create cells
        self.grid_cells = {}
        for row in range(self.rows):
            for col in range(self.cols):
                cell_x = self.rect.x + self.padding[0] + (col * cell_width)
                cell_y = self.rect.y + self.padding[1] + (row * cell_height)
                cell_rect = pygame.Rect(cell_x, cell_y, cell_width, cell_height)
                self.grid_cells[(row, col)] = cell_rect
    
    def grid_place(self, element, row, col, rowspan=1, colspan=1, sticky=None):
        """Place an element in the grid"""
        if not self.is_grid:
            logger.warning(f"Cannot place element in container {self.name} - not a grid layout")
            return False
            
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            logger.warning(f"Grid position ({row}, {col}) is out of bounds for container {self.name}")
            return False
            
        # Calculate spanning area
        rowspan = min(rowspan, self.rows - row)
        colspan = min(colspan, self.cols - col)
        
        combined_rect = None
        for r in range(row, row + rowspan):
            for c in range(col, col + colspan):
                cell_key = (r, c)
                if cell_key not in self.grid_cells:
                    continue
                    
                cell_rect = self.grid_cells[cell_key]
                if combined_rect is None:
                    combined_rect = cell_rect.copy()
                else:
                    combined_rect.union_ip(cell_rect)
        
        if combined_rect is None:
            logger.warning(f"Failed to create combined rect for grid position ({row}, {col})")
            return False
        
        # Apply padding to the combined rect
        combined_rect.inflate_ip(-self.grid_padding[0] * 2, -self.grid_padding[1] * 2)
        
        # Position the element within the combined rect
        if sticky:
            # Parse sticky string: 'n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw' or 'center'
            element_rect = element.rect.copy()
            
            # Default to center
            element_x = combined_rect.x + (combined_rect.width - element_rect.width) / 2
            element_y = combined_rect.y + (combined_rect.height - element_rect.height) / 2
            
            if 'n' in sticky:
                element_y = combined_rect.y
            elif 's' in sticky:
                element_y = combined_rect.y + combined_rect.height - element_rect.height
                
            if 'w' in sticky:
                element_x = combined_rect.x
            elif 'e' in sticky:
                element_x = combined_rect.x + combined_rect.width - element_rect.width
                
            element.rect.x = int(element_x)
            element.rect.y = int(element_y)
        else:
            # Center the element in the combined rect
            element.rect.center = combined_rect.center
        
        # Store the element
        for r in range(row, row + rowspan):
            for c in range(col, col + colspan):
                self.grid_elements[(r, c)] = element
                
        if element not in self.elements:
            self.elements.append(element)
            
        return True
    
    def pack(self, element, side="top", fill=None, expand=False, padding=None):
        """Pack an element in the container"""
        if self.is_grid:
            logger.warning(f"Cannot pack element in container {self.name} - using grid layout")
            return False
            
        # Store packing information
        pack_padding = padding if padding is not None else self.padding
        self.pack_info.append((element, side, fill, expand, pack_padding))
        
        if element not in self.elements:
            self.elements.append(element)
            
        # Calculate packed positions
        self._calculate_packed_positions()
        return True
    
    def _calculate_packed_positions(self):
        """Calculate positions for packed elements"""
        if self.is_grid:
            return
            
        # Available space
        content_rect = pygame.Rect(
            self.rect.x + self.padding[0], 
            self.rect.y + self.padding[1],
            self.rect.width - (2 * self.padding[0]),
            self.rect.height - (2 * self.padding[1])
        )
        
        # Keep track of space used so far from each side
        used_top = 0
        used_bottom = 0
        used_left = 0
        used_right = 0
        
        # Process elements in the order they were packed
        for element, side, fill, expand, padding in self.pack_info:
            pad_x, pad_y = padding
            
            # Get element's natural size
            element_width = element.rect.width
            element_height = element.rect.height
            
            if side == "top":
                # Calculate position from top
                position_x = content_rect.x + used_left
                position_y = content_rect.y + used_top + pad_y
                
                # Adjust width if fill
                if fill == "x" or fill == "both":
                    element_width = content_rect.width - used_left - used_right - (2 * pad_x)
                
                # Update used space
                used_top += element_height + (2 * pad_y)
                
            elif side == "bottom":
                # Calculate position from bottom
                position_x = content_rect.x + used_left
                position_y = content_rect.bottom - used_bottom - element_height - pad_y
                
                # Adjust width if fill
                if fill == "x" or fill == "both":
                    element_width = content_rect.width - used_left - used_right - (2 * pad_x)
                
                # Update used space
                used_bottom += element_height + (2 * pad_y)
                
            elif side == "left":
                # Calculate position from left
                position_x = content_rect.x + used_left + pad_x
                position_y = content_rect.y + used_top
                
                # Adjust height if fill
                if fill == "y" or fill == "both":
                    element_height = content_rect.height - used_top - used_bottom - (2 * pad_y)
                
                # Update used space
                used_left += element_width + (2 * pad_x)
                
            elif side == "right":
                # Calculate position from right
                position_x = content_rect.right - used_right - element_width - pad_x
                position_y = content_rect.y + used_top
                
                # Adjust height if fill
                if fill == "y" or fill == "both":
                    element_height = content_rect.height - used_top - used_bottom - (2 * pad_y)
                
                # Update used space
                used_right += element_width + (2 * pad_x)
                
            else:
                # Default to top
                position_x = content_rect.x + used_left
                position_y = content_rect.y + used_top + pad_y
                used_top += element_height + (2 * pad_y)
            
            # Set element position and size
            element.rect.x = int(position_x)
            element.rect.y = int(position_y)
            
            # Apply fill/expand by adjusting width/height
            old_width = element.rect.width
            old_height = element.rect.height
            
            if fill or expand:
                if fill == "x" or fill == "both" or (expand and side in ("top", "bottom")):
                    element.rect.width = int(element_width)
                    
                if fill == "y" or fill == "both" or (expand and side in ("left", "right")):
                    element.rect.height = int(element_height)
                    
                # If element has a resize method, call it
                if hasattr(element, "resize") and callable(element.resize):
                    element.resize(element.rect.width, element.rect.height)
    
    def update_layout(self):
        """Update the layout of elements"""
        if self.is_grid:
            self._calculate_grid_cells()
            # Reapply grid placement for all elements
            # This would require storing grid placement info and re-applying it
        else:
            self._calculate_packed_positions()
            
    def clear(self):
        """Remove all elements from the container"""
        self.elements = []
        self.grid_elements = {}
        self.pack_info = []
        
    def draw(self, surface):
        """Draw all elements in the container"""
        for element in self.elements:
            if hasattr(element, 'draw') and callable(element.draw):
                element.draw(surface)