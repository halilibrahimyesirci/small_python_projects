# CustomTkinter Application Base

A template desktop application built with the CustomTkinter library, providing a foundation for future feature additions.

## Features

- **Main Application Window** with customizable dimensions and styling
- **Tabbed Interface** with Home, Data, and Settings sections
- **Settings Management** with save/load functionality
- **Theme Switching** between Light and Dark modes
- **Common UI Elements** including:
  - Buttons, Labels, Entry fields
  - Switches, Sliders, Dropdown menus
  - Text display area

## Requirements

- Python 3.9 or higher
- CustomTkinter 5.2.0 or higher

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application by executing:
```
python main.py
```

## Structure

- `main.py` - The main application file that contains the entire app
- `requirements.txt` - List of required dependencies
- `settings.json` - Created automatically when settings are saved

## Customization

This template is designed to be easily customizable:

1. Add new tabs by calling `self.tabview.add("Tab Name")`
2. Create new settings by adding entries to the `self.settings` dictionary
3. Extend functionality by adding new methods to the `App` class
4. Customize the appearance by modifying the theme settings

## License

This project is open source and available for any use.