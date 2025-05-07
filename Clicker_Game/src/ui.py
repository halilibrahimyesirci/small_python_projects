import pygame
import logging
import random
from src.utils.ui_layout import UILayout, safe_label, safe_button_layout

logger = logging.getLogger(__name__)

class Button:
    """Interactive button class with hover and click states"""
    
    def __init__(self, rect, text, font, colors, border_width=0, border_color=None):
        self.rect = rect
        self.text = text
        self.font = font
        self.colors = colors  # Dict with 'normal', 'hover', and 'clicked' colors
        self.state = "normal"
        self.click_time = 0
        self.click_duration = 0.1  # Duration of 'clicked' visual state
        self.border_width = border_width
        self.border_color = border_color
        self.was_clicked = False  # Track if button was clicked but not yet released
        
    def update(self, mouse_pos, mouse_clicked, current_time):
        """Update button state based on mouse interaction"""
        # Reset to normal if click animation is complete
        if self.state == "clicked" and current_time - self.click_time >= self.click_duration:
            self.state = "normal"
        
        # Check if mouse is over button
        if self.rect.collidepoint(mouse_pos):
            if mouse_clicked and not self.was_clicked:
                self.state = "clicked"
                self.click_time = current_time
                self.was_clicked = True
                return True
            elif not mouse_clicked:
                self.was_clicked = False  # Reset the clicked state when mouse button is released
                if self.state != "clicked":
                    self.state = "hover"
            elif self.state != "clicked":
                self.state = "hover"
        else:
            if not mouse_clicked:
                self.was_clicked = False  # Reset clicked state if mouse moves away and button is released
            if self.state != "clicked":
                self.state = "normal"
            
        return False
        
    def draw(self, surface):
        """Draw the button on the given surface"""
        color = self.colors.get(self.state, self.colors["normal"])
        
        # Draw border if specified
        if self.border_width > 0 and self.border_color:
            border_rect = self.rect.inflate(self.border_width * 2, self.border_width * 2)
            pygame.draw.rect(surface, self.border_color, border_rect)
            
        # Draw button
        pygame.draw.rect(surface, color, self.rect)
        
        # Draw text
        if self.text and self.font:
            text_surf = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    @staticmethod
    def create_button_group(buttons_data, ui_layout=None, start_x=None, start_y=None, 
                          direction="vertical", spacing=10):
        """
        Create a group of buttons with safe layout.
        
        Args:
            buttons_data: List of (rect, text, font, colors) tuples
            ui_layout: Optional UILayout manager
            start_x, start_y: Starting position
            direction: "vertical" or "horizontal"
            spacing: Spacing between buttons
            
        Returns:
            List of Button objects
        """
        buttons = []
        
        # Create buttons first
        for rect, text, font, colors, border_width, border_color in buttons_data:
            button = Button(rect, text, font, colors, border_width, border_color)
            buttons.append(button)
            
        # If we have a layout manager, use it to position buttons
        if ui_layout and start_x is not None and start_y is not None:
            positions = safe_button_layout(buttons, start_x, start_y, direction, spacing, ui_layout)
            
            # Update button positions
            for i, (x, y) in enumerate(positions):
                buttons[i].rect.x = x
                buttons[i].rect.y = y
                
        return buttons


class ProgressBar:
    """Progress bar with fill animation"""
    
    def __init__(self, rect, bg_color, fill_color, border_color=None, border_width=0):
        self.rect = rect
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_width = border_width
        self.progress = 0  # 0.0 to 1.0
        self.target_progress = 0
        self.animation_speed = 0.05  # Progress per frame
        
    def set_progress(self, value):
        """Set the target progress value (0.0 to 1.0)"""
        self.target_progress = max(0, min(1, value))
        
    def update(self):
        """Update the progress animation"""
        if self.progress < self.target_progress:
            self.progress = min(self.target_progress, self.progress + self.animation_speed)
        elif self.progress > self.target_progress:
            self.progress = max(self.target_progress, self.progress - self.animation_speed)
            
    def draw(self, surface):
        """Draw the progress bar"""
        # Draw border if specified
        if self.border_width > 0 and self.border_color:
            border_rect = self.rect.inflate(self.border_width * 2, self.border_width * 2)
            pygame.draw.rect(surface, self.border_color, border_rect)
            
        # Draw background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        
        # Draw fill
        if self.progress > 0:
            fill_rect = pygame.Rect(
                self.rect.x,
                self.rect.y,
                int(self.rect.width * self.progress),
                self.rect.height
            )
            pygame.draw.rect(surface, self.fill_color, fill_rect)


