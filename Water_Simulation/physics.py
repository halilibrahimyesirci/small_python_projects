"""
Project: Advanced Water Simulation
Description: Physics engines for different water simulation methods
"""

import numpy as np
import random
import math
from constants import *
import pygame

class Vector2D:
    """A simple 2D vector class for physics calculations"""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        if scalar == 0:
            return Vector2D()
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def length_squared(self):
        return self.x**2 + self.y**2
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def distance_squared_to(self, other):
        return (self.x - other.x)**2 + (self.y - other.y)**2
    
    def normalize(self):
        length = self.length()
        if length != 0:
            self.x /= length
            self.y /= length
        return self
    
    def normalized(self):
        result = Vector2D(self.x, self.y)
        return result.normalize()
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def to_tuple(self):
        return (self.x, self.y)
    
    def to_int_tuple(self):
        return (int(self.x), int(self.y))
    
    @staticmethod
    def from_tuple(t):
        return Vector2D(t[0], t[1])


class Particle:
    """Base particle class for water simulation"""
    def __init__(self, x, y, color=None):
        self.position = Vector2D(x, y)
        self.velocity = Vector2D(random.uniform(-0.5, 0.5), random.uniform(-0.2, 0.5))
        self.acceleration = Vector2D(0, 0)
        self.force = Vector2D(0, 0)
        
        # Random variation in water color
        if color is None:
            r = max(0, min(255, WATER_COLOR[0] + random.randint(-WATER_COLOR_VARIATION, WATER_COLOR_VARIATION)))
            g = max(0, min(255, WATER_COLOR[1] + random.randint(-WATER_COLOR_VARIATION, WATER_COLOR_VARIATION)))
            b = max(0, min(255, WATER_COLOR[2] + random.randint(-WATER_COLOR_VARIATION, WATER_COLOR_VARIATION)))
            self.color = (r, g, b)
        else:
            self.color = color
            
        self.radius = PARTICLE_RADIUS
        self.mass = PARTICLE_MASS
        self.density = 0
        self.pressure = 0
        
        # For visualization
        self.trail = []  # Stores recent positions for drawing trails
        self.max_trail_length = 5
        
    def apply_force(self, force):
        """Apply a force to the particle"""
        self.force = self.force + force
        
    def reset_forces(self):
        """Reset accumulated forces"""
        self.force = Vector2D(0, 0)
        
    def update(self, dt, objects):
        """Basic update method to be overridden by specific simulation types"""
        # Apply forces
        self.acceleration = self.force * (1.0 / self.mass)
        self.velocity = self.velocity + self.acceleration * dt
        
        # Store position for trail effect if enabled
        if self.max_trail_length > 0:
            self.trail.append(self.position.to_tuple())
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)
        
        # Update position
        self.position = self.position + self.velocity * dt
        
        # Reset forces for next update
        self.reset_forces()
        
    def handle_boundary_collision(self, width, height):
        """Handle collisions with screen boundaries"""
        # Left and right boundaries
        if self.position.x < self.radius:
            self.position.x = self.radius
            self.velocity.x *= -RESTITUTION
        elif self.position.x > width - self.radius:
            self.position.x = width - self.radius
            self.velocity.x *= -RESTITUTION
            
        # Top and bottom boundaries
        if self.position.y < self.radius:
            self.position.y = self.radius
            self.velocity.y *= -RESTITUTION
        elif self.position.y > height - self.radius:
            self.position.y = height - self.radius
            self.velocity.y *= -RESTITUTION
            self.velocity.x *= FRICTION  # Apply friction on the ground
            
    def handle_object_collision(self, objects):
        """Handle collisions with simulation objects"""
        for obj in objects:
            if obj.contains_point(self.position.x, self.position.y):
                # Get collision normal
                normal = obj.get_collision_normal(self.position.x, self.position.y)
                
                # Move particle outside object
                correction = normal * (self.radius + 0.1)
                self.position = self.position + correction
                
                # Reflect velocity based on collision normal
                dot = self.velocity.dot(normal)
                self.velocity = self.velocity - normal * (2 * dot * RESTITUTION)
                self.velocity.x *= FRICTION  # Apply friction along surface
            elif obj.object_type == OBJ_CIRCLE:
                # Special case for circle objects - check distance
                dx = self.position.x - obj.center_x
                dy = self.position.y - obj.center_y
                distance_squared = dx*dx + dy*dy
                min_distance = obj.radius + self.radius
                
                if distance_squared < min_distance*min_distance:
                    # Collision with circle
                    distance = math.sqrt(distance_squared)
                    normal = Vector2D(dx/distance, dy/distance)
                    
                    # Move particle outside circle
                    correction = normal * (min_distance - distance + 0.1)
                    self.position = self.position + correction
                    
                    # Reflect velocity
                    dot = self.velocity.dot(normal)
                    if dot < 0:  # Only reflect if moving toward the circle
                        self.velocity = self.velocity - normal * (2 * dot * RESTITUTION)
        
    def draw(self, surface):
        """Draw the particle on the surface"""
        # Draw trail if enabled
        if len(self.trail) > 1:
            points = self.trail + [self.position.to_tuple()]
            pygame.draw.lines(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2, 100), False, points, 1)
            
        # Draw particle
        pygame.draw.circle(surface, self.color, self.position.to_int_tuple(), int(self.radius))


