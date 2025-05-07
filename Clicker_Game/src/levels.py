import random
import logging
import math
import pygame
from enum import Enum

logger = logging.getLogger(__name__)

class BossAbilityType(Enum):
    """Types of boss abilities"""
    MOVE_BUTTON = "move_button"  # Button randomly moves
    TIME_WARP = "time_warp"  # Timer temporarily speeds up
    CLICK_BLOCK = "click_block"  # Some clicks are temporarily blocked
    OBSTACLE = "obstacle"  # Obstacles appear and block the button (requires clicking green circles to remove)
    PRESSURE_BAR = "pressure_bar"  # Fishing-like minigame with a pressure bar
    WINDOW_SHAKE = "window_shake"  # Screen shakes making it hard to click

class Level:
    """Base class for game levels"""
    
    def __init__(self, level_number, resource_manager=None):
        self.level_number = level_number
        self.resource_manager = resource_manager
        self.is_boss = False
        
        # Get config values or use defaults
        if resource_manager:
            self.click_target = resource_manager.get_config_value("gameplay", "initial_click_target")
            self.target_increment = resource_manager.get_config_value("gameplay", "target_increment")
            self.timer_duration = resource_manager.get_config_value("gameplay", "timer_duration")
        else:
            self.click_target = 100  # Increased from 50 for V0.3.3
            self.target_increment = 25  # Increased from 10 for V0.3.3
            self.timer_duration = 30
            
        # Calculate the target for this level (now with exponential scaling)
        self._calculate_target()
        
    def _calculate_target(self):
        """Calculate the click target for this level with exponential scaling"""
        # Base target increases exponentially with level
        level_factor = 1 + (self.level_number * 0.1)  # 10% increase per level
        self.click_target = int(self.click_target * level_factor)
        
        # For higher levels, add even more scaling
        if self.level_number > 5:
            extra_scaling = (self.level_number - 5) * self.target_increment * 0.5
            self.click_target += int(extra_scaling)
        
    def get_description(self):
        """Get the level description"""
        return f"Level {self.level_number}"
        
    def get_objective_text(self):
        """Get text describing the level objective"""
        return f"Get {self.click_target} clicks in {self.timer_duration} seconds!"
        
    def check_completion(self, clicks, time_remaining):
        """Check if the level is completed"""
        return clicks >= self.click_target


