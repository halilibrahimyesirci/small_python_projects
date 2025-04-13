import pygame
import random
import heapq
import json
import os

# Constants
WIDTH, HEIGHT = 800, 900
ROWS, COLS = 16, 8
CELL_SIZE = 40
MAZE_WIDTH = CELL_SIZE * COLS
MAZE_HEIGHT = CELL_SIZE * ROWS
MAZE_X_OFFSET = (WIDTH - MAZE_WIDTH) // 2
MAZE_Y_OFFSET = (HEIGHT - MAZE_HEIGHT) // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Simulation")
font = pygame.font.Font(None, 24)

# Function to draw the grid
def draw_grid():
    for x in range(MAZE_X_OFFSET, MAZE_X_OFFSET + MAZE_WIDTH, CELL_SIZE):
        for y in range(MAZE_Y_OFFSET, MAZE_Y_OFFSET + MAZE_HEIGHT, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect)

def create_custom_maze():
    maze = [[[0, 0, 0, 0] for _ in range(COLS)] for _ in range(ROWS)]
    editing = True
    selected_wall = None
    start = (ROWS - 1, 3)  # Default start
    end = (0, 3)  # Default end
    
    while editing:
        screen.fill(BLACK)
        draw_grid()
        
        # Draw existing walls
        for row in range(ROWS):
            for col in range(COLS):
                x = MAZE_X_OFFSET + col * CELL_SIZE
                y = MAZE_Y_OFFSET + row * CELL_SIZE
                # Draw start and end points
                if (row, col) == start:
                    pygame.draw.rect(screen, GREEN, (x, y, CELL_SIZE, CELL_SIZE))
                if (row, col) == end:
                    pygame.draw.rect(screen, RED, (x, y, CELL_SIZE, CELL_SIZE))
                    
                for wall_idx, (start_pos, end_pos) in enumerate([
                    ((x, y), (x + CELL_SIZE, y)),  # Top wall
                    ((x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE)),  # Right wall
                    ((x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE)),  # Bottom wall
                    ((x, y), (x, y + CELL_SIZE))  # Left wall
                ]):
                    if maze[row][col][wall_idx]:
                        pygame.draw.line(screen, RED, start_pos, end_pos, 2)
        
        # Draw instructions
        font = pygame.font.Font(None, 24)
        instructions = [
            "Click to add/remove walls",
            "Press S to set start point",
            "Press E to set end point",
            "Press ENTER when done",
            "Press SPACE to clear all walls",
            "Press K to save maze",
            "Press L to load maze"
        ]
        for i, text in enumerate(instructions):
            text_surface = font.render(text, True, WHITE)
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                col = (mouse_pos[0] - MAZE_X_OFFSET) // CELL_SIZE
                row = (mouse_pos[1] - MAZE_Y_OFFSET) // CELL_SIZE
                
                if 0 <= row < ROWS and 0 <= col < COLS:
                    # Handle wall placement
                    x = MAZE_X_OFFSET + col * CELL_SIZE
                    y = MAZE_Y_OFFSET + row * CELL_SIZE
                    mouse_x, mouse_y = mouse_pos
                    
                    for wall_idx, (wall_start, wall_end) in enumerate([
                        ((x, y), (x + CELL_SIZE, y)),
                        ((x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE)),
                        ((x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE)),
                        ((x, y), (x, y + CELL_SIZE))
                    ]):
                        if abs(mouse_y - wall_start[1]) < 5 and wall_start[0] <= mouse_x <= wall_end[0] or \
                           abs(mouse_x - wall_start[0]) < 5 and wall_start[1] <= mouse_y <= wall_end[1]:
                            maze[row][col][wall_idx] = 1 - maze[row][col][wall_idx]
                            # Update adjacent walls
                            if wall_idx == 0 and row > 0:
                                maze[row-1][col][2] = maze[row][col][0]
                            elif wall_idx == 1 and col < COLS-1:
                                maze[row][col+1][3] = maze[row][col][1]
                            elif wall_idx == 2 and row < ROWS-1:
                                maze[row+1][col][0] = maze[row][col][2]
                            elif wall_idx == 3 and col > 0:
                                maze[row][col-1][1] = maze[row][col][3]
                            break
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    editing = False
                elif event.key == pygame.K_SPACE:
                    maze = [[[0, 0, 0, 0] for _ in range(COLS)] for _ in range(ROWS)]
                elif event.key == pygame.K_s:
                    # Set start point
                    mouse_pos = pygame.mouse.get_pos()
                    col = (mouse_pos[0] - MAZE_X_OFFSET) // CELL_SIZE
                    row = (mouse_pos[1] - MAZE_Y_OFFSET) // CELL_SIZE
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        start = (row, col)
                elif event.key == pygame.K_e:
                    # Set end point
                    mouse_pos = pygame.mouse.get_pos()
                    col = (mouse_pos[0] - MAZE_X_OFFSET) // CELL_SIZE
                    row = (mouse_pos[1] - MAZE_Y_OFFSET) // CELL_SIZE
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        end = (row, col)
                elif event.key == pygame.K_k:
                    # Save maze
                    maze_data = {
                        'maze': maze,
                        'start': start,
                        'end': end
                    }
                    with open('saved_maze.json', 'w') as f:
                        json.dump(maze_data, f)
                elif event.key == pygame.K_l:
                    # Load maze
                    if os.path.exists('saved_maze.json'):
                        with open('saved_maze.json', 'r') as f:
                            maze_data = json.load(f)
                            maze = maze_data['maze']
                            start = tuple(maze_data['start'])
                            end = tuple(maze_data['end'])
    
    return maze, start, end

