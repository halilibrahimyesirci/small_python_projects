import numpy as np
import math
import random
import pygame
from constants import *

class Vector2D:
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
            return Vector2D(0, 0)
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
    def __init__(self, x, y, color=None):
        self.position = Vector2D(x, y)
        self.velocity = Vector2D(random.uniform(-0.5, 0.5), random.uniform(-0.2, 0.5))
        self.acceleration = Vector2D(0, 0)
        self.force = Vector2D(0, 0)
        
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
        
        self.trail = []
        self.max_trail_length = 5
        
    def apply_force(self, force):
        self.force = self.force + force
        
    def reset_forces(self):
        self.force = Vector2D(0, 0)
        
    def update(self, dt, objects):
        self.acceleration = self.force * (1.0 / self.mass)
        self.velocity = self.velocity + self.acceleration * dt
        
        if self.max_trail_length > 0:
            self.trail.append(self.position.to_tuple())
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)
        
        self.position = self.position + self.velocity * dt
        
        self.reset_forces()
        
    def handle_boundary_collision(self, width, height):
        if self.position.x < self.radius:
            self.position.x = self.radius
            self.velocity.x *= -RESTITUTION
        elif self.position.x > width - self.radius:
            self.position.x = width - self.radius
            self.velocity.x *= -RESTITUTION
            
        if self.position.y < self.radius:
            self.position.y = self.radius
            self.velocity.y *= -RESTITUTION
        elif self.position.y > height - self.radius:
            self.position.y = height - self.radius
            self.velocity.y *= -RESTITUTION
            self.velocity.x *= FRICTION

    def handle_object_collision(self, objects):
        for obj in objects:
            if obj.object_type == OBJ_RECT:
                if (obj.rect.left - self.radius <= self.position.x <= obj.rect.right + self.radius and
                    obj.rect.top - self.radius <= self.position.y <= obj.rect.bottom + self.radius):
                    
                    closest_x = max(obj.rect.left, min(self.position.x, obj.rect.right))
                    closest_y = max(obj.rect.top, min(self.position.y, obj.rect.bottom))
                    
                    distance_x = self.position.x - closest_x
                    distance_y = self.position.y - closest_y
                    distance_sq = distance_x**2 + distance_y**2
                    
                    if distance_sq < self.radius**2:
                        if distance_sq < 0.0001:
                            angle = random.uniform(0, 2 * math.pi)
                            self.position.x = closest_x + math.cos(angle) * self.radius
                            self.position.y = closest_y + math.sin(angle) * self.radius
                        else:
                            distance = math.sqrt(distance_sq)
                            penetration = self.radius - distance
                            
                            nx = distance_x / distance
                            ny = distance_y / distance
                            
                            self.position.x = closest_x + nx * self.radius
                            self.position.y = closest_y + ny * self.radius
                            
                            normal = Vector2D(nx, ny)
                            dot_product = self.velocity.x * normal.x + self.velocity.y * normal.y
                            self.velocity.x -= (1 + RESTITUTION) * dot_product * normal.x
                            self.velocity.y -= (1 + RESTITUTION) * dot_product * normal.y
                            
                            tangent = Vector2D(-normal.y, normal.x)
                            dot_product = self.velocity.x * tangent.x + self.velocity.y * tangent.y
                            self.velocity.x -= FRICTION * dot_product * tangent.x
                            self.velocity.y -= FRICTION * dot_product * tangent.y
                            
            elif obj.object_type == OBJ_CIRCLE:
                dx = self.position.x - obj.center_x
                dy = self.position.y - obj.center_y
                distance_sq = dx**2 + dy**2
                
                sum_radii = self.radius + obj.radius
                
                if distance_sq < sum_radii**2:
                    if distance_sq < 0.0001:
                        angle = random.uniform(0, 2 * math.pi)
                        self.position.x = obj.center_x + math.cos(angle) * sum_radii
                        self.position.y = obj.center_y + math.sin(angle) * sum_radii
                    else:
                        distance = math.sqrt(distance_sq)
                        penetration = sum_radii - distance
                        
                        nx = dx / distance
                        ny = dy / distance
                        
                        self.position.x = obj.center_x + nx * sum_radii
                        self.position.y = obj.center_y + ny * sum_radii
                        
                        normal = Vector2D(nx, ny)
                        dot_product = self.velocity.x * normal.x + self.velocity.y * normal.y
                        self.velocity.x -= (1 + RESTITUTION) * dot_product * normal.x
                        self.velocity.y -= (1 + RESTITUTION) * dot_product * normal.y
                        
                        tangent = Vector2D(-normal.y, normal.x)
                        dot_product = self.velocity.x * tangent.x + self.velocity.y * tangent.y
                        self.velocity.x -= FRICTION * dot_product * tangent.x
                        self.velocity.y -= FRICTION * dot_product * tangent.y
                        
            elif obj.object_type == OBJ_POLYGON:
                if obj.contains_point(self.position.x, self.position.y):
                    edge_distances = []
                    for i in range(len(obj.points)):
                        p1 = obj.points[i]
                        p2 = obj.points[(i + 1) % len(obj.points)]
                        
                        line_vec = Vector2D(p2[0] - p1[0], p2[1] - p1[1])
                        point_vec = Vector2D(self.position.x - p1[0], self.position.y - p1[1])
                        
                        line_length = line_vec.length()
                        if line_length < 0.0001:
                            continue
                            
                        t = max(0, min(1, point_vec.dot(line_vec) / line_vec.length_squared()))
                        projection = Vector2D(p1[0], p1[1]) + line_vec * t
                        
                        dist_vec = Vector2D(self.position.x - projection.x, self.position.y - projection.y)
                        distance = dist_vec.length()
                        
                        edge_distances.append((distance, dist_vec.normalize(), projection))
                    
                    if edge_distances:
                        closest = min(edge_distances, key=lambda x: x[0])
                        distance, normal, projection = closest
                        
                        penetration = self.radius + distance
                        self.position.x = projection.x + normal.x * penetration
                        self.position.y = projection.y + normal.y * penetration
                        
                        dot_product = self.velocity.x * normal.x + self.velocity.y * normal.y
                        self.velocity.x -= (1 + RESTITUTION) * dot_product * normal.x
                        self.velocity.y -= (1 + RESTITUTION) * dot_product * normal.y
                        
                        tangent = Vector2D(-normal.y, normal.x)
                        dot_product = self.velocity.x * tangent.x + self.velocity.y * tangent.y
                        self.velocity.x -= FRICTION * dot_product * tangent.x
                        self.velocity.y -= FRICTION * dot_product * tangent.y
    
    def draw(self, screen):
        if self.max_trail_length > 0 and len(self.trail) > 1:
            for i in range(1, len(self.trail)):
                alpha = int(255 * (i / len(self.trail)))
                trail_color = (self.color[0], self.color[1], self.color[2], alpha)
                trail_radius = self.radius * (i / len(self.trail))
                pygame.draw.circle(screen, trail_color, self.trail[i], max(1, int(trail_radius)))
                
        pygame.draw.circle(screen, self.color, self.position.to_tuple(), self.radius)

