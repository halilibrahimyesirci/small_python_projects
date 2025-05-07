"""
Engine utilities package.
Provides modules for UI management, audio, transitions, and debugging.
"""

# Import all modules for easy access
from .ui_manager import UIManager, UIElement
from .audio import AudioManager
from .transitions import TransitionManager, TRANSITION_FADE, TRANSITION_SLIDE_LEFT, TRANSITION_SLIDE_RIGHT, TRANSITION_ZOOM
from .debug import DebugManager

# Version information
__version__ = "0.1.0"