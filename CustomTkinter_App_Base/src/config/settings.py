import os

# Application settings
APP_NAME = "CustomTkinter App Base"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "1000x700"
MIN_WINDOW_SIZE = (800, 600)

# Theme settings
DEFAULT_THEME = "System"  # Options: "System", "Dark", "Light"
DEFAULT_COLOR_THEME = "blue"  # Options: "blue", "green", "dark-blue"

# Default application settings
DEFAULT_SETTINGS = {
    "theme": DEFAULT_THEME,
    "feature_enabled": True,
    "username": "",
    "selected_option": "Option 1",
    "font_size": 12,
    "font_family": "Default",
    "ui_scaling": "100%",
    "auto_save": False,
    "custom_directory": os.path.expanduser("~")
}

# File paths
SETTINGS_FILE = "settings.json"

# UI Configuration
FONTS = ["Default", "Arial", "Times New Roman", "Verdana"]
SCALING_OPTIONS = ["80%", "90%", "100%", "110%", "120%"]
THEME_OPTIONS = ["System", "Light", "Dark"]
DEFAULT_OPTIONS = ["Option 1", "Option 2", "Option 3"]