class ComboMeter:
    """Visual indicator for active combos"""
    
    def __init__(self, rect, colors, font, decay_rate=0.5):
        self.rect = rect
        self.colors = colors  # List of colors for different combo levels
        self.font = font
        self.combo_count = 0
        self.max_combo = 0
        self.decay_rate = decay_rate  # How fast combo decays (seconds per combo)
        self.last_click_time = 0
        self.active = False
        
    def add_click(self, current_time):
        """Register a click and update combo"""
        time_diff = current_time - self.last_click_time
        
        # If clicked within the combo window
        if time_diff < self.decay_rate:
            self.combo_count += 1
        else:
            self.combo_count = 1
        
        self.last_click_time = current_time
        self.active = True
        
        # Track max combo
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count
            
        return self.combo_count
        
    def update(self, current_time):
        """Update combo state"""
        if not self.active:
            return
            
        time_diff = current_time - self.last_click_time
        
        # If combo has expired
        if time_diff >= self.decay_rate:
            self.combo_count = 0
            self.active = False
            
    def get_combo_bonus(self):
        """Get the bonus multiplier based on combo count"""
        if self.combo_count < 3:
            return 0  # No bonus
        elif self.combo_count < 5:
            return 0.5  # 50% bonus
        elif self.combo_count < 10:
            return 1  # 100% bonus (double)
        else:
            return 2  # 200% bonus (triple)
    
    def draw(self, surface):
        """Draw the combo meter"""
        if not self.active:
            return
            
        # Determine color based on combo count
        color_index = min(len(self.colors) - 1, self.combo_count // 3)
        color = self.colors[color_index]
        
        # Draw background
        pygame.draw.rect(surface, (30, 30, 30), self.rect)
        
        # Draw combo text
        text = f"Combo: {self.combo_count}x"
        if self.combo_count >= 3:
            bonus = self.get_combo_bonus()
            text += f" (+{int(bonus * 100)}%)"
            
        text_surf = self.font.render(text, True, color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class ParticleSystem:
    """System for managing visual particle effects"""
    
    def __init__(self):
        self.particles = []
        
    def add_particle(self, particle):
        """Add a particle to the system"""
        self.particles.append(particle)
        
    def update(self):
        """Update all particles"""
        for particle in self.particles[:]:  # Use a copy for safe removal
            if not particle.update():
                self.particles.remove(particle)
                
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(surface)
            
    def clear(self):
        """Clear all particles"""
        self.particles.clear()


class ClickParticle:
    """Particle effect for clicks"""
    
    def __init__(self, x, y, color, size=5, speed=1, life=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed
        self.life = life
        self.alpha = 255
        self.creation_time = pygame.time.get_ticks() / 1000.0
        self.angle = pygame.math.Vector2(0, -1).angle_to(
            pygame.math.Vector2(
                pygame.math.Vector2(0.5, 0.5).normalize().x,
                pygame.math.Vector2(0.5, 0.5).normalize().y
            )
        )
        
    def update(self):
        """Update particle position and properties"""
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed = current_time - self.creation_time
        
        if elapsed > self.life:
            return False
            
        # Update position
        self.x += self.speed * pygame.math.Vector2(1, 0).rotate(self.angle).x
        self.y += self.speed * pygame.math.Vector2(1, 0).rotate(self.angle).y
        
        # Update alpha
        self.alpha = int(255 * (1 - (elapsed / self.life)))
        
        return True
        
    def draw(self, surface):
        """Draw the particle"""
        # Create a temporary surface for the particle
        particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            particle_surf,
            (*self.color, self.alpha),
            (self.size, self.size),
            self.size
        )
        surface.blit(particle_surf, (self.x - self.size, self.y - self.size))


class TextParticle:
    """Floating text effect"""
    
    def __init__(self, x, y, text, font, color, speed=1, life=1.0):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.color = color
        self.speed = speed
        self.life = life
        self.alpha = 255
        self.creation_time = pygame.time.get_ticks() / 1000.0
        
    def update(self):
        """Update particle position and properties"""
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed = current_time - self.creation_time
        
        if elapsed > self.life:
            return False
            
        # Update position
        self.y -= self.speed
        
        # Update alpha
        self.alpha = int(255 * (1 - (elapsed / self.life)))
        
        return True
        
    def draw(self, surface):
        """Draw the text particle"""
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        surface.blit(text_surf, (self.x, self.y))


class Slider:
    """Interactive slider UI element"""
    
    def __init__(self, rect, initial_value, min_value, max_value, bg_color, handle_color, font, label=None):
        self.rect = rect
        self.value = initial_value
        self.min_value = min_value
        self.max_value = max_value
        self.bg_color = bg_color
        self.handle_color = handle_color
        self.font = font
        self.label = label
        self.dragging = False
        
        # Make the handle height match the slider height for better usability
        self.handle_width = 20
        self.handle_rect = pygame.Rect(0, 0, self.handle_width, rect.height)
        self._update_handle_position()
        
    def _update_handle_position(self):
        """Update the handle position based on the current value"""
        value_percent = (self.value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.rect.x + int(value_percent * (self.rect.width - self.handle_rect.width))
        self.handle_rect.x = handle_x
        self.handle_rect.y = self.rect.y
        
    def update(self, mouse_pos, mouse_pressed, mouse_released=False):
        """Update slider state based on mouse interaction"""
        # Check if mouse is over handle or slider
        if self.handle_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                self.dragging = True
        # Allow clicking anywhere on the slider to move the handle directly
        elif self.rect.collidepoint(mouse_pos) and mouse_pressed:
            # Calculate new handle position based on mouse click
            rel_x = max(0, min(mouse_pos[0] - self.rect.x, self.rect.width - self.handle_rect.width))
            self.handle_rect.x = self.rect.x + rel_x
            
            # Update value based on handle position
            value_percent = rel_x / (self.rect.width - self.handle_rect.width)
            self.value = self.min_value + value_percent * (self.max_value - self.min_value)
            self.dragging = True
            return True
        
        # Stop dragging if mouse released
        if not mouse_pressed:
            self.dragging = False
            
        # Update position while dragging
        if self.dragging:
            mouse_x = mouse_pos[0]
            rel_x = max(0, min(mouse_x - self.rect.x, self.rect.width - self.handle_rect.width))
            self.handle_rect.x = self.rect.x + rel_x
            
            # Update value based on handle position
            value_percent = rel_x / (self.rect.width - self.handle_rect.width)
            self.value = self.min_value + value_percent * (self.max_value - self.min_value)
            return True  # Value changed
            
        return False
        
    def draw(self, surface):
        """Draw the slider on the given surface"""
        # Draw background bar
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        
        # Draw filled portion of the slider
        value_percent = (self.value - self.min_value) / (self.max_value - self.min_value)
        fill_width = int(self.rect.width * value_percent)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, (100, 100, 150), fill_rect)
        
        # Draw handle with increased size for better usability
        pygame.draw.rect(surface, self.handle_color, self.handle_rect)
        
        # Draw border
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        
        # Draw label and value if provided
        if self.label and self.font:
            # Draw label above slider
            label_surf = self.font.render(self.label, True, (255, 255, 255))
            label_rect = label_surf.get_rect(midtop=(self.rect.centerx, self.rect.y - 25))
            surface.blit(label_surf, label_rect)
            
            # Draw value below slider
            value_text = f"{int(self.value * 100)}%"
            value_surf = self.font.render(value_text, True, (255, 255, 255))
            value_rect = value_surf.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 5))
            surface.blit(value_surf, value_rect)


