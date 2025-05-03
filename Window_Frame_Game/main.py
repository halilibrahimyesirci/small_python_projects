import tkinter as tk
import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

from src.engine.game_engine import GameEngine
from src.ui.ui_manager import UIManager
from src.utils.logger import Logger

class WindowFrameGame:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Window Frame Game")
        
        self.logger = Logger("WindowFrameGame", log_level=Logger.INFO)
        self.logger.info("Initializing Window Frame Game")
        
        self.root.geometry("1024x768")
        self.root.configure(bg="#333333")
        self.root.resizable(True, True)
        
        self.ui_manager = UIManager(self.root)
        
        self.game_engine = GameEngine(self.root)
        self.game_engine.set_ui_manager(self.ui_manager)
        
        self._setup_event_handlers()
        
        self._register_key_bindings()
        
        self.logger.info("Showing main menu")
        self.game_engine.show_main_menu()
        
    def _setup_event_handlers(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.root.bind("<Configure>", self._on_resize)
        
    def _register_key_bindings(self):
        self.root.bind("<KeyPress>", self.game_engine.handle_key_press)
        self.root.bind("<KeyRelease>", self.game_engine.handle_key_release)
        
    def _on_close(self):
        self.logger.info("Window close requested")
        
        self.game_engine.shutdown()
        
        self.root.destroy()
        
    def _on_resize(self, event):
        if event.widget == self.root:
            if hasattr(self.ui_manager, 'handle_resize'):
                self.ui_manager.handle_resize(event.width, event.height)
                
    def run(self):
        self.logger.info("Starting game main loop")
        
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.exception("Error in main loop", e)
        finally:
            self.logger.info("Game exited")
            
if __name__ == "__main__":
    game = WindowFrameGame()
    game.run()