# Function to create a maze using Prim's algorithm
def create_maze_prim():
    # Initialize maze with all walls
    maze = [[[1, 1, 1, 1] for _ in range(COLS)] for _ in range(ROWS)]
    visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
    walls = []
    
    # Start from a random cell
    start_x, start_y = random.randrange(ROWS), random.randrange(COLS)
    visited[start_x][start_y] = True
    
    # Add surrounding walls to wall list
    directions = [(0, -1, 3, 1), (0, 1, 1, 3), (-1, 0, 0, 2), (1, 0, 2, 0)]
    for dx, dy, wall, owall in directions:
        nx, ny = start_x + dx, start_y + dy
        if 0 <= nx < ROWS and 0 <= ny < COLS:
            walls.append((start_x, start_y, nx, ny, wall, owall))
    
    # Process walls
    while walls:
        # Pick a random wall
        wall = walls.pop(random.randrange(len(walls)))
        x1, y1, x2, y2, wall1, wall2 = wall
        
        # If only one of the cells is visited
        if visited[x1][y1] != visited[x2][y2]:
            # Remove the wall
            maze[x1][y1][wall1] = 0
            maze[x2][y2][wall2] = 0
            
            # Mark the unvisited cell
            if not visited[x1][y1]:
                visited[x1][y1] = True
                x, y = x1, y1
            else:
                visited[x2][y2] = True
                x, y = x2, y2
            
            # Add new walls from the newly visited cell
            for dx, dy, w1, w2 in directions:
                nx, ny = x + dx, y + dy
                if (0 <= nx < ROWS and 0 <= ny < COLS and 
                    not visited[nx][ny]):
                    walls.append((x, y, nx, ny, w1, w2))
    
    # Ensure start and end paths are accessible
    maze[ROWS-1][3][0] = 0  # Start point (bottom)
    maze[ROWS-2][3][2] = 0  # Connect to start
    maze[0][random.randrange(COLS)][2] = 0  # End point (top)
    
    return maze