def display_text(surface, text, font, color, x, y, center=False, ui_layout=None):
    """Helper function to draw text on a surface with safe positioning"""
    if ui_layout:
        return safe_label(surface, text, font, color, x, y, center=center, ui_layout=ui_layout)
    else:
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
            
        surface.blit(text_surf, text_rect)
        return text_rect


class UIElement:
    """Base class for UI elements with collision detection"""
    
    def __init__(self, rect, z_index=0):
        self.rect = rect
        self.visible = True
        self.collision_enabled = True
        self.z_index = z_index  # Higher z-index means element is rendered on top
        
    def check_collision(self, other_element):
        """Check if this element collides with another element"""
        if not self.collision_enabled or not other_element.collision_enabled:
            return False
        return self.rect.colliderect(other_element.rect)
    
    def check_screen_bounds(self, screen_width, screen_height):
        """Check if element is within screen boundaries"""
        return (self.rect.x >= 0 and self.rect.y >= 0 and 
                self.rect.right <= screen_width and self.rect.bottom <= screen_height)
    
    def adjust_position(self, elements, screen_width, screen_height):
        """Adjust position to avoid collisions with other elements and stay within screen bounds"""
        # First check and fix screen boundaries
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.right > screen_width:
            self.rect.x = screen_width - self.rect.width
        if self.rect.bottom > screen_height:
            self.rect.y = screen_height - self.rect.height
            
        # Check collisions with other elements
        for element in elements:
            if element is self:
                continue
                
            if self.check_collision(element):
                # Move away from collision
                overlap_x = min(self.rect.right - element.rect.left, element.rect.right - self.rect.left)
                overlap_y = min(self.rect.bottom - element.rect.top, element.rect.bottom - self.rect.top)
                
                # Move along the axis with the smallest overlap
                if overlap_x < overlap_y:
                    if self.rect.centerx < element.rect.centerx:
                        self.rect.x -= overlap_x
                    else:
                        self.rect.x += overlap_x
                else:
                    if self.rect.centery < element.rect.centery:
                        self.rect.y -= overlap_y
                    else:
                        self.rect.y += overlap_y
                        
                # Recheck screen boundaries after adjustment
                self.adjust_position([], screen_width, screen_height)
                
