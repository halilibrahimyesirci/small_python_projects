import pygame
import logging

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


def display_text(surface, text, font, color, x, y, center=False):
    """Helper function to draw text on a surface"""
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
        
    surface.blit(text_surf, text_rect)
    return text_rect