"""
RPG Clicker Game V0.3.3
A clicker-style game with RPG elements.
"""

import logging
import os
import sys
import time
import traceback
from logging.handlers import RotatingFileHandler

# Setup logging
log_file = 'rpg_clicker.log'
try:
    # Ensure the log directory exists
    log_dir = os.path.dirname(os.path.abspath(log_file))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger with a rotating file handler
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Add rotating file handler (max 5MB per file, keep 3 backup files)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Add console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and above go to console
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Add a timestamp to the log file
    logging.info("=" * 80)
    logging.info(f"Log session started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 80)
    
except Exception as e:
    print(f"Failed to set up logging: {e}")
    # Set up a basic configuration if the advanced one fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Create a logger for the main module
logger = logging.getLogger("main")

# Ensure we can import from the src directory
if os.path.exists(os.path.join(os.path.dirname(__file__), "src")):
    sys.path.append(os.path.dirname(__file__))
    
try:
    import pygame
    from src.utils.helpers import ResourceManager
    from src.player import Player
    from src.levels import LevelManager
    from src.engine import GameEngine
    from src.shop import ShopManager
    
    def main():
        """Main entry point for the game"""
        logger.info("Starting RPG Clicker V0.3.3")
        
        # Initialize the resource manager
        resource_manager = ResourceManager()
        
        # Initialize the player
        player = Player(resource_manager)
        
        # Initialize the level manager
        level_manager = LevelManager(resource_manager)
        
        # Initialize the shop manager
        shop_manager = ShopManager(resource_manager)
        
        # Initialize the game engine with shop manager
        engine = GameEngine(resource_manager, player, level_manager, shop_manager)
        
        # Run the game
        engine.run()
        
    if __name__ == "__main__":
        try:
            main()
        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)
            print(f"An error occurred: {e}")
            sys.exit(1)
            
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you have installed all required dependencies.")
    print("Try running: pip install pygame")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