class UIManager:
    """Manager class for handling UI elements, their collisions, and screen boundaries"""
    
    def __init__(self, screen_width, screen_height):
        self.elements = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        
    def add_element(self, element):
        """Add UI element to the manager"""
        self.elements.append(element)
        
    def remove_element(self, element):
        """Remove UI element from the manager"""
        if element in self.elements:
            self.elements.remove(element)
            
    def adjust_all_positions(self):
        """Adjust positions of all elements to avoid collisions and respect screen boundaries"""
        for element in self.elements:
            element.adjust_position(self.elements, self.screen_width, self.screen_height)
    
    def get_sorted_elements(self):
        """Get all elements sorted by z-index (lower z-index elements are drawn first)"""
        return sorted(self.elements, key=lambda elem: elem.z_index)
            
    def convert_to_ui_element(self, pygame_element, element_type="generic", z_index=0):
        """Convert a Pygame element with a rect to a UIElement"""
        ui_element = UIElement(pygame_element.rect, z_index=z_index)
        ui_element.original_element = pygame_element
        ui_element.element_type = element_type
        return ui_element
        
    def manage_button(self, button, z_index=10):
        """Add a button to the manager and convert it to a UIElement"""
        ui_element = self.convert_to_ui_element(button, "button", z_index=z_index)
        self.add_element(ui_element)
        return ui_element
        
    def update_element_position(self, ui_element):
        """Update the position of the original element from the managed UIElement"""
        if hasattr(ui_element, 'original_element'):
            ui_element.original_element.rect = ui_element.rect


