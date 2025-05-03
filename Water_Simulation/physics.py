import numpy as np
import math
import random
import pygame
from constants import *

class Vector2D:
    """2D vector class for physics calculations"""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        if scalar == 0:
            return Vector2D(0, 0)  # Prevent division by zero
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def length_squared(self):
        return self.x**2 + self.y**2
    
    def normalize(self):
        length = self.length()
        if length < 0.0001:
            return Vector2D(0, 0)
        return Vector2D(self.x / length, self.y / length)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def to_tuple(self):
        return (self.x, self.y)

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
        # Apply forces - scale by delta time for consistent physics regardless of framerate
        self.acceleration = self.force * (1.0 / self.mass)
        self.velocity = self.velocity + self.acceleration * dt
        
        # Store position for trail effect if enabled
        if self.max_trail_length > 0:
            self.trail.append(self.position.to_tuple())
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)
        
        # Update position using delta time for frame-rate independent movement
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
            if obj.object_type == OBJ_RECT:
                # Rectangle collision
                # Check if particle is inside the rectangle
                if (obj.rect.left - self.radius <= self.position.x <= obj.rect.right + self.radius and
                    obj.rect.top - self.radius <= self.position.y <= obj.rect.bottom + self.radius):
                    
                    # Find the closest point on the rectangle to the particle
                    closest_x = max(obj.rect.left, min(self.position.x, obj.rect.right))
                    closest_y = max(obj.rect.top, min(self.position.y, obj.rect.bottom))
                    
                    # Vector from closest point to particle center
                    distance_x = self.position.x - closest_x
                    distance_y = self.position.y - closest_y
                    distance_sq = distance_x**2 + distance_y**2
                    
                    # Check if we're actually colliding (distance < radius)
                    if distance_sq < self.radius**2:
                        if distance_sq < 0.0001:  # Avoid division by zero
                            # Push slightly away in random direction
                            angle = random.uniform(0, 2 * math.pi)
                            self.position.x = closest_x + math.cos(angle) * self.radius
                            self.position.y = closest_y + math.sin(angle) * self.radius
                        else:
                            # Calculate penetration depth
                            distance = math.sqrt(distance_sq)
                            penetration = self.radius - distance
                            
                            # Normal vector
                            nx = distance_x / distance
                            ny = distance_y / distance
                            
                            # Push particle out along normal
                            self.position.x = closest_x + nx * self.radius
                            self.position.y = closest_y + ny * self.radius
                            
                            # Reflect velocity with some energy loss
                            normal = Vector2D(nx, ny)
                            dot_product = self.velocity.x * normal.x + self.velocity.y * normal.y
                            self.velocity.x -= (1 + RESTITUTION) * dot_product * normal.x
                            self.velocity.y -= (1 + RESTITUTION) * dot_product * normal.y
                            
                            # Apply some friction to the tangential component
                            tangent = Vector2D(-normal.y, normal.x)
                            dot_product = self.velocity.x * tangent.x + self.velocity.y * tangent.y
                            self.velocity.x -= FRICTION * dot_product * tangent.x
                            self.velocity.y -= FRICTION * dot_product * tangent.y
                            
            elif obj.object_type == OBJ_CIRCLE:
                # Circle collision
                # Calculate distance between centers
                dx = self.position.x - obj.center_x
                dy = self.position.y - obj.center_y
                distance_sq = dx**2 + dy**2
                
                # Sum of radii
                sum_radii = self.radius + obj.radius
                
                # Check for collision
                if distance_sq < sum_radii**2:
                    if distance_sq < 0.0001:  # Avoid division by zero
                        # Push slightly away in random direction
                        angle = random.uniform(0, 2 * math.pi)
                        self.position.x = obj.center_x + math.cos(angle) * sum_radii
                        self.position.y = obj.center_y + math.sin(angle) * sum_radii
                    else:
                        # Calculate penetration depth
                        distance = math.sqrt(distance_sq)
                        penetration = sum_radii - distance
                        
                        # Normal vector
                        nx = dx / distance
                        ny = dy / distance
                        
                        # Push particle out along normal
                        self.position.x = obj.center_x + nx * sum_radii
                        self.position.y = obj.center_y + ny * sum_radii
                        
                        # Reflect velocity with some energy loss
                        normal = Vector2D(nx, ny)
                        dot_product = self.velocity.x * normal.x + self.velocity.y * normal.y
                        self.velocity.x -= (1 + RESTITUTION) * dot_product * normal.x
                        self.velocity.y -= (1 + RESTITUTION) * dot_product * normal.y
                        
                        # Apply some friction to the tangential component
                        tangent = Vector2D(-normal.y, normal.x)
                        dot_product = self.velocity.x * tangent.x + self.velocity.y * tangent.y
                        self.velocity.x -= FRICTION * dot_product * tangent.x
                        self.velocity.y -= FRICTION * dot_product * tangent.y
                        
            elif obj.object_type == OBJ_POLYGON:
                # Polygon collision is more complex
                # For simplicity, we'll just handle basic penetration
                if obj.contains_point(self.position.x, self.position.y):
                    # Find the closest edge
                    edge_distances = []
                    for i in range(len(obj.points)):
                        p1 = obj.points[i]
                        p2 = obj.points[(i + 1) % len(obj.points)]
                        
                        # Calculate distance to line segment
                        line_vec = Vector2D(p2[0] - p1[0], p2[1] - p1[1])
                        point_vec = Vector2D(self.position.x - p1[0], self.position.y - p1[1])
                        
                        line_length = line_vec.length()
                        if line_length < 0.0001:
                            continue
                            
                        # Project point onto line
                        t = max(0, min(1, point_vec.dot(line_vec) / line_vec.length_squared()))
                        projection = Vector2D(p1[0], p1[1]) + line_vec * t
                        
                        # Distance from point to projection
                        dist_vec = Vector2D(self.position.x - projection.x, self.position.y - projection.y)
                        distance = dist_vec.length()
                        
                        edge_distances.append((distance, dist_vec.normalize(), projection))
                    
                    if edge_distances:
                        # Find the closest edge
                        closest = min(edge_distances, key=lambda x: x[0])
                        distance, normal, projection = closest
                        
                        # Push particle out
                        penetration = self.radius + distance
                        self.position.x = projection.x + normal.x * penetration
                        self.position.y = projection.y + normal.y * penetration
                        
                        # Reflect velocity with some energy loss
                        dot_product = self.velocity.x * normal.x + self.velocity.y * normal.y
                        self.velocity.x -= (1 + RESTITUTION) * dot_product * normal.x
                        self.velocity.y -= (1 + RESTITUTION) * dot_product * normal.y
                        
                        # Apply some friction to the tangential component
                        tangent = Vector2D(-normal.y, normal.x)
                        dot_product = self.velocity.x * tangent.x + self.velocity.y * tangent.y
                        self.velocity.x -= FRICTION * dot_product * tangent.x
                        self.velocity.y -= FRICTION * dot_product * tangent.y
    
    def draw(self, screen):
        """Draw the particle on the screen"""
        # Draw trail if enabled
        if self.max_trail_length > 0 and len(self.trail) > 1:
            for i in range(1, len(self.trail)):
                alpha = int(255 * (i / len(self.trail)))
                trail_color = (self.color[0], self.color[1], self.color[2], alpha)
                trail_radius = self.radius * (i / len(self.trail))
                pygame.draw.circle(screen, trail_color, self.trail[i], max(1, int(trail_radius)))
                
        # Draw the particle
        pygame.draw.circle(screen, self.color, self.position.to_tuple(), self.radius)

