import os
import json
import customtkinter as ctk
from tkinter import messagebox

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")  # Options: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue" (default), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("CustomTkinter App Base")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Create variables for settings
        self.settings = {
            "theme": ctk.get_appearance_mode(),
            "feature_enabled": True,
            "username": "",
            "selected_option": "Option 1",
            "font_size": 12
        }
        
        # Load settings if file exists
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        self.load_settings()
        
        # Create the main layout
        self.create_widgets()
        
    def create_widgets(self):
        # Create the tabview (tabbed interface)
        self.tabview = ctk.CTkTabview(self, width=800, height=500)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Create tabs
        self.tab_home = self.tabview.add("Home")
        self.tab_data = self.tabview.add("Data")
        self.tab_settings = self.tabview.add("Settings")
        
        # Set the default tab
        self.tabview.set("Home")
        
        # Configure the layout for each tab
        self.setup_home_tab()
        self.setup_data_tab()
        self.setup_settings_tab()
    
    def setup_home_tab(self):
        # Welcome message
        welcome_label = ctk.CTkLabel(
            self.tab_home, 
            text="Welcome to CustomTkinter App Base",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        welcome_label.pack(padx=20, pady=(40, 20))
        
        description_label = ctk.CTkLabel(
            self.tab_home,
            text="This is a template application with a tabbed interface.\nUse it as a starting point for your own projects.",
            font=ctk.CTkFont(size=16)
        )
        description_label.pack(padx=20, pady=10)
        
        # Example button
        action_button = ctk.CTkButton(
            self.tab_home,
            text="Click Me!",
            command=self.example_action
        )
        action_button.pack(padx=20, pady=20)
    
    def setup_data_tab(self):
        # Frame for data controls
        control_frame = ctk.CTkFrame(self.tab_data)
        control_frame.pack(padx=20, pady=20, fill="x")
        
        # Filter entry
        filter_label = ctk.CTkLabel(control_frame, text="Filter:")
        filter_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.filter_entry = ctk.CTkEntry(control_frame, width=200)
        self.filter_entry.pack(side="left", padx=5, pady=10)
        
        # Filter button
        filter_button = ctk.CTkButton(
            control_frame,
            text="Apply Filter",
            command=self.apply_filter
        )
        filter_button.pack(side="left", padx=10, pady=10)
        
        # Data display area
        self.data_textbox = ctk.CTkTextbox(self.tab_data, width=700, height=400)
        self.data_textbox.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        
        # Insert placeholder text
        sample_data = "Sample data would appear here.\n\n"
        sample_data += "This textbox can display:\n"
        sample_data += "- Program outputs\n"
        sample_data += "- Log information\n"
        sample_data += "- Data analysis results\n"
        sample_data += "- File contents\n\n"
        sample_data += "Apply filters using the control panel above."
        
        self.data_textbox.insert("1.0", sample_data)
        self.data_textbox.configure(state="disabled")  # Make it read-only
    
    def setup_settings_tab(self):
        # Create a frame for settings
        settings_frame = ctk.CTkFrame(self.tab_settings)
        settings_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Theme selection
        theme_label = ctk.CTkLabel(
            settings_frame, 
            text="Theme:",
            font=ctk.CTkFont(size=16)
        )
        theme_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.theme_options = ["System", "Light", "Dark"]
        self.theme_dropdown = ctk.CTkOptionMenu(
            settings_frame,
            values=self.theme_options,
            command=self.change_theme
        )
        self.theme_dropdown.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="w")
        self.theme_dropdown.set(self.settings["theme"])
        
        # Feature toggle
        self.feature_var = ctk.BooleanVar(value=self.settings["feature_enabled"])
        feature_switch = ctk.CTkSwitch(
            settings_frame,
            text="Enable Feature",
            variable=self.feature_var,
            command=self.toggle_feature
        )
        feature_switch.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        
        # Username entry
        username_label = ctk.CTkLabel(settings_frame, text="Username:")
        username_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.username_entry = ctk.CTkEntry(settings_frame, width=200)
        self.username_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        self.username_entry.insert(0, self.settings["username"])
        
        # Options combobox
        option_label = ctk.CTkLabel(settings_frame, text="Select Option:")
        option_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        self.options = ["Option 1", "Option 2", "Option 3"]
        self.option_dropdown = ctk.CTkOptionMenu(
            settings_frame,
            values=self.options
        )
        self.option_dropdown.grid(row=3, column=1, padx=20, pady=10, sticky="w")
        self.option_dropdown.set(self.settings["selected_option"])
        
        # Font size slider
        fontsize_label = ctk.CTkLabel(settings_frame, text="Font Size:")
        fontsize_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        
        self.fontsize_slider = ctk.CTkSlider(
            settings_frame,
            from_=8,
            to=24,
            number_of_steps=16,
            command=self.update_font_size
        )
        self.fontsize_slider.grid(row=4, column=1, padx=20, pady=10, sticky="w")
        self.fontsize_slider.set(self.settings["font_size"])
        
        self.fontsize_value_label = ctk.CTkLabel(settings_frame, text=f"{self.settings['font_size']}px")
        self.fontsize_value_label.grid(row=4, column=2, padx=(0, 20), pady=10, sticky="w")
        
        # Buttons for settings actions
        button_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=3, padx=20, pady=(30, 20), sticky="ew")
        
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
    
    def example_action(self):
        messagebox.showinfo("Action", "You clicked the button!")
    
    def apply_filter(self):
        filter_text = self.filter_entry.get()
        messagebox.showinfo("Filter Applied", f"Filter applied: {filter_text}\n\nThis is a placeholder for actual filter functionality.")
    
    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)
        self.settings["theme"] = new_theme
    
    def toggle_feature(self):
        self.settings["feature_enabled"] = self.feature_var.get()
    
    def update_font_size(self, value):
        font_size = int(value)
        self.settings["font_size"] = font_size
        self.fontsize_value_label.configure(text=f"{font_size}px")
    
    def save_settings(self):
        # Update settings from UI
        self.settings["username"] = self.username_entry.get()
        self.settings["selected_option"] = self.option_dropdown.get()
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings dictionary with loaded values
                    for key, value in loaded_settings.items():
                        if key in self.settings:
                            self.settings[key] = value
        except Exception as e:
            print(f"Failed to load settings: {str(e)}")
    
    def reset_settings(self):
        # Reset to default values
        default_settings = {
            "theme": "System",
            "feature_enabled": True,
            "username": "",
            "selected_option": "Option 1",
            "font_size": 12
        }
        
        # Update UI
        self.theme_dropdown.set(default_settings["theme"])
        self.change_theme(default_settings["theme"])
        
        self.feature_var.set(default_settings["feature_enabled"])
        
        self.username_entry.delete(0, 'end')
        self.username_entry.insert(0, default_settings["username"])
        
        self.option_dropdown.set(default_settings["selected_option"])
        
        self.fontsize_slider.set(default_settings["font_size"])
        self.fontsize_value_label.configure(text=f"{default_settings['font_size']}px")
        
        # Update settings dictionary
        self.settings = default_settings.copy()
        
        messagebox.showinfo("Settings", "Settings reset to defaults.")

if __name__ == "__main__":
    app = App()
    app.mainloop()