class BasicParticle(Particle):
    """Particle with basic physics for simple simulation"""
    def __init__(self, x, y, color=None):
        super().__init__(x, y, color)
        # Reduce trail for basic particles
        self.max_trail_length = 0
        
    def update(self, dt, objects):
        """Simple physics update"""
        # Apply gravity
        self.apply_force(Vector2D(0, GRAVITY * self.mass))
        
        # Basic physics update
        super().update(dt, objects)
        
        # Handle boundary collisions
        self.handle_boundary_collision(WIDTH, HEIGHT)
        
        # Handle object collisions
        self.handle_object_collision(objects)


class SPHParticle(Particle):
    """Particle using Smoothed Particle Hydrodynamics for more realistic fluid simulation"""
    def __init__(self, x, y, color=None):
        super().__init__(x, y, color)
        self.density = 0
        self.pressure = 0
        self.neighbors = []
        
    def calculate_density_and_pressure(self, particles):
        """Calculate particle density and pressure based on neighboring particles"""
        self.density = 0
        self.neighbors = []
        
        # Find neighbors and calculate density
        for particle in particles:
            # Skip self
            if particle is self:
                continue
                
            # Calculate distance
            distance_vec = self.position - particle.position
            distance_squared = distance_vec.length_squared()
            
            # Check if particle is within smoothing radius
            if distance_squared < SMOOTHING_LENGTH_SQ:
                # Poly6 kernel for density
                self.neighbors.append(particle)
                distance = math.sqrt(distance_squared)
                if distance < 0.0001:
                    continue
                
                # Calculate density contribution
                h_minus_r = SMOOTHING_LENGTH - distance
                self.density += MASS * (315.0 / (64.0 * math.pi * math.pow(SMOOTHING_LENGTH, 9))) * math.pow(h_minus_r, 3)
        
        # Calculate pressure (follows ideal gas law)
        self.pressure = GAS_CONSTANT * (self.density - REST_DENSITY)
    
    def calculate_forces(self, particles):
        """Calculate forces acting on the particle from neighbors"""
        # Reset forces
        self.reset_forces()
        
        # Apply gravity
        self.apply_force(Vector2D(0, GRAVITY * self.mass))
        
        pressure_force = Vector2D(0, 0)
        viscosity_force = Vector2D(0, 0)
        surface_tension_force = Vector2D(0, 0)
        
        # Calculate forces from neighbors
        for neighbor in self.neighbors:
            # Skip self (should not be in neighbors but just in case)
            if neighbor is self:
                continue
                
            # Get direction vector
            direction = self.position - neighbor.position
            distance = direction.length()
            
            # Skip very close particles to avoid division by zero
            if distance < 0.0001:
                continue
                
            # Normalize direction
            direction = direction / distance
            
            # Calculate pressure force (using Spiky kernel)
            h_minus_r = SMOOTHING_LENGTH - distance
            pressure_magnitude = -MASS * (self.pressure + neighbor.pressure) / (2 * neighbor.density)
            pressure_magnitude *= (45.0 / (math.pi * math.pow(SMOOTHING_LENGTH, 6))) * math.pow(h_minus_r, 2)
            pressure_force = pressure_force + direction * pressure_magnitude
            
            # Calculate viscosity force (using Viscosity kernel)
            relative_velocity = neighbor.velocity - self.velocity
            viscosity_magnitude = VISCOSITY_STRENGTH * MASS * h_minus_r / neighbor.density
            viscosity_magnitude *= (45.0 / (math.pi * math.pow(SMOOTHING_LENGTH, 6)))
            viscosity_force = viscosity_force + relative_velocity * viscosity_magnitude
            
            # Surface tension (simplified)
            if distance < SMOOTHING_LENGTH * 0.5:
                surface_tension_force = surface_tension_force + direction * SURFACE_TENSION
        
        # Apply calculated forces
        self.apply_force(pressure_force)
        self.apply_force(viscosity_force)
        self.apply_force(surface_tension_force)
    
    def update(self, dt, objects):
        """Update particle using SPH forces"""
        # Physics update (SPH forces are applied separately)
        super().update(dt, objects)
        
        # Handle boundary collisions
        self.handle_boundary_collision(WIDTH, HEIGHT)
        
        # Handle object collisions
        self.handle_object_collision(objects)


