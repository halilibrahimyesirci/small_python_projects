"""
Project: Advanced Water Simulation
Description: Shared constants for the water simulation
"""

# Display settings
WIDTH = 1024
HEIGHT = 768
FPS = 60
TITLE = "Advanced Water Simulation"

# Colors
BG_COLOR = (0, 10, 20)  # Dark blue background
UI_COLOR = (220, 220, 220)  # Light gray for UI
UI_BG_COLOR = (40, 40, 45, 180)  # Semi-transparent dark gray
BUTTON_COLOR = (60, 60, 80)
BUTTON_HOVER_COLOR = (80, 80, 100)
BUTTON_TEXT_COLOR = (240, 240, 240)
WATER_COLOR = (10, 150, 255)  # Base water color
WATER_COLOR_VARIATION = 30  # Random variation in color
OBJECT_COLOR = (155, 85, 25)  # Brown for objects
GLASS_COLOR = (200, 230, 255, 100)  # Translucent blue for glass objects

# Simulation types
SIM_PARTICLE = "particle"
SIM_SPH = "sph"  # Smoothed Particle Hydrodynamics
SIM_GRID = "grid"
SIM_TYPES = [SIM_PARTICLE, SIM_SPH, SIM_GRID]

# Simulation constants - Particle
GRAVITY = 9.81 * 0.25  # Scaled gravity
WATER_DENSITY = 0.5
VISCOSITY = 0.1
PARTICLE_RADIUS = 4.0
PARTICLE_MASS = 1.0

# SPH constants
SMOOTHING_LENGTH = PARTICLE_RADIUS * 4.0
SMOOTHING_LENGTH_SQ = SMOOTHING_LENGTH * SMOOTHING_LENGTH
GAS_CONSTANT = 2000.0
REST_DENSITY = 1000.0
MASS = 65.0
VISCOSITY_STRENGTH = 0.08
SURFACE_TENSION = 0.0728

# Maximum particles to spawn at once
MAX_PARTICLES_PER_CLICK = 10

# Grid constants
CELL_SIZE = 4
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
EMPTY = 0
WATER = 1
SOLID = 2
AIR_PRESSURE = 0.1
FLOW_SPEED = 4

# UI constants
FONT_SIZE_LARGE = 36
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 18

# Game states
STATE_MENU = "menu"
STATE_SIMULATION = "simulation"
STATE_PAUSED = "paused"
STATE_SETTINGS = "settings"

# Object types
OBJ_RECT = "rectangle"
OBJ_CIRCLE = "circle"
OBJ_POLYGON = "polygon"
OBJ_GLASS = "glass"  # Special translucent object

# Object interaction settings
RESTITUTION = 0.4  # Bounciness factor
FRICTION = 0.9  # Friction with objects

# Predefined scene options
SCENE_EMPTY = "empty"
SCENE_BUCKET = "bucket"
SCENE_POOL = "pool"
SCENE_WATERFALL = "waterfall"
SCENE_MAZE = "maze"
SCENE_FOUNTAIN = "fountain"
SCENES = [SCENE_EMPTY, SCENE_BUCKET, SCENE_POOL, SCENE_WATERFALL, SCENE_MAZE, SCENE_FOUNTAIN]