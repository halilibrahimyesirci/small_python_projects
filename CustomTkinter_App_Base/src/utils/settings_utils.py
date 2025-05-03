import os
import json
import customtkinter as ctk

from src.config.settings import DEFAULT_SETTINGS, SETTINGS_FILE


class SettingsManager:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), SETTINGS_FILE)
        self.load_settings()
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    for key, value in loaded_settings.items():
                        if key in self.settings:
                            self.settings[key] = value
        except Exception as e:
            print(f"Failed to load settings: {str(e)}")
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Failed to save settings: {str(e)}")
            return False
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        if key in self.settings:
            self.settings[key] = value
            return True
        return False
    
    def reset_to_defaults(self):
        self.settings = DEFAULT_SETTINGS.copy()
        return True


def apply_theme(theme_name):
    ctk.set_appearance_mode(theme_name)


def apply_scaling(scaling_value):
    try:
        scaling_factor = float(scaling_value.strip("%")) / 100
        ctk.set_widget_scaling(scaling_factor)
        return True
    except ValueError:
        return False


def get_actual_font_name(font_name):
    if font_name == "Default":
        return None  # Use system default font
    return font_name