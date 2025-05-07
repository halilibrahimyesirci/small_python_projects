"""
Shop system for RPG Clicker Game
Implements purchasable items with effects
"""

import logging
import random
import json
import os

logger = logging.getLogger(__name__)

class ShopItem:
    """
    Represents a purchasable item in the shop
    Items can have various effects on the player
    """
    
    def __init__(self, name, base_cost, description, effect_type, effect_value, 
                 max_quantity=None, cost_increase=1.5):
        self.name = name
        self.base_cost = base_cost
        self.cost = base_cost  # Current cost (increases with each purchase)
        self.description = description
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.purchased_quantity = 0
        self.max_quantity = max_quantity  # None means unlimited
        self.cost_increase = cost_increase  # How much cost increases per purchase
        
    def can_purchase(self, player_coins):
        """Check if player can afford this item and hasn't reached max quantity"""
        if self.max_quantity is not None and self.purchased_quantity >= self.max_quantity:
            return False
        return player_coins >= self.cost
        
    def purchase(self):
        """Process a purchase of this item"""
        self.purchased_quantity += 1
        
        # Calculate new cost if this item can be purchased again
        if self.max_quantity is None or self.purchased_quantity < self.max_quantity:
            self.cost = self.get_next_cost()
            
        return True
        
    def get_next_cost(self):
        """Calculate the cost for the next purchase"""
        return int(self.base_cost * (self.cost_increase ** self.purchased_quantity))
        
    def apply_effect(self, player):
        """Apply this item's effect to the player"""
        if self.effect_type == "click_power":
            # Increase click power by effect_value
            player.stats["click_power"]["value"] += self.effect_value
            logger.info(f"Applied {self.effect_type} effect: +{self.effect_value}")
            
        elif self.effect_type == "crit_chance":
            # Increase critical chance by effect_value (percentage)
            player.stats["critical_chance"]["value"] += (self.effect_value / 100.0)
            logger.info(f"Applied {self.effect_type} effect: +{self.effect_value}%")
            
        elif self.effect_type == "crit_multiplier":
            # Increase critical multiplier by effect_value
            player.stats["critical_multiplier"]["value"] += self.effect_value
            logger.info(f"Applied {self.effect_type} effect: +{self.effect_value}x")
            
        elif self.effect_type == "coins":
            # Add coins to player
            player.coins += self.effect_value
            logger.info(f"Applied {self.effect_type} effect: +{self.effect_value}")
            
        elif self.effect_type == "coin_drop_rate":
            # Increase coin drop rate
            player.coin_upgrade_level += self.effect_value
            logger.info(f"Applied {self.effect_type} effect: +{self.effect_value}")
            
        elif self.effect_type == "auto_clicker":
            # Give auto-clicker ability
            player.abilities["auto_clicker"] = True
            logger.info(f"Unlocked auto-clicker ability")
            
        elif self.effect_type == "coin_magnet":
            # Give coin magnet ability
            player.abilities["coin_magnet"] = True
            logger.info(f"Unlocked coin magnet ability")
        
        else:
            logger.warning(f"Unknown effect type: {self.effect_type}")
            return False
            
        return True
        
    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            "name": self.name,
            "base_cost": self.base_cost,
            "cost": self.cost,
            "description": self.description,
            "effect_type": self.effect_type,
            "effect_value": self.effect_value,
            "purchased_quantity": self.purchased_quantity,
            "max_quantity": self.max_quantity,
            "cost_increase": self.cost_increase
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create a ShopItem from dictionary data"""
        item = cls(
            data["name"],
            data["base_cost"],
            data["description"],
            data["effect_type"],
            data["effect_value"],
            data.get("max_quantity"),
            data.get("cost_increase", 1.5)
        )
        item.cost = data["cost"]
        item.purchased_quantity = data["purchased_quantity"]
        return item

class ShopManager:
    """
    Manages the shop system
    Handles item creation, purchases, and persistence
    """
    
    def __init__(self, resource_manager=None):
        self.items = []
        self.resource_manager = resource_manager
        
        # Create default shop items
        self._create_default_items()
        
        # Load saved shop state
        self._load_shop_state()
        
    def _create_default_items(self):
        """Create the default set of shop items"""
        self.items = [
            ShopItem(
                "Click Power Boost",
                50,
                "Increases click power by 2",
                "click_power",
                2,
                max_quantity=None,
                cost_increase=1.5
            ),
            ShopItem(
                "Critical Chance Boost",
                100,
                "Increases critical hit chance by 5%",
                "crit_chance",
                5,
                max_quantity=None,
                cost_increase=1.6
            ),
            ShopItem(
                "Critical Multiplier Boost",
                150,
                "Increases critical hit multiplier by 0.5",
                "crit_multiplier",
                0.5,
                max_quantity=None,
                cost_increase=1.7
            ),
            ShopItem(
                "Auto-Clicker",
                500,
                "Automatically clicks every few seconds",
                "auto_clicker",
                1,
                max_quantity=1
            ),
            ShopItem(
                "Coin Magnet",
                300,
                "Increases the range to collect falling coins",
                "coin_magnet",
                1,
                max_quantity=1
            ),
            ShopItem(
                "Coin Boost",
                200,
                "Increases coin drop rate",
                "coin_drop_rate",
                1,
                max_quantity=10,
                cost_increase=1.3
            ),
            ShopItem(
                "Lucky Coin",
                100,
                "Instantly gives you 200 coins",
                "coins",
                200,
                max_quantity=None,
                cost_increase=1.2
            )
        ]
        
    def purchase_item(self, item_index, player):
        """
        Purchase an item for the player
        Returns True if successful, False otherwise
        """
        if item_index < 0 or item_index >= len(self.items):
            logger.error(f"Invalid item index: {item_index}")
            return False
            
        item = self.items[item_index]
        
        # Check if purchase is valid
        if not item.can_purchase(player.coins):
            return False
            
        # Deduct coins
        player.coins -= item.cost
        
        # Process the purchase
        item.purchase()
        
        # Apply the effect
        item.apply_effect(player)
        
        # Save shop state
        self._save_shop_state()
        
        return True
        
    def _save_shop_state(self):
        """Save shop state to file"""
        if not self.resource_manager:
            logger.warning("No resource manager available to save shop state")
            return
            
        shop_data = {
            "items": [item.to_dict() for item in self.items]
        }
        
        try:
            shop_path = os.path.join("data", "shop.json")
            with open(shop_path, 'w') as f:
                json.dump(shop_data, f, indent=4)
            logger.info("Shop state saved")
        except Exception as e:
            logger.error(f"Error saving shop state: {e}")
            
    def _load_shop_state(self):
        """Load shop state from file"""
        if not self.resource_manager:
            logger.warning("No resource manager available to load shop state")
            return
            
        try:
            shop_path = os.path.join("data", "shop.json")
            if os.path.exists(shop_path):
                with open(shop_path, 'r') as f:
                    shop_data = json.load(f)
                    
                # Clear existing items
                self.items = []
                
                # Create items from saved data
                for item_data in shop_data.get("items", []):
                    item = ShopItem.from_dict(item_data)
                    self.items.append(item)
                    
                logger.info("Shop state loaded")
            else:
                logger.info("No saved shop state found")
        except Exception as e:
            logger.error(f"Error loading shop state: {e}")
            self._create_default_items()  # Fallback to defaults