class Tooltip:
    """Tooltip display for UI elements"""
    
    def __init__(self, text, font, bg_color=(30, 30, 40, 220), text_color=(255, 255, 255),
                 border_color=(200, 200, 200, 100), border_width=1, padding=10):
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.padding = padding
        self.visible = False
        self.rect = pygame.Rect(0, 0, 0, 0)
        
    def update_position(self, mouse_pos, offset_x=15, offset_y=10):
        """Update tooltip position based on mouse position"""
        # Create multi-line text surfaces
        if isinstance(self.text, list):
            text_lines = self.text
        else:
            text_lines = [self.text]  # Convert to list for single line
            
        text_surfs = [self.font.render(line, True, self.text_color) for line in text_lines]
        max_width = max([surf.get_width() for surf in text_surfs])
        total_height = sum([surf.get_height() for surf in text_surfs])
        
        # Calculate tooltip size
        width = max_width + self.padding * 2
        height = total_height + self.padding * 2 + (len(text_lines) - 1) * 5  # 5px spacing between lines
        
        # Update rect
        self.rect = pygame.Rect(mouse_pos[0] + offset_x, mouse_pos[1] + offset_y, width, height)
        
    def draw(self, surface, mouse_pos):
        """Draw the tooltip at the current mouse position"""
        if not self.visible:
            return
            
        self.update_position(mouse_pos)
        
        # Create tooltip surface with transparency
        tooltip_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        tooltip_surface.fill(self.bg_color)
        
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(tooltip_surface, self.border_color, 
                            (0, 0, self.rect.width, self.rect.height), self.border_width)
        
        # Draw text
        if isinstance(self.text, list):
            text_lines = self.text
        else:
            text_lines = [self.text]
            
        y_offset = self.padding
        for line in text_lines:
            text_surf = self.font.render(line, True, self.text_color)
            text_rect = text_surf.get_rect(topleft=(self.padding, y_offset))
            tooltip_surface.blit(text_surf, text_rect)
            y_offset += text_rect.height + 5  # 5px spacing between lines
        
        # Draw tooltip
        surface.blit(tooltip_surface, self.rect)

class TransparentImageMaker:
    """Utility class for creating transparent PNG images"""
    
    @staticmethod
    def create_rounded_rect(width, height, color, alpha=255, radius=10):
        """Create a surface with a rounded rectangle shape"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, width, height)
        pygame.draw.rect(surface, (*color, alpha), rect, border_radius=radius)
        return surface
    
    @staticmethod
    def create_button_image(width, height, bg_color, border_color=None, border_width=0, radius=10, alpha=255):
        """Create a button image with optional border"""
        surface = TransparentImageMaker.create_rounded_rect(width, height, bg_color, alpha, radius)
        
        # Add border if specified
        if border_width > 0 and border_color:
            rect = pygame.Rect(border_width//2, border_width//2, 
                              width - border_width, height - border_width)
            pygame.draw.rect(surface, (*border_color, alpha), rect, 
                             width=border_width, border_radius=radius)
        
        return surface
    
    @staticmethod
    def create_icon(size, icon_type, color=(255, 255, 255), bg_color=None, bg_alpha=0):
        """Create a basic icon image
        
        Args:
            size: Size of the icon (square)
            icon_type: Type of icon ('play', 'pause', 'gear', etc.)
            color: Color of the icon
            bg_color: Optional background color
            bg_alpha: Background transparency (0-255)
        """
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Add background if specified
        if bg_color:
            pygame.draw.rect(surface, (*bg_color, bg_alpha), (0, 0, size, size))
        
        # Draw icon based on type
        if icon_type == 'play':
            points = [(size//4, size//4), (size//4, 3*size//4), (3*size//4, size//2)]
            pygame.draw.polygon(surface, color, points)
        elif icon_type == 'pause':
            bar_width = size // 3
            pygame.draw.rect(surface, color, (size//4, size//4, bar_width, size//2))
            pygame.draw.rect(surface, color, (size//2, size//4, bar_width, size//2))
        elif icon_type == 'gear':
            # Gear outer circle
            pygame.draw.circle(surface, color, (size//2, size//2), size//2 - 4)
            # Gear inner circle (empty)
            pygame.draw.circle(surface, (0, 0, 0, 0), (size//2, size//2), size//3)
            # Gear teeth (simple version)
            for i in range(8):
                angle = i * 45
                x = size//2 + int((size//2) * 0.8 * pygame.math.Vector2(1, 0).rotate(angle).x)
                y = size//2 + int((size//2) * 0.8 * pygame.math.Vector2(1, 0).rotate(angle).y)
                pygame.draw.circle(surface, color, (x, y), size//8)
        
        return surface
    
    @staticmethod
    def save_surface_as_png(surface, filename):
        """Save a surface as a PNG file"""
        pygame.image.save(surface, filename)
        return filename