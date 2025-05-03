# Window Frame Game

A unique gaming experience that breaks the fourth wall by turning windows themselves into game elements. In this innovative game, you control a player window that must interact with target windows while avoiding obstacles in a desktop environment.

## Features

- **Innovative Gameplay**: Control a window on your desktop to catch targets, avoid obstacles, and collect powerups
- **Multiple Target Types**: Different target windows with varying behaviors and point values
- **Powerup System**: Collect special windows that grant abilities like speed boost, shield, and more
- **Difficulty Progression**: Increasing challenge with 10 difficulty levels
- **Custom Physics**: Window-based collision and movement system
- **Customizable Settings**: Adjust difficulty, sound settings, and visual preferences

## Requirements

- Python 3.7+
- Tkinter (included with standard Python installation)

## Installation

1. Clone this repository
2. Navigate to the project directory
3. No additional dependencies required - the game uses only standard Python libraries!

## How to Play

Run the game with:

```bash
python main.py
```

### Controls

- **Movement**: WASD or Arrow Keys
- **Dash**: Spacebar (quick burst of speed with short cooldown)
- **Exit**: Escape key or close the main window

### Gameplay

- Control your player window (the "Hunter") to catch target windows
- Different targets have different behaviors and point values
- Avoid obstacle windows that can freeze or block your movement
- Collect powerup windows for special abilities
- Advance through levels by reaching the target score for each level

## Game Elements

### Player
- The window you control
- Has health indicated by a bar on the window
- Can dash to move quickly (with cooldown)

### Targets
- **Standard**: Static targets worth 10 points
- **Moving**: Targets that move randomly, worth 20 points
- **Evasive**: Targets that try to avoid the player, worth 30 points
- **Boss**: Tough targets that chase the player, worth 50 points and have multiple health points

### Obstacles
- **Barrier**: Blocks player movement
- **Trap**: Freezes the player temporarily
- **Decoy**: Looks like a target but gives no points

### Powerups
- **Speed**: Temporarily increases movement speed
- **Magnet**: Attracts nearby targets
- **Shield**: Provides temporary invulnerability
- **Time**: Slows down other windows

## Configuration

Game settings can be customized in the `config/game_config.py` file, including:

- Difficulty settings
- Window sizes and colors
- Spawn rates and probabilities
- Player abilities and cooldowns
- Sound and visual options

## Project Structure

- `main.py`: Entry point for the game
- `config/`: Configuration files
- `src/`: Source code
  - `engine/`: Game engine components
  - `entities/`: Game entity classes
  - `ui/`: User interface components
  - `utils/`: Utility functions and classes

## License

This project is available under the terms of the license file included in the repository.

## Acknowledgments

- Built with Python and Tkinter
- Works on Windows, macOS, and Linux platforms

## Future Plans

- Additional game modes
- More powerup and obstacle types
- Multiplayer support
- Custom theming options