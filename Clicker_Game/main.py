"""
RPG Clicker Game V0.3.2
A clicker-style game with RPG elements.
"""

import logging
import os
import sys

# Setup logging
logging.basicConfig(
    filename='rpg_clicker.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    
    def main():
        """Main entry point for the game"""
        logger.info("Starting RPG Clicker V0.3.2")
        
        # Initialize the resource manager
        resource_manager = ResourceManager()
        
        # Initialize the player
        player = Player(resource_manager)
        
        # Initialize the level manager
        level_manager = LevelManager(resource_manager)
        
        # Initialize the game engine
        engine = GameEngine(resource_manager, player, level_manager)
        
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
