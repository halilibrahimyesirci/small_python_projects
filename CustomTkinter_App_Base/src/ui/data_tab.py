import customtkinter as ctk
from tkinter import Listbox

from src.utils.ui_utils import UIUtils


class DataTab:
    def __init__(self, parent):
        self.parent = parent
        self.tab = parent
        
        # Configure grid layout
        self.tab.grid_columnconfigure(0, weight=1)
        self.tab.grid_columnconfigure(1, weight=1)
        
        self._create_input_form()
        self._create_data_display()
    
    def _create_input_form(self):
        input_frame = ctk.CTkFrame(self.tab)
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
    
    def _create_data_display(self):
        display_frame = ctk.CTkFrame(self.tab)
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
    
    def submit_data(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        age = self.age_entry.get()
        description = self.desc_textbox.get("1.0", "end-1c")
        
        # Simple validation
        if not name or not email:
            UIUtils.show_warning("Incomplete Data", "Name and email are required fields.")
            return
        
        # Display the submitted data
        display_text = f"Name: {name}\nEmail: {email}\n"
        if age:
            display_text += f"Age: {age}\n"
        if description and description != "Enter additional information here...":
            display_text += f"Description: {description}"
        
        self.data_display_label.configure(text=display_text)
        UIUtils.show_message("Success", "Data submitted successfully!")
        
        # Clear the form for new entry
        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.age_entry.delete(0, "end")
        self.desc_textbox.delete("1.0", "end")
        self.desc_textbox.insert("1.0", "Enter additional information here...")
    
    def select_next_item(self):
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
        self.items_listbox.selection_clear(0, "end")