import pygame
import sys
import os
import random
import time

# Pygame chosen for its flexibility in graphics and animations, suitable for visual feedback.
# Future versions will leverage this for combo effects, critical clicks, and dynamic UI.

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TIMER_DURATION = 30  # seconds
INITIAL_CLICK_TARGET = 50
TARGET_INCREMENT = 10  # Increase target by this amount each level

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BUTTON_COLOR = (100, 100, 255)
BUTTON_HOVER_COLOR = (150, 150, 255)
BUTTON_CLICK_COLOR = (200, 200, 255)
BORDER_COLOR = (50, 50, 200)

# Game States
STATE_START = "START"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER_WIN = "GAME_OVER_WIN"
STATE_GAME_OVER_LOSE = "GAME_OVER_LOSE"

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG Clicker V0.2")
clock = pygame.time.Clock()
font_style = pygame.font.SysFont(None, 50)
small_font_style = pygame.font.SysFont(None, 30)
tiny_font_style = pygame.font.SysFont(None, 20)

# --- Game Variables ---
clicks = 0
click_value = 1  # How many clicks each click is worth
start_ticks = 0  # For timer
game_state = STATE_START
current_target = INITIAL_CLICK_TARGET  # Initial target
current_level = 1  # Start at level 1

# Clickable button properties
button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 100)
button_state = "normal"  # States: normal, hover, clicked
button_click_time = 0
button_click_duration = 0.1  # How long the button stays in "clicked" state

# Visual feedback
click_texts = []  # List to store floating +1 text animations

# Background
background = None
try:
    background_path = os.path.join("assets", "images", "background.png")
    if os.path.exists(background_path):
        background = pygame.image.load(background_path)
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception as e:
    print(f"Could not load background: {e}")

class ClickText:
    def __init__(self, x, y, value=1, color=WHITE):
        self.x = x
        self.y = y
        self.value = value
        self.color = color
        self.alpha = 255  # Full opacity
        self.life = 1.0  # Life in seconds
        self.creation_time = time.time()
        
    def update(self):
        """Update position and opacity"""
        current_time = time.time()
        elapsed = current_time - self.creation_time
        if elapsed > self.life:
            return False  # Text should be removed
        
        # Move upward
        self.y -= 1
        
        # Fade out
        self.alpha = int(255 * (1 - (elapsed / self.life)))
        
        return True  # Text should continue to be displayed
    
    def draw(self, surface):
        """Draw the text on the surface"""
        # Create a temporary surface with per-pixel alpha
        font = small_font_style
        if self.value > 1:  # Make critical clicks bigger
            font = font_style
            
        text_obj = font.render(f"+{self.value}", True, self.color)
        text_obj.set_alpha(self.alpha)
        surface.blit(text_obj, (self.x, self.y))

def display_text(text, font, color, surface, x, y, center=False):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

