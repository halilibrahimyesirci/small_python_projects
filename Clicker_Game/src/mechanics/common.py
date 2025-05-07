"""
Common constants and imports for game mechanics
"""
import pygame
import random
import logging
import math
import os
from src.ui import Button, display_text, TextParticle

logger = logging.getLogger(__name__)

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER_WIN = "game_over_win"
STATE_GAME_OVER_LOSE = "game_over_lose"
STATE_UPGRADE = "upgrade"
STATE_PAUSE = "pause"
STATE_SETTINGS = "settings"
STATE_ABILITY_SELECT = "ability_select"
STATE_ESC_MENU = "esc_menu"
STATE_SHOP = "shop"

# Game constants
CLICK_DELAY = 0.45  # Seconds between clicks