class BasicParticle(Particle):
    def __init__(self, x, y, color=None):
        super().__init__(x, y, color)
        self.collision_cooldown = 0
        self.force_scale = 0.8
        
    def update(self, dt, objects, particles=None):
        self.apply_force(Vector2D(0, GRAVITY * self.mass) * self.force_scale)
        
        if self.collision_cooldown > 0:
            self.collision_cooldown -= dt
        
        if particles is not None:
            self.handle_particle_collisions(particles, dt)
        
        super().update(dt, objects)
        
        self.handle_boundary_collision(WIDTH, HEIGHT)
        self.handle_object_collision(objects)
        
        velocity_length = self.velocity.length()
        max_velocity = 80.0
        if velocity_length > max_velocity:
            self.velocity = self.velocity * (max_velocity / velocity_length)
            
        if velocity_length < 5.0 and random.random() < 0.02:
            jitter = Vector2D(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3))
            self.velocity = self.velocity + jitter
    
    def handle_particle_collisions(self, particles, dt):
        if self.collision_cooldown > 0:
            return
            
        for other in particles:
            if other is self:
                continue
                
            if other.collision_cooldown > 0:
                continue
                
            displacement = self.position - other.position
            distance_squared = displacement.length_squared()
            
            min_distance = self.radius + other.radius
            
            if distance_squared < min_distance * min_distance and distance_squared > 0.0001:
                distance = math.sqrt(distance_squared)
                
                normal = displacement / distance
                
                penetration = min_distance - distance
                
                correction = normal * (penetration * 0.5)
                self.position = self.position + correction
                other.position = other.position - correction
                
                relative_velocity = self.velocity - other.velocity
                
                velocity_along_normal = relative_velocity.dot(normal)
                
                if velocity_along_normal < 0:
                    restitution = 0.3
                    
                    impulse_scalar = -(1 + restitution) * velocity_along_normal / 2
                    
                    impulse = normal * impulse_scalar
                    self.velocity = self.velocity + impulse
                    other.velocity = other.velocity - impulse
                    
                    cohesion = 0.2
                    lateral_force = Vector2D(-normal.y, normal.x) * (relative_velocity.dot(Vector2D(-normal.y, normal.x)) * cohesion)
                    
                    self.velocity = self.velocity - lateral_force
                    other.velocity = other.velocity + lateral_force
                
                self.collision_cooldown = dt * 0.5
                other.collision_cooldown = dt * 0.5