# --- Game Loop ---
running = True
while running:
    time_delta = clock.tick(FPS) / 1000.0  # Time since last frame in seconds
    current_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if game_state == STATE_START:
                    game_state = STATE_PLAYING
                    clicks = 0
                    start_ticks = pygame.time.get_ticks()
                elif game_state == STATE_PLAYING:
                    if button_rect.collidepoint(event.pos):
                        # Visual feedback
                        button_state = "clicked"
                        button_click_time = current_time
                        
                        # Add floating +1 text
                        x = event.pos[0]
                        y = event.pos[1] - 20  # Position slightly above click
                        
                        # 10% chance for a critical click (worth 2)
                        if random.random() < 0.1:
                            clicks += 2
                            click_texts.append(ClickText(x, y, 2, YELLOW))
                        else:
                            clicks += click_value
                            click_texts.append(ClickText(x, y))
                            
                elif game_state == STATE_GAME_OVER_WIN or game_state == STATE_GAME_OVER_LOSE:
                    # Handle game restart
                    if game_state == STATE_GAME_OVER_WIN:
                        # Level up and increase target only if player won
                        current_level += 1
                        current_target += TARGET_INCREMENT
                    else:
                        # Reset to initial values if player lost
                        current_level = 1
                        current_target = INITIAL_CLICK_TARGET
                    
                    # Reset game state
                    game_state = STATE_START

    # --- Game Logic ---
    
    # Update button state
    mouse_pos = pygame.mouse.get_pos()
    if button_state == "clicked" and current_time - button_click_time >= button_click_duration:
        button_state = "normal"  # Reset after duration
    
    if button_rect.collidepoint(mouse_pos):
        if button_state != "clicked":  # Don't override clicked state
            button_state = "hover"
    else:
        if button_state != "clicked":  # Don't override clicked state
            button_state = "normal"
    
    # Update floating click texts
    for text in click_texts[:]:  # Use a copy of the list for safe removal
        if not text.update():
            click_texts.remove(text)
    
    # Game state specific logic
    if game_state == STATE_PLAYING:
        seconds_elapsed = (pygame.time.get_ticks() - start_ticks) / 1000
        if seconds_elapsed >= TIMER_DURATION:
            if clicks >= current_target:
                game_state = STATE_GAME_OVER_WIN
            else:
                game_state = STATE_GAME_OVER_LOSE
        elif clicks >= current_target:  # Reached target before time ran out
            game_state = STATE_GAME_OVER_WIN


    # --- Drawing ---
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BLACK)  # Default background

    if game_state == STATE_START:
        display_text("RPG Clicker", font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, center=True)
        display_text("Click to Start", font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
        display_text(f"Level {current_level}: Target {current_target} clicks in {TIMER_DURATION}s", 
                    small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)

    elif game_state == STATE_PLAYING:
        # Draw Level Info (top center)
        display_text(f"Level {current_level}", font_style, WHITE, screen, SCREEN_WIDTH // 2, 20, center=True)
        
        # Draw Click Button with border
        if button_state == "normal":
            button_color = BUTTON_COLOR
        elif button_state == "hover":
            button_color = BUTTON_HOVER_COLOR
        else:  # clicked
            button_color = BUTTON_CLICK_COLOR
            
        # Draw border (slightly larger rectangle behind the button)
        border_rect = button_rect.inflate(10, 10)
        pygame.draw.rect(screen, BORDER_COLOR, border_rect)
        pygame.draw.rect(screen, button_color, button_rect)
        
        display_text("Click Me!", font_style, BLACK, screen, button_rect.centerx, button_rect.centery, center=True)

        # Display Clicks (top left)
        display_text(f"Clicks: {clicks}/{current_target}", font_style, WHITE, screen, 20, 20)
        
        # Display Timer (top right)
        seconds_remaining = max(0, TIMER_DURATION - ((pygame.time.get_ticks() - start_ticks) / 1000))
        display_text(f"Time: {seconds_remaining:.1f}s", font_style, WHITE, screen, SCREEN_WIDTH - 200, 20)
        
        # Draw any active floating click texts
        for text in click_texts:
            text.draw(screen)


    elif game_state == STATE_GAME_OVER_WIN:
        display_text("Level Complete!", font_style, GREEN, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 50, center=True)
        display_text(f"Total Clicks: {clicks}/{current_target}", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, center=True)
        display_text(f"Level {current_level} Completed", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, center=True)
        display_text(f"Next Level: {current_level + 1}, Target: {current_target + TARGET_INCREMENT}", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, center=True)
        display_text("Click to Continue", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, center=True)

    elif game_state == STATE_GAME_OVER_LOSE:
        display_text("Game Over!", font_style, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 50, center=True)
        display_text(f"Clicks: {clicks} / Target: {current_target}", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, center=True)
        display_text(f"You reached Level {current_level}", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, center=True)
        display_text("Click to Restart from Level 1", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)

    # Display version in bottom right
    display_text("V0.2", tiny_font_style, WHITE, screen, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 20)

    pygame.display.flip()  # Update the full screen

pygame.quit()
sys.exit()
