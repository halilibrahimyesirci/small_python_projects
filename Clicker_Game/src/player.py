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
        
        # Coin and shop related stats
        self.coins = 0
        self.coin_upgrade_level = 0
        self.coin_upgrade_max_level = 5
        self.passive_income = 0  # Coins generated per second
        self.coin_multiplier = 1  # Multiplier for coin drops
        
        # Upgradable stats - initial values intentionally reduced for V0.3.3
        self.stats = {
            "click_power": {
                "level": 0,
                "value": 1,  # Base clicks per click
                "max_level": 10
            },
            "critical_chance": {
                "level": 0,
                "value": 0.05,  # 5% chance by default (reduced from 10%)
                "max_level": 10
            },
            "critical_multiplier": {
                "level": 0,
                "value": 1.5,  # Critical clicks worth 1.5x (reduced from 2x)
                "max_level": 10
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
            "coin_upgrade_level": self.coin_upgrade_level,
            "coins": self.coins,
            "passive_income": self.passive_income,
            "coin_multiplier": self.coin_multiplier
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
            
            # Load coin and shop related stats (default values if not in save file)
            self.coin_upgrade_level = player_data.get("coin_upgrade_level", 0)
            self.coins = player_data.get("coins", 0)
            self.passive_income = player_data.get("passive_income", 0)
            self.coin_multiplier = player_data.get("coin_multiplier", 1)
            
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
        self.coins = 0
        self.passive_income = 0
        self.coin_multiplier = 1
        
        # Reset stats to initial values
        for stat in self.stats:
            self.stats[stat]["level"] = 0
        
        self.stats["click_power"]["value"] = 1
        self.stats["critical_chance"]["value"] = 0.05  # Reduced from 0.1
        self.stats["critical_multiplier"]["value"] = 1.5  # Reduced from 2
        
        logger.info("Player progress reset")
        return True
    
    def complete_level(self, win=True):
        """Handle level completion logic"""
        if win:
            self.level += 1
            self.upgrade_points += 1
            
            # Award coins for level completion
            level_coins = 5 * self.level
            self.coins += level_coins
            logger.info(f"Awarded {level_coins} coins for completing level {self.level-1}")
            
            if self.level > self.highest_level:
                self.highest_level = self.level
                # Bonus coins for reaching a new highest level
                bonus_coins = 10 * self.level
                self.coins += bonus_coins
                logger.info(f"Awarded {bonus_coins} bonus coins for reaching new highest level")
                
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
        
        # Update the value based on the stat type - V0.3.3 has more balanced progression
        if stat_name == "click_power":
            stat["value"] = 1 + (stat["level"] * 0.5)  # 1-6 clicks per click (slower progression)
        elif stat_name == "critical_chance":
            stat["value"] = 0.05 + (stat["level"] * 0.03)  # 5-35% chance (slower progression)
        elif stat_name == "critical_multiplier":
            stat["value"] = 1.5 + (stat["level"] * 0.3)  # 1.5-4.5x multiplier (slower progression)
            
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
    def can_upgrade_coins(self):
        """Check if coin drop rate can be upgraded"""
        return self.coin_upgrade_level < self.coin_upgrade_max_level and self.upgrade_points > 0
        
    def add_passive_income(self, time_delta):
        """Add passive income based on elapsed time"""
        if self.passive_income > 0:
            earned_coins = self.passive_income * time_delta
            self.coins += earned_coins
            return earned_coins
        return 0
        
    def collect_coin(self, value=1):
        """Collect a coin with the given value, applying multipliers"""
        coin_value = value * self.coin_multiplier
        self.coins += coin_value
        return coin_value