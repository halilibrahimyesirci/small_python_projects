"""
Project: Advanced Water Simulation
Description: Main program file
"""

import pygame
import sys
import random
import time
from constants import *
from physics import BasicParticle, SPHParticle, GridSimulation
from objects import get_scene_objects

class Button:
    """Button for UI interactions"""
    def __init__(self, x, y, width, height, text, callback, font_size=FONT_SIZE_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font_size = font_size
        self.hovered = False
        
    def draw(self, surface, font):
        # Draw button background
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, UI_COLOR, self.rect, 2)  # Border
        
        # Draw text
        text_surf = font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, mouse_pos):
        """Check if mouse is hovering over button and update state"""
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered
        
    def handle_event(self, event):
        """Handle mouse events for this button"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.callback()
                return True
        return False


class Slider:
    """Slider UI element for adjusting values"""
    def __init__(self, x, y, width, height, min_value, max_value, current_value, label, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_width = 12
        self.handle_rect = pygame.Rect(0, y, self.handle_width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = current_value
        self.label = label
        self.callback = callback
        self.active = False
        self.discrete_mode = False  # For integer-only values
        self.update_handle_position()
        
    def update_handle_position(self):
        """Update handle position based on current value"""
        normalized_value = (self.value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.rect.x + int(normalized_value * (self.rect.width - self.handle_width))
        self.handle_rect.x = handle_x
    
    def update_value_from_position(self, mouse_x):
        """Update value based on handle position"""
        relative_x = max(0, min(mouse_x - self.rect.x, self.rect.width - self.handle_width))
        normalized_value = relative_x / (self.rect.width - self.handle_width)
        new_value = self.min_value + normalized_value * (self.max_value - self.min_value)
        
        # For discrete (integer) values, round to nearest integer
        if self.discrete_mode:
            new_value = round(new_value)
        
        # Ensure the value is valid and within range
        self.value = max(self.min_value, min(self.max_value, new_value))
        self.update_handle_position()
        
        if self.callback:
            self.callback(self.value)
    
    def handle_event(self, event):
        """Handle mouse events for the slider"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.active = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active:
                self.active = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.active:
                self.update_value_from_position(event.pos[0])
                return True
        return False
    
    def draw(self, surface, font):
        # Draw slider background
        pygame.draw.rect(surface, BUTTON_COLOR, self.rect)
        pygame.draw.rect(surface, UI_COLOR, self.rect, 1)
        
        # Draw handle
        pygame.draw.rect(surface, BUTTON_HOVER_COLOR if self.active else UI_COLOR, self.handle_rect)
        
        # Draw label and value
        value_text = f"{self.label}: {self.value:.2f}" if isinstance(self.value, float) else f"{self.label}: {self.value}"
        text_surf = font.render(value_text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + self.rect.width + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)


