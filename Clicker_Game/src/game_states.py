"""
Game state management system
"""
import pygame
import logging
import random
import math
import os
from src.mechanics.common import *
from src.mechanics.menu_state import update_menu, render_menu
from src.mechanics.playing_state import update_playing, render_playing
from src.mechanics.esc_menu_state import update_esc_menu, render_esc_menu
from src.mechanics.settings_state import update_settings, render_settings
from src.mechanics.shop_state import update_shop, render_shop
from src.mechanics.upgrade_state import update_upgrade, render_upgrade
from src.mechanics.game_over_states import update_game_over_win, render_game_over_win, update_game_over_lose, render_game_over_lose
from src.mechanics.ability_select_state import update_ability_select, render_ability_select

# Set up logger
logger = logging.getLogger(__name__)

class GameStateManager:
    """Handles transitions between different game states"""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.state_update_functions = {
            STATE_MENU: update_menu,
            STATE_PLAYING: update_playing,
            STATE_GAME_OVER_WIN: update_game_over_win,
            STATE_GAME_OVER_LOSE: update_game_over_lose,
            STATE_UPGRADE: update_upgrade,
            STATE_SETTINGS: update_settings,
            STATE_ABILITY_SELECT: update_ability_select,
            STATE_ESC_MENU: update_esc_menu,
            STATE_SHOP: update_shop
        }
        
        self.state_render_functions = {
            STATE_MENU: render_menu,
            STATE_PLAYING: render_playing,
            STATE_GAME_OVER_WIN: render_game_over_win,
            STATE_GAME_OVER_LOSE: render_game_over_lose,
            STATE_UPGRADE: render_upgrade,
            STATE_SETTINGS: render_settings,
            STATE_ABILITY_SELECT: render_ability_select,
            STATE_ESC_MENU: render_esc_menu,
            STATE_SHOP: render_shop
        }
    
    def update(self, state, time_delta):
        """Update current game state"""
        if state in self.state_update_functions:
            self.state_update_functions[state](self.game_engine, time_delta)
    
    def render(self, state):
        """Render current game state"""
        if state in self.state_render_functions:
            self.state_render_functions[state](self.game_engine)