class BasicParticle(Particle):
    """Simple particle class for basic water simulation"""
    def __init__(self, x, y, color=None):
        super().__init__(x, y, color)
        # No additional properties needed for basic particles as they inherit everything from Particle
        
    def update(self, dt, objects):
        """Update particle using simple physics"""
        # Apply gravity force
        self.apply_force(Vector2D(0, GRAVITY * self.mass))
        
        # Basic physics update from parent class
        super().update(dt, objects)
        
        # Handle boundary and object collisions
        self.handle_boundary_collision(WIDTH, HEIGHT)
        self.handle_object_collision(objects)

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
        self.update_count = 0  # Counter for optimization
        
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
        # Performance optimization: Skip some updates for cells that don't change much
        self.update_count += 1
        update_all = (self.update_count % 3 == 0)  # Full update every 3 frames
        
        # Create copies for updating
        new_grid = self.grid.copy()
        new_water_levels = self.water_levels.copy()
        
        # Process water cells from bottom to top, right to left for better flow behavior
        water_changed = False
        active_water_cells = 0
        
        for y in range(self.height - 2, -1, -1):
            for x in range(self.width - 1, -1, -1):
                if self.grid[y, x] == WATER and self.water_levels[y, x] > 0:
                    active_water_cells += 1
                    # Process water cells with significant water or periodically do full update
                    if self.water_levels[y, x] > 0.05 or update_all:
                        water_moved = self._process_water_cell(x, y, new_grid, new_water_levels)
                        water_changed = water_changed or water_moved
        
        # Update the grid state
        np.copyto(self.grid, new_grid)
        np.copyto(self.water_levels, new_water_levels)
        
        # Remove empty water cells and fix infinite water sources
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] == WATER:
                    # Fix: Remove water cells with very low water level to prevent infinite sources
                    if self.water_levels[y, x] <= 0.01:
                        self.grid[y, x] = EMPTY
                        self.water_levels[y, x] = 0
                    # Fix: Cap water level at 1.0 to prevent infinite accumulation
                    elif self.water_levels[y, x] > 1.0:
                        self.water_levels[y, x] = 1.0
        
        # For very small numbers of active cells, add some randomization to prevent stagnation
        if active_water_cells > 0 and active_water_cells < 200 and not water_changed:
            # Add small perturbations to a few random water cells
            for _ in range(min(5, active_water_cells)):
                # Find a random water cell
                water_cells = np.where(self.grid == WATER)
                if len(water_cells[0]) > 0:
                    idx = np.random.randint(0, len(water_cells[0]))
                    y, x = water_cells[0][idx], water_cells[1][idx]
                    # Add small random variation to water level
                    self.water_levels[y, x] = min(1.0, max(0.01, 
                                                         self.water_levels[y, x] + np.random.uniform(-0.03, 0.03)))
    
    def _process_water_cell(self, x, y, new_grid, new_water_levels):
        """Process water movement from a single cell. Returns True if water moved."""
        current_water = self.water_levels[y, x]
        if current_water <= 0:
            return False
            
        remaining_water = current_water
        water_moved = False
        
        # Try to flow down
        if y < self.height - 1:
            if self.grid[y + 1, x] == EMPTY:
                # Empty cell below, transfer all water
                flow_amount = remaining_water
                new_grid[y + 1, x] = WATER
                new_water_levels[y + 1, x] += flow_amount
                new_water_levels[y, x] = 0
                return True
            elif self.grid[y + 1, x] == WATER and self.water_levels[y + 1, x] < 1.0:
                # Water cell below with space
                available_space = 1.0 - self.water_levels[y + 1, x]
                flow_amount = min(remaining_water, available_space)
                new_water_levels[y + 1, x] += flow_amount
                remaining_water -= flow_amount
                water_moved = flow_amount > 0.001
                if remaining_water <= 0:
                    new_water_levels[y, x] = 0
                    return water_moved
        
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
            if flow_to_left > 0.001:
                new_grid[y, x - 1] = WATER
                new_water_levels[y, x - 1] = min(1.0, left_water + flow_to_left)
                remaining_water -= flow_to_left
                water_moved = True
            
            # Set right cell
            flow_to_right = max(0, avg_water - right_water)
            if flow_to_right > 0.001:
                new_grid[y, x + 1] = WATER
                new_water_levels[y, x + 1] = min(1.0, right_water + flow_to_right)
                remaining_water -= flow_to_right
                water_moved = True
                
        elif can_flow_left:
            # Only flow left
            left_water = self.water_levels[y, x - 1] if self.grid[y, x - 1] == WATER else 0
            if left_water < remaining_water:
                # Try to equalize
                avg_water = (remaining_water + left_water) / 2.0
                flow_amount = avg_water - left_water
                
                if flow_amount > 0.001:
                    new_grid[y, x - 1] = WATER
                    new_water_levels[y, x - 1] = min(1.0, left_water + flow_amount)
                    remaining_water -= flow_amount
                    water_moved = True
                
        elif can_flow_right:
            # Only flow right
            right_water = self.water_levels[y, x + 1] if self.grid[y, x + 1] == WATER else 0
            if right_water < remaining_water:
                # Try to equalize
                avg_water = (remaining_water + right_water) / 2.0
                flow_amount = avg_water - right_water
                
                if flow_amount > 0.001:
                    new_grid[y, x + 1] = WATER
                    new_water_levels[y, x + 1] = min(1.0, right_water + flow_amount)
                    remaining_water -= flow_amount
                    water_moved = True
        
        # Update current cell with remaining water
        new_water_levels[y, x] = max(0, remaining_water)
        if remaining_water <= 0:
            new_grid[y, x] = EMPTY
            
        return water_moved
    
    def draw(self, screen):
        """Draw the grid-based fluid simulation on the screen"""
        # Draw water cells
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] == WATER:
                    # Calculate position
                    screen_x = x * CELL_SIZE
                    screen_y = y * CELL_SIZE
                    
                    # Calculate color based on water level
                    water_level = self.water_levels[y, x]
                    r = max(0, min(255, WATER_COLOR[0] - int(40 * water_level)))
                    g = max(0, min(255, WATER_COLOR[1] - int(20 * water_level)))
                    b = max(0, min(255, WATER_COLOR[2] + int(20 * water_level)))
                    color = (r, g, b)
                    
                    # Draw the water cell
                    cell_rect = pygame.Rect(screen_x, screen_y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, color, cell_rect)
                    
                    # Draw cell outline for better visibility
                    # Ensure outline color values are properly clamped to valid range (0-255)
                    outline_r = max(0, min(255, r-20))
                    outline_g = max(0, min(255, g-20))
                    outline_b = max(0, min(255, b+20))
                    pygame.draw.rect(screen, (outline_r, outline_g, outline_b), cell_rect, 1)
                
                # Optionally draw solid cells if needed
                elif self.grid[y, x] == SOLID:
                    screen_x = x * CELL_SIZE
                    screen_y = y * CELL_SIZE
                    cell_rect = pygame.Rect(screen_x, screen_y, CELL_SIZE, CELL_SIZE)
                    # Only draw solid cells that aren't drawn by objects
                    # Uncomment if you want to see the grid's solid cells
                    # pygame.draw.rect(screen, (100, 100, 100), cell_rect)