class WaterSimulation:
    """Main water simulation class"""
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Create window and set caption
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        
        # Create clock for timing
        self.clock = pygame.time.Clock()
        
        # Create fonts
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        
        # Initialize state variables
        self.state = STATE_MENU
        self.sim_type = None
        self.scene_name = SCENE_BUCKET
        
        # Particles and objects
        self.particles = []
        self.objects = []
        
        # Grid simulation
        self.grid_sim = GridSimulation()
        
        # Mouse state for continuous water addition
        self.mouse_down = False
        self.last_water_add_time = 0
        self.water_add_delay = 0.05  # seconds between water spawns
        
        # Statistics
        self.particle_count = 0
        self.fps = 0
        
        # Menu buttons
        self.create_menu_buttons()
        
        # Settings
        self.particle_size = PARTICLE_RADIUS  # For UI adjustment
        self.water_release_rate = 10  # Particles per click/hold interval
        self.sim_speed = 1.0  # Simulation speed multiplier
        
        # Debug mode
        self.debug_mode = False
        
        # Initialize simulation buttons and sliders
        self.simulation_buttons = []
        self.simulation_sliders = []
        self.show_settings_panel = False
        
    def create_menu_buttons(self):
        """Create buttons for the main menu"""
        self.menu_buttons = []
        
        # Simulation type buttons
        button_width = 200
        button_height = 50
        button_margin = 20
        button_x = WIDTH // 2 - button_width // 2
        button_y = HEIGHT // 4
        
        # Particle simulation button
        self.menu_buttons.append(Button(
            button_x, button_y, 
            button_width, button_height, 
            "Particle Simulation", 
            lambda: self.start_simulation(SIM_PARTICLE)
        ))
        
        # SPH simulation button
        button_y += button_height + button_margin
        self.menu_buttons.append(Button(
            button_x, button_y, 
            button_width, button_height, 
            "Fluid Simulation (SPH)", 
            lambda: self.start_simulation(SIM_SPH)
        ))
        
        # Grid simulation button
        button_y += button_height + button_margin
        self.menu_buttons.append(Button(
            button_x, button_y, 
            button_width, button_height, 
            "Grid Simulation", 
            lambda: self.start_simulation(SIM_GRID)
        ))
        
        # Scene selection buttons
        button_y += button_height + button_margin * 2
        scene_button_width = 150
        scene_button_height = 40
        scene_button_x = WIDTH // 2 - (scene_button_width * 3 + button_margin * 2) // 2
        
        # First row of scene buttons
        self.menu_buttons.append(Button(
            scene_button_x, button_y,
            scene_button_width, scene_button_height,
            "Bucket", 
            lambda: self.set_scene(SCENE_BUCKET)
        ))
        
        scene_button_x += scene_button_width + button_margin
        self.menu_buttons.append(Button(
            scene_button_x, button_y,
            scene_button_width, scene_button_height,
            "Pool", 
            lambda: self.set_scene(SCENE_POOL)
        ))
        
        scene_button_x += scene_button_width + button_margin
        self.menu_buttons.append(Button(
            scene_button_x, button_y,
            scene_button_width, scene_button_height,
            "Waterfall", 
            lambda: self.set_scene(SCENE_WATERFALL)
        ))
        
        # Second row of scene buttons
        button_y += scene_button_height + button_margin
        scene_button_x = WIDTH // 2 - (scene_button_width * 3 + button_margin * 2) // 2
        
        self.menu_buttons.append(Button(
            scene_button_x, button_y,
            scene_button_width, scene_button_height,
            "Maze", 
            lambda: self.set_scene(SCENE_MAZE)
        ))
        
        scene_button_x += scene_button_width + button_margin
        self.menu_buttons.append(Button(
            scene_button_x, button_y,
            scene_button_width, scene_button_height,
            "Fountain", 
            lambda: self.set_scene(SCENE_FOUNTAIN)
        ))
        
        scene_button_x += scene_button_width + button_margin
        self.menu_buttons.append(Button(
            scene_button_x, button_y,
            scene_button_width, scene_button_height,
            "Empty", 
            lambda: self.set_scene(SCENE_EMPTY)
        ))
        
    def create_simulation_buttons(self):
        """Create buttons for the simulation interface"""
        self.simulation_buttons = []
        self.simulation_sliders = []
        
        # Button dimensions
        button_width = 100
        button_height = 30
        button_margin = 10
        button_x = 10
        button_y = 10
        
        # Menu button
        self.simulation_buttons.append(Button(
            button_x, button_y,
            button_width, button_height,
            "Menu",
            self.return_to_menu
        ))
        
        # Reset button
        button_x += button_width + button_margin
        self.simulation_buttons.append(Button(
            button_x, button_y,
            button_width, button_height,
            "Reset",
            self.reset_simulation
        ))
        
        # Debug toggle button
        button_x += button_width + button_margin
        self.simulation_buttons.append(Button(
            button_x, button_y,
            button_width, button_height,
            "Debug: Off",
            self.toggle_debug_mode
        ))
        
        # Settings button (opens/closes settings panel)
        button_x += button_width + button_margin
        self.simulation_buttons.append(Button(
            button_x, button_y,
            button_width, button_height,
            "Settings",
            self.toggle_settings_panel
        ))
        
        # Create sliders for settings
        self.create_settings_sliders()
        
    def create_settings_sliders(self):
        """Create sliders for simulation settings"""
        slider_width = 150
        slider_height = 20
        slider_margin = 10
        slider_x = WIDTH - slider_width - 200
        slider_y = 60  # Start below the top UI panel
        
        # Simulation speed slider
        self.simulation_sliders.append(Slider(
            slider_x, slider_y,
            slider_width, slider_height,
            0.2, 3.0, self.sim_speed,
            "Speed",
            self.set_simulation_speed
        ))
        
        # Particle count / water rate slider
        slider_y += slider_height + slider_margin
        self.simulation_sliders.append(Slider(
            slider_x, slider_y,
            slider_width, slider_height,
            1, 50, self.water_release_rate,
            "Water Amount",
            self.set_water_release_rate
         ))
        self.simulation_sliders[-1].discrete_mode = True  # Enable discrete mode
        
        # Particle size slider (affects visual size)
        slider_y += slider_height + slider_margin
        self.simulation_sliders.append(Slider(
            slider_x, slider_y,
            slider_width, slider_height,
            1.0, 10.0, self.particle_size,
            "Particle Size",
            self.set_particle_size
        ))
        
        # Initialize settings panel visibility
        self.show_settings_panel = False
        
    def toggle_settings_panel(self):
        """Toggle settings panel visibility"""
        self.show_settings_panel = not self.show_settings_panel
        
    def set_simulation_speed(self, value):
        """Set simulation speed multiplier"""
        self.sim_speed = value
        
    def set_water_release_rate(self, value):
        """Set number of particles to release per click/interval"""
        self.water_release_rate = int(value)
        
    def set_particle_size(self, value):
        """Set visual size of particles"""
        self.particle_size = value
        # Update existing particle sizes
        for particle in self.particles:
            particle.radius = value
        
    def set_scene(self, scene_name):
        """Set the current scene"""
        self.scene_name = scene_name
        # Set some UI feedback for the selected scene
    
    def start_simulation(self, sim_type):
        """Start the simulation with the selected type"""
        self.sim_type = sim_type
        self.state = STATE_SIMULATION
        
        # Clear existing particles
        self.particles.clear()
        
        # Load objects for the selected scene
        self.objects = get_scene_objects(self.scene_name)
        
        # Create simulation UI buttons
        self.create_simulation_buttons()
        
        # Initialize grid if needed
        if self.sim_type == SIM_GRID:
            self.grid_sim = GridSimulation()
            self.grid_sim.initialize_from_objects(self.objects)
    
    def return_to_menu(self):
        """Return to the main menu"""
        self.state = STATE_MENU
        self.particles.clear()
    
    def reset_simulation(self):
        """Reset the current simulation"""
        self.particles.clear()
        
        if self.sim_type == SIM_GRID:
            self.grid_sim = GridSimulation()
            self.grid_sim.initialize_from_objects(self.objects)
    
    def toggle_debug_mode(self):
        """Toggle debug visualization mode"""
        self.debug_mode = not self.debug_mode
        
        # Update button text
        for button in self.simulation_buttons:
            if button.text.startswith("Debug:"):
                button.text = "Debug: On" if self.debug_mode else "Debug: Off"
    
    def add_water(self, x, y):
        """Add water at the specified position"""
        # Don't add water if settings panel is open and mouse is over it
        if self.show_settings_panel:
            # Calculate settings panel area
            panel_width = 400
            panel_height = len(self.simulation_sliders) * 30 + 50
            panel_x = WIDTH - panel_width - 20
            panel_y = 50
            
            # Create a rect for the settings panel
            settings_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            
            # If mouse position is inside the settings panel, don't add water
            if settings_panel_rect.collidepoint(x, y):
                return
        
        # Normal water addition logic
        if time.time() - self.last_water_add_time < self.water_add_delay:
            return
                
        self.last_water_add_time = time.time()
        
        if self.sim_type == SIM_PARTICLE:
            # Add a burst of simple particles
            for _ in range(self.water_release_rate):
                offset_x = random.uniform(-10, 10)
                offset_y = random.uniform(-10, 10)
                self.particles.append(BasicParticle(x + offset_x, y + offset_y))
                
        elif self.sim_type == SIM_SPH:
            # Add a burst of SPH particles
            for _ in range(self.water_release_rate):
                offset_x = random.uniform(-10, 10)
                offset_y = random.uniform(-10, 10)
                self.particles.append(SPHParticle(x + offset_x, y + offset_y))
                
        elif self.sim_type == SIM_GRID:
            # Add water to grid
            self.grid_sim.add_water(x, y)
    
    def update(self, dt):
        """Update simulation state"""
        # Calculate actual simulation time step with speed adjustment
        sim_dt = dt * self.sim_speed
        
        if self.state == STATE_MENU:
            # No updates needed for menu
            pass
            
        elif self.state == STATE_SIMULATION:
            # Handle continuous water addition if mouse is held down
            if self.mouse_down:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.add_water(mouse_x, mouse_y)
            
            # Update simulation based on type
            if self.sim_type == SIM_PARTICLE or self.sim_type == SIM_SPH:
                # Limit the number of particles for performance
                self.particle_count = len(self.particles)
                
                if self.sim_type == SIM_SPH:
                    # SPH density and pressure calculation
                    for particle in self.particles:
                        particle.calculate_density_and_pressure(self.particles)
                    
                    # SPH force calculation
                    for particle in self.particles:
                        particle.calculate_forces(self.particles)
                
                # Update all particles
                for particle in self.particles:
                    if self.sim_type == SIM_PARTICLE:
                        # For basic particles, pass the full particle list for collision detection
                        particle.update(sim_dt, self.objects, self.particles)
                    else:
                        # SPH particles handle interactions differently
                        particle.update(sim_dt, self.objects)
                
            elif self.sim_type == SIM_GRID:
                # Update grid simulation
                for _ in range(3):  # Multiple updates per frame for smoother flow
                    self.grid_sim.update(sim_dt / 3)
    
    def draw(self):
        """Draw the current state"""
        # Clear the screen
        self.screen.fill(BG_COLOR)
        
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_SIMULATION:
            self.draw_simulation()
            
        # Update display
        pygame.display.flip()
    
    def draw_menu(self):
        """Draw the main menu"""
        # Draw title
        title_text = self.font_large.render("Advanced Water Simulation", True, UI_COLOR)
        title_rect = title_text.get_rect(centerx=WIDTH//2, y=50)
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle with currently selected scene
        scene_text = self.font_medium.render(f"Selected Scene: {self.scene_name.title()}", True, UI_COLOR)
        scene_rect = scene_text.get_rect(centerx=WIDTH//2, y=100)
        self.screen.blit(scene_text, scene_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.menu_buttons:
            button.check_hover(mouse_pos)
            button.draw(self.screen, self.font_medium)
        
        # Draw instructions
        instructions = [
            "Click to add water",
            "Hold mouse to continuously add water",
            "Press ESC to return to this menu",
            "Press R to reset the simulation"
        ]
        
        y = HEIGHT - 120
        for instruction in instructions:
            text = self.font_small.render(instruction, True, UI_COLOR)
            rect = text.get_rect(centerx=WIDTH//2, y=y)
            self.screen.blit(text, rect)
            y += 30
    
    def draw_simulation(self):
        """Draw the simulation"""
        # Draw simulation objects
        for obj in self.objects:
            obj.draw(self.screen)
        
        # Draw water based on simulation type
        if self.sim_type == SIM_PARTICLE or self.sim_type == SIM_SPH:
            for particle in self.particles:
                particle.draw(self.screen)
                
        elif self.sim_type == SIM_GRID:
            self.grid_sim.draw(self.screen)
        
        # Draw UI panel
        panel_height = 40
        panel_surface = pygame.Surface((WIDTH, panel_height), pygame.SRCALPHA)
        panel_surface.fill(UI_BG_COLOR)
        self.screen.blit(panel_surface, (0, 0))
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.simulation_buttons:
            button.check_hover(mouse_pos)
            button.draw(self.screen, self.font_small)
        
        # Draw settings panel if visible
        if self.show_settings_panel:
            # Panel background
            panel_width = 400
            panel_height = len(self.simulation_sliders) * 30 + 50
            panel_x = WIDTH - panel_width - 20
            panel_y = 50
            
            settings_panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            settings_panel.fill((30, 30, 40, 220))  # Semi-transparent panel
            self.screen.blit(settings_panel, (panel_x, panel_y))
            
            # Panel title
            title_text = self.font_medium.render("Settings", True, UI_COLOR)
            title_rect = title_text.get_rect(midtop=(panel_x + panel_width//2, panel_y + 10))
            self.screen.blit(title_text, title_rect)
            
            # Draw sliders
            y_offset = 50
            for slider in self.simulation_sliders:
                slider.draw(self.screen, self.font_small)
        
        # Draw stats
        stats_text = f"FPS: {int(self.fps)}"
        if self.sim_type == SIM_PARTICLE or self.sim_type == SIM_SPH:
            stats_text += f" | Particles: {self.particle_count}"
        
        stats_surface = self.font_small.render(stats_text, True, UI_COLOR)
        self.screen.blit(stats_surface, (WIDTH - stats_surface.get_width() - 10, 10))
        
        # Draw debug info if enabled
        if self.debug_mode:
            self.draw_debug_info()
    
    def draw_debug_info(self):
        """Draw debug visualization and information"""
        # Add more technical information at the bottom
        debug_info = [
            f"Simulation Type: {self.sim_type}",
            f"Scene: {self.scene_name}",
            f"Object Count: {len(self.objects)}",
            f"Sim Speed: {self.sim_speed:.2f}x"
        ]
        
        if self.sim_type == SIM_GRID:
            debug_info.append(f"Grid Size: {GRID_WIDTH}x{GRID_HEIGHT} ({CELL_SIZE}px cells)")
        
        y = HEIGHT - (len(debug_info) * 20 + 10)
        panel_height = len(debug_info) * 20 + 10
        
        # Debug panel background
        debug_panel = pygame.Surface((300, panel_height), pygame.SRCALPHA)
        debug_panel.fill((0, 0, 0, 180))
        self.screen.blit(debug_panel, (10, y))
        
        # Draw debug text
        y += 5
        for info in debug_info:
            debug_text = self.font_small.render(info, True, (200, 200, 200))
            self.screen.blit(debug_text, (20, y))
            y += 20
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_SIMULATION:
                        self.return_to_menu()
                    else:
                        return False  # Exit if in menu
                elif event.key == pygame.K_r:
                    if self.state == STATE_SIMULATION:
                        self.reset_simulation()
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.state == STATE_MENU:
                        # Check menu buttons
                        mouse_pos = pygame.mouse.get_pos()
                        for button in self.menu_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                button.callback()
                                break
                    elif self.state == STATE_SIMULATION:
                        # Check simulation buttons
                        mouse_pos = pygame.mouse.get_pos()
                        button_clicked = False
                        for button in self.simulation_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                button.callback()
                                button_clicked = True
                                break
                        
                        # Add water if not clicking on a button
                        if not button_clicked:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            self.add_water(mouse_x, mouse_y)
                            self.mouse_down = True
                        
                        # Check sliders
                        for slider in self.simulation_sliders:
                            slider.handle_event(event)
                
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.mouse_down = False
                    for slider in self.simulation_sliders:
                        slider.handle_event(event)
            
            if event.type == pygame.MOUSEMOTION:
                for slider in self.simulation_sliders:
                    slider.handle_event(event)
        
        return True
    
    def run(self):
        """Main game loop"""
        running = True
        last_time = time.time()
        
        while running:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Cap dt to avoid large jumps
            dt = min(dt, 0.05)
            
            # Calculate FPS
            self.fps = self.clock.get_fps()
            
            # Handle events
            running = self.handle_events()
            
            # Update simulation
            self.update(dt)
            
            # Draw everything
            self.draw()
            
            # Cap frame rate
            self.clock.tick(FPS)
        
        # Clean up
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    # Start the simulation
    sim = WaterSimulation()
    sim.run()