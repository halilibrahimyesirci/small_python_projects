"""
Project: Advanced Water Simulation
Description: Objects for water interaction (bucket, bottle, etc.)
"""

import pygame
import math
from constants import *
from physics import Vector2D

class SimObject:
    """Base class for all simulation objects"""
    def __init__(self, object_type=OBJ_RECT):
        self.object_type = object_type
        self.is_movable = False
        self.color = OBJECT_COLOR
        
    def contains_point(self, x, y):
        """Check if the object contains the given point. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement contains_point")
        
    def get_collision_normal(self, x, y):
        """Get the collision normal vector at the given point. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement get_collision_normal")
        
    def draw(self, surface):
        """Draw the object. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement draw")


class RectObject(SimObject):
    """Rectangular object"""
    def __init__(self, x, y, width, height, color=None, is_glass=False):
        super().__init__(OBJ_GLASS if is_glass else OBJ_RECT)
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color if color else (GLASS_COLOR if is_glass else OBJECT_COLOR)
        self.is_glass = is_glass
        
    def contains_point(self, x, y):
        """Check if the rectangle contains the given point"""
        return self.rect.collidepoint(x, y)
        
    def get_collision_normal(self, x, y):
        """Get the collision normal vector at the given point"""
        # Calculate which side of the rectangle is closest to the point
        left_dist = abs(x - self.rect.left)
        right_dist = abs(x - self.rect.right)
        top_dist = abs(y - self.rect.top)
        bottom_dist = abs(y - self.rect.bottom)
        
        min_dist = min(left_dist, right_dist, top_dist, bottom_dist)
        
        if min_dist == left_dist:
            return Vector2D(-1, 0)
        elif min_dist == right_dist:
            return Vector2D(1, 0)
        elif min_dist == top_dist:
            return Vector2D(0, -1)
        else:  # bottom_dist
            return Vector2D(0, 1)
            
    def draw(self, surface):
        """Draw the rectangle"""
        if self.is_glass:
            # For glass, draw a semi-transparent rectangle with a border
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            s.fill(self.color)
            surface.blit(s, (self.rect.x, self.rect.y))
            pygame.draw.rect(surface, (255, 255, 255, 120), self.rect, 1)
        else:
            # For solid objects, draw a fully opaque rectangle
            pygame.draw.rect(surface, self.color, self.rect)


class CircleObject(SimObject):
    """Circular object"""
    def __init__(self, center_x, center_y, radius, color=None, is_glass=False):
        super().__init__(OBJ_GLASS if is_glass else OBJ_CIRCLE)
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color if color else (GLASS_COLOR if is_glass else OBJECT_COLOR)
        self.is_glass = is_glass
        
    def contains_point(self, x, y):
        """Check if the circle contains the given point"""
        dx = x - self.center_x
        dy = y - self.center_y
        return dx*dx + dy*dy <= self.radius*self.radius
        
    def get_collision_normal(self, x, y):
        """Get the collision normal vector at the given point"""
        dx = x - self.center_x
        dy = y - self.center_y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length < 0.0001:  # Avoid division by zero
            return Vector2D(0, -1)  # Default to upward normal
            
        return Vector2D(dx/length, dy/length)
        
    def draw(self, surface):
        """Draw the circle"""
        if self.is_glass:
            # For glass, draw a semi-transparent circle with a border
            circle_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, self.color, (self.radius, self.radius), self.radius)
            surface.blit(circle_surface, (self.center_x - self.radius, self.center_y - self.radius))
            pygame.draw.circle(surface, (255, 255, 255, 120), (int(self.center_x), int(self.center_y)), int(self.radius), 1)
        else:
            # For solid objects, draw a fully opaque circle
            pygame.draw.circle(surface, self.color, (int(self.center_x), int(self.center_y)), int(self.radius))


class PolygonObject(SimObject):
    """Polygon object"""
    def __init__(self, points, color=None, is_glass=False):
        super().__init__(OBJ_GLASS if is_glass else OBJ_POLYGON)
        self.points = points
        self.color = color if color else (GLASS_COLOR if is_glass else OBJECT_COLOR)
        self.is_glass = is_glass
        
        # Calculate bounding box for optimization
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        self.bounds = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        
    def contains_point(self, x, y):
        """Check if the polygon contains the given point using ray casting algorithm"""
        # Quick check using bounding box
        if not self.bounds.collidepoint(x, y):
            return False
            
        # Ray casting algorithm
        inside = False
        j = len(self.points) - 1
        
        for i in range(len(self.points)):
            pi = self.points[i]
            pj = self.points[j]
            
            if ((pi[1] > y) != (pj[1] > y)) and (x < (pj[0] - pi[0]) * (y - pi[1]) / (pj[1] - pi[1]) + pi[0]):
                inside = not inside
                
            j = i
            
        return inside
        
    def get_collision_normal(self, x, y):
        """Get approximate collision normal vector at the given point"""
        # This is a simplification - for a proper polygon, we should find the closest edge
        # For now, we'll use a simple approximation based on the center of the polygon
        center_x = self.bounds.centerx
        center_y = self.bounds.centery
        
        dx = x - center_x
        dy = y - center_y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length < 0.0001:  # Avoid division by zero
            return Vector2D(0, -1)  # Default to upward normal
            
        return Vector2D(dx/length, dy/length)
        
    def draw(self, surface):
        """Draw the polygon"""
        if self.is_glass:
            # For glass, draw a semi-transparent polygon with a border
            polygon_surface = pygame.Surface((self.bounds.width, self.bounds.height), pygame.SRCALPHA)
            
            # Adjust points to local coordinate system
            local_points = [(p[0] - self.bounds.x, p[1] - self.bounds.y) for p in self.points]
            
            pygame.draw.polygon(polygon_surface, self.color, local_points)
            surface.blit(polygon_surface, (self.bounds.x, self.bounds.y))
            pygame.draw.polygon(surface, (255, 255, 255, 120), self.points, 1)
        else:
            # For solid objects, draw a fully opaque polygon
            pygame.draw.polygon(surface, self.color, self.points)


# --- Scene Factory Functions ---

def create_empty_scene():
    """Create an empty scene with only boundaries"""
    objects = []
    
    # Add boundary walls just outside the visible area
    wall_thickness = 20
    
    # Top, bottom, left, right walls
    objects.append(RectObject(-wall_thickness, -wall_thickness, WIDTH + wall_thickness*2, wall_thickness))  # Top
    objects.append(RectObject(-wall_thickness, HEIGHT, WIDTH + wall_thickness*2, wall_thickness))  # Bottom
    objects.append(RectObject(-wall_thickness, 0, wall_thickness, HEIGHT))  # Left
    objects.append(RectObject(WIDTH, 0, wall_thickness, HEIGHT))  # Right
    
    return objects

def create_bucket_scene():
    """Create a scene with buckets and containers"""
    objects = create_empty_scene()
    
    # Add a big bucket in the center bottom
    bucket_width = 200
    bucket_height = 150
    wall_thickness = 12
    bucket_x = WIDTH//2 - bucket_width//2
    bucket_y = HEIGHT - bucket_height - 20
    
    # Bucket walls
    objects.append(RectObject(bucket_x, bucket_y, wall_thickness, bucket_height))  # Left wall
    objects.append(RectObject(bucket_x + bucket_width - wall_thickness, bucket_y, wall_thickness, bucket_height))  # Right wall
    objects.append(RectObject(bucket_x, bucket_y + bucket_height - wall_thickness, bucket_width, wall_thickness))  # Bottom
    
    # Add a small glass container on the left
    glass_x = 100
    glass_y = HEIGHT - 120
    glass_width = 100
    glass_height = 80
    glass_thickness = 6
    
    objects.append(RectObject(glass_x, glass_y, glass_thickness, glass_height, is_glass=True))  # Left wall
    objects.append(RectObject(glass_x + glass_width - glass_thickness, glass_y, glass_thickness, glass_height, is_glass=True))  # Right wall
    objects.append(RectObject(glass_x, glass_y + glass_height - glass_thickness, glass_width, glass_thickness, is_glass=True))  # Bottom
    
    # Add a bottle shape on the right
    bottle_x = WIDTH - 200
    bottle_y = HEIGHT - 200
    bottle_width = 80
    neck_width = 30
    bottle_height = 160
    
    # Bottle body
    objects.append(RectObject(bottle_x, bottle_y, wall_thickness, bottle_height))  # Left wall
    objects.append(RectObject(bottle_x + bottle_width - wall_thickness, bottle_y, wall_thickness, bottle_height))  # Right wall
    objects.append(RectObject(bottle_x, bottle_y + bottle_height - wall_thickness, bottle_width, wall_thickness))  # Bottom
    
    # Bottle neck
    neck_x = bottle_x + (bottle_width - neck_width) // 2
    objects.append(RectObject(neck_x, bottle_y - 60, wall_thickness, 60))  # Left neck
    objects.append(RectObject(neck_x + neck_width - wall_thickness, bottle_y - 60, wall_thickness, 60))  # Right neck
    
    return objects

def create_pool_scene():
    """Create a scene with a pool/tank setup"""
    objects = create_empty_scene()
    
    # Main pool
    pool_width = WIDTH - 200
    pool_height = HEIGHT // 2
    wall_thickness = 15
    pool_x = 100
    pool_y = HEIGHT - pool_height - 50
    
    # Pool walls
    objects.append(RectObject(pool_x, pool_y, wall_thickness, pool_height))  # Left wall
    objects.append(RectObject(pool_x + pool_width - wall_thickness, pool_y, wall_thickness, pool_height))  # Right wall
    objects.append(RectObject(pool_x, pool_y + pool_height - wall_thickness, pool_width, wall_thickness))  # Bottom
    
    # Add some obstacles inside the pool
    # Center pillar
    pillar_width = 30
    pillar_x = WIDTH // 2 - pillar_width // 2
    objects.append(RectObject(pillar_x, pool_y, pillar_width, pool_height - wall_thickness))
    
    # Submerged platform
    platform_width = 150
    platform_height = 20
    platform_x = pool_x + 100
    platform_y = pool_y + pool_height - wall_thickness - 80
    objects.append(RectObject(platform_x, platform_y, platform_width, platform_height))
    
    # Floating object
    float_radius = 40
    float_x = pool_x + pool_width - 100
    float_y = pool_y + 100
    objects.append(CircleObject(float_x, float_y, float_radius))
    
    return objects

def create_waterfall_scene():
    """Create a scene with platforms to form a waterfall"""
    objects = create_empty_scene()
    
    # Series of platforms for water to cascade down
    platform_width = 300
    platform_height = 20
    gap = 150  # Gap between platforms
    
    # First platform (top)
    platform_y = 150
    platform_x = 50
    objects.append(RectObject(platform_x, platform_y, platform_width, platform_height))
    
    # Second platform (middle)
    platform_y += 150
    platform_x += gap
    objects.append(RectObject(platform_x, platform_y, platform_width, platform_height))
    
    # Third platform (bottom)
    platform_y += 150
    platform_x += gap
    objects.append(RectObject(platform_x, platform_y, platform_width, platform_height))
    
    # Collection pool at bottom
    pool_width = WIDTH - 200
    pool_height = 120
    wall_thickness = 15
    pool_x = 100
    pool_y = HEIGHT - pool_height - 20
    
    # Pool walls
    objects.append(RectObject(pool_x, pool_y, wall_thickness, pool_height))  # Left wall
    objects.append(RectObject(pool_x + pool_width - wall_thickness, pool_y, wall_thickness, pool_height))  # Right wall
    objects.append(RectObject(pool_x, pool_y + pool_height - wall_thickness, pool_width, wall_thickness))  # Bottom
    
    return objects

def create_maze_scene():
    """Create a maze-like scene for water to navigate"""
    objects = create_empty_scene()
    
    wall_thickness = 15
    maze_y_start = 100
    
    # Horizontal walls
    h_walls = [
        (50, maze_y_start, 350, wall_thickness),
        (500, maze_y_start, 350, wall_thickness),
        (200, maze_y_start + 150, 300, wall_thickness),
        (600, maze_y_start + 150, 300, wall_thickness),
        (50, maze_y_start + 300, 350, wall_thickness),
        (500, maze_y_start + 300, 350, wall_thickness),
        (200, maze_y_start + 450, 700, wall_thickness),
    ]
    
    # Vertical walls
    v_walls = [
        (WIDTH//2 - wall_thickness//2, maze_y_start, wall_thickness, 150),
        (200, maze_y_start + 150, wall_thickness, 150),
        (500, maze_y_start + 150, wall_thickness, 150),
        (WIDTH//2 - wall_thickness//2, maze_y_start + 300, wall_thickness, 150),
    ]
    
    # Add all maze walls
    for wall in h_walls:
        objects.append(RectObject(*wall))
    for wall in v_walls:
        objects.append(RectObject(*wall))
    
    # Collection area at the bottom
    basin_width = 300
    basin_height = 80
    basin_x = WIDTH//2 - basin_width//2
    basin_y = HEIGHT - basin_height - 20
    
    objects.append(RectObject(basin_x, basin_y, wall_thickness, basin_height))  # Left wall
    objects.append(RectObject(basin_x + basin_width - wall_thickness, basin_y, wall_thickness, basin_height))  # Right wall
    objects.append(RectObject(basin_x, basin_y + basin_height - wall_thickness, basin_width, wall_thickness))  # Bottom
    
    return objects

def create_fountain_scene():
    """Create a scene with circular shapes that can act as a fountain"""
    objects = create_empty_scene()
    
    # Base pool
    pool_width = WIDTH - 200
    pool_height = 80
    wall_thickness = 15
    pool_x = 100
    pool_y = HEIGHT - pool_height - 20
    
    # Pool walls
    objects.append(RectObject(pool_x, pool_y, wall_thickness, pool_height))  # Left wall
    objects.append(RectObject(pool_x + pool_width - wall_thickness, pool_y, wall_thickness, pool_height))  # Right wall
    objects.append(RectObject(pool_x, pool_y + pool_height - wall_thickness, pool_width, wall_thickness))  # Bottom
    
    # Center fountain base
    base_radius = 120
    base_x = WIDTH // 2
    base_y = HEIGHT - 200
    objects.append(CircleObject(base_x, base_y, base_radius))
    
    # Middle tier
    middle_radius = 80
    middle_x = WIDTH // 2
    middle_y = HEIGHT - 350
    objects.append(CircleObject(middle_x, middle_y, middle_radius))
    
    # Top tier
    top_radius = 40
    top_x = WIDTH // 2
    top_y = HEIGHT - 450
    objects.append(CircleObject(top_x, top_y, top_radius))
    
    return objects

def get_scene_objects(scene_name):
    """Get objects for the specified scene"""
    if scene_name == SCENE_EMPTY:
        return create_empty_scene()
    elif scene_name == SCENE_BUCKET:
        return create_bucket_scene()
    elif scene_name == SCENE_POOL:
        return create_pool_scene()
    elif scene_name == SCENE_WATERFALL:
        return create_waterfall_scene()
    elif scene_name == SCENE_MAZE:
        return create_maze_scene()
    elif scene_name == SCENE_FOUNTAIN:
        return create_fountain_scene()
    else:
        # Default to empty scene
        return create_empty_scene()