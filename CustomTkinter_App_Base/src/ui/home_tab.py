import os
import customtkinter as ctk
from PIL import Image
from tkinter import Listbox, StringVar

from src.utils.ui_utils import UIUtils


class HomeTab:
    def __init__(self, parent):
        self.parent = parent
        self.tab = parent
        self.progress_running = False
        self.current_slider_value = 50
        
        # Configure grid layout
        self.tab.grid_columnconfigure(0, weight=1)
        self.tab.grid_columnconfigure(1, weight=1)
        self.tab.grid_columnconfigure(2, weight=1)
        
        self._create_title_section()
        self._create_description_section()
        self._create_image_section()
        self._create_progress_section()
        self._create_slider_section()
        self._create_control_section()
    
    def _create_title_section(self):
        title_label = ctk.CTkLabel(
            self.tab, 
            text="Welcome to CustomTkinter App Base",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1E3A8A", "#3B82F6")
        )
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="ew")
    
    def _create_description_section(self):
        description_frame = ctk.CTkFrame(self.tab)
        description_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="ew")
        
        description_text = (
            "This is a comprehensive template application built with CustomTkinter, "
            "showcasing various UI components and functionalities. It provides a solid "
            "foundation for developing desktop applications with a modern look and feel."
        )
        
        description_textbox = ctk.CTkTextbox(description_frame, height=80, wrap="word")
        description_textbox.pack(padx=10, pady=10, fill="both", expand=True)
        description_textbox.insert("1.0", description_text)
        description_textbox.configure(state="disabled")
    
    def _create_image_section(self):
        image_frame = ctk.CTkFrame(self.tab)
        image_frame.grid(row=2, column=0, rowspan=3, padx=(20, 10), pady=10, sticky="nsew")
        
        try:
            image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                     "assets", "placeholder.png")
            
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
            image_label = ctk.CTkLabel(
                image_frame,
                text=f"Image Placeholder",
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
    
    def _create_progress_section(self):
        progress_frame = ctk.CTkFrame(self.tab)
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
        self.progress_bar.set(0)
        
        self.progress_value_label = ctk.CTkLabel(progress_frame, text="0%")
        self.progress_value_label.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")
        
        progress_button = ctk.CTkButton(
            progress_frame,
            text="Start Progress",
            command=self.start_progress_animation
        )
        progress_button.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
    
    def _create_slider_section(self):
        slider_frame = ctk.CTkFrame(self.tab)
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
        self.value_slider.set(50)
        
        self.slider_value_label = ctk.CTkLabel(slider_frame, text="Value: 50")
        self.slider_value_label.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")
    
    def _create_control_section(self):
        control_frame = ctk.CTkFrame(self.tab)
        control_frame.grid(row=2, column=2, rowspan=2, padx=(10, 20), pady=10, sticky="nsew")
        
        segment_label = ctk.CTkLabel(
            control_frame,
            text="Control Panel",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        segment_label.pack(padx=10, pady=(10, 10))
        
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
    
    def start_progress_animation(self):
        if not self.progress_running:
            self.progress_running = True
            UIUtils.run_progress_animation(
                self.progress_bar, 
                self.progress_value_label, 
                self
            )
    
    def update_slider_value(self, value):
        self.current_slider_value = int(value)
        self.slider_value_label.configure(text=f"Value: {self.current_slider_value}")
    
    def segmented_callback(self, value):
        self.segment_result_label.configure(text=f"Selected: {value}")
    
    def perform_action(self, action_number):
        UIUtils.show_message("Action", f"Action {action_number} performed!")