"""
Market system for RPG Clicker Game
Manages items, shop interface and purchases
"""

import pygame
import logging

logger = logging.getLogger(__name__)

class ShopItem:
    """Represents a purchasable item in the shop"""
    
    def __init__(self, name, description, cost, effect_type, effect_value, icon=None, max_quantity=None):
        self.name = name
        self.description = description
        self.cost = cost
        self.effect_type = effect_type  # 'click_power', 'critical_chance', 'critical_multiplier', 'passive_income', etc.
        self.effect_value = effect_value  # Value to add/multiply when applied
        self.icon = icon
        self.max_quantity = max_quantity
        self.purchased_quantity = 0
        
    def can_purchase(self, coins):
        """Check if player can purchase the item"""
        if self.max_quantity is not None and self.purchased_quantity >= self.max_quantity:
            return False
        return coins >= self.cost
        
    def purchase(self, player):
        """Apply the item effect to the player"""
        if not self.can_purchase(player.coins):
            return False
            
        player.coins -= self.cost
        self.purchased_quantity += 1
        
        # Apply effect based on type
        if self.effect_type == "click_power":
            player.stats["click_power"]["value"] += self.effect_value
        elif self.effect_type == "critical_chance":
            player.stats["critical_chance"]["value"] += self.effect_value
        elif self.effect_type == "critical_multiplier":
            player.stats["critical_multiplier"]["value"] += self.effect_value
        elif self.effect_type == "passive_income":
            player.passive_income += self.effect_value
        # Add more effect types as needed
        
        logger.info(f"Player purchased {self.name} for {self.cost} coins")
        return True
        
    def get_next_cost(self):
        """Get the cost for the next purchase (for items with scaling costs)"""
        # For items that get more expensive with each purchase
        return int(self.cost * (1.2 ** self.purchased_quantity))

class ShopManager:
    """Manages the shop and purchasable items"""
    
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.items = []
        self._initialize_shop_items()
        
    def _initialize_shop_items(self):
        """Set up default shop items"""
        # Basic click upgrades
        self.items.append(ShopItem(
            "Pointer Upgrade",
            "Increases click power by 1",
            cost=10,
            effect_type="click_power",
            effect_value=1
        ))
        
        self.items.append(ShopItem(
            "Critical Eye",
            "Increases critical chance by 5%",
            cost=25,
            effect_type="critical_chance",
            effect_value=0.05,
            max_quantity=10
        ))
        
        self.items.append(ShopItem(
            "Critical Force",
            "Increases critical multiplier by 0.5",
            cost=40,
            effect_type="critical_multiplier",
            effect_value=0.5,
            max_quantity=10
        ))
        
        # Passive income
        self.items.append(ShopItem(
            "Auto-Clicker",
            "Generates 1 click per second automatically",
            cost=100,
            effect_type="passive_income",
            effect_value=1,
            max_quantity=5
        ))
        
        # Special items with unique effects
        self.items.append(ShopItem(
            "Lucky Charm",
            "Doubles coin drops",
            cost=500,
            effect_type="coin_multiplier",
            effect_value=2,
            max_quantity=1
        ))
        
    def get_available_items(self, player_coins):
        """Get items that the player can afford"""
        return [item for item in self.items if item.can_purchase(player_coins)]
    
    def purchase_item(self, item_index, player):
        """Purchase an item for the player"""
        if 0 <= item_index < len(self.items):
            return self.items[item_index].purchase(player)
        return False