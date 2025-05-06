\
import pygame
import sys

# Pygame chosen for its flexibility in graphics and animations, suitable for visual feedback.
# Future versions will leverage this for combo effects, critical clicks, and dynamic UI.

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TIMER_DURATION = 30  # seconds
CLICK_TARGET = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BUTTON_COLOR = (100, 100, 255)
BUTTON_HOVER_COLOR = (150, 150, 255)

# Game States
STATE_START = "START"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER_WIN = "GAME_OVER_WIN"
STATE_GAME_OVER_LOSE = "GAME_OVER_LOSE"

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG Clicker V0.1")
clock = pygame.time.Clock()
font_style = pygame.font.SysFont(None, 50)
small_font_style = pygame.font.SysFont(None, 30)

# --- Game Variables ---
clicks = 0
start_ticks = 0  # For timer
game_state = STATE_START
current_target = CLICK_TARGET # Initial target

# Clickable button properties
button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 100)

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
                        clicks += 1
                elif game_state == STATE_GAME_OVER_WIN or game_state == STATE_GAME_OVER_LOSE:
                    # Restart the game
                    game_state = STATE_START
                    current_target = CLICK_TARGET # Reset target for now

    # --- Game Logic ---
    if game_state == STATE_PLAYING:
        seconds_elapsed = (pygame.time.get_ticks() - start_ticks) / 1000
        if seconds_elapsed >= TIMER_DURATION:
            if clicks >= current_target:
                game_state = STATE_GAME_OVER_WIN
            else:
                game_state = STATE_GAME_OVER_LOSE
        elif clicks >= current_target: # Reached target before time ran out
             game_state = STATE_GAME_OVER_WIN


    # --- Drawing ---
    screen.fill(BLACK) # Default background

    if game_state == STATE_START:
        display_text("Click to Start", font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
        display_text(f"Target: {current_target} clicks in {TIMER_DURATION}s", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)

    elif game_state == STATE_PLAYING:
        # Draw Click Button
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
        display_text("Click Me!", font_style, BLACK, screen, button_rect.centerx, button_rect.centery, center=True)

        # Display Clicks
        display_text(f"Clicks: {clicks}", font_style, WHITE, screen, 20, 20)
        # Display Timer
        seconds_remaining = max(0, TIMER_DURATION - ((pygame.time.get_ticks() - start_ticks) / 1000))
        display_text(f"Time: {seconds_remaining:.1f}s", font_style, WHITE, screen, SCREEN_WIDTH - 200, 20)
        # Display Target
        display_text(f"Target: {current_target}", font_style, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 60, center=True)


    elif game_state == STATE_GAME_OVER_WIN:
        display_text("You Won!", font_style, GREEN, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, center=True)
        display_text(f"Total Clicks: {clicks}", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
        display_text("Click to Restart", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)

    elif game_state == STATE_GAME_OVER_LOSE:
        display_text("Game Over!", font_style, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, center=True)
        display_text(f"Clicks: {clicks} / Target: {current_target}", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
        display_text("Click to Restart", small_font_style, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)

    pygame.display.flip() # Update the full screen

pygame.quit()
sys.exit()
