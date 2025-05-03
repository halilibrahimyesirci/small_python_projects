import os
import customtkinter as ctk
from tkinter import filedialog, BooleanVar

from src.config.settings import (
    THEME_OPTIONS, FONTS, SCALING_OPTIONS, DEFAULT_OPTIONS, 
    APP_VERSION, DEFAULT_SETTINGS
)
from src.utils.settings_utils import get_actual_font_name
from src.utils.ui_utils import UIUtils


class SettingsTab:
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.tab = parent
        self.settings_manager = settings_manager
        
        self._create_scrollable_frame()
    
    def _create_scrollable_frame(self):
        self.settings_scroll = ctk.CTkScrollableFrame(self.tab)
        self.settings_scroll.pack(padx=20, pady=20, fill="both", expand=True)
        
        settings_frame = ctk.CTkFrame(self.settings_scroll, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True)
        
        # Configure grid
        settings_frame.grid_columnconfigure(0, weight=0)
        settings_frame.grid_columnconfigure(1, weight=1)
        settings_frame.grid_columnconfigure(2, weight=0)
        
        # Create settings sections
        self._create_title(settings_frame)
        self._create_appearance_settings(settings_frame)
        self._create_behavior_settings(settings_frame)
        self._create_info_section(settings_frame)
        self._create_extra_settings(settings_frame)
        self._create_action_buttons(settings_frame)
    
    def _create_title(self, frame):
        settings_title = ctk.CTkLabel(
            frame, 
            text="Application Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        settings_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 30), sticky="w")
    
    def _create_appearance_settings(self, frame):
        appearance_label = ctk.CTkLabel(
            frame, 
            text="Appearance Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        appearance_label.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="w")
        
        # Theme selection
        theme_label = ctk.CTkLabel(frame, text="Theme:")
        theme_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.theme_dropdown = ctk.CTkOptionMenu(
            frame,
            values=THEME_OPTIONS,
            command=self.change_theme
        )
        self.theme_dropdown.grid(row=2, column=1, padx=20, pady=(10, 5), sticky="w")
        self.theme_dropdown.set(self.settings_manager.get("theme"))
        
        # Font selection
        font_label = ctk.CTkLabel(frame, text="Font:")
        font_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        
        self.font_dropdown = ctk.CTkOptionMenu(
            frame,
            values=FONTS,
            command=self.change_font
        )
        self.font_dropdown.grid(row=3, column=1, padx=20, pady=5, sticky="w")
        self.font_dropdown.set(self.settings_manager.get("font_family", "Default"))
        
        # Font sample
        self.font_sample_label = ctk.CTkLabel(
            frame,
            text="Font Sample",
            font=ctk.CTkFont(family=get_actual_font_name(self.settings_manager.get("font_family", "Default")), size=14)
        )
        self.font_sample_label.grid(row=3, column=2, padx=20, pady=5, sticky="w")
        
        # Font size slider
        fontsize_label = ctk.CTkLabel(frame, text="Font Size:")
        fontsize_label.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        
        self.fontsize_slider = ctk.CTkSlider(
            frame,
            from_=8,
            to=24,
            number_of_steps=16,
            command=self.update_font_size
        )
        self.fontsize_slider.grid(row=4, column=1, padx=20, pady=5, sticky="w")
        self.fontsize_slider.set(self.settings_manager.get("font_size"))
        
        self.fontsize_value_label = ctk.CTkLabel(frame, text=f"{self.settings_manager.get('font_size')}px")
        self.fontsize_value_label.grid(row=4, column=2, padx=20, pady=5, sticky="w")
        
        # UI Scaling
        scaling_label = ctk.CTkLabel(frame, text="UI Scaling:")
        scaling_label.grid(row=5, column=0, padx=20, pady=5, sticky="w")
        
        self.scaling_dropdown = ctk.CTkOptionMenu(
            frame,
            values=SCALING_OPTIONS,
            command=self.change_scaling
        )
        self.scaling_dropdown.grid(row=5, column=1, padx=20, pady=5, sticky="w")
        self.scaling_dropdown.set(self.settings_manager.get("ui_scaling", "100%"))
    
    def _create_behavior_settings(self, frame):
        behavior_label = ctk.CTkLabel(
            frame, 
            text="Application Behavior",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        behavior_label.grid(row=6, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Auto-save feature toggle
        self.autosave_var = BooleanVar(value=self.settings_manager.get("auto_save", False))
        autosave_switch = ctk.CTkSwitch(
            frame,
            text="Enable Auto-Save",
            variable=self.autosave_var,
            command=self.toggle_autosave
        )
        autosave_switch.grid(row=7, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        
        self.autosave_status_label = ctk.CTkLabel(
            frame, 
            text=f"Auto-Save is {'enabled' if self.settings_manager.get('auto_save', False) else 'disabled'}"
        )
        self.autosave_status_label.grid(row=7, column=2, padx=20, pady=5, sticky="w")
        
        # Feature toggle
        self.feature_var = BooleanVar(value=self.settings_manager.get("feature_enabled"))
        feature_switch = ctk.CTkSwitch(
            frame,
            text="Enable Feature",
            variable=self.feature_var,
            command=self.toggle_feature
        )
        feature_switch.grid(row=8, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        
        # Custom directory setting
        directory_label = ctk.CTkLabel(frame, text="Custom Directory:")
        directory_label.grid(row=9, column=0, padx=20, pady=5, sticky="w")
        
        directory_frame = ctk.CTkFrame(frame, fg_color="transparent")
        directory_frame.grid(row=9, column=1, columnspan=2, padx=20, pady=5, sticky="ew")
        
        self.directory_entry = ctk.CTkEntry(directory_frame, width=300)
        self.directory_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.directory_entry.insert(0, self.settings_manager.get("custom_directory", os.path.expanduser("~")))
        
        browse_button = ctk.CTkButton(
            directory_frame,
            text="Browse...",
            width=100,
            command=self.browse_directory
        )
        browse_button.pack(side="right")
        
        # Username entry
        username_label = ctk.CTkLabel(frame, text="Username:")
        username_label.grid(row=10, column=0, padx=20, pady=5, sticky="w")
        
        self.username_entry = ctk.CTkEntry(frame, width=200)
        self.username_entry.grid(row=10, column=1, padx=20, pady=5, sticky="w")
        self.username_entry.insert(0, self.settings_manager.get("username"))
        
        # Options combobox
        option_label = ctk.CTkLabel(frame, text="Select Option:")
        option_label.grid(row=11, column=0, padx=20, pady=5, sticky="w")
        
        self.option_dropdown = ctk.CTkOptionMenu(
            frame,
            values=DEFAULT_OPTIONS
        )
        self.option_dropdown.grid(row=11, column=1, padx=20, pady=5, sticky="w")
        self.option_dropdown.set(self.settings_manager.get("selected_option"))
    
    def _create_info_section(self, frame):
        info_label = ctk.CTkLabel(
            frame, 
            text="Application Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        info_label.grid(row=12, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Version display
        version_label = ctk.CTkLabel(frame, text="Version:")
        version_label.grid(row=13, column=0, padx=20, pady=5, sticky="w")
        
        version_value = ctk.CTkLabel(
            frame, 
            text=APP_VERSION,
            font=ctk.CTkFont(weight="bold")
        )
        version_value.grid(row=13, column=1, padx=20, pady=5, sticky="w")
        
        # Help button
        help_button = ctk.CTkButton(
            frame,
            text="Help",
            width=100,
            command=self.show_help
        )
        help_button.grid(row=14, column=0, padx=20, pady=(20, 5), sticky="w")
    
    def _create_extra_settings(self, frame):
        for i in range(5):
            extra_label = ctk.CTkLabel(
                frame,
                text=f"Additional Setting {i+1}",
                font=ctk.CTkFont(size=14)
            )
            extra_label.grid(row=15+i, column=0, padx=20, pady=5, sticky="w")
            
            extra_entry = ctk.CTkEntry(frame, width=200)
            extra_entry.grid(row=15+i, column=1, padx=20, pady=5, sticky="w")
            extra_entry.insert(0, f"Value {i+1}")
    
    def _create_action_buttons(self, frame):
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=30, column=0, columnspan=3, padx=20, pady=(30, 20), sticky="ew")
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            command=self.save_settings
        )
        save_button.pack(side="left", padx=(0, 10))
        
        reset_button = ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_settings
        )
        reset_button.pack(side="left")
    
    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)
        self.settings_manager.set("theme", new_theme)
    
    def change_font(self, new_font):
        self.settings_manager.set("font_family", new_font)
        actual_font = get_actual_font_name(new_font)
        self.font_sample_label.configure(
            font=ctk.CTkFont(family=actual_font, size=14)
        )
    
    def change_scaling(self, new_scaling):
        self.settings_manager.set("ui_scaling", new_scaling)
        # Extract the numeric value from the scaling string (e.g., "100%" -> 1.0)
        scaling_factor = float(new_scaling.strip("%")) / 100
        ctk.set_widget_scaling(scaling_factor)
        UIUtils.show_message("UI Scaling", f"UI scaling changed to {new_scaling}.")
    
    def toggle_autosave(self):
        self.settings_manager.set("auto_save", self.autosave_var.get())
        status = "enabled" if self.autosave_var.get() else "disabled"
        self.autosave_status_label.configure(text=f"Auto-Save is {status}")
    
    def toggle_feature(self):
        self.settings_manager.set("feature_enabled", self.feature_var.get())
    
    def browse_directory(self):
        directory = filedialog.askdirectory(
            initialdir=self.settings_manager.get("custom_directory", os.path.expanduser("~"))
        )
        if directory:  # User selected a directory (not canceled)
            self.settings_manager.set("custom_directory", directory)
            self.directory_entry.delete(0, "end")
            self.directory_entry.insert(0, directory)
    
    def show_help(self):
        help_text = (
            f"CustomTkinter App Base v{APP_VERSION}\n\n"
            "This is a template application built with CustomTkinter.\n\n"
            "• Home Tab: Interactive demo elements\n"
            "• Data Tab: Form input and data display\n"
            "• Settings Tab: Application configuration\n\n"
            "This application serves as a starting point for your own projects."
        )
        UIUtils.show_message("Help", help_text)
    
    def update_font_size(self, value):
        font_size = int(value)
        self.settings_manager.set("font_size", font_size)
        self.fontsize_value_label.configure(text=f"{font_size}px")
        
        # Update the font sample to show the new size
        self.font_sample_label.configure(
            font=ctk.CTkFont(
                family=get_actual_font_name(self.settings_manager.get("font_family", "Default")), 
                size=font_size
            )
        )
    
    def save_settings(self):
        # Update settings from UI
        self.settings_manager.set("username", self.username_entry.get())
        self.settings_manager.set("selected_option", self.option_dropdown.get())
        self.settings_manager.set("custom_directory", self.directory_entry.get())
        
        if self.settings_manager.save_settings():
            UIUtils.show_message("Settings", "Settings saved successfully!")
        else:
            UIUtils.show_error("Error", "Failed to save settings.")
    
    def reset_settings(self):
        # Reset to default values
        self.settings_manager.reset_to_defaults()
        
        # Update UI
        self.theme_dropdown.set(DEFAULT_SETTINGS["theme"])
        self.change_theme(DEFAULT_SETTINGS["theme"])
        
        self.feature_var.set(DEFAULT_SETTINGS["feature_enabled"])
        self.autosave_var.set(DEFAULT_SETTINGS["auto_save"])
        self.toggle_autosave()
        
        self.username_entry.delete(0, 'end')
        self.username_entry.insert(0, DEFAULT_SETTINGS["username"])
        
        self.option_dropdown.set(DEFAULT_SETTINGS["selected_option"])
        
        self.fontsize_slider.set(DEFAULT_SETTINGS["font_size"])
        self.fontsize_value_label.configure(text=f"{DEFAULT_SETTINGS['font_size']}px")
        
        self.font_dropdown.set(DEFAULT_SETTINGS["font_family"])
        self.change_font(DEFAULT_SETTINGS["font_family"])
        
        self.scaling_dropdown.set(DEFAULT_SETTINGS["ui_scaling"])
        
        self.directory_entry.delete(0, 'end')
        self.directory_entry.insert(0, DEFAULT_SETTINGS["custom_directory"])
        
        UIUtils.show_message("Settings", "Settings reset to defaults.")