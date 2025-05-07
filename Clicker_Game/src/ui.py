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
        
    def update(self, mouse_pos, mouse_clicked, current_time):
        """Update button state based on mouse interaction"""
        # Reset to normal if click animation is complete
        if self.state == "clicked" and current_time - self.click_time >= self.click_duration:
            self.state = "normal"
        
        # Check if mouse is over button
        if self.rect.collidepoint(mouse_pos):
            if mouse_clicked:
                self.state = "clicked"
                self.click_time = current_time
                return True
            elif self.state != "clicked":
                self.state = "hover"
        elif self.state != "clicked":
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
        self.handle_rect = pygame.Rect(0, 0, 20, rect.height)
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
        
        # Draw handle
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