class SPHParticle(Particle):
    """Particle using Smoothed Particle Hydrodynamics for more realistic fluid simulation"""
    def __init__(self, x, y, color=None):
        super().__init__(x, y, color)
        self.density = 0
        self.pressure = 0
        self.neighbors = []
        # Damping to control excessive bouncing
        self.restitution = 0.3  # Lower value than RESTITUTION constant
        self.max_velocity = 100.0  # Cap velocity to prevent extreme speeds
        
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
        # Clamp pressure to avoid extreme values
        self.pressure = max(-1000, min(3000, self.pressure))
    
    def calculate_forces(self, particles):
        """Calculate forces acting on the particle from neighbors"""
        # Reset forces
        self.reset_forces()
        
        # Apply gravity - scaled properly with delta time in update method
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
            # Scale down pressure force for stability
            pressure_magnitude *= 0.5
            pressure_force = pressure_force + direction * pressure_magnitude
            
            # Calculate viscosity force (using Viscosity kernel)
            relative_velocity = neighbor.velocity - self.velocity
            viscosity_magnitude = VISCOSITY_STRENGTH * MASS * h_minus_r / neighbor.density
            viscosity_magnitude *= (45.0 / (math.pi * math.pow(SMOOTHING_LENGTH, 6)))
            viscosity_force = viscosity_force + relative_velocity * viscosity_magnitude
            
            # Surface tension (simplified)
            if distance < SMOOTHING_LENGTH * 0.5:
                surface_tension_force = surface_tension_force + direction * (SURFACE_TENSION * 0.5)  # Reduced strength
        
        # Apply calculated forces with clamping to prevent extreme accelerations
        self.apply_force(Vector2D(
            max(-500, min(500, pressure_force.x)),
            max(-500, min(500, pressure_force.y))
        ))
        self.apply_force(viscosity_force)
        self.apply_force(surface_tension_force)
    
    def update(self, dt, objects):
        """Update particle using SPH forces"""
        # Cap dt to avoid instability
        capped_dt = min(dt, 0.016)  # Maximum of ~60FPS equivalent
        
        # Physics update (SPH forces are applied separately)
        super().update(capped_dt, objects)
        
        # Cap velocity to prevent extreme speeds
        velocity_length = self.velocity.length()
        if velocity_length > self.max_velocity:
            self.velocity = self.velocity * (self.max_velocity / velocity_length)
        
        # Handle boundary collisions with custom restitution
        if self.position.x < self.radius:
            self.position.x = self.radius
            self.velocity.x *= -self.restitution
        elif self.position.x > WIDTH - self.radius:
            self.position.x = WIDTH - self.radius
            self.velocity.x *= -self.restitution
            
        if self.position.y < self.radius:
            self.position.y = self.radius
            self.velocity.y *= -self.restitution
        elif self.position.y > HEIGHT - self.radius:
            self.position.y = HEIGHT - self.radius
            self.velocity.y *= -self.restitution
            self.velocity.x *= FRICTION
        
        # Handle object collisions
        self.handle_object_collision(objects)