class BossLevel(Level):
    """Special boss level with additional mechanics"""
    
    def __init__(self, level_number, resource_manager=None):
        super().__init__(level_number, resource_manager)
        self.is_boss = True
        
        # Boss levels have higher targets and shorter timers
        self.click_target = int(self.click_target * 1.5)  # 50% more clicks
        self.timer_duration = max(20, self.timer_duration - 5)  # 5 seconds less, minimum 20
        
        # Boss properties
        self.boss_name = self._generate_boss_name()
        self.boss_health = self.click_target
        self.boss_max_health = self.boss_health
        self.boss_ability = self._select_boss_ability()
        self.ability_cooldown = 5.0  # seconds
        self.ability_timer = 0.0
        self.ability_active = False
        self.ability_duration = 3.0  # seconds
        
        # Special mechanics tracking
        self.obstacles = []  # For obstacle mechanic
        self.pressure_bar = {
            "position": 0.5,  # 0.0 to 1.0
            "target": 0.5,  # 0.0 to 1.0
            "success_zone_size": 0.2,  # Size of target zone (0.0 to 1.0)
            "direction": 1,  # 1 or -1
            "speed": 0.01,  # How fast bar changes per frame
            "active": False
        }
        self.shake_offset = {"x": 0, "y": 0}  # For screen shake mechanic
        
    def _generate_boss_name(self):
        """Generate a random boss name"""
        prefixes = ["Commander", "Overlord", "Captain", "Lord", "Master", "King"]
        names = ["Clickbot", "Chronos", "Fingercrusher", "Timeeater", "Speedclicker", "Buttonmasher"]
        
        tier = min(5, self.level_number // 5)
        tier_names = ["Apprentice", "Veteran", "Elite", "Champion", "Legendary"]
        
        prefix = random.choice(prefixes)
        name = random.choice(names)
        tier_prefix = tier_names[tier-1] if tier > 0 else ""
        
        if tier_prefix:
            return f"{tier_prefix} {prefix} {name}"
        return f"{prefix} {name}"
        
    def _select_boss_ability(self):
        """Select a boss ability based on the level number"""
        boss_tier = self.level_number // 5
        
        if boss_tier == 1:
            # First boss - Obstacle mechanic
            return BossAbilityType.OBSTACLE.value
        elif boss_tier == 2:
            # Second boss - Pressure bar mechanic
            return BossAbilityType.PRESSURE_BAR.value
        elif boss_tier == 3:
            # Third boss - Window shake mechanic
            return BossAbilityType.WINDOW_SHAKE.value
        else:
            # Higher tier bosses - Random advanced mechanics
            abilities = [
                BossAbilityType.OBSTACLE.value,
                BossAbilityType.PRESSURE_BAR.value,
                BossAbilityType.WINDOW_SHAKE.value
            ]
            return random.choice(abilities)
        
    def update_ability(self, elapsed_time, total_time):
        """Update the boss ability state"""
        if self.ability_active:
            # Check if ability duration is over
            if elapsed_time - self.ability_timer >= self.ability_duration:
                self.ability_active = False
                logger.info(f"Boss ability '{self.boss_ability}' ended")
                
                # Reset specific mechanics
                if self.boss_ability == BossAbilityType.OBSTACLE.value:
                    self.obstacles.clear()
                elif self.boss_ability == BossAbilityType.PRESSURE_BAR.value:
                    self.pressure_bar["active"] = False
                elif self.boss_ability == BossAbilityType.WINDOW_SHAKE.value:
                    self.shake_offset = {"x": 0, "y": 0}
        else:
            # Check if cooldown is over and we should activate ability
            if total_time - self.ability_timer >= self.ability_cooldown:
                self.ability_active = True
                self.ability_timer = total_time
                
                # Initialize specific mechanics
                if self.boss_ability == BossAbilityType.OBSTACLE.value:
                    self._spawn_obstacles()
                elif self.boss_ability == BossAbilityType.PRESSURE_BAR.value:
                    self._initialize_pressure_bar()
                elif self.boss_ability == BossAbilityType.WINDOW_SHAKE.value:
                    self.shake_offset = {"x": 0, "y": 0}
                    
                logger.info(f"Boss ability '{self.boss_ability}' activated")
                return True  # Ability just activated
                
        return False  # No new activation
    
    def _spawn_obstacles(self):
        """Create obstacles for the obstacle mechanic"""
        # Create 1-3 green circles that player must click to clear
        num_obstacles = random.randint(1, 3)
        self.obstacles = []
        
        for _ in range(num_obstacles):
            self.obstacles.append({
                "x": random.randint(100, 700),
                "y": random.randint(100, 500),
                "radius": 20,
                "clicked": False
            })
            
    def _initialize_pressure_bar(self):
        """Initialize the pressure bar mechanic"""
        self.pressure_bar["position"] = 0.5
        self.pressure_bar["target"] = random.uniform(0.3, 0.7)
        self.pressure_bar["success_zone_size"] = 0.15  # Shrinks with level
        self.pressure_bar["direction"] = 1 if random.random() > 0.5 else -1
        self.pressure_bar["speed"] = 0.005 + (self.level_number * 0.001)  # Gets faster with level
        self.pressure_bar["active"] = True
        
    def update_pressure_bar(self):
        """Update the pressure bar position"""
        if self.pressure_bar["active"]:
            # Update position
            self.pressure_bar["position"] += self.pressure_bar["direction"] * self.pressure_bar["speed"]
            
            # Bounce at edges
            if self.pressure_bar["position"] <= 0:
                self.pressure_bar["position"] = 0
                self.pressure_bar["direction"] = 1
            elif self.pressure_bar["position"] >= 1:
                self.pressure_bar["position"] = 1
                self.pressure_bar["direction"] = -1
                
            # Check if in success zone
            lower_bound = self.pressure_bar["target"] - self.pressure_bar["success_zone_size"] / 2
            upper_bound = self.pressure_bar["target"] + self.pressure_bar["success_zone_size"] / 2
            
            return lower_bound <= self.pressure_bar["position"] <= upper_bound
            
        return False
        
    def update_shake(self):
        """Update the screen shake effect"""
        if self.ability_active and self.boss_ability == BossAbilityType.WINDOW_SHAKE.value:
            # Generate random shake offset
            shake_intensity = 5 + (self.level_number // 5)
            self.shake_offset = {
                "x": random.randint(-shake_intensity, shake_intensity),
                "y": random.randint(-shake_intensity, shake_intensity)
            }
            return self.shake_offset
        else:
            self.shake_offset = {"x": 0, "y": 0}
            return self.shake_offset
        
    def check_obstacle_click(self, mouse_pos):
        """Check if player clicked on an obstacle and remove it if so"""
        for obstacle in self.obstacles[:]:
            distance = math.sqrt((mouse_pos[0] - obstacle["x"])**2 + (mouse_pos[1] - obstacle["y"])**2)
            if distance <= obstacle["radius"]:
                self.obstacles.remove(obstacle)
                logger.info("Obstacle removed")
                return True
        return False
        
    def damage_boss(self, damage):
        """Apply damage to the boss"""
        self.boss_health = max(0, self.boss_health - damage)
        return self.boss_health <= 0  # Return True if boss is defeated
        
    def get_health_percent(self):
        """Get the boss health as a percentage"""
        return self.boss_health / self.boss_max_health
        
    def get_description(self):
        """Get the boss level description"""
        return f"BOSS: {self.boss_name} - Level {self.level_number}"
        
    def get_objective_text(self):
        """Get text describing the boss level objective"""
        return f"Defeat {self.boss_name} with {self.click_target} clicks in {self.timer_duration} seconds!"


class LevelManager:
    """Manages level creation and progression"""
    
    def __init__(self, resource_manager=None):
        self.resource_manager = resource_manager
        self.current_level = None
        
    def create_level(self, level_number):
        """Create a new level based on the level number"""
        # Check if this is a boss level
        is_boss = False
        
        if self.resource_manager:
            boss_levels = self.resource_manager.get_config_value("boss_levels")
            is_boss = level_number in boss_levels
        else:
            is_boss = level_number % 5 == 0 and level_number > 0
            
        if is_boss:
            self.current_level = BossLevel(level_number, self.resource_manager)
            logger.info(f"Created boss level: {self.current_level.get_description()}")
        else:
            self.current_level = Level(level_number, self.resource_manager)
            logger.info(f"Created level: {self.current_level.get_description()}")
            
        return self.current_level
        
    def get_current_level(self):
        """Get the current level"""
        return self.current_level