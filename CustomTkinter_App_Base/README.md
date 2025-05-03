# CustomTkinter Application Base

A professionally structured desktop application template built with the CustomTkinter library, providing a robust foundation for Python GUI development with a modern look and feel.

## Features

### Modern User Interface
- Clean, responsive design with customizable themes
- Tabbed interface for organized content layout
- Status bar with application information
- Cross-platform compatibility (Windows, macOS, Linux)

### Home Tab
- Interactive dashboard layout with multi-column organization
- Image display with proper fallback handling
- Animated progress bar demonstration
- Adjustable value slider with real-time updates
- Segmented button control panel
- Action buttons with event handling

### Data Tab
- Complete data input form with validation
- Multiple field types (text, numeric, multi-line)
- Form submission with success notification
- Real-time data display in formatted view
- Interactive listbox with sample data
- Item selection and management controls

### Settings Tab
- Scrollable settings panel for extensive configuration options
- Theme switching (System, Light, Dark)
- Font customization with live preview
- UI scaling for different display resolutions
- Multiple toggleable application behaviors
- Custom directory selection with file dialog
- Version information and help documentation
- Settings persistence with JSON storage

## Project Structure

```
CustomTkinter_App_Base/
├── high_quality.py                 # Main application entry point
├── requirements.txt       # Project dependencies
├── README.md              # Project documentation
├── assets/                # Images and resources
└── src/                   # Source code directory
    ├── config/            # Configuration files
    │   └── settings.py    # Default application settings
    ├── ui/                # User interface components
    │   ├── home_tab.py    # Home tab implementation
    │   ├── data_tab.py    # Data tab implementation
    │   └── settings_tab.py# Settings tab implementation
    └── utils/             # Utility functions
        ├── settings_utils.py  # Settings management
        └── ui_utils.py    # UI helper functions
```

## Requirements

- Python 3.9 or higher
- CustomTkinter 5.2.0 or higher
- Pillow 9.0.0 or higher (for image handling)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/CustomTkinter_App_Base.git
   ```

2. Navigate to the project directory:
   ```
   cd CustomTkinter_App_Base
   ```

3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python high_quality.py
```
Or you can look for basic start:
```
python basic_start.py
```

## Customization

This template is designed to be easily customizable for your own projects:

1. **Add new tabs**: Extend the tabview in the main App class
2. **Create new settings**: Add entries to the settings configuration
3. **Extend functionality**: Add new methods or classes as needed
4. **Customize appearance**: Modify the theme settings in src/config/settings.py
5. **Add custom components**: Create new UI elements following the established patterns

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI library for Tkinter
- [Pillow](https://python-pillow.org/) - Python Imaging Library