"""
Window Frame Game - Main Entry Point
This module initializes and launches the game

Author: GitHub Copilot
Date: May 3, 2025
"""

import tkinter as tk
import sys
import os
from pathlib import Path

# Add the project directory to the path to ensure imports work properly
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

# Import game engine and UI manager
from src.engine.game_engine import GameEngine
from src.ui.ui_manager import UIManager

# Import utility for logging
from src.utils.logger import Logger

class WindowFrameGame:
    """Main game class that initializes the window and game components"""
    
    def __init__(self):
        # Create root window
        self.root = tk.Tk()
        self.root.title("Window Frame Game")
        
        # Initialize logger
        self.logger = Logger("WindowFrameGame", log_level=Logger.INFO)
        self.logger.info("Initializing Window Frame Game")
        
        # Set window properties
        self.root.geometry("1024x768")
        self.root.configure(bg="#333333")
        self.root.resizable(True, True)
        
        # Initialize UI manager
        self.ui_manager = UIManager(self.root)
        
        # Initialize game engine
        self.game_engine = GameEngine(self.root)
        self.game_engine.set_ui_manager(self.ui_manager)
        
        # Set up event handlers
        self._setup_event_handlers()
        
        # Register key bindings
        self._register_key_bindings()
        
        # Show the main menu
        self.logger.info("Showing main menu")
        self.game_engine.show_main_menu()
        
    def _setup_event_handlers(self):
        """Set up event handlers for window events"""
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Handle window resize
        self.root.bind("<Configure>", self._on_resize)
        
    def _register_key_bindings(self):
        """Register keyboard bindings"""
        # Game controls
        self.root.bind("<KeyPress>", self.game_engine.handle_key_press)
        self.root.bind("<KeyRelease>", self.game_engine.handle_key_release)
        
    def _on_close(self):
        """Handle window close event"""
        self.logger.info("Window close requested")
        
        # Shut down game engine
        self.game_engine.shutdown()
        
        # Destroy the root window
        self.root.destroy()
        
    def _on_resize(self, event):
        """
        Handle window resize event
        
        Args:
            event: Tkinter event object
        """
        # Only handle if this is for the main window
        if event.widget == self.root:
            # Update UI layout
            if hasattr(self.ui_manager, 'handle_resize'):
                self.ui_manager.handle_resize(event.width, event.height)
                
    def run(self):
        """Run the game"""
        self.logger.info("Starting game main loop")
        
        try:
            # Start Tkinter main loop
            self.root.mainloop()
        except Exception as e:
            self.logger.exception("Error in main loop", e)
        finally:
            self.logger.info("Game exited")
            
if __name__ == "__main__":
    # Create and run the game
    game = WindowFrameGame()
    game.run()
