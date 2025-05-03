import os
import customtkinter as ctk
from tkinter import Menu

from src.ui.home_tab import HomeTab
from src.ui.data_tab import DataTab
from src.ui.settings_tab import SettingsTab
from src.utils.settings_utils import SettingsManager, apply_theme, apply_scaling
from src.config.settings import APP_NAME, WINDOW_SIZE, MIN_WINDOW_SIZE, APP_VERSION


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.minsize(MIN_WINDOW_SIZE[0], MIN_WINDOW_SIZE[1])
        
        self.settings_manager = SettingsManager()
        self.app_version = APP_VERSION
        
        self.setup_initial_theme()
        self.create_widgets()
        self.create_menu()
    
    def setup_initial_theme(self):
        apply_theme(self.settings_manager.get("theme"))
        apply_scaling(self.settings_manager.get("ui_scaling", "100%"))
    
    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.tab_home = self.tabview.add("Home")
        self.tab_data = self.tabview.add("Data")
        self.tab_settings = self.tabview.add("Settings")
        
        self.tabview.set("Home")
        
        # Configure all tab sections
        self.setup_home_tab()
        self.setup_data_tab()
        self.setup_settings_tab()
        
        # Status bar at the bottom
        self.status_bar = ctk.CTkFrame(self, height=25)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(
            self.status_bar, 
            text=f"{APP_NAME} | Version: {self.app_version}",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)
    
    def create_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Settings", command=self.save_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # View menu
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Home", command=lambda: self.tabview.set("Home"))
        view_menu.add_command(label="Data", command=lambda: self.tabview.set("Data"))
        view_menu.add_command(label="Settings", command=lambda: self.tabview.set("Settings"))
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_home_tab(self):
        self.home_tab = HomeTab(self.tab_home)
    
    def setup_data_tab(self):
        self.data_tab = DataTab(self.tab_data)
    
    def setup_settings_tab(self):
        self.settings_tab = SettingsTab(self.tab_settings, self.settings_manager)
    
    def save_settings(self):
        self.settings_tab.save_settings()
    
    def show_about(self):
        about_window = ctk.CTkToplevel(self)
        about_window.title("About")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.focus_set()
        
        # Make the window modal
        about_window.grab_set()
        about_window.transient(self)
        
        app_title = ctk.CTkLabel(
            about_window,
            text=APP_NAME,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        app_title.pack(pady=(20, 5))
        
        version_label = ctk.CTkLabel(
            about_window,
            text=f"Version {self.app_version}",
            font=ctk.CTkFont(size=14)
        )
        version_label.pack(pady=(0, 20))
        
        description = ctk.CTkLabel(
            about_window,
            text=(
                "A comprehensive template application built with CustomTkinter.\n"
                "Features tabbed interface, modern UI components,\n"
                "and extensive configuration options."
            ),
            wraplength=350,
            justify="center"
        )
        description.pack(pady=10, padx=20)
        
        copyright_label = ctk.CTkLabel(
            about_window,
            text="© 2025 Your Name",
            font=ctk.CTkFont(size=12)
        )
        copyright_label.pack(pady=(20, 5))
        
        close_button = ctk.CTkButton(
            about_window,
            text="Close",
            command=about_window.destroy
        )
        close_button.pack(pady=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()