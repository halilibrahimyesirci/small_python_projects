import os
import json
import time
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox, Listbox, StringVar
from PIL import Image  # Required for CTkImage

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")  # Options: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue" (default), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("CustomTkinter App Base")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Create variables for settings
        self.settings = {
            "theme": ctk.get_appearance_mode(),
            "feature_enabled": True,
            "username": "",
            "selected_option": "Option 1",
            "font_size": 12,
            "font_family": "Default",
            "ui_scaling": "100%",
            "auto_save": False,
            "custom_directory": os.path.expanduser("~")
        }
        
        # Initialize additional variables
        self.current_progress = 0
        self.progress_running = False
        self.progress_thread = None
        self.current_slider_value = 50
        self.app_version = "1.0.0"
        
        # Load settings if file exists
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        self.load_settings()
        
        # Create the main layout
        self.create_widgets()
        
    def create_widgets(self):
        # Create the tabview (tabbed interface)
        self.tabview = ctk.CTkTabview(self, width=900, height=600)
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
        """
        Enhanced Home tab with more interactive elements and better layout.
        Includes welcome section, image display, progress bar, slider, and segmented button.
        """
        # Configure grid layout (3 columns x 8 rows)
        self.tab_home.grid_columnconfigure(0, weight=1)
        self.tab_home.grid_columnconfigure(1, weight=1)
        self.tab_home.grid_columnconfigure(2, weight=1)
        
        # Title section
        title_label = ctk.CTkLabel(
            self.tab_home, 
            text="Welcome to CustomTkinter App Base",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1E3A8A", "#3B82F6")  # Dark blue in light mode, lighter blue in dark mode
        )
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="ew")
        
        # Description section (with detailed text)
        description_frame = ctk.CTkFrame(self.tab_home)
        description_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="ew")
        
        description_text = (
            "This is a comprehensive template application built with CustomTkinter, "
            "showcasing various UI components and functionalities. It provides a solid "
            "foundation for developing desktop applications with a modern look and feel. "
            "The tabbed interface allows for organized content presentation, and the settings "
            "system enables easy configuration and personalization."
        )
        
        description_textbox = ctk.CTkTextbox(description_frame, height=80, wrap="word")
        description_textbox.pack(padx=10, pady=10, fill="both", expand=True)
        description_textbox.insert("1.0", description_text)
        description_textbox.configure(state="disabled")  # Make it read-only
        
        # Left column - Image display area
        image_frame = ctk.CTkFrame(self.tab_home)
        image_frame.grid(row=2, column=0, rowspan=3, padx=(20, 10), pady=10, sticky="nsew")
        
        # Create a placeholder image (default icon)
        # Load placeholder image or use a colored frame if image doesn't exist
        try:
            # Path to a placeholder image in resources directory
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "resources", "placeholder.png")
            
            # If the image doesn't exist, we'll use a colored frame
            if not os.path.exists(image_path):
                image_label = ctk.CTkLabel(
                    image_frame,
                    text="Placeholder Image\n(200x200px)",
                    width=200,
                    height=200,
                    fg_color=("gray70", "gray30"),
                    corner_radius=10
                )
            else:
                # Load the image if it exists
                placeholder_image = ctk.CTkImage(
                    light_image=Image.open(image_path),
                    dark_image=Image.open(image_path),
                    size=(200, 200)
                )
                image_label = ctk.CTkLabel(
                    image_frame, 
                    image=placeholder_image,
                    text=""
                )
        except Exception as e:
            # Fallback if there's an issue with the image
            image_label = ctk.CTkLabel(
                image_frame,
                text=f"Image Placeholder\n{str(e)}",
                width=200,
                height=200,
                fg_color=("gray70", "gray30"),
                corner_radius=10
            )
        
        image_label.pack(padx=20, pady=20)
        
        image_caption = ctk.CTkLabel(
            image_frame,
            text="Application Logo",
            font=ctk.CTkFont(size=14)
        )
        image_caption.pack(pady=(0, 10))
        
        # Middle column - Progress bar and slider
        progress_frame = ctk.CTkFrame(self.tab_home)
        progress_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        progress_frame.grid_columnconfigure(0, weight=1)
        
        progress_label = ctk.CTkLabel(
            progress_frame,
            text="Progress Demonstration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        progress_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="ew")
        self.progress_bar.set(0)  # Initialize to 0
        
        self.progress_value_label = ctk.CTkLabel(progress_frame, text="0%")
        self.progress_value_label.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")
        
        progress_button = ctk.CTkButton(
            progress_frame,
            text="Start Progress",
            command=self.start_progress_animation
        )
        progress_button.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        
        # Slider section
        slider_frame = ctk.CTkFrame(self.tab_home)
        slider_frame.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
        slider_frame.grid_columnconfigure(0, weight=1)
        
        slider_label = ctk.CTkLabel(
            slider_frame,
            text="Adjustable Value",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        slider_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.value_slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self.update_slider_value
        )
        self.value_slider.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="ew")
        self.value_slider.set(50)  # Default to 50%
        
        self.slider_value_label = ctk.CTkLabel(slider_frame, text="Value: 50")
        self.slider_value_label.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")
        
        # Right column - Segmented button
        control_frame = ctk.CTkFrame(self.tab_home)
        control_frame.grid(row=2, column=2, rowspan=2, padx=(10, 20), pady=10, sticky="nsew")
        
        segment_label = ctk.CTkLabel(
            control_frame,
            text="Control Panel",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        segment_label.pack(padx=10, pady=(10, 10))
        
        # Segmented button with at least three segments
        self.segmented_button = ctk.CTkSegmentedButton(
            control_frame,
            values=["Option 1", "Option 2", "Option 3"],
            command=self.segmented_callback
        )
        self.segmented_button.pack(padx=10, pady=10, fill="x")
        self.segmented_button.set("Option 1")
        
        self.segment_result_label = ctk.CTkLabel(
            control_frame, 
            text="Selected: Option 1",
            font=ctk.CTkFont(size=14)
        )
        self.segment_result_label.pack(padx=10, pady=(5, 10))
        
        # Action buttons for different functions
        action_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        action_frame.pack(padx=10, pady=10, fill="x")
        
        action_button1 = ctk.CTkButton(
            action_frame,
            text="Action 1",
            command=lambda: self.perform_action(1)
        )
        action_button1.pack(pady=(0, 5), fill="x")
        
        action_button2 = ctk.CTkButton(
            action_frame,
            text="Action 2",
            command=lambda: self.perform_action(2)
        )
        action_button2.pack(pady=5, fill="x")
        
        action_button3 = ctk.CTkButton(
            action_frame,
            text="Action 3",
            command=lambda: self.perform_action(3)
        )
        action_button3.pack(pady=(5, 0), fill="x")
    
    def setup_data_tab(self):
        """
        Enhanced Data tab with input fields, data display, and manipulation options.
        Includes a form for data entry, a submission system, and a listbox.
        """
        # Configure grid layout (2 columns x 8 rows)
        self.tab_data.grid_columnconfigure(0, weight=1)
        self.tab_data.grid_columnconfigure(1, weight=1)
        
        # Data Input section - Left column
        input_frame = ctk.CTkFrame(self.tab_data)
        input_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        
        input_title = ctk.CTkLabel(
            input_frame,
            text="Data Input Form",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        input_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 15), sticky="w")
        
        # Name entry
        name_label = ctk.CTkLabel(input_frame, text="Name:")
        name_label.grid(row=1, column=0, padx=(20, 10), pady=(10, 5), sticky="w")
        
        self.name_entry = ctk.CTkEntry(input_frame, width=200, placeholder_text="Enter your name")
        self.name_entry.grid(row=1, column=1, padx=(0, 20), pady=(10, 5), sticky="ew")
        
        # Email entry
        email_label = ctk.CTkLabel(input_frame, text="Email:")
        email_label.grid(row=2, column=0, padx=(20, 10), pady=5, sticky="w")
        
        self.email_entry = ctk.CTkEntry(input_frame, width=200, placeholder_text="Enter your email")
        self.email_entry.grid(row=2, column=1, padx=(0, 20), pady=5, sticky="ew")
        
        # Age entry
        age_label = ctk.CTkLabel(input_frame, text="Age:")
        age_label.grid(row=3, column=0, padx=(20, 10), pady=5, sticky="w")
        
        self.age_entry = ctk.CTkEntry(input_frame, width=200, placeholder_text="Enter your age")
        self.age_entry.grid(row=3, column=1, padx=(0, 20), pady=5, sticky="ew")
        
        # Description section
        desc_label = ctk.CTkLabel(input_frame, text="Description:")
        desc_label.grid(row=4, column=0, padx=(20, 10), pady=(15, 5), sticky="nw")
        
        self.desc_textbox = ctk.CTkTextbox(input_frame, width=200, height=100)
        self.desc_textbox.grid(row=4, column=1, padx=(0, 20), pady=(15, 5), sticky="nsew")
        self.desc_textbox.insert("1.0", "Enter additional information here...")
        
        # Submit button
        submit_button = ctk.CTkButton(
            input_frame,
            text="Submit Data",
            command=self.submit_data
        )
        submit_button.grid(row=5, column=0, columnspan=2, padx=20, pady=(15, 20), sticky="ew")
        
        # Data Display section - Right column
        display_frame = ctk.CTkFrame(self.tab_data)
        display_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        
        display_title = ctk.CTkLabel(
            display_frame,
            text="Data Display",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        display_title.pack(padx=20, pady=(20, 15), anchor="w")
        
        # Frame for submitted data display
        self.data_display_frame = ctk.CTkFrame(display_frame, fg_color=("gray90", "gray20"))
        self.data_display_frame.pack(padx=20, pady=(0, 15), fill="x")
        
        self.data_display_label = ctk.CTkLabel(
            self.data_display_frame,
            text="No data submitted yet",
            font=ctk.CTkFont(size=14),
            wraplength=300
        )
        self.data_display_label.pack(padx=20, pady=20)
        
        # Listbox section
        listbox_title = ctk.CTkLabel(
            display_frame,
            text="Items List",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        listbox_title.pack(padx=20, pady=(15, 10), anchor="w")
        
        # Create listbox with items
        self.items_listbox = Listbox(display_frame, height=10)
        self.items_listbox.pack(padx=20, pady=(0, 10), fill="x")
        
        # Add items to the listbox
        list_items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
        for item in list_items:
            self.items_listbox.insert("end", item)
        
        # Listbox control buttons
        listbox_btn_frame = ctk.CTkFrame(display_frame, fg_color="transparent")
        listbox_btn_frame.pack(padx=20, pady=(0, 20), fill="x")
        
        select_next_btn = ctk.CTkButton(
            listbox_btn_frame,
            text="Select Next Item",
            command=self.select_next_item
        )
        select_next_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        clear_selection_btn = ctk.CTkButton(
            listbox_btn_frame,
            text="Clear Selection",
            command=self.clear_listbox_selection
        )
        clear_selection_btn.pack(side="left", fill="x", expand=True)
    
    def setup_settings_tab(self):
        """
        Enhanced Settings tab with more configuration options.
        Includes appearance settings, application behavior settings, and information display.
        """
        # Create a frame for settings
        settings_frame = ctk.CTkFrame(self.tab_settings)
        settings_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Configure grid with 3 columns
        settings_frame.grid_columnconfigure(0, weight=0)  # Labels column - fixed width
        settings_frame.grid_columnconfigure(1, weight=1)  # Controls column - expands
        settings_frame.grid_columnconfigure(2, weight=0)  # Extra column for additional info
        
        # Title
        settings_title = ctk.CTkLabel(
            settings_frame, 
            text="Application Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        settings_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 30), sticky="w")
        
        # --- APPEARANCE SETTINGS SECTION ---
        appearance_label = ctk.CTkLabel(
            settings_frame, 
            text="Appearance Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        appearance_label.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="w")
        
        # Theme selection
        theme_label = ctk.CTkLabel(settings_frame, text="Theme:")
        theme_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.theme_options = ["System", "Light", "Dark"]
        self.theme_dropdown = ctk.CTkOptionMenu(
            settings_frame,
            values=self.theme_options,
            command=self.change_theme
        )
        self.theme_dropdown.grid(row=2, column=1, padx=20, pady=(10, 5), sticky="w")
        self.theme_dropdown.set(self.settings["theme"])
        
        # Font selection
        font_label = ctk.CTkLabel(settings_frame, text="Font:")
        font_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        
        self.font_options = ["Default", "Arial", "Times New Roman", "Verdana"]
        self.font_dropdown = ctk.CTkOptionMenu(
            settings_frame,
            values=self.font_options,
            command=self.change_font
        )
        self.font_dropdown.grid(row=3, column=1, padx=20, pady=5, sticky="w")
        self.font_dropdown.set(self.settings.get("font_family", "Default"))
        
        # Font sample
        self.font_sample_label = ctk.CTkLabel(
            settings_frame,
            text="Font Sample",
            font=ctk.CTkFont(family=self.get_actual_font_name(self.settings.get("font_family", "Default")), size=14)
        )
        self.font_sample_label.grid(row=3, column=2, padx=20, pady=5, sticky="w")
        
        # Font size slider
        fontsize_label = ctk.CTkLabel(settings_frame, text="Font Size:")
        fontsize_label.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        
        self.fontsize_slider = ctk.CTkSlider(
            settings_frame,
            from_=8,
            to=24,
            number_of_steps=16,
            command=self.update_font_size
        )
        self.fontsize_slider.grid(row=4, column=1, padx=20, pady=5, sticky="w")
        self.fontsize_slider.set(self.settings["font_size"])
        
        self.fontsize_value_label = ctk.CTkLabel(settings_frame, text=f"{self.settings['font_size']}px")
        self.fontsize_value_label.grid(row=4, column=2, padx=20, pady=5, sticky="w")
        
        # UI Scaling
        scaling_label = ctk.CTkLabel(settings_frame, text="UI Scaling:")
        scaling_label.grid(row=5, column=0, padx=20, pady=5, sticky="w")
        
        self.scaling_options = ["80%", "90%", "100%", "110%", "120%"]
        self.scaling_dropdown = ctk.CTkOptionMenu(
            settings_frame,
            values=self.scaling_options,
            command=self.change_scaling
        )
        self.scaling_dropdown.grid(row=5, column=1, padx=20, pady=5, sticky="w")
        self.scaling_dropdown.set(self.settings.get("ui_scaling", "100%"))
        
        # --- APPLICATION BEHAVIOR SECTION ---
        behavior_label = ctk.CTkLabel(
            settings_frame, 
            text="Application Behavior",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        behavior_label.grid(row=6, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Auto-save feature toggle
        self.autosave_var = ctk.BooleanVar(value=self.settings.get("auto_save", False))
        autosave_switch = ctk.CTkSwitch(
            settings_frame,
            text="Enable Auto-Save",
            variable=self.autosave_var,
            command=self.toggle_autosave
        )
        autosave_switch.grid(row=7, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        
        self.autosave_status_label = ctk.CTkLabel(
            settings_frame, 
            text=f"Auto-Save is {'enabled' if self.settings.get('auto_save', False) else 'disabled'}"
        )
        self.autosave_status_label.grid(row=7, column=2, padx=20, pady=5, sticky="w")
        
        # Feature toggle (from original code)
        self.feature_var = ctk.BooleanVar(value=self.settings["feature_enabled"])
        feature_switch = ctk.CTkSwitch(
            settings_frame,
            text="Enable Feature",
            variable=self.feature_var,
            command=self.toggle_feature
        )
        feature_switch.grid(row=8, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        
        # Custom directory setting
        directory_label = ctk.CTkLabel(settings_frame, text="Custom Directory:")
        directory_label.grid(row=9, column=0, padx=20, pady=5, sticky="w")
        
        directory_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        directory_frame.grid(row=9, column=1, columnspan=2, padx=20, pady=5, sticky="ew")
        
        self.directory_entry = ctk.CTkEntry(directory_frame, width=300)
        self.directory_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.directory_entry.insert(0, self.settings.get("custom_directory", os.path.expanduser("~")))
        
        browse_button = ctk.CTkButton(
            directory_frame,
            text="Browse...",
            width=100,
            command=self.browse_directory
        )
        browse_button.pack(side="right")
        
        # Username entry (from original code)
        username_label = ctk.CTkLabel(settings_frame, text="Username:")
        username_label.grid(row=10, column=0, padx=20, pady=5, sticky="w")
        
        self.username_entry = ctk.CTkEntry(settings_frame, width=200)
        self.username_entry.grid(row=10, column=1, padx=20, pady=5, sticky="w")
        self.username_entry.insert(0, self.settings["username"])
        
        # Options combobox (from original code)
        option_label = ctk.CTkLabel(settings_frame, text="Select Option:")
        option_label.grid(row=11, column=0, padx=20, pady=5, sticky="w")
        
        self.options = ["Option 1", "Option 2", "Option 3"]
        self.option_dropdown = ctk.CTkOptionMenu(
            settings_frame,
            values=self.options
        )
        self.option_dropdown.grid(row=11, column=1, padx=20, pady=5, sticky="w")
        self.option_dropdown.set(self.settings["selected_option"])
        
        # --- INFORMATION AND ACTION SECTION ---
        info_label = ctk.CTkLabel(
            settings_frame, 
            text="Application Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        info_label.grid(row=12, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Version display
        version_label = ctk.CTkLabel(settings_frame, text="Version:")
        version_label.grid(row=13, column=0, padx=20, pady=5, sticky="w")
        
        version_value = ctk.CTkLabel(
            settings_frame, 
            text=self.app_version,
            font=ctk.CTkFont(weight="bold")
        )
        version_value.grid(row=13, column=1, padx=20, pady=5, sticky="w")
        
        # Help button
        help_button = ctk.CTkButton(
            settings_frame,
            text="Help",
            width=100,
            command=self.show_help
        )
        help_button.grid(row=14, column=0, padx=20, pady=(20, 5), sticky="w")
        
        # Buttons for settings actions
        button_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        button_frame.grid(row=15, column=0, columnspan=3, padx=20, pady=(30, 20), sticky="ew")
        
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
    
    # --- HOME TAB FUNCTIONS ---
    def start_progress_animation(self):
        """Start a progress bar animation in a separate thread."""
        if not self.progress_running:
            self.progress_running = True
            self.progress_thread = threading.Thread(target=self._progress_animation)
            self.progress_thread.daemon = True
            self.progress_thread.start()
    
    def _progress_animation(self):
        """Simulate a progress animation from 0 to 100%."""
        self.current_progress = 0
        while self.current_progress < 1 and self.progress_running:
            self.current_progress += 0.01
            if self.current_progress > 1:
                self.current_progress = 1
                
            # Update progress bar - needs to be done in the main thread
            self.after(10, lambda p=self.current_progress: self._update_progress_ui(p))
            time.sleep(0.05)
            
        self.progress_running = False
    
    def _update_progress_ui(self, progress_value):
        """Update the progress bar UI with the current progress value."""
        self.progress_bar.set(progress_value)
        percentage = int(progress_value * 100)
        self.progress_value_label.configure(text=f"{percentage}%")
    
    def update_slider_value(self, value):
        """Update the displayed slider value when the slider is moved."""
        self.current_slider_value = int(value)
        self.slider_value_label.configure(text=f"Value: {self.current_slider_value}")
    
    def segmented_callback(self, value):
        """Handle segmented button selection."""
        self.segment_result_label.configure(text=f"Selected: {value}")
    
    def perform_action(self, action_number):
        """Perform a placeholder action based on the button clicked."""
        messagebox.showinfo("Action", f"Action {action_number} performed!")
    
    # --- DATA TAB FUNCTIONS ---
    def submit_data(self):
        """Process and display the data submitted via the form."""
        name = self.name_entry.get()
        email = self.email_entry.get()
        age = self.age_entry.get()
        description = self.desc_textbox.get("1.0", "end-1c")
        
        # Simple validation
        if not name or not email:
            messagebox.showwarning("Incomplete Data", "Name and email are required fields.")
            return
        
        # Display the submitted data
        display_text = f"Name: {name}\nEmail: {email}\n"
        if age:
            display_text += f"Age: {age}\n"
        if description and description != "Enter additional information here...":
            display_text += f"Description: {description}"
        
        self.data_display_label.configure(text=display_text)
        messagebox.showinfo("Success", "Data submitted successfully!")
        
        # Clear the form for new entry
        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.age_entry.delete(0, "end")
        self.desc_textbox.delete("1.0", "end")
        self.desc_textbox.insert("1.0", "Enter additional information here...")
    
    def select_next_item(self):
        """Select the next item in the listbox, or loop back to the beginning."""
        try:
            current_index = self.items_listbox.curselection()
            items_count = self.items_listbox.size()
            
            if not current_index:  # No selection, select the first item
                next_index = 0
            else:
                # Select the next item or loop back to the beginning
                next_index = (current_index[0] + 1) % items_count
            
            self.items_listbox.selection_clear(0, "end")
            self.items_listbox.selection_set(next_index)
            self.items_listbox.activate(next_index)
            
        except Exception as e:
            print(f"Error selecting next item: {str(e)}")
    
    def clear_listbox_selection(self):
        """Clear the current selection in the listbox."""
        self.items_listbox.selection_clear(0, "end")
    
    # --- SETTINGS TAB FUNCTIONS ---
    def change_theme(self, new_theme):
        """Change the application theme."""
        ctk.set_appearance_mode(new_theme)
        self.settings["theme"] = new_theme
    
    def change_font(self, new_font):
        """Change the font family for the sample text."""
        self.settings["font_family"] = new_font
        actual_font = self.get_actual_font_name(new_font)
        self.font_sample_label.configure(
            font=ctk.CTkFont(family=actual_font, size=14)
        )
    
    def get_actual_font_name(self, font_name):
        """Convert font name to actual font family name."""
        if font_name == "Default":
            return None  # Use system default font
        return font_name
    
    def change_scaling(self, new_scaling):
        """Change the UI scaling factor."""
        self.settings["ui_scaling"] = new_scaling
        # Extract the numeric value from the scaling string (e.g., "100%" -> 1.0)
        scaling_factor = float(new_scaling.strip("%")) / 100
        ctk.set_widget_scaling(scaling_factor)
        messagebox.showinfo("UI Scaling", f"UI scaling changed to {new_scaling}.")
    
    def toggle_autosave(self):
        """Toggle the auto-save feature."""
        self.settings["auto_save"] = self.autosave_var.get()
        status = "enabled" if self.settings["auto_save"] else "disabled"
        self.autosave_status_label.configure(text=f"Auto-Save is {status}")
    
    def toggle_feature(self):
        """Toggle the generic feature (from original code)."""
        self.settings["feature_enabled"] = self.feature_var.get()
    
    def browse_directory(self):
        """Open a directory selection dialog and update the directory entry field."""
        directory = filedialog.askdirectory(
            initialdir=self.settings.get("custom_directory", os.path.expanduser("~"))
        )
        if directory:  # User selected a directory (not canceled)
            self.settings["custom_directory"] = directory
            self.directory_entry.delete(0, "end")
            self.directory_entry.insert(0, directory)
            print(f"Selected directory: {directory}")
    
    def show_help(self):
        """Display a help message about the application."""
        help_text = (
            f"CustomTkinter App Base v{self.app_version}\n\n"
            "This is a template application built with CustomTkinter.\n\n"
            "• Home Tab: Interactive demo elements\n"
            "• Data Tab: Form input and data display\n"
            "• Settings Tab: Application configuration\n\n"
            "This application serves as a starting point for your own projects."
        )
        messagebox.showinfo("Help", help_text)
    
    def update_font_size(self, value):
        """Update the font size from the slider."""
        font_size = int(value)
        self.settings["font_size"] = font_size
        self.fontsize_value_label.configure(text=f"{font_size}px")
        
        # Update the font sample to show the new size
        self.font_sample_label.configure(
            font=ctk.CTkFont(
                family=self.get_actual_font_name(self.settings.get("font_family", "Default")), 
                size=font_size
            )
        )
    
    def save_settings(self):
        """Save all settings to a JSON file."""
        # Update settings from UI
        self.settings["username"] = self.username_entry.get()
        self.settings["selected_option"] = self.option_dropdown.get()
        self.settings["custom_directory"] = self.directory_entry.get()
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def load_settings(self):
        """Load settings from a JSON file if it exists."""
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
        """Reset all settings to default values."""
        # Reset to default values
        default_settings = {
            "theme": "System",
            "feature_enabled": True,
            "username": "",
            "selected_option": "Option 1",
            "font_size": 12,
            "font_family": "Default",
            "ui_scaling": "100%",
            "auto_save": False,
            "custom_directory": os.path.expanduser("~")
        }
        
        # Update UI
        self.theme_dropdown.set(default_settings["theme"])
        self.change_theme(default_settings["theme"])
        
        self.feature_var.set(default_settings["feature_enabled"])
        self.autosave_var.set(default_settings["auto_save"])
        self.toggle_autosave()
        
        self.username_entry.delete(0, 'end')
        self.username_entry.insert(0, default_settings["username"])
        
        self.option_dropdown.set(default_settings["selected_option"])
        
        self.fontsize_slider.set(default_settings["font_size"])
        self.fontsize_value_label.configure(text=f"{default_settings['font_size']}px")
        
        self.font_dropdown.set(default_settings["font_family"])
        self.change_font(default_settings["font_family"])
        
        self.scaling_dropdown.set(default_settings["ui_scaling"])
        # Don't actually change scaling here as it might disrupt the UI
        
        self.directory_entry.delete(0, 'end')
        self.directory_entry.insert(0, default_settings["custom_directory"])
        
        # Update settings dictionary
        self.settings = default_settings.copy()
        
        messagebox.showinfo("Settings", "Settings reset to defaults.")
    
    # --- ORIGINAL FUNCTIONS ---
    def example_action(self):
        messagebox.showinfo("Action", "You clicked the button!")
    
    def apply_filter(self):
        filter_text = self.filter_entry.get()
        messagebox.showinfo("Filter Applied", f"Filter applied: {filter_text}\n\nThis is a placeholder for actual filter functionality.")

if __name__ == "__main__":
    app = App()
    app.mainloop()