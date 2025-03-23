import pygame
from pygame import Rect
import random
import sys
import numpy as np



class Tetris:
    def __init__(self):
        pygame.init()

        # Fonts and Paths
        self.font_path = "assets/fonts/OpenSans-Light.ttf"
        self.h4 = pygame.font.Font(self.font_path, 35)
        self.h5 = pygame.font.Font(self.font_path, 24)

        # Colors
        self.BLACK = (10, 10, 10)
        self.WHITE = (255, 255, 255)
        self.GREY_1 = (26, 26, 26)
        self.GREY_2 = (35, 35, 35)
        self.GREY_3 = (55, 55, 55)
        
        self.CYAN = (69, 206, 204)  # I
        self.BLUE = (64, 111, 249)  # J
        self.ORANGE = (253, 189, 53)  # L
        self.YELLOW = (246, 227, 90)  # O
        self.GREEN = (98, 190, 68)  # S
        self.PINK = (242, 64, 235)  # T
        self.RED = (225, 13, 27)  # Z

        # Tetrominos
        self.TETROMINOS = [
            [[1], [1], [1], [1]],  # I
            [[2, 0, 0], [2, 2, 2]],  # J
            [[0, 0, 3], [3, 3, 3]],  # L
            [[4, 4], [4, 4]],  # O
            [[0, 5, 5], [5, 5, 0]],  # S
            [[0, 6, 0], [6, 6, 6]],  # T
            [[7, 7, 0], [0, 7, 7]]   # Z
        ]

        self.TETROMINO_COLORS = [self.GREY_2, self.CYAN, self.BLUE, self.ORANGE, self.YELLOW, self.GREEN, self.PINK, self.RED, self.GREY_3]

        # Grid and screen dimensions
        self.GRID_WIDTH = 10
        self.GRID_HEIGHT = 20
        self.BLOCK_SIZE = 34

        self.SCREEN_WIDTH = self.GRID_WIDTH * self.BLOCK_SIZE
        self.SCREEN_HEIGHT = self.GRID_HEIGHT * self.BLOCK_SIZE
        self.screen = pygame.display.set_mode((600, 748))
        pygame.display.set_caption("Tetris")

        # Initialize game variables
        self.initialize_game_variables()
        

    def initialize_game_variables(self):
        # Game variables
        self.board = [[0] * self.GRID_WIDTH for _ in range(self.GRID_HEIGHT)]
        self.game_over = False
        self.clock = pygame.time.Clock()
    
        self.SCORE = 0
        self.LEVEL = 1
        self.GOAL = 5 * self.LEVEL
        self.lines_cleared = 0
        self.cl = 0
                
        self.index = random.randint(0, 6)
        self.current_tetromino = self.TETROMINOS[self.index]
        self.tetromino_dx = self.GRID_WIDTH // 2 - len(self.current_tetromino[0]) // 2
        self.tetromino_dy = 0
        
        self.currant_rotation = 0
    
        self.next_index = random.randint(0, 6)
        self.next_tetromino = self.TETROMINOS[self.next_index]
        self.hold_tetromino = None  # Variable to store the held tetromino
        self.can_hold = True  # Flag to prevent multiple holds in one turn
        self.fall_time = 10
        self.last_fall_time = pygame.time.get_ticks()
        self.last_move_time = pygame.time.get_ticks()
        self.move_delay = 100  # Delay for continuous movement

    def reset(self):
        self.initialize_game_variables()
        # return np.array(self.get_possible_states(), dtype=object)


    def move(self, direction):
        if self.check_collision(self.current_tetromino, self.tetromino_dx, self.tetromino_dy + 1):
            return
        
        # Calculate the new horizontal position by adding the direction (-1 for left, 1 for right) to the current position
        new_dx = self.tetromino_dx + direction
        
        # Check if the new position would result in a collision
        if not self.check_collision(self.current_tetromino, new_dx, self.tetromino_dy):
            # If no collision, update the current horizontal position to the new position
            self.tetromino_dx = new_dx
            

    def rotate_tetromino(self, tetromino, direction):
        if self.check_collision(self.current_tetromino, self.tetromino_dx, self.tetromino_dy + 1):
            return
        
        if direction == 1:
            # Rotate right (clockwise)
            mino = list(zip(*tetromino[::-1]))
        elif direction == -1:
            # Rotate left (counterclockwise)
            mino = list(zip(*tetromino))[::-1]
        
        # Check if the rotated tetromino would cause a collision
        if not self.check_collision(mino, self.tetromino_dx, self.tetromino_dy):
            # If no collision, update the current tetromino to the rotated version
            self.current_tetromino = mino
            self.currant_rotation += direction
            

    def insta_drop(self):
        # Move the tetromino down until it collides with something.
        while not self.check_collision(self.current_tetromino, self.tetromino_dx, self.tetromino_dy + 1):
            self.tetromino_dy += 1
            
    def hold_current_tetromino(self):
        if self.can_hold:
            if self.hold_tetromino is None:
                self.hold_tetromino = self.current_tetromino
                self.current_tetromino = self.next_tetromino
                
                self.next_index = random.randint(0, 6)
                self.next_tetromino = self.TETROMINOS[self.next_index]
            else:
                self.hold_tetromino, self.current_tetromino = self.current_tetromino, self.hold_tetromino
            self.tetromino_dx = self.GRID_WIDTH // 2 - len(self.current_tetromino[0]) // 2
            self.tetromino_dy = 0
            self.can_hold = False
    
    def move_down(self):
        """
        Moves the piece one step down without locking it.
        """
        if not self.check_collision(self.current_tetromino, self.tetromino_dx, self.tetromino_dy + 1):
            self.tetromino_dy += 1


    def draw_ghost_piece(self):
        # Calculate the ghost piece's position
        ghost_dy = self.tetromino_dy
        while not self.check_collision(self.current_tetromino, self.tetromino_dx, ghost_dy + 1):
            ghost_dy += 1
    
        for row in range(len(self.current_tetromino)):
            for col in range(len(self.current_tetromino[row])):
                if self.current_tetromino[row][col]:
                    # Calculate the position of the ghost block
                    dx = 34 + self.BLOCK_SIZE * (self.tetromino_dx + col)
                    dy = 34 + self.BLOCK_SIZE * (ghost_dy + row)
    
                    # Draw the ghost block in GREY_3
                    pygame.draw.rect(self.screen, self.GREY_3, pygame.Rect(dx, dy, self.BLOCK_SIZE, self.BLOCK_SIZE))
    
                    # Draw the border of the ghost block in GREY_1 for contrast
                    pygame.draw.rect(self.screen, self.GREY_1, pygame.Rect(dx, dy, self.BLOCK_SIZE, self.BLOCK_SIZE), 1)

    def draw_grid(self):
        self.screen.fill(self.GREY_1)
        pygame.draw.rect(self.screen, self.WHITE, pygame.Rect(408, 0, 192, 748))
    
        for x in range(self.GRID_WIDTH):
            for y in range(self.GRID_HEIGHT):
                px = 34 + self.BLOCK_SIZE * x
                py = 34 + self.BLOCK_SIZE * y
                self.draw_tetromino(px, py, self.TETROMINO_COLORS[self.board[y][x]])
    
        # Draw the ghost piece
        self.draw_ghost_piece()
    
        for row in range(len(self.current_tetromino)):
            for col in range(len(self.current_tetromino[row])):
                if self.current_tetromino[row][col]:
                    dx = 34 + self.BLOCK_SIZE * (self.tetromino_dx + col)
                    dy = 34 + self.BLOCK_SIZE * (self.tetromino_dy + row)
                    pygame.draw.rect(self.screen, self.TETROMINO_COLORS[self.current_tetromino[row][col]], pygame.Rect(dx, dy, self.BLOCK_SIZE, self.BLOCK_SIZE))
                    pygame.draw.rect(self.screen, self.GREY_1, Rect(dx, dy, self.BLOCK_SIZE, self.BLOCK_SIZE), 1)
    
        for i, row in enumerate(self.next_tetromino):
            for j, col in enumerate(row):
                if col:
                    dx = 440 + self.BLOCK_SIZE * j
                    dy = 260 + self.BLOCK_SIZE * i
                    pygame.draw.rect(self.screen, self.TETROMINO_COLORS[col], pygame.Rect(dx, dy, self.BLOCK_SIZE, self.BLOCK_SIZE))
    
        if self.hold_tetromino:
            for i, row in enumerate(self.hold_tetromino):
                for j, col in enumerate(row):
                    if col:
                        dx = 440 + self.BLOCK_SIZE * j
                        dy = 70 + self.BLOCK_SIZE * i
                        pygame.draw.rect(self.screen, self.TETROMINO_COLORS[col], pygame.Rect(dx, dy, self.BLOCK_SIZE, self.BLOCK_SIZE))
    
        text_hold = self.h5.render("HOLD", 1, self.BLACK)
        text_next = self.h5.render("NEXT", 1, self.BLACK)
        text_score = self.h5.render("SCORE", 1, self.BLACK)
        score_value = self.h4.render(str(self.SCORE), 1, self.BLACK)
        text_level = self.h5.render("LEVEL", 1, self.BLACK)
        level_value = self.h4.render(str(self.LEVEL), 1, self.BLACK)
        # text_goal = self.h5.render("GOAL", 1, self.BLACK)
        # goal_value = self.h4.render(str(self.GOAL), 1, self.BLACK)
        text_lines = self.h5.render("CLEARED LINES", 1, self.BLACK)
        lines_value = self.h4.render(str(self.lines_cleared), 1, self.BLACK)
        
    
        self.screen.blit(text_hold, (420, 28))
        self.screen.blit(text_next, (420, 218))
        self.screen.blit(text_score, (420, 408))
        self.screen.blit(score_value, (420, 440))
        self.screen.blit(text_level, (420, 528))
        self.screen.blit(level_value, (420, 560))
        # self.screen.blit(text_goal, (430, 648))
        # self.screen.blit(goal_value, (440, 680))
        self.screen.blit(text_lines, (420, 648))
        self.screen.blit(lines_value, (420, 680))

    
    def draw_tetromino(self, x, y, color):
        # Draw the main rectangle of the tetromino block
        pygame.draw.rect(self.screen, color, Rect(x, y, self.BLOCK_SIZE, self.BLOCK_SIZE))
        # Draw the border of the tetromino block for better visibility
        pygame.draw.rect(self.screen, self.GREY_1, Rect(x, y, self.BLOCK_SIZE, self.BLOCK_SIZE), 1)

    def check_collision(self, tetromino, dx, dy):
        for row in range(len(tetromino)):
            for col in range(len(tetromino[row])):
                if tetromino[row][col]:
                    x = dx + col
                    y = dy + row
                    if x < 0 or x >= self.GRID_WIDTH or y >= self.GRID_HEIGHT or self.board[y][x]:
                        return True
        return False

    

    def clear_lines(self):
        # Find all full lines
        full_lines = [i for i, row in enumerate(self.board) if all(row)]
        
        # Remove full lines and insert empty lines at the top
        for i in full_lines:
            del self.board[i]
            self.board.insert(0, [0] * self.GRID_WIDTH)
        
        # Return the number of full lines cleared
        return len(full_lines)
    

    def update(self):
        if pygame.time.get_ticks() - self.last_fall_time >= self.fall_time:
            new_dy = self.tetromino_dy + 1
            if not self.check_collision(self.current_tetromino, self.tetromino_dx, new_dy):
                self.tetromino_dy = new_dy
            else:
                for row in range(len(self.current_tetromino)):
                    for col in range(len(self.current_tetromino[row])):
                        if self.current_tetromino[row][col]:
                            self.board[self.tetromino_dy + row][self.tetromino_dx + col] = self.current_tetromino[row][col]
                
                # Clear lines and update score
                lines_cleared = self.clear_lines()
                if lines_cleared == 1:
                    self.SCORE += 50 * self.LEVEL
                elif lines_cleared == 2:
                    self.SCORE += 150 * self.LEVEL
                elif lines_cleared == 3:
                    self.SCORE += 350 * self.LEVEL
                elif lines_cleared == 4:
                    self.SCORE += 1000 * self.LEVEL
    
                self.GOAL -= lines_cleared
                if self.GOAL < 1 and self.LEVEL < 15:
                    self.LEVEL += 1
                    self.GOAL += self.LEVEL * 5
                    # self.fall_time = int(self.fall_time * 0.8)
                    self.fall_time = int(self.fall_time * 1)
                self.SCORE += 10
                self.lines_cleared += lines_cleared
                self.cl = lines_cleared
    
                self.current_tetromino = self.next_tetromino
                self.tetromino_dx = self.GRID_WIDTH // 2 - len(self.current_tetromino[0]) // 2
                self.tetromino_dy = 0
                
                self.next_index = random.randint(0, 6)
                self.next_tetromino = self.TETROMINOS[self.next_index]
                self.can_hold = True
    
                if self.check_collision(self.current_tetromino, self.tetromino_dx, self.tetromino_dy):
                    self.game_over = True
    
            self.last_fall_time = pygame.time.get_ticks()
            

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move(-1)
                elif event.key == pygame.K_RIGHT:
                    self.move(1)
                elif event.key == pygame.K_UP:
                    self.rotate_tetromino(self.current_tetromino, 1)  # Rotate right
                elif event.key == pygame.K_z:
                    self.rotate_tetromino(self.current_tetromino, -1)  # Rotate left
                elif event.key == pygame.K_DOWN:
                    self.move_down()
                elif event.key == pygame.K_SPACE:
                    self.insta_drop()  # Instantly drop the tetromino
                elif event.key == pygame.K_h:
                    self.hold_current_tetromino() # Hold current tetromino

    def run(self):
        while not self.game_over:
            self.handle_events()
            self.update()
            self.draw_grid()
            pygame.display.update()
            self.clock.tick(30)

            if self.game_over:
                self.reset()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Tetris()
    game.run()