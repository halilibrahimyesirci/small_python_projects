import json
import os
import logging

logger = logging.getLogger(__name__)

class Player:
    """Manages player data, stats, and progression"""
    
    def __init__(self, resource_manager=None):
        self.resource_manager = resource_manager
        
        # Core stats
        self.level = 1
        self.highest_level = 1
        self.upgrade_points = 0
        self.total_clicks = 0
        
        # Coin upgrade stats
        self.coin_upgrade_level = 0
        self.coin_upgrade_max_level = 5
        
        # Upgradable stats
        self.stats = {
            "click_power": {
                "level": 0,
                "value": 1,  # Base clicks per click
                "max_level": 5
            },
            "critical_chance": {
                "level": 0,
                "value": 0.1,  # 10% chance by default
                "max_level": 5
            },
            "critical_multiplier": {
                "level": 0,
                "value": 2,  # Critical clicks worth 2x
                "max_level": 5
            }
        }
        
        # Load saved data if exists
        self.load_progress()
    
    def save_progress(self):
        """Save player progress to a file"""
        player_data = {
            "level": self.level,
            "highest_level": self.highest_level,
            "upgrade_points": self.upgrade_points,
            "total_clicks": self.total_clicks,
            "stats": self.stats,
            "coin_upgrade_level": self.coin_upgrade_level
        }
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        try:
            with open(os.path.join("data", "save_data.json"), 'w') as f:
                json.dump(player_data, f, indent=4)
            logger.info("Player progress saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving player progress: {e}")
            return False
    
    def load_progress(self):
        """Load player progress from a file"""
        save_path = os.path.join("data", "save_data.json")
        
        if not os.path.exists(save_path):
            logger.info("No save data found, using default values")
            return False
        
        try:
            with open(save_path, 'r') as f:
                player_data = json.load(f)
                
            self.level = player_data["level"]
            self.highest_level = player_data["highest_level"]
            self.upgrade_points = player_data["upgrade_points"]
            self.total_clicks = player_data["total_clicks"]
            self.stats = player_data["stats"]
            
            # Load coin upgrade level (default to 0 if not in save file)
            self.coin_upgrade_level = player_data.get("coin_upgrade_level", 0)
            
            logger.info("Player progress loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading player progress: {e}")
            return False
    
    def reset_progress(self):
        """Reset player progress"""
        self.level = 1
        self.highest_level = 1
        self.upgrade_points = 0
        self.total_clicks = 0
        self.coin_upgrade_level = 0
        
        # Reset stats to initial values
        for stat in self.stats:
            self.stats[stat]["level"] = 0
        
        self.stats["click_power"]["value"] = 1
        self.stats["critical_chance"]["value"] = 0.1
        self.stats["critical_multiplier"]["value"] = 2
        
        logger.info("Player progress reset")
        return True
    
    def complete_level(self, win=True):
        """Handle level completion logic"""
        if win:
            self.level += 1
            self.upgrade_points += 1
            
            if self.level > self.highest_level:
                self.highest_level = self.level
                
            logger.info(f"Level {self.level - 1} completed. New level: {self.level}")
            return True
        else:
            # Failed level - reset to level 1 but keep upgrades
            logger.info(f"Failed level {self.level}. Resetting to level 1.")
            self.level = 1
            return False
    
    def can_upgrade(self, stat_name):
        """Check if a stat can be upgraded"""
        if stat_name not in self.stats:
            return False
            
        stat = self.stats[stat_name]
        if stat["level"] >= stat["max_level"]:
            return False
            
        return self.upgrade_points > 0
    
    def upgrade_stat(self, stat_name):
        """Upgrade a player stat"""
        if not self.can_upgrade(stat_name):
            return False
            
        # Get the upgrade values from config
        stat = self.stats[stat_name]
        
        # Apply upgrade
        stat["level"] += 1
        self.upgrade_points -= 1
        
        # Update the value based on the stat type
        if stat_name == "click_power":
            stat["value"] = 1 + stat["level"]  # 1-6 clicks per click
        elif stat_name == "critical_chance":
            stat["value"] = 0.1 + (stat["level"] * 0.05)  # 10-35% chance
        elif stat_name == "critical_multiplier":
            stat["value"] = 2 + stat["level"]  # 2-7x multiplier
            
        logger.info(f"Upgraded {stat_name} to level {stat['level']}")
        return True
    
    def upgrade_coin_rate(self):
        """Upgrade coin drop rate and value"""
        if self.coin_upgrade_level >= self.coin_upgrade_max_level or self.upgrade_points <= 0:
            return False
            
        self.coin_upgrade_level += 1
        self.upgrade_points -= 1
        
        logger.info(f"Upgraded coin drop rate to level {self.coin_upgrade_level}")
        return True
    
    def is_boss_level(self):
        """Check if current level is a boss level"""
        if not self.resource_manager:
            # Default boss levels if no resource manager
            return self.level % 5 == 0
            
        boss_levels = self.resource_manager.get_config_value("boss_levels")
        return self.level in boss_levels