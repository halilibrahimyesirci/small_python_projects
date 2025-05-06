import random
import logging

logger = logging.getLogger(__name__)

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
            self.click_target = 50
            self.target_increment = 10
            self.timer_duration = 30
            
        # Calculate the target for this level
        self._calculate_target()
        
    def _calculate_target(self):
        """Calculate the click target for this level"""
        self.click_target += (self.level_number - 1) * self.target_increment
        
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
        
    def _generate_boss_name(self):
        """Generate a random boss name"""
        prefixes = ["Commander", "Overlord", "Captain", "Lord", "Master", "King"]
        names = ["Clickbot", "Chronos", "Fingercrusher", "Timeeater", "Speedclicker", "Buttonmasher"]
        
        prefix = random.choice(prefixes)
        name = random.choice(names)
        
        return f"{prefix} {name}"
        
    def _select_boss_ability(self):
        """Select a boss ability based on the level number"""
        # For now, just return one of three basic abilities
        abilities = [
            "move_button",   # Button randomly moves
            "time_warp",     # Timer temporarily speeds up
            "click_block"    # Some clicks are temporarily blocked
        ]
        
        index = (self.level_number // 5 - 1) % len(abilities)
        return abilities[index]
        
    def update_ability(self, elapsed_time, total_time):
        """Update the boss ability state"""
        if self.ability_active:
            # Check if ability duration is over
            if elapsed_time - self.ability_timer >= self.ability_duration:
                self.ability_active = False
                logger.info(f"Boss ability '{self.boss_ability}' ended")
        else:
            # Check if cooldown is over and we should activate ability
            if total_time - self.ability_timer >= self.ability_cooldown:
                self.ability_active = True
                self.ability_timer = total_time
                logger.info(f"Boss ability '{self.boss_ability}' activated")
                return True  # Ability just activated
                
        return False  # No new activation
        
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