class GridCell:
    """Cell for grid-based fluid simulation"""
    def __init__(self):
        self.type = EMPTY
        self.water_level = 0  # 0 to 1 representing water fill level
        self.velocity_x = 0
        self.velocity_y = 0
        self.pressure = 0


class GridSimulation:
    """Grid-based fluid simulation engine"""
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.grid = np.zeros((self.height, self.width), dtype=np.int8)
        self.water_levels = np.zeros((self.height, self.width), dtype=np.float32)
        self.velocity_x = np.zeros((self.height, self.width), dtype=np.float32)
        self.velocity_y = np.zeros((self.height, self.width), dtype=np.float32)
        self.pressure = np.zeros((self.height, self.width), dtype=np.float32)
        
    def add_water(self, x, y, amount=1.0):
        """Add water to a grid cell"""
        grid_x, grid_y = int(x // CELL_SIZE), int(y // CELL_SIZE)
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            if self.grid[grid_y, grid_x] == EMPTY:
                self.grid[grid_y, grid_x] = WATER
                self.water_levels[grid_y, grid_x] = min(1.0, self.water_levels[grid_y, grid_x] + amount)
                
    def add_solid(self, x, y):
        """Add a solid cell to the grid"""
        grid_x, grid_y = int(x // CELL_SIZE), int(y // CELL_SIZE)
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.grid[grid_y, grid_x] = SOLID
            self.water_levels[grid_y, grid_x] = 0
            
    def initialize_from_objects(self, objects):
        """Initialize grid cells based on simulation objects"""
        # Reset grid
        self.grid.fill(EMPTY)
        self.water_levels.fill(0)
        self.velocity_x.fill(0)
        self.velocity_y.fill(0)
        self.pressure.fill(0)
        
        # Add solids from objects
        for obj in objects:
            if obj.object_type == OBJ_RECT:
                # For rectangles, fill the area
                x1 = max(0, int(obj.rect.left // CELL_SIZE))
                x2 = min(self.width, int(obj.rect.right // CELL_SIZE) + 1)
                y1 = max(0, int(obj.rect.top // CELL_SIZE))
                y2 = min(self.height, int(obj.rect.bottom // CELL_SIZE) + 1)
                
                self.grid[y1:y2, x1:x2] = SOLID
                
            elif obj.object_type == OBJ_CIRCLE:
                # For circles, fill approximation of the circle
                center_x = int(obj.center_x // CELL_SIZE)
                center_y = int(obj.center_y // CELL_SIZE)
                radius_cells = int(obj.radius // CELL_SIZE) + 1
                
                for y in range(max(0, center_y - radius_cells), min(self.height, center_y + radius_cells + 1)):
                    for x in range(max(0, center_x - radius_cells), min(self.width, center_x + radius_cells + 1)):
                        dx = (x * CELL_SIZE + CELL_SIZE/2) - obj.center_x
                        dy = (y * CELL_SIZE + CELL_SIZE/2) - obj.center_y
                        if dx*dx + dy*dy <= (obj.radius * obj.radius):
                            self.grid[y, x] = SOLID
                            
            elif obj.object_type == OBJ_POLYGON:
                # For polygons, check each cell against the polygon
                # This is a simple approximation that considers the cell center
                for y in range(self.height):
                    for x in range(self.width):
                        cell_center_x = x * CELL_SIZE + CELL_SIZE/2
                        cell_center_y = y * CELL_SIZE + CELL_SIZE/2
                        if obj.contains_point(cell_center_x, cell_center_y):
                            self.grid[y, x] = SOLID
    
    def update(self, dt):
        """Update the grid-based fluid simulation"""
        # Create copies for updating
        new_grid = self.grid.copy()
        new_water_levels = self.water_levels.copy()
        
        # Process each cell from bottom to top, right to left (for better flow behavior)
        for y in range(self.height - 2, -1, -1):
            for x in range(self.width - 1, -1, -1):
                if self.grid[y, x] == WATER and self.water_levels[y, x] > 0:
                    self._process_water_cell(x, y, new_grid, new_water_levels)
        
        # Update the grid state
        np.copyto(self.grid, new_grid)
        np.copyto(self.water_levels, new_water_levels)
        
        # Remove empty water cells
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] == WATER and self.water_levels[y, x] <= 0.01:
                    self.grid[y, x] = EMPTY
                    self.water_levels[y, x] = 0
    
    def _process_water_cell(self, x, y, new_grid, new_water_levels):
        """Process water movement from a single cell"""
        current_water = self.water_levels[y, x]
        if current_water <= 0:
            return
            
        remaining_water = current_water
        
        # Try to flow down
        if y < self.height - 1:
            if self.grid[y + 1, x] == EMPTY:
                # Empty cell below, transfer all water
                flow_amount = remaining_water
                new_grid[y + 1, x] = WATER
                new_water_levels[y + 1, x] += flow_amount
                new_water_levels[y, x] = 0
                return
            elif self.grid[y + 1, x] == WATER and self.water_levels[y + 1, x] < 1.0:
                # Water cell below with space
                available_space = 1.0 - self.water_levels[y + 1, x]
                flow_amount = min(remaining_water, available_space)
                new_water_levels[y + 1, x] += flow_amount
                remaining_water -= flow_amount
                if remaining_water <= 0:
                    new_water_levels[y, x] = 0
                    return
        
        # If we couldn't flow down completely, try to flow sideways
        # Check both left and right
        can_flow_left = x > 0 and self.grid[y, x - 1] != SOLID
        can_flow_right = x < self.width - 1 and self.grid[y, x + 1] != SOLID
        
        if can_flow_left and can_flow_right:
            # Try to equalize between three cells (current, left, right)
            left_water = self.water_levels[y, x - 1] if self.grid[y, x - 1] == WATER else 0
            right_water = self.water_levels[y, x + 1] if self.grid[y, x + 1] == WATER else 0
            
            total_water = remaining_water + left_water + right_water
            avg_water = total_water / 3.0
            
            # Set left cell
            flow_to_left = max(0, avg_water - left_water)
            if flow_to_left > 0:
                new_grid[y, x - 1] = WATER
                new_water_levels[y, x - 1] = min(1.0, left_water + flow_to_left)
                remaining_water -= flow_to_left
            
            # Set right cell
            flow_to_right = max(0, avg_water - right_water)
            if flow_to_right > 0:
                new_grid[y, x + 1] = WATER
                new_water_levels[y, x + 1] = min(1.0, right_water + flow_to_right)
                remaining_water -= flow_to_right
                
        elif can_flow_left:
            # Only flow left
            left_water = self.water_levels[y, x - 1] if self.grid[y, x - 1] == WATER else 0
            if left_water < remaining_water:
                # Try to equalize
                avg_water = (remaining_water + left_water) / 2.0
                flow_amount = avg_water - left_water
                
                new_grid[y, x - 1] = WATER
                new_water_levels[y, x - 1] = min(1.0, left_water + flow_amount)
                remaining_water -= flow_amount
                
        elif can_flow_right:
            # Only flow right
            right_water = self.water_levels[y, x + 1] if self.grid[y, x + 1] == WATER else 0
            if right_water < remaining_water:
                # Try to equalize
                avg_water = (remaining_water + right_water) / 2.0
                flow_amount = avg_water - right_water
                
                new_grid[y, x + 1] = WATER
                new_water_levels[y, x + 1] = min(1.0, right_water + flow_amount)
                remaining_water -= flow_amount
        
        # Update current cell with remaining water
        new_water_levels[y, x] = max(0, remaining_water)
        if remaining_water <= 0:
            new_grid[y, x] = EMPTY
            
    def draw(self, surface):
        """Draw the grid-based simulation"""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] != EMPTY:
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    
                    if self.grid[y, x] == WATER:
                        # Calculate water color based on water level
                        level = self.water_levels[y, x]
                        r = int(max(0, min(255, WATER_COLOR[0] - 30 + 60 * level)))
                        g = int(max(0, min(255, WATER_COLOR[1] - 20 + 40 * level)))
                        b = int(max(0, min(255, WATER_COLOR[2])))
                        color = (r, g, b)
                        pygame.draw.rect(surface, color, rect)
                        
                    elif self.grid[y, x] == SOLID:
                        pygame.draw.rect(surface, OBJECT_COLOR, rect)