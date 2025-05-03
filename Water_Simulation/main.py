import pygame
import sys
import random
import time
from constants import *
from physics import BasicParticle, SPHParticle, GridSimulation
from objects import get_scene_objects

class Button:
    def __init__(self, x, y, width, height, text, callback, font_size=FONT_SIZE_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font_size = font_size
        self.hovered = False
        
    def draw(self, surface, font):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, UI_COLOR, self.rect, 2)
        
        text_surf = font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.callback()
                return True
        return False


class Slider:
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
        self.discrete_mode = False
        self.update_handle_position()
        
    def update_handle_position(self):
        normalized_value = (self.value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.rect.x + int(normalized_value * (self.rect.width - self.handle_width))
        self.handle_rect.x = handle_x
    
    def update_value_from_position(self, mouse_x):
        relative_x = max(0, min(mouse_x - self.rect.x, self.rect.width - self.handle_width))
        normalized_value = relative_x / (self.rect.width - self.handle_width)
        new_value = self.min_value + normalized_value * (self.max_value - self.min_value)
        
        if self.discrete_mode:
            new_value = round(new_value)
        
        self.value = max(self.min_value, min(self.max_value, new_value))
        self.update_handle_position()
        
        if self.callback:
            self.callback(self.value)
    
    def handle_event(self, event):
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
        pygame.draw.rect(surface, BUTTON_COLOR, self.rect)
        pygame.draw.rect(surface, UI_COLOR, self.rect, 1)
        
        pygame.draw.rect(surface, BUTTON_HOVER_COLOR if self.active else UI_COLOR, self.handle_rect)
        
        value_text = f"{self.label}: {self.value:.2f}" if isinstance(self.value, float) else f"{self.label}: {self.value}"
        text_surf = font.render(value_text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + self.rect.width + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)


class WaterSimulation:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        
        self.clock = pygame.time.Clock()
        
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        
        self.state = STATE_MENU
        self.sim_type = None
        self.scene_name = SCENE_BUCKET
        
        self.particles = []
        self.objects = []
        
        self.grid_sim = GridSimulation()
        
        self.mouse_down = False
        self.last_water_add_time = 0
        self.water_add_delay = 0.05
        
        self.particle_count = 0
        self.fps = 0
        
        self.create_menu_buttons()
        
        self.particle_size = PARTICLE_RADIUS
        self.water_release_rate = 10
        self.sim_speed = 1.0
        
        self.debug_mode = False
        
        self.simulation_buttons = []
        self.simulation_sliders = []
        self.show_settings_panel = False
        
    def create_menu_buttons(self):
        self.menu_buttons = []
        
        button_width = 200
        button_height = 50
        button_margin = 20
        button_x = WIDTH // 2 - button_width // 2
        button_y = HEIGHT // 4
        
        self.menu_buttons.append(Button(
            button_x, button_y, 
            button_width, button_height, 
            "Particle Simulation", 
            lambda: self.start_simulation(SIM_PARTICLE)
        ))
        
        button_y += button_height + button_margin
        self.menu_buttons.append(Button(
            button_x, button_y, 
            button_width, button_height, 
            "Fluid Simulation (SPH)", 
            lambda: self.start_simulation(SIM_SPH)
        ))
        
        button_y += button_height + button_margin
        self.menu_buttons.append(Button(
            button_x, button_y, 
            button_width, button_height, 
            "Grid Simulation", 
            lambda: self.start_simulation(SIM_GRID)
        ))
        
        button_y += button_height + button_margin * 2
        scene_button_width = 150
        scene_button_height = 40
        scene_button_x = WIDTH // 2 - (scene_button_width * 3 + button_margin * 2) // 2
        
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
        self.simulation_buttons = []
        self.simulation_sliders = []
        
        button_width = 100
        button_height = 30
        button_margin = 10
        button_x = 10
        button_y = 10
        
        self.simulation_buttons.append(Button(
            button_x, button_y,
            button_width, button_height,
            "Menu",
            self.return_to_menu
        ))
        
        button_x += button_width + button_margin
        self.simulation_buttons.append(Button(
            button_x, button_y,
            button_width, button_height,
            "Reset",
            self.reset_simulation
        ))
        
        button_x += button_width + button_margin
        self.simulation_buttons.append(Button(
            button_x, button_y,
            button_width, button_height,
            "Debug: Off",
            self.toggle_debug_mode
        ))
        
        button_x += button_width + button_margin
        self.simulation_buttons.append(Button(
            button_x, button_y,
            button_width, button_height,
            "Settings",
            self.toggle_settings_panel
        ))
        
        self.create_settings_sliders()
        
    def create_settings_sliders(self):
        slider_width = 150
        slider_height = 20
        slider_margin = 10
        slider_x = WIDTH - slider_width - 200
        slider_y = 60
        
        self.simulation_sliders.append(Slider(
            slider_x, slider_y,
            slider_width, slider_height,
            0.2, 3.0, self.sim_speed,
            "Speed",
            self.set_simulation_speed
        ))
        
        slider_y += slider_height + slider_margin
        self.simulation_sliders.append(Slider(
            slider_x, slider_y,
            slider_width, slider_height,
            1, 50, self.water_release_rate,
            "Water Amount",
            self.set_water_release_rate
         ))
        self.simulation_sliders[-1].discrete_mode = True
        
        slider_y += slider_height + slider_margin
        self.simulation_sliders.append(Slider(
            slider_x, slider_y,
            slider_width, slider_height,
            1.0, 10.0, self.particle_size,
            "Particle Size",
            self.set_particle_size
        ))
        
        self.show_settings_panel = False
        
    def toggle_settings_panel(self):
        self.show_settings_panel = not self.show_settings_panel
        
    def set_simulation_speed(self, value):
        self.sim_speed = value
        
    def set_water_release_rate(self, value):
        self.water_release_rate = int(value)
        
    def set_particle_size(self, value):
        self.particle_size = value
        for particle in self.particles:
            particle.radius = value
        
    def set_scene(self, scene_name):
        self.scene_name = scene_name
    
    def start_simulation(self, sim_type):
        self.sim_type = sim_type
        self.state = STATE_SIMULATION
        
        self.particles.clear()
        
        self.objects = get_scene_objects(self.scene_name)
        
        self.create_simulation_buttons()
        
        if self.sim_type == SIM_GRID:
            self.grid_sim = GridSimulation()
            self.grid_sim.initialize_from_objects(self.objects)
    
    def return_to_menu(self):
        self.state = STATE_MENU
        self.particles.clear()
    
    def reset_simulation(self):
        self.particles.clear()
        
        if self.sim_type == SIM_GRID:
            self.grid_sim = GridSimulation()
            self.grid_sim.initialize_from_objects(self.objects)
    
    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        
        for button in self.simulation_buttons:
            if button.text.startswith("Debug:"):
                button.text = "Debug: On" if self.debug_mode else "Debug: Off"
    
    def add_water(self, x, y):
        if self.show_settings_panel:
            panel_width = 400
            panel_height = len(self.simulation_sliders) * 30 + 50
            panel_x = WIDTH - panel_width - 20
            panel_y = 50
            
            settings_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            
            if settings_panel_rect.collidepoint(x, y):
                return
        
        if time.time() - self.last_water_add_time < self.water_add_delay:
            return
                
        self.last_water_add_time = time.time()
        
        if self.sim_type == SIM_PARTICLE:
            for _ in range(self.water_release_rate):
                offset_x = random.uniform(-10, 10)
                offset_y = random.uniform(-10, 10)
                self.particles.append(BasicParticle(x + offset_x, y + offset_y))
                
        elif self.sim_type == SIM_SPH:
            for _ in range(self.water_release_rate):
                offset_x = random.uniform(-10, 10)
                offset_y = random.uniform(-10, 10)
                self.particles.append(SPHParticle(x + offset_x, y + offset_y))
                
        elif self.sim_type == SIM_GRID:
            self.grid_sim.add_water(x, y)
    
    def update(self, dt):
        sim_dt = dt * self.sim_speed
        
        if self.state == STATE_MENU:
            pass
            
        elif self.state == STATE_SIMULATION:
            if self.mouse_down:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.add_water(mouse_x, mouse_y)
            
            if self.sim_type == SIM_PARTICLE or self.sim_type == SIM_SPH:
                self.particle_count = len(self.particles)
                
                if self.sim_type == SIM_SPH:
                    for particle in self.particles:
                        particle.calculate_density_and_pressure(self.particles)
                    
                    for particle in self.particles:
                        particle.calculate_forces(self.particles)
                
                for particle in self.particles:
                    if self.sim_type == SIM_PARTICLE:
                        particle.update(sim_dt, self.objects, self.particles)
                    else:
                        particle.update(sim_dt, self.objects)
                
            elif self.sim_type == SIM_GRID:
                for _ in range(3):
                    self.grid_sim.update(sim_dt / 3)
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_SIMULATION:
            self.draw_simulation()
            
        pygame.display.flip()
    
    def draw_menu(self):
        title_text = self.font_large.render("Advanced Water Simulation", True, UI_COLOR)
        title_rect = title_text.get_rect(centerx=WIDTH//2, y=50)
        self.screen.blit(title_text, title_rect)
        
        scene_text = self.font_medium.render(f"Selected Scene: {self.scene_name.title()}", True, UI_COLOR)
        scene_rect = scene_text.get_rect(centerx=WIDTH//2, y=100)
        self.screen.blit(scene_text, scene_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        for button in self.menu_buttons:
            button.check_hover(mouse_pos)
            button.draw(self.screen, self.font_medium)
        
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
        for obj in self.objects:
            obj.draw(self.screen)
        
        if self.sim_type == SIM_PARTICLE or self.sim_type == SIM_SPH:
            for particle in self.particles:
                particle.draw(self.screen)
                
        elif self.sim_type == SIM_GRID:
            self.grid_sim.draw(self.screen)
        
        panel_height = 40
        panel_surface = pygame.Surface((WIDTH, panel_height), pygame.SRCALPHA)
        panel_surface.fill(UI_BG_COLOR)
        self.screen.blit(panel_surface, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        for button in self.simulation_buttons:
            button.check_hover(mouse_pos)
            button.draw(self.screen, self.font_small)
        
        if self.show_settings_panel:
            panel_width = 400
            panel_height = len(self.simulation_sliders) * 30 + 50
            panel_x = WIDTH - panel_width - 20
            panel_y = 50
            
            settings_panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            settings_panel.fill((30, 30, 40, 220))
            self.screen.blit(settings_panel, (panel_x, panel_y))
            
            title_text = self.font_medium.render("Settings", True, UI_COLOR)
            title_rect = title_text.get_rect(midtop=(panel_x + panel_width//2, panel_y + 10))
            self.screen.blit(title_text, title_rect)
            
            y_offset = 50
            for slider in self.simulation_sliders:
                slider.draw(self.screen, self.font_small)
        
        stats_text = f"FPS: {int(self.fps)}"
        if self.sim_type == SIM_PARTICLE or self.sim_type == SIM_SPH:
            stats_text += f" | Particles: {self.particle_count}"
        
        stats_surface = self.font_small.render(stats_text, True, UI_COLOR)
        self.screen.blit(stats_surface, (WIDTH - stats_surface.get_width() - 10, 10))
        
        if self.debug_mode:
            self.draw_debug_info()
    
    def draw_debug_info(self):
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
        
        debug_panel = pygame.Surface((300, panel_height), pygame.SRCALPHA)
        debug_panel.fill((0, 0, 0, 180))
        self.screen.blit(debug_panel, (10, y))
        
        y += 5
        for info in debug_info:
            debug_text = self.font_small.render(info, True, (200, 200, 200))
            self.screen.blit(debug_text, (20, y))
            y += 20
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_SIMULATION:
                        self.return_to_menu()
                    else:
                        return False
                elif event.key == pygame.K_r:
                    if self.state == STATE_SIMULATION:
                        self.reset_simulation()
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.state == STATE_MENU:
                        mouse_pos = pygame.mouse.get_pos()
                        for button in self.menu_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                button.callback()
                                break
                    elif self.state == STATE_SIMULATION:
                        mouse_pos = pygame.mouse.get_pos()
                        button_clicked = False
                        for button in self.simulation_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                button.callback()
                                button_clicked = True
                                break
                        
                        if not button_clicked:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            self.add_water(mouse_x, mouse_y)
                            self.mouse_down = True
                        
                        for slider in self.simulation_sliders:
                            slider.handle_event(event)
                
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False
                    for slider in self.simulation_sliders:
                        slider.handle_event(event)
            
            if event.type == pygame.MOUSEMOTION:
                for slider in self.simulation_sliders:
                    slider.handle_event(event)
        
        return True
    
    def run(self):
        running = True
        last_time = time.time()
        
        while running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            dt = min(dt, 0.05)
            
            self.fps = self.clock.get_fps()
            
            running = self.handle_events()
            
            self.update(dt)
            
            self.draw()
            
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    sim = WaterSimulation()
    sim.run()