# Function to number the maze cells starting from the end point
def number_maze(maze, end, discovered_walls=None):
    numbers = [[float('inf') for _ in range(COLS)] for _ in range(ROWS)]
    
    # Orta sütundan numaralandırmaya başla
    mid_col = 3  # 8 sütunun ortasına yakın (3. indeks)
    numbers[0][mid_col] = 0  # İlk satırda orta noktayı 0 yap
    
    changed = True
    directions = [(0, -1, 3, 1), (0, 1, 1, 3), (-1, 0, 0, 2), (1, 0, 2, 0)]

    while changed:
        changed = False
        for x in range(ROWS):
            for y in range(COLS):
                current = numbers[x][y]
                for dx, dy, wall1, wall2 in directions:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < ROWS and 0 <= ny < COLS):
                        wall_blocks = False
                        if discovered_walls:
                            if discovered_walls[x][y][wall1] == 1:
                                wall_blocks = True
                        else:
                            if maze[x][y][wall1] == 1:
                                wall_blocks = True

                        if not wall_blocks:
                            if numbers[nx][ny] + 1 < numbers[x][y]:
                                numbers[x][y] = numbers[nx][ny] + 1
                                changed = True

    # Gerçek bitiş noktasını sıfırla
    numbers[end[0]][end[1]] = 0

    # Tekrar numaralandır
    changed = True
    while changed:
        changed = False
        for x in range(ROWS):
            for y in range(COLS):
                current = numbers[x][y]
                for dx, dy, wall1, wall2 in directions:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < ROWS and 0 <= ny < COLS):
                        wall_blocks = False
                        if discovered_walls:
                            if discovered_walls[x][y][wall1] == 1:
                                wall_blocks = True
                        else:
                            if maze[x][y][wall1] == 1:
                                wall_blocks = True

                        if not wall_blocks:
                            if numbers[nx][ny] + 1 < numbers[x][y]:
                                numbers[x][y] = numbers[nx][ny] + 1
                                changed = True

    # Ulaşılamayan hücreleri None yap
    for x in range(ROWS):
        for y in range(COLS):
            if numbers[x][y] == float('inf'):
                numbers[x][y] = None

    return numbers