class GridSimulation:
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.grid = np.zeros((self.height, self.width), dtype=np.int8)
        self.water_levels = np.zeros((self.height, self.width), dtype=np.float32)
        self.velocity_x = np.zeros((self.height, self.width), dtype=np.float32)
        self.velocity_y = np.zeros((self.height, self.width), dtype=np.float32)
        self.pressure = np.zeros((self.height, self.width), dtype=np.float32)
        self.update_count = 0
        
        self.active_cells = set()
        self.prev_water_positions = set()
        
    def add_water(self, x, y, amount=1.0):
        grid_x, grid_y = int(x // CELL_SIZE), int(y // CELL_SIZE)
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            if self.grid[grid_y, grid_x] == EMPTY:
                self.grid[grid_y, grid_x] = WATER
                self.water_levels[grid_y, grid_x] = min(1.0, self.water_levels[grid_y, grid_x] + amount)
                self.active_cells.add((grid_x, grid_y))
                
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = grid_x + dx, grid_y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            self.active_cells.add((nx, ny))
                
    def add_solid(self, x, y):
        grid_x, grid_y = int(x // CELL_SIZE), int(y // CELL_SIZE)
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.grid[grid_y, grid_x] = SOLID
            self.water_levels[grid_y, grid_x] = 0
            
    def initialize_from_objects(self, objects):
        self.grid.fill(EMPTY)
        self.water_levels.fill(0)
        self.velocity_x.fill(0)
        self.velocity_y.fill(0)
        self.pressure.fill(0)
        self.active_cells.clear()
        self.prev_water_positions.clear()
        
        for obj in objects:
            if obj.object_type == OBJ_RECT:
                x1 = max(0, int(obj.rect.left // CELL_SIZE))
                x2 = min(self.width, int(obj.rect.right // CELL_SIZE) + 1)
                y1 = max(0, int(obj.rect.top // CELL_SIZE))
                y2 = min(self.height, int(obj.rect.bottom // CELL_SIZE) + 1)
                
                self.grid[y1:y2, x1:x2] = SOLID
                
            elif obj.object_type == OBJ_CIRCLE:
                center_x = int(obj.center_x // CELL_SIZE)
                center_y = int(obj.center_y // CELL_SIZE)
                radius_cells = int(obj.radius // CELL_SIZE) + 1
                
                y_range = np.arange(max(0, center_y - radius_cells), min(self.height, center_y + radius_cells + 1))
                x_range = np.arange(max(0, center_x - radius_cells), min(self.width, center_x + radius_cells + 1))
                y_coords, x_coords = np.meshgrid(y_range, x_range, indexing='ij')
                
                dx = (x_coords * CELL_SIZE + CELL_SIZE/2) - obj.center_x
                dy = (y_coords * CELL_SIZE + CELL_SIZE/2) - obj.center_y
                distances_sq = dx*dx + dy*dy
                
                mask = distances_sq <= (obj.radius * obj.radius)
                self.grid[y_coords[mask], x_coords[mask]] = SOLID
                            
            elif obj.object_type == OBJ_POLYGON:
                for y in range(self.height):
                    for x in range(self.width):
                        cell_center_x = x * CELL_SIZE + CELL_SIZE/2
                        cell_center_y = y * CELL_SIZE + CELL_SIZE/2
                        if obj.contains_point(cell_center_x, cell_center_y):
                            self.grid[y, x] = SOLID
    
    def update(self, dt):
        self.update_count += 1
        
        new_grid = self.grid.copy()
        new_water_levels = self.water_levels.copy()
        
        current_water_positions = set()
        newly_active_cells = set()
        
        sorted_cells = sorted(self.active_cells, key=lambda pos: (pos[1], -pos[0]))
        water_changed = False
        
        for x, y in sorted_cells:
            if y >= self.height - 1:
                continue
                
            if self.grid[y, x] == WATER and self.water_levels[y, x] > 0:
                current_water_positions.add((x, y))
                water_moved = self._process_water_cell(x, y, new_grid, new_water_levels, newly_active_cells)
                water_changed = water_changed or water_moved
        
        self.active_cells.update(newly_active_cells)
        
        if not water_changed and self.update_count % 5 == 0:
            unchanged_cells = self.prev_water_positions.intersection(current_water_positions)
            if len(unchanged_cells) > 0.9 * len(current_water_positions) and len(current_water_positions) > 10:
                for x, y in list(self.active_cells):
                    if (x, y) not in current_water_positions:
                        has_water_neighbor = False
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) in current_water_positions:
                                    has_water_neighbor = True
                                    break
                        
                        if not has_water_neighbor:
                            self.active_cells.remove((x, y))
        
        np.copyto(self.grid, new_grid)
        np.copyto(self.water_levels, new_water_levels)
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] == WATER:
                    if self.water_levels[y, x] <= 0.01:
                        self.grid[y, x] = EMPTY
                        self.water_levels[y, x] = 0
                        if (x, y) in self.active_cells:
                            self.active_cells.remove((x, y))
                    elif self.water_levels[y, x] > 1.0:
                        self.water_levels[y, x] = 1.0
        
        if len(current_water_positions) > 0 and len(current_water_positions) < 100 and self.update_count % 10 == 0:
            current_water_list = list(current_water_positions)
            random_cells = random.sample(current_water_list, min(5, len(current_water_list)))
            for x, y in random_cells:
                self.water_levels[y, x] = min(1.0, max(0.01, 
                                            self.water_levels[y, x] + np.random.uniform(-0.02, 0.02)))
                
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            self.active_cells.add((nx, ny))
        
        self.prev_water_positions = current_water_positions
    
    def _process_water_cell(self, x, y, new_grid, new_water_levels, newly_active_cells):
        current_water = self.water_levels[y, x]
        if current_water <= 0:
            return False
            
        remaining_water = current_water
        water_moved = False
        
        if y < self.height - 1:
            if self.grid[y + 1, x] == EMPTY:
                flow_amount = remaining_water
                new_grid[y + 1, x] = WATER
                new_water_levels[y + 1, x] += flow_amount
                new_water_levels[y, x] = 0
                
                newly_active_cells.add((x, y+1))
                for dx in [-1, 0, 1]:
                    nx = x + dx
                    if 0 <= nx < self.width:
                        newly_active_cells.add((nx, y+1))
                        
                return True
                
            elif self.grid[y + 1, x] == WATER and self.water_levels[y + 1, x] < 1.0:
                available_space = 1.0 - self.water_levels[y + 1, x]
                flow_rate = min(available_space, remaining_water)
                flow_amount = min(flow_rate, 0.8 * remaining_water)
                
                new_water_levels[y + 1, x] += flow_amount
                remaining_water -= flow_amount
                water_moved = flow_amount > 0.001
                
                newly_active_cells.add((x, y+1))
                
                if remaining_water <= 0:
                    new_water_levels[y, x] = 0
                    return water_moved
        
        can_flow_left = x > 0 and self.grid[y, x - 1] != SOLID
        can_flow_right = x < self.width - 1 and self.grid[y, x + 1] != SOLID
        
        horizontal_flow = False
        
        if can_flow_left and can_flow_right:
            left_water = self.water_levels[y, x - 1] if self.grid[y, x - 1] == WATER else 0
            right_water = self.water_levels[y, x + 1] if self.grid[y, x + 1] == WATER else 0
            
            if abs(left_water - remaining_water) > 0.05 or abs(right_water - remaining_water) > 0.05:
                total_water = remaining_water + left_water + right_water
                avg_water = total_water / 3.0
                
                flow_to_left = max(0, avg_water - left_water)
                if flow_to_left > 0.001:
                    new_grid[y, x - 1] = WATER
                    new_water_levels[y, x - 1] = min(1.0, left_water + flow_to_left * 0.8)
                    remaining_water -= flow_to_left * 0.8
                    water_moved = True
                    horizontal_flow = True
                    newly_active_cells.add((x-1, y))
                
                flow_to_right = max(0, avg_water - right_water)
                if flow_to_right > 0.001:
                    new_grid[y, x + 1] = WATER
                    new_water_levels[y, x + 1] = min(1.0, right_water + flow_to_right * 0.8)
                    remaining_water -= flow_to_right * 0.8
                    water_moved = True
                    horizontal_flow = True
                    newly_active_cells.add((x+1, y))
                    
        elif can_flow_left:
            left_water = self.water_levels[y, x - 1] if self.grid[y, x - 1] == WATER else 0
            
            if remaining_water - left_water > 0.05:
                avg_water = (remaining_water + left_water) / 2.0
                flow_amount = (avg_water - left_water) * 0.6
                
                if flow_amount > 0.001:
                    new_grid[y, x - 1] = WATER
                    new_water_levels[y, x - 1] = min(1.0, left_water + flow_amount)
                    remaining_water -= flow_amount
                    water_moved = True
                    horizontal_flow = True
                    newly_active_cells.add((x-1, y))
                
        elif can_flow_right:
            right_water = self.water_levels[y, x + 1] if self.grid[y, x + 1] == WATER else 0
            
            if remaining_water - right_water > 0.05:
                avg_water = (remaining_water + right_water) / 2.0
                flow_amount = (avg_water - right_water) * 0.6
                
                if flow_amount > 0.001:
                    new_grid[y, x + 1] = WATER
                    new_water_levels[y, x + 1] = min(1.0, right_water + flow_amount)
                    remaining_water -= flow_amount
                    water_moved = True
                    horizontal_flow = True
                    newly_active_cells.add((x+1, y))
        
        if horizontal_flow and y > 0:
            if self.grid[y-1, x] == WATER:
                newly_active_cells.add((x, y-1))
        
        new_water_levels[y, x] = max(0, remaining_water)
        if remaining_water <= 0:
            new_grid[y, x] = EMPTY
            
        return water_moved
    
    def draw(self, screen):
        water_cells = []
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] == WATER:
                    screen_x = x * CELL_SIZE
                    screen_y = y * CELL_SIZE
                    
                    water_level = self.water_levels[y, x]
                    r = max(0, min(255, WATER_COLOR[0] - int(40 * water_level)))
                    g = max(0, min(255, WATER_COLOR[1] - int(20 * water_level)))
                    b = max(0, min(255, WATER_COLOR[2] + int(20 * water_level)))
                    color = (r, g, b)
                    
                    water_cells.append((pygame.Rect(screen_x, screen_y, CELL_SIZE, CELL_SIZE), color))
        
        for rect, color in water_cells:
            pygame.draw.rect(screen, color, rect)
            
            outline_r = max(0, min(255, color[0]-10))
            outline_g = max(0, min(255, color[1]-10))
            outline_b = max(0, min(255, color[2]+10))
            pygame.draw.rect(screen, (outline_r, outline_g, outline_b), rect, 1)

class SPHParticle(Particle):
    def __init__(self, x, y, color=None):
        super().__init__(x, y, color)
        self.density = 0
        self.pressure = 0
        self.neighbors = []
        self.restitution = 0.3
        self.max_velocity = 100.0
        self.cell_x = 0
        self.cell_y = 0
        self.last_density_calc_time = 0
        
    def calculate_density_and_pressure(self, particles):
        self.density = 0
        self.neighbors = []
        
        cell_size = SMOOTHING_LENGTH
        self.cell_x = int(self.position.x / cell_size)
        self.cell_y = int(self.position.y / cell_size)
        
        for particle in particles:
            if particle is self:
                continue
                
            dx = abs(self.position.x - particle.position.x)
            dy = abs(self.position.y - particle.position.y)
            
            if dx > SMOOTHING_LENGTH or dy > SMOOTHING_LENGTH:
                continue
                
            distance_vec = self.position - particle.position
            distance_squared = distance_vec.length_squared()
            
            if distance_squared < SMOOTHING_LENGTH_SQ:
                self.neighbors.append(particle)
                distance = math.sqrt(distance_squared)
                if distance < 0.0001:
                    continue
                
                h2 = SMOOTHING_LENGTH_SQ
                r2 = distance_squared
                kernel_value = max(0, h2 - r2)
                kernel_value = kernel_value * kernel_value * kernel_value
                self.density += MASS * 315.0 / (64.0 * math.pi * math.pow(SMOOTHING_LENGTH, 9)) * kernel_value
        
        self.density = max(1.0, self.density + 0.000001)
        
        self.pressure = GAS_CONSTANT * (self.density - REST_DENSITY)
        self.pressure = max(-1000, min(3000, self.pressure))
    
    def calculate_forces(self, particles):
        self.reset_forces()
        
        self.apply_force(Vector2D(0, GRAVITY * self.mass))
        
        pressure_force = Vector2D(0, 0)
        viscosity_force = Vector2D(0, 0)
        surface_tension_force = Vector2D(0, 0)
        cohesion_force = Vector2D(0, 0)
        
        center_of_mass = Vector2D(0, 0)
        total_mass = 0
        
        for neighbor in self.neighbors:
            if neighbor is self:
                continue
                
            direction = self.position - neighbor.position
            distance = direction.length()
            
            if distance < 0.0001:
                continue
                
            direction = direction / distance
            
            h_minus_r = SMOOTHING_LENGTH - distance
            pressure_magnitude = -MASS * (self.pressure + neighbor.pressure) / (2 * neighbor.density) 
            pressure_magnitude *= (45.0 / (math.pi * math.pow(SMOOTHING_LENGTH, 6))) * math.pow(h_minus_r, 2)
            
            scale_factor = 0.5 * (1.0 + 0.5 * min(1.0, len(self.neighbors) / 20.0))
            pressure_magnitude *= scale_factor
            
            pressure_force = pressure_force + direction * pressure_magnitude
            
            relative_velocity = neighbor.velocity - self.velocity
            viscosity_magnitude = VISCOSITY_STRENGTH * MASS * h_minus_r / neighbor.density
            viscosity_magnitude *= (45.0 / (math.pi * math.pow(SMOOTHING_LENGTH, 6)))
            viscosity_force = viscosity_force + relative_velocity * viscosity_magnitude
            
            surface_kernel = 1.0 - distance / SMOOTHING_LENGTH
            surface_kernel = surface_kernel * surface_kernel * surface_kernel
            surface_tension_force = surface_tension_force + direction * (SURFACE_TENSION * surface_kernel * 0.5)
            
            center_of_mass = center_of_mass + neighbor.position
            total_mass += 1
            
        if total_mass > 0:
            center_of_mass = center_of_mass / total_mass
            cohesion_direction = center_of_mass - self.position
            cohesion_distance = cohesion_direction.length()
            if cohesion_distance > 0.0001:
                cohesion_direction = cohesion_direction / cohesion_distance
                cohesion_strength = 3.0 * max(0, 1.0 - len(self.neighbors) / 30.0)
                cohesion_force = cohesion_direction * cohesion_strength
        
        self.apply_force(Vector2D(
            max(-500, min(500, pressure_force.x)),
            max(-500, min(500, pressure_force.y))
        ))
        self.apply_force(viscosity_force)
        self.apply_force(surface_tension_force)
        self.apply_force(cohesion_force)
    
    def update(self, dt, objects):
        capped_dt = min(dt, 0.016)
        
        super().update(capped_dt, objects)
        
        velocity_length = self.velocity.length()
        if velocity_length > self.max_velocity:
            self.velocity = self.velocity * (self.max_velocity / velocity_length)
        
        if velocity_length < 2.0 and random.random() < 0.05:
            jitter = Vector2D(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
            self.velocity = self.velocity + jitter
        
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
        
        self.handle_object_collision(objects)