# CustomTkinter Application Base

A comprehensive desktop application template built with the CustomTkinter library, providing a robust foundation for future feature additions with a modern UI.

## Features

### Main Application Window
- Customizable window with responsive design
- Modern UI with themed widgets
- Tabbed interface for organized content layout

### Home Tab
- Stylized welcome section with application introduction
- Image display area with placeholder handling
- Interactive progress bar with animation
- Value slider with dynamic updating
- Segmented button for option selection
- Action buttons for demonstrating functions

### Data Tab
- Complete data input form with multiple field types
- Multi-line text input with placeholder text
- Form submission with data validation
- Real-time data display and feedback
- Interactive listbox with sample data
- Item selection and manipulation controls

### Settings Tab
- Theme switching between System, Light, and Dark modes
- Font family selection with live preview
- Font size adjustment via slider
- UI scaling controls
- Application behavior toggles (Auto-Save feature)
- Custom directory selection with file dialog
- Version information and help section
- Settings persistence across application restarts

## Requirements

- Python 3.9 or higher
- CustomTkinter 5.2.0 or higher
- Pillow (PIL) for image handling

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the standard version of the application:
```
python main.py
```

Run the enhanced version with more features:
```
python enhanced_app.py
```

## Structure

- `main.py` - The basic application implementation
- `enhanced_app.py` - The comprehensive application with extended features
- `requirements.txt` - List of required dependencies
- `settings.json` - Created automatically when settings are saved
- `resources/` - Directory for application images and assets

## Customization

This template is designed to be easily customizable:

1. Add new tabs by calling `self.tabview.add("Tab Name")`
2. Create new settings by adding entries to the `self.settings` dictionary
3. Extend functionality by adding new methods to the `App` class
4. Customize the appearance by modifying the theme settings
5. Add your own widgets and layouts using the provided patterns

## License

This project is open source and available for any use.