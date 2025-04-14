from create_window import GameWindow
from conf import *
import keyboard
import time
import random

class Game:
    def __init__(self):
        self.running = True
        self.score = 0
        self.player = GameWindow(PLAYER_WINDOW_TITLE, PLAYER_WINDOW_SIZE, 
                               PLAYER_WINDOW_COLOR, is_player=True)
        self.targets = []
        self.create_targets()
        self.movement = {'up': False, 'down': False, 'left': False, 'right': False}
        self.last_update = time.time()
        self.setup_controls()
        self.update_game()

    def create_targets(self):
        for i in range(TARGET_WINDOW_COUNT):
            target = GameWindow(TARGET_WINDOW_TITLE, TARGET_WINDOW_SIZE,
                              TARGET_WINDOW_COLORS[i % len(TARGET_WINDOW_COLORS)])
            self.targets.append(target)

    def setup_controls(self):
        keyboard.on_press_key('w', lambda _: self.set_movement('up', True))
        keyboard.on_release_key('w', lambda _: self.set_movement('up', False))
        keyboard.on_press_key('s', lambda _: self.set_movement('down', True))
        keyboard.on_release_key('s', lambda _: self.set_movement('down', False))
        keyboard.on_press_key('a', lambda _: self.set_movement('left', True))
        keyboard.on_release_key('a', lambda _: self.set_movement('left', False))
        keyboard.on_press_key('d', lambda _: self.set_movement('right', True))
        keyboard.on_release_key('d', lambda _: self.set_movement('right', False))
        keyboard.on_press_key('esc', lambda _: self.quit_game())

    def set_movement(self, direction, value):
        self.movement[direction] = value

    def update_game(self):
        try:
            if not self.running:
                return

            current_time = time.time()
            delta_time = current_time - self.last_update
            self.last_update = current_time

            # Check if any target windows need to be restored
            self.check_target_windows()

            # Calculate movement based on delta time
            dx = dy = 0
            if self.movement['up']: dy -= PLAYER_WINDOW_SPEED * delta_time * 60
            if self.movement['down']: dy += PLAYER_WINDOW_SPEED * delta_time * 60
            if self.movement['left']: dx -= PLAYER_WINDOW_SPEED * delta_time * 60
            if self.movement['right']: dx += PLAYER_WINDOW_SPEED * delta_time * 60

            if dx != 0 or dy != 0:
                self.move_player(int(dx), int(dy))

            if self.running:
                self.player.window.after(UPDATE_INTERVAL, self.update_game)
        except Exception as e:
            print(f"Error in game update: {e}")
            self.quit_game()

    def check_target_windows(self):
        try:
            for target in self.targets[:]:
                if not target.is_window_visible():
                    try:
                        target.window.deiconify()
                        x = random.randint(0, SCREEN_WIDTH - TARGET_WINDOW_SIZE[0])
                        y = random.randint(0, SCREEN_HEIGHT - TARGET_WINDOW_SIZE[1])
                        target.window.geometry(f"+{x}+{y}")
                    except:
                        self.targets.remove(target)
        except Exception as e:
            print(f"Error checking target windows: {e}")

    def move_player(self, dx, dy):
        self.player.move(dx, dy)
        self.check_collisions()

    def check_collisions(self):
        player_pos = self.player.get_position()
        player_size = self.player.get_size()

        for target in self.targets[:]:
            target_pos = target.get_position()
            target_size = target.get_size()

            if (player_pos[0] < target_pos[0] + target_size[0] and
                player_pos[0] + player_size[0] > target_pos[0] and
                player_pos[1] < target_pos[1] + target_size[1] and
                player_pos[1] + player_size[1] > target_pos[1]):
                
                self.score += SCORE_INCREMENT
                target.destroy()
                self.targets.remove(target)

                # Check if only one target remains, create new targets if needed
                if len(self.targets) < 2:
                    self.create_new_targets()

    def create_new_targets(self):
        new_count = TARGET_WINDOW_COUNT - len(self.targets)
        for i in range(new_count):
            target = GameWindow(TARGET_WINDOW_TITLE, TARGET_WINDOW_SIZE,
                              TARGET_WINDOW_COLORS[i % len(TARGET_WINDOW_COLORS)])
            self.targets.append(target)

    def quit_game(self):
        try:
            self.running = False
            keyboard.unhook_all()  # Remove all keyboard hooks
            
            for target in self.targets[:]:
                try:
                    target.destroy()
                except:
                    pass
                    
            self.targets.clear()
            
            if hasattr(self, 'player') and self.player:
                try:
                    self.player.destroy()
                except:
                    pass
                    
        except Exception as e:
            print(f"Error during quit: {e}")
        finally:
            try:
                if hasattr(self, 'player') and self.player and hasattr(self.player, 'window'):
                    self.player.window.quit()
            except:
                pass

    def run(self):
        self.player.window.mainloop()

if __name__ == "__main__":
    game = Game()
    game.run()
