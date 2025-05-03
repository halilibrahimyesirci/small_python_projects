"""
UI Manager Module
Handles UI components, windows, and menus for the game
"""

import tkinter as tk
from tkinter import ttk, font
import sys
from typing import Dict, List, Any, Optional, Tuple, Callable

# Import configuration
sys.path.append("../../config")
try:
    from config.game_config import *
except ImportError:
    try:
        from Window_Frame_Game.config.game_config import *
    except ImportError:
        # Fallback to prevent errors
        print("Warning: Could not import game_config, using fallback values")

# Import logger
from ..utils.logger import Logger

class UIManager:
    """
    Manages all UI elements, menus, and windows for the game
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the UI manager
        
        Args:
            root: Main Tkinter root window
        """
        self.root = root
        self.logger = Logger("UIManager", log_level=Logger.INFO)
        self.logger.info("Initializing UI Manager")
        
        # Dictionary to store windows by name
        self.windows = {}
        
        # Dictionary to store callback functions
        self.callbacks = {}
        
        # Set up styles
        self._setup_styles()
        
    def _setup_styles(self):
        """Set up UI styles and fonts"""
        # Create custom fonts
        self.title_font = font.Font(family="Arial", size=24, weight="bold")
        self.subtitle_font = font.Font(family="Arial", size=18, weight="bold")
        self.button_font = font.Font(family="Arial", size=14, weight="bold")
        self.label_font = font.Font(family="Arial", size=12)
        self.small_font = font.Font(family="Arial", size=10)
        
        # Configure ttk styles
        self.style = ttk.Style()
        
        # Button styles
        self.style.configure("TButton", font=self.button_font, padding=10)
        self.style.configure("Menu.TButton", font=self.button_font, padding=15)
        self.style.configure("Small.TButton", font=self.small_font, padding=5)
        
        # Label styles
        self.style.configure("TLabel", font=self.label_font)
        self.style.configure("Title.TLabel", font=self.title_font)
        self.style.configure("Subtitle.TLabel", font=self.subtitle_font)
        
        # Progress bar style (for health bar, etc.)
        self.style.configure("Health.Horizontal.TProgressbar",
                            background="green",
                            troughcolor="#444444")
                            
        # Level progress style
        self.style.configure("Level.Horizontal.TProgressbar",
                            background="blue",
                            troughcolor="#444444")
        
    def register_callback(self, name: str, callback: Callable):
        """
        Register a callback function
        
        Args:
            name: Name of the callback
            callback: Callback function
        """
        self.callbacks[name] = callback
        
    def trigger_callback(self, name: str, *args, **kwargs):
        """
        Trigger a callback function
        
        Args:
            name: Name of the callback
            *args, **kwargs: Arguments to pass to the callback
        """
        if name in self.callbacks:
            try:
                return self.callbacks[name](*args, **kwargs)
            except Exception as e:
                self.logger.exception(f"Error in callback '{name}'", e)
        else:
            self.logger.warning(f"Callback '{name}' not registered")
            
    def create_window(self, name: str, title: str = "", width: int = 400, height: int = 300) -> tk.Toplevel:
        """
        Create a new window
        
        Args:
            name: Window identifier name
            title: Window title
            width: Window width
            height: Window height
            
        Returns:
            The created window
        """
        # Create window
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(f"{width}x{height}")
        window.resizable(False, False)
        window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(name))
        
        # Make it transient (always on top of the main window)
        window.transient(self.root)
        
        # Make it modal (blocks input to other windows)
        window.grab_set()
        
        # Center window on screen
        window.withdraw()
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"+{x}+{y}")
        
        # Store in windows dictionary
        self.windows[name] = window
        
        # Add a frame to contain all controls
        frame = ttk.Frame(window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Make the window visible
        window.deiconify()
        window.update()
        
        self.logger.debug(f"Created window '{name}'", {"title": title, "dimensions": f"{width}x{height}"})
        
        return window
        
    def show_window(self, name: str):
        """
        Show a window by name
        
        Args:
            name: Window identifier name
        """
        if name in self.windows:
            window = self.windows[name]
            window.deiconify()
            window.lift()
            window.focus_set()
            self.logger.debug(f"Showing window '{name}'")
        else:
            self.logger.warning(f"Window '{name}' not found")
            
    def close_window(self, name: str):
        """
        Close a window by name
        
        Args:
            name: Window identifier name
        """
        if name in self.windows:
            window = self.windows[name]
            window.grab_release()
            window.destroy()
            del self.windows[name]
            self.logger.debug(f"Closed window '{name}'")
        else:
            self.logger.warning(f"Window '{name}' not found")
            
    def create_main_menu(self) -> tk.Toplevel:
        """
        Create the main menu window
        
        Returns:
            Main menu window
        """
        # Create window
        window = self.create_window("main_menu", GAME_TITLE, 600, 500)
        frame = window.winfo_children()[0]  # Get the main frame
        
        # Add title
        title_label = ttk.Label(frame, text=GAME_TITLE, style="Title.TLabel")
        title_label.pack(pady=(0, 30))
        
        # Add buttons
        play_button = ttk.Button(
            frame, 
            text="Play Game", 
            style="Menu.TButton",
            command=lambda: self.trigger_callback("menu_play", None)
        )
        play_button.pack(fill=tk.X, pady=10)
        
        settings_button = ttk.Button(
            frame, 
            text="Settings", 
            style="Menu.TButton",
            command=lambda: self.trigger_callback("menu_settings", None)
        )
        settings_button.pack(fill=tk.X, pady=10)
        
        help_button = ttk.Button(
            frame, 
            text="Help", 
            style="Menu.TButton",
            command=lambda: self.trigger_callback("menu_help", None)
        )
        help_button.pack(fill=tk.X, pady=10)
        
        quit_button = ttk.Button(
            frame, 
            text="Quit", 
            style="Menu.TButton",
            command=lambda: self.trigger_callback("menu_quit", None)
        )
        quit_button.pack(fill=tk.X, pady=10)
        
        # Add version info at bottom
        version_label = ttk.Label(
            frame, 
            text="Version 1.0",
            font=self.small_font
        )
        version_label.pack(side=tk.BOTTOM, pady=10)
        
        # Ensure window is visible
        window.deiconify()
        window.lift()
        window.attributes('-topmost', True)
        window.after(100, lambda: window.attributes('-topmost', False))
        window.focus_force()
        
        self.logger.info("Main menu created")
        
        return window
        
    def create_settings_menu(self) -> tk.Toplevel:
        """
        Create the settings menu window
        
        Returns:
            Settings menu window
        """
        # Create window
        window = self.create_window("settings_menu", "Settings", 500, 400)
        frame = window.winfo_children()[0]  # Get the main frame
        
        # Add title
        title_label = ttk.Label(frame, text="Game Settings", style="Subtitle.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Load current settings
        current_settings = load_settings()
        
        # Create settings frame
        settings_frame = ttk.Frame(frame)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Difficulty setting
        diff_frame = ttk.Frame(settings_frame)
        diff_frame.pack(fill=tk.X, pady=10)
        
        diff_label = ttk.Label(diff_frame, text="Difficulty:", width=20, anchor=tk.W)
        diff_label.pack(side=tk.LEFT)
        
        difficulty_var = tk.StringVar(value=current_settings.get("difficulty", "medium"))
        diff_combo = ttk.Combobox(
            diff_frame, 
            textvariable=difficulty_var,
            values=["easy", "medium", "hard", "expert"],
            state="readonly",
            width=30
        )
        diff_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Sound enabled setting
        sound_frame = ttk.Frame(settings_frame)
        sound_frame.pack(fill=tk.X, pady=10)
        
        sound_label = ttk.Label(sound_frame, text="Sound Enabled:", width=20, anchor=tk.W)
        sound_label.pack(side=tk.LEFT)
        
        sound_enabled_var = tk.BooleanVar(value=current_settings.get("sound_enabled", True))
        sound_check = ttk.Checkbutton(sound_frame, variable=sound_enabled_var)
        sound_check.pack(side=tk.LEFT)
        
        # Music volume setting
        music_frame = ttk.Frame(settings_frame)
        music_frame.pack(fill=tk.X, pady=10)
        
        music_label = ttk.Label(music_frame, text="Music Volume:", width=20, anchor=tk.W)
        music_label.pack(side=tk.LEFT)
        
        music_volume_var = tk.DoubleVar(value=current_settings.get("music_volume", 0.7))
        music_scale = ttk.Scale(
            music_frame, 
            from_=0.0, 
            to=1.0, 
            orient=tk.HORIZONTAL,
            variable=music_volume_var
        )
        music_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # SFX volume setting
        sfx_frame = ttk.Frame(settings_frame)
        sfx_frame.pack(fill=tk.X, pady=10)
        
        sfx_label = ttk.Label(sfx_frame, text="SFX Volume:", width=20, anchor=tk.W)
        sfx_label.pack(side=tk.LEFT)
        
        sfx_volume_var = tk.DoubleVar(value=current_settings.get("sfx_volume", 1.0))
        sfx_scale = ttk.Scale(
            sfx_frame, 
            from_=0.0, 
            to=1.0, 
            orient=tk.HORIZONTAL,
            variable=sfx_volume_var
        )
        sfx_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Show FPS setting
        fps_frame = ttk.Frame(settings_frame)
        fps_frame.pack(fill=tk.X, pady=10)
        
        fps_label = ttk.Label(fps_frame, text="Show FPS:", width=20, anchor=tk.W)
        fps_label.pack(side=tk.LEFT)
        
        show_fps_var = tk.BooleanVar(value=current_settings.get("show_fps", True))
        fps_check = ttk.Checkbutton(fps_frame, variable=show_fps_var)
        fps_check.pack(side=tk.LEFT)
        
        # Show hitboxes setting
        hitbox_frame = ttk.Frame(settings_frame)
        hitbox_frame.pack(fill=tk.X, pady=10)
        
        hitbox_label = ttk.Label(hitbox_frame, text="Show Hitboxes:", width=20, anchor=tk.W)
        hitbox_label.pack(side=tk.LEFT)
        
        show_hitboxes_var = tk.BooleanVar(value=current_settings.get("show_hitboxes", False))
        hitbox_check = ttk.Checkbutton(hitbox_frame, variable=show_hitboxes_var)
        hitbox_check.pack(side=tk.LEFT)
        
        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Save and cancel buttons
        save_button = ttk.Button(
            button_frame, 
            text="Save",
            command=lambda: self._save_settings(
                difficulty_var.get(),
                sound_enabled_var.get(),
                music_volume_var.get(),
                sfx_volume_var.get(),
                show_fps_var.get(),
                show_hitboxes_var.get()
            )
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel",
            command=lambda: self.close_window("settings_menu")
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.logger.info("Settings menu created")
        
        return window
        
    def _save_settings(self, difficulty, sound_enabled, music_volume, sfx_volume, show_fps, show_hitboxes):
        """
        Save settings and close the settings window
        
        Args:
            difficulty: Game difficulty
            sound_enabled: Whether sound is enabled
            music_volume: Music volume level
            sfx_volume: Sound effects volume level
            show_fps: Whether to show FPS
            show_hitboxes: Whether to show hitboxes
        """
        # Create settings dictionary
        settings = {
            "difficulty": difficulty,
            "sound_enabled": sound_enabled,
            "music_volume": music_volume,
            "sfx_volume": sfx_volume,
            "show_fps": show_fps,
            "show_hitboxes": show_hitboxes
        }
        
        # Trigger callback
        self.trigger_callback("settings_saved", settings)
        
        # Close window
        self.close_window("settings_menu")
        
    def create_help_menu(self) -> tk.Toplevel:
        """
        Create the help menu window
        
        Returns:
            Help menu window
        """
        # Create window
        window = self.create_window("help_menu", "Help", 600, 500)
        frame = window.winfo_children()[0]  # Get the main frame
        
        # Add title
        title_label = ttk.Label(frame, text="Game Instructions", style="Subtitle.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Add scrollable text area for instructions
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        help_text = tk.Text(text_frame, yscrollcommand=text_scroll.set, wrap=tk.WORD, font=self.label_font)
        help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        text_scroll.config(command=help_text.yview)
        
        # Insert help text
        help_text.insert(tk.END, "Window Frame Game\n\n", "title")
        help_text.insert(tk.END, "Game Objective:\n", "heading")
        help_text.insert(tk.END, "Capture target windows by moving your player window to collide with them. "
                             "Avoid obstacles that will slow you down or block your movement. "
                             "Collect powerups to gain special abilities.\n\n")
                             
        help_text.insert(tk.END, "Controls:\n", "heading")
        help_text.insert(tk.END, "- Arrow Keys: Move your player window\n"
                             "- Space: Activate special ability (when available)\n"
                             "- Escape: Pause game\n\n")
                             
        help_text.insert(tk.END, "Game Elements:\n", "heading")
        help_text.insert(tk.END, "- Targets: Capture these to gain points\n"
                             "- Obstacles: Avoid these as they will block or slow you\n"
                             "- Powerups: Collect these for special abilities\n\n")
                             
        help_text.insert(tk.END, "Target Types:\n", "heading")
        help_text.insert(tk.END, "- Standard: Stationary targets\n"
                             "- Moving: Targets that move around\n"
                             "- Evasive: Targets that try to avoid you\n"
                             "- Boss: Tough targets that require multiple hits\n\n")
                             
        help_text.insert(tk.END, "Powerup Types:\n", "heading")
        help_text.insert(tk.END, "- Speed: Increases your movement speed\n"
                             "- Magnet: Pulls targets toward you\n"
                             "- Shield: Protects you from obstacles\n"
                             "- Time: Slows down all other windows\n\n")
                             
        help_text.insert(tk.END, "Scoring:\n", "heading")
        help_text.insert(tk.END, "- Standard Target: 10 points\n"
                             "- Moving Target: 20 points\n"
                             "- Evasive Target: 30 points\n"
                             "- Boss Target: 50 points\n\n")
                             
        help_text.insert(tk.END, "Level Progression:\n", "heading")
        help_text.insert(tk.END, "Each level requires a certain number of points to complete. "
                             "As you progress, targets become more challenging, but you'll "
                             "earn more points for capturing them.")
                             
        # Configure text tags
        help_text.tag_configure("title", font=self.title_font, justify=tk.CENTER)
        help_text.tag_configure("heading", font=self.subtitle_font)
        
        # Make text read-only
        help_text.config(state=tk.DISABLED)
        
        # Close button
        close_button = ttk.Button(
            frame, 
            text="Close",
            command=lambda: self.close_window("help_menu")
        )
        close_button.pack(pady=20)
        
        self.logger.info("Help menu created")
        
        return window
        
    def create_game_hud(self, parent: tk.Widget) -> Dict[str, tk.Widget]:
        """
        Create the in-game heads-up display
        
        Args:
            parent: Parent widget
            
        Returns:
            Dictionary of HUD elements
        """
        # Create a frame for the HUD at the top of the screen
        hud_frame = ttk.Frame(parent, padding=10)
        hud_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Left side - score and level
        left_frame = ttk.Frame(hud_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        score_label = ttk.Label(left_frame, text="Score: 0", font=self.button_font)
        score_label.pack(anchor=tk.W)
        
        level_label = ttk.Label(left_frame, text="Level: 1", font=self.button_font)
        level_label.pack(anchor=tk.W)
        
        # Center - health bar
        center_frame = ttk.Frame(hud_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        
        health_label = ttk.Label(center_frame, text="Health:", font=self.label_font)
        health_label.pack(anchor=tk.W)
        
        health_bar = ttk.Progressbar(
            center_frame, 
            orient=tk.HORIZONTAL, 
            length=200, 
            mode="determinate",
            style="Health.Horizontal.TProgressbar"
        )
        health_bar.pack(fill=tk.X)
        health_bar["value"] = 100
        
        # Right side - active powerups and time
        right_frame = ttk.Frame(hud_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        powerup_label = ttk.Label(right_frame, text="Active Powerups:", font=self.label_font)
        powerup_label.pack(anchor=tk.E)
        
        powerup_text = ttk.Label(right_frame, text="None", font=self.small_font)
        powerup_text.pack(anchor=tk.E)
        
        time_label = ttk.Label(right_frame, text="Time: 0:00", font=self.label_font)
        time_label.pack(anchor=tk.E, pady=(10, 0))
        
        # Progress bar for level completion
        progress_frame = ttk.Frame(hud_frame)
        progress_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        progress_bar = ttk.Progressbar(
            progress_frame, 
            orient=tk.HORIZONTAL, 
            length=200, 
            mode="determinate",
            style="Level.Horizontal.TProgressbar"
        )
        progress_bar.pack(fill=tk.X)
        progress_bar["value"] = 0
        
        # Return dictionary of HUD elements
        hud_elements = {
            "frame": hud_frame,
            "score_label": score_label,
            "level_label": level_label,
            "health_bar": health_bar,
            "powerup_text": powerup_text,
            "time_label": time_label,
            "progress_bar": progress_bar
        }
        
        self.logger.debug("Game HUD created")
        
        return hud_elements
        
    def update_hud(self, hud_elements: Dict[str, tk.Widget], score: int, level: int, 
                  active_effects: List[str], health_percent: float = 100, 
                  progress_percent: float = 0, game_time: float = 0):
        """
        Update the HUD with current game state
        
        Args:
            hud_elements: Dictionary of HUD elements
            score: Current score
            level: Current level
            active_effects: List of active effect names
            health_percent: Health percentage (0-100)
            progress_percent: Level progress percentage (0-100)
            game_time: Game time in seconds
        """
        # Update score and level
        hud_elements["score_label"].config(text=f"Score: {score}")
        hud_elements["level_label"].config(text=f"Level: {level}")
        
        # Update health bar
        hud_elements["health_bar"]["value"] = max(0, min(100, health_percent))
        
        # Update powerups text
        if active_effects:
            hud_elements["powerup_text"].config(text=", ".join(active_effects))
        else:
            hud_elements["powerup_text"].config(text="None")
            
        # Update time
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        hud_elements["time_label"].config(text=f"Time: {minutes}:{seconds:02d}")
        
        # Update progress bar
        hud_elements["progress_bar"]["value"] = max(0, min(100, progress_percent))
        
    def create_pause_menu(self, parent: tk.Widget) -> Dict[str, tk.Widget]:
        """
        Create the pause menu overlay
        
        Args:
            parent: Parent widget
            
        Returns:
            Dictionary of pause menu elements
        """
        # Create a semi-transparent overlay frame
        overlay = tk.Frame(parent, bg="#000000")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.configure(bg="#333333")
        
        # Create a frame for the pause menu
        pause_frame = ttk.Frame(overlay, padding=20)
        pause_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Add title
        title_label = ttk.Label(pause_frame, text="Game Paused", style="Title.TLabel")
        title_label.pack(pady=(0, 30))
        
        # Add buttons
        resume_button = ttk.Button(
            pause_frame, 
            text="Resume Game", 
            style="Menu.TButton",
            command=lambda: self.trigger_callback("pause_resume", None)
        )
        resume_button.pack(fill=tk.X, pady=10)
        
        settings_button = ttk.Button(
            pause_frame, 
            text="Settings", 
            style="Menu.TButton",
            command=lambda: self.trigger_callback("pause_settings", None)
        )
        settings_button.pack(fill=tk.X, pady=10)
        
        quit_button = ttk.Button(
            pause_frame, 
            text="Quit to Menu", 
            style="Menu.TButton",
            command=lambda: self.trigger_callback("pause_quit", None)
        )
        quit_button.pack(fill=tk.X, pady=10)
        
        # Return dictionary of pause menu elements
        pause_elements = {
            "overlay": overlay,
            "frame": pause_frame,
            "title": title_label,
            "resume_button": resume_button,
            "settings_button": settings_button,
            "quit_button": quit_button
        }
        
        self.logger.debug("Pause menu created")
        
        return pause_elements
        
    def show_pause_menu(self, pause_elements: Dict[str, tk.Widget]):
        """
        Show the pause menu
        
        Args:
            pause_elements: Dictionary of pause menu elements
        """
        pause_elements["overlay"].lift()
        pause_elements["overlay"].place(relx=0, rely=0, relwidth=1, relheight=1)
        
    def hide_pause_menu(self, pause_elements: Dict[str, tk.Widget]):
        """
        Hide the pause menu
        
        Args:
            pause_elements: Dictionary of pause menu elements
        """
        pause_elements["overlay"].place_forget()
        
    def create_level_complete_screen(self, parent: tk.Widget) -> Dict[str, tk.Widget]:
        """
        Create the level complete overlay
        
        Args:
            parent: Parent widget
            
        Returns:
            Dictionary of level complete elements
        """
        # Create a semi-transparent overlay frame
        overlay = tk.Frame(parent, bg="#000000")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.configure(bg="#333333")
        
        # Create a frame for the level complete screen
        level_frame = ttk.Frame(overlay, padding=20)
        level_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Add title
        title_label = ttk.Label(level_frame, text="Level Complete!", style="Title.TLabel")
        title_label.pack(pady=(0, 30))
        
        # Add stats
        stats_frame = ttk.Frame(level_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        level_label = ttk.Label(stats_frame, text="Level: 1", font=self.subtitle_font)
        level_label.pack(pady=5)
        
        score_label = ttk.Label(stats_frame, text="Score: 0", font=self.subtitle_font)
        score_label.pack(pady=5)
        
        targets_label = ttk.Label(stats_frame, text="Targets Captured: 0", font=self.subtitle_font)
        targets_label.pack(pady=5)
        
        # Add continue button
        continue_button = ttk.Button(
            level_frame, 
            text="Continue to Next Level", 
            style="Menu.TButton",
            command=lambda: self.trigger_callback("level_continue", None)
        )
        continue_button.pack(fill=tk.X, pady=20)
        
        # Return dictionary of level complete elements
        level_elements = {
            "overlay": overlay,
            "frame": level_frame,
            "title": title_label,
            "level_label": level_label,
            "score_label": score_label,
            "targets_label": targets_label,
            "continue_button": continue_button
        }
        
        # Hide initially
        overlay.place_forget()
        
        self.logger.debug("Level complete screen created")
        
        return level_elements
        
    def show_level_complete(self, level_elements: Dict[str, tk.Widget], level: int, score: int, targets: int):
        """
        Show the level complete screen with stats
        
        Args:
            level_elements: Dictionary of level complete elements
            level: Current level
            score: Current score
            targets: Number of targets captured
        """
        # Update stats
        level_elements["level_label"].config(text=f"Level: {level}")
        level_elements["score_label"].config(text=f"Score: {score}")
        level_elements["targets_label"].config(text=f"Targets Captured: {targets}")
        
        # Show overlay
        level_elements["overlay"].lift()
        level_elements["overlay"].place(relx=0, rely=0, relwidth=1, relheight=1)
        
    def hide_level_complete(self, level_elements: Dict[str, tk.Widget]):
        """
        Hide the level complete screen
        
        Args:
            level_elements: Dictionary of level complete elements
        """
        level_elements["overlay"].place_forget()
        
    def create_game_over_screen(self, parent: tk.Widget) -> Dict[str, tk.Widget]:
        """
        Create the game over overlay
        
        Args:
            parent: Parent widget
            
        Returns:
            Dictionary of game over elements
        """
        # Create a semi-transparent overlay frame
        overlay = tk.Frame(parent, bg="#000000")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.configure(bg="#333333")
        
        # Create a frame for the game over screen
        gameover_frame = ttk.Frame(overlay, padding=20)
        gameover_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Add title
        title_label = ttk.Label(gameover_frame, text="Game Over", style="Title.TLabel")
        title_label.pack(pady=(0, 30))
        
        # Add stats
        stats_frame = ttk.Frame(gameover_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        final_score_label = ttk.Label(stats_frame, text="Final Score: 0", font=self.subtitle_font)
        final_score_label.pack(pady=5)
        
        levels_label = ttk.Label(stats_frame, text="Levels Completed: 0", font=self.subtitle_font)
        levels_label.pack(pady=5)
        
        # Add buttons
        retry_button = ttk.Button(
            gameover_frame, 
            text="Retry", 
            style="Menu.TButton",
            command=lambda: self.trigger_callback("gameover_retry", None)
        )
        retry_button.pack(fill=tk.X, pady=10)
        
        menu_button = ttk.Button(
            gameover_frame, 
            text="Return to Menu", 
            style="Menu.TButton",
            command=lambda: self.trigger_callback("gameover_menu", None)
        )
        menu_button.pack(fill=tk.X, pady=10)
        
        # Return dictionary of game over elements
        gameover_elements = {
            "overlay": overlay,
            "frame": gameover_frame,
            "title": title_label,
            "final_score_label": final_score_label,
            "levels_label": levels_label,
            "retry_button": retry_button,
            "menu_button": menu_button
        }
        
        # Hide initially
        overlay.place_forget()
        
        self.logger.debug("Game over screen created")
        
        return gameover_elements
        
    def show_game_over(self, gameover_elements: Dict[str, tk.Widget], score: int, levels: int):
        """
        Show the game over screen with stats
        
        Args:
            gameover_elements: Dictionary of game over elements
            score: Final score
            levels: Number of levels completed
        """
        # Update stats
        gameover_elements["final_score_label"].config(text=f"Final Score: {score}")
        gameover_elements["levels_label"].config(text=f"Levels Completed: {levels}")
        
        # Show overlay
        gameover_elements["overlay"].lift()
        gameover_elements["overlay"].place(relx=0, rely=0, relwidth=1, relheight=1)
        
    def handle_resize(self, width: int, height: int):
        """
        Handle window resize event
        
        Args:
            width: New window width
            height: New window height
        """
        # Update UI layouts if needed
        self.logger.debug(f"Window resized", {"width": width, "height": height})