# Function to draw the maze
def draw_maze(maze, numbers, start, end, discovered_walls=None):
    for row in range(ROWS):
        for col in range(COLS):
            x = MAZE_X_OFFSET + col * CELL_SIZE
            y = MAZE_Y_OFFSET + row * CELL_SIZE
            if maze[row][col][0] == 1:  # Top wall
                color = LIGHT_BLUE if discovered_walls and discovered_walls[row][col][0] else RED
                pygame.draw.line(screen, color, (x, y), (x + CELL_SIZE, y), 2)
            if maze[row][col][1] == 1:  # Right wall
                color = LIGHT_BLUE if discovered_walls and discovered_walls[row][col][1] else RED
                pygame.draw.line(screen, color, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
            if maze[row][col][2] == 1:  # Bottom wall
                color = LIGHT_BLUE if discovered_walls and discovered_walls[row][col][2] else RED
                pygame.draw.line(screen, color, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
            if maze[row][col][3] == 1:  # Left wall
                color = LIGHT_BLUE if discovered_walls and discovered_walls[row][col][3] else RED
                pygame.draw.line(screen, color, (x, y), (x, y + CELL_SIZE), 2)
            # Draw the number in the center of the cell
            if numbers and numbers[row][col] is not None:
                text = font.render(str(numbers[row][col]), True, BLACK)
                text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                screen.blit(text, text_rect)
    # Draw start and end points
    pygame.draw.rect(screen, GREEN, (MAZE_X_OFFSET + start[1] * CELL_SIZE, MAZE_Y_OFFSET + start[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, GREEN, (MAZE_X_OFFSET + end[1] * CELL_SIZE, MAZE_Y_OFFSET + end[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Function to get user choice for maze creation
def get_user_choice():
    font = pygame.font.Font(None, 36)
    text_plain = font.render('Press 1 for Plain Maze', True, WHITE)
    text_numbered = font.render('Press 2 for Numbered Maze with Discovery', True, WHITE)
    text_custom = font.render('Press 3 to Create Custom Maze', True, WHITE)
    screen.fill(BLACK)
    screen.blit(text_plain, (WIDTH // 4, HEIGHT // 4))
    screen.blit(text_numbered, (WIDTH // 4, HEIGHT // 3))
    screen.blit(text_custom, (WIDTH // 4, HEIGHT // 2))
    pygame.display.flip()
    choice = None
    while choice not in ['1', '2', '3']:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    choice = '1'
                elif event.key == pygame.K_2:
                    choice = '2'
                elif event.key == pygame.K_3:
                    choice = '3'
    return choice

def get_next_move(px, py, numbers, maze):
    current_value = numbers[px][py]
    # Hareket önceliği: sol, yukarı, sağ, aşağı
    moves = [
        ((0, -1, 3), "left"),  # sol
        ((-1, 0, 0), "up"),    # yukarı
        ((0, 1, 1), "right"),  # sağ
        ((1, 0, 2), "down")    # aşağı
    ]
    
    best_move = None
    best_value = float('inf')
    
    for (dx, dy, wall), direction in moves:
        nx, ny = px + dx, py + dy
        if (0 <= nx < ROWS and 0 <= ny < COLS and 
            not maze[px][py][wall] and  # duvar kontrolü
            numbers[nx][ny] is not None and
            numbers[nx][ny] < best_value):
            best_value = numbers[nx][ny]
            best_move = (dx, dy)
    
    return best_move

def main():
    choice = get_user_choice()
    if choice == '3':
        maze, start, end = create_custom_maze()
    else:
        maze = create_maze_prim()
        start = (ROWS - 1, 3)
        end = (0, random.randint(0, COLS - 1))
    
    # Tek robot (mavi)
    player1_pos = [MAZE_X_OFFSET + start[1] * CELL_SIZE + CELL_SIZE // 2, 
                   MAZE_Y_OFFSET + start[0] * CELL_SIZE + CELL_SIZE // 2]
    move_history1 = [(player1_pos[0], player1_pos[1])]
    current_move_index1 = 0
    
    # Her seçenek için numbers ve discovered_walls oluştur
    numbers = number_maze(maze, end)  # Her durumda numbers gerekli
    discovered_walls = [[[False]*4 for _ in range(COLS)] for _ in range(ROWS)] if choice == '2' else None
    
    auto_move_timer = 0
    auto_move_delay = 500

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if current_move_index1 < len(move_history1) - 1:
                        current_move_index1 += 1
                        player1_pos[0], player1_pos[1] = move_history1[current_move_index1]
                elif event.key == pygame.K_LEFT:
                    if current_move_index1 > 0:
                        current_move_index1 -= 1
                        player1_pos[0], player1_pos[1] = move_history1[current_move_index1]

        # Otomatik hareket
        if current_time > auto_move_timer:
            # Mavi robot (en küçük sayı algoritması)
            if current_move_index1 == len(move_history1) - 1:
                px = (player1_pos[1] - MAZE_Y_OFFSET) // CELL_SIZE
                py = (player1_pos[0] - MAZE_X_OFFSET) // CELL_SIZE
                
                # Mavi robotun keşif güncellemesi
                if choice == '2' and discovered_walls is not None and 0 <= px < ROWS and 0 <= py < COLS:
                    discovered_walls[px][py] = maze[px][py].copy()
                    for dx, dy, wall in [(0,1,3), (0,-1,1), (1,0,0), (-1,0,2)]:
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < ROWS and 0 <= ny < COLS:
                            discovered_walls[nx][ny][wall] = maze[nx][ny][wall]
                
                next_move = get_next_move(px, py, numbers, maze)
                if next_move:
                    dx, dy = next_move
                    player1_pos[1] += dx * CELL_SIZE
                    player1_pos[0] += dy * CELL_SIZE
                    move_history1.append((player1_pos[0], player1_pos[1]))
                    current_move_index1 = len(move_history1) - 1

            auto_move_timer = current_time + auto_move_delay

        screen.fill(BLACK)
        draw_grid()
        if choice == '2' and discovered_walls is not None:
            px, py = (player1_pos[1] - MAZE_Y_OFFSET) // CELL_SIZE, (player1_pos[0] - MAZE_X_OFFSET) // CELL_SIZE
            if 0 <= px < ROWS and 0 <= py < COLS:
                discovered_walls[px][py] = maze[px][py].copy()
                
                # Komşu hücrelerin duvarlarını keşfet
                if py < COLS - 1:
                    discovered_walls[px][py+1][3] = maze[px][py+1][3]
                if py > 0:
                    discovered_walls[px][py-1][1] = maze[px][py-1][1]
                if px > 0:
                    discovered_walls[px-1][py][2] = maze[px-1][py][2]
                if px < ROWS - 1:
                    discovered_walls[px+1][py][0] = maze[px+1][py][0]
                
                numbers = number_maze(maze, end, discovered_walls)
                
        draw_maze(maze, numbers if choice == '2' else None, start, end, discovered_walls)
        pygame.draw.circle(screen, BLUE, player1_pos, CELL_SIZE // 4)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()