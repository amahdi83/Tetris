"""
Created on Thu May 16 04:20:00 2024

@author: alimahdi

"""

import os
import sys

# Set the working directory to the directory of the executable
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Now the working directory is set correctly, you can proceed with your script...


import pygame
import operator
from random import *
from pygame.locals import *



class ui_variables:
    # Fonts
    
    pygame.init()
    
    font_path = "assets/fonts/OpenSans-Light.ttf"
    font_path_b = "assets/fonts/OpenSans-Bold.ttf"
    font_path_i = "assets/fonts/Inconsolata.otf"
    font_path_x = "assets/fonts/WtfAfroboyRegular-K7Lme.ttf"

    
    h1 = pygame.font.Font(font_path_x, 100)
    h2 = pygame.font.Font(font_path, 60)
    h4 = pygame.font.Font(font_path, 40)
    h5 = pygame.font.Font(font_path, 26)
    h6 = pygame.font.Font(font_path, 18)
    h2_b = pygame.font.Font(font_path_b, 50)

    h2_i = pygame.font.Font(font_path_i, 60)
    h5_i = pygame.font.Font(font_path_i, 26)

    # Sounds
    click_sound = pygame.mixer.Sound("assets/sounds/SFX_ButtonUp.wav")
    move_sound = pygame.mixer.Sound("assets/sounds/SFX_PieceMoveLR.wav")
    drop_sound = pygame.mixer.Sound("assets/sounds/SFX_PieceHardDrop.wav")
    single_sound = pygame.mixer.Sound("assets/sounds/SFX_SpecialLineClearSingle.wav")
    double_sound = pygame.mixer.Sound("assets/sounds/SFX_SpecialLineClearDouble.wav")
    triple_sound = pygame.mixer.Sound("assets/sounds/SFX_SpecialLineClearTriple.wav")
    tetris_sound = pygame.mixer.Sound("assets/sounds/SFX_SpecialTetris.wav")

    # Background colors
    black = (10, 10, 10)
    white = (255, 255, 255)
    grey_1 = (26, 26, 26)
    grey_2 = (35, 35, 35)
    grey_3 = (55, 55, 55)

    # Tetrimino colors
    cyan = (69, 206, 204)  # I
    blue = (64, 111, 249) # J
    orange = (253, 189, 53) # L
    yellow = (246, 227, 90) # O
    green = (98, 190, 68) # S
    pink = (242, 64, 235) # T
    red = (225, 13, 27) # Z

    t_color = [grey_2, cyan, blue, orange, yellow, green, pink, red, grey_3]
    
    
            
            




class Tetris:
    def __init__(self):
        self.tetrimino = [
            [[1], [1], [1], [1]],
                
            [[2, 0, 0], 
             [2, 2, 2]],

            [[0, 0, 3], 
             [3, 3, 3]],

            [[4, 4],
             [4, 4]],

            [[0, 5, 5],
             [5, 5, 0]],

            [[0, 6, 0],
             [6, 6, 6]],

            [[7, 7, 0],
             [0, 7, 7]]
        ]    

        # Define
        self.block_size = 34 # Height, width of single block
        self.width = 10 # Board width
        self.height = 20 # Board height
        self.framerate = 30 # Bigger -> Slower



        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((600, 748))
        pygame.time.set_timer(pygame.USEREVENT, self.framerate * 10)
        pygame.display.set_caption("AI Tetris in Python")



        # Initial values
        self.blink = False
        self.start = False
        self.pause = False
        self.done = False
        self.game_over = False

        self.rotate = False

        self.score = 0
        self.level = 1
        self.goal = self.level * 5
        self.bottom_count = 0
        self.hard_drop = False

        self.dx, self.dy = 3, 0 # Minos location status
        self.rotation = 0 # Minos rotation status

        self.mino = randint(1, 7) # Current mino
        self.next_mino = randint(1, 7) # Next mino

        self.mino_block = self.tetrimino[self.mino-1]
        self.next_mino_block = self.tetrimino[self.next_mino-1]

        self.hold = False # Hold status
        self.hold_mino = -1 # Holded mino
        self.hold_mino_block = self.tetrimino[self.hold_mino]

        self.name_location = 0
        self.name = [65, 65, 65]

        with open('leaderboard.txt') as f:
            lines = f.readlines()
        lines = [line.rstrip('\n') for line in open('leaderboard.txt')]

        self.leaders = {'AAA': 0, 'BBB': 0, 'CCC': 0}
        for i in lines:
            self.leaders[i.split(' ')[0]] = int(i.split(' ')[1])
        self.leaders = sorted(self.leaders.items(), key=operator.itemgetter(1), reverse=True)

        self.matrix = [[0 for y in range(self.width)] for x in range(self.height + 1)] # Board matrix
        self.board = [[0 for y in range(self.width)] for x in range(self.height + 1)] # Board matrix
        
    
    def reset(self):
        self.game_over = False
        self.hold = False
        self.dx, self.dy = 3, 0
        self.rotation = 0
        self.mino = randint(1, 7)
        self.next_mino = randint(1, 7)
        self.hold_mino = -1
        self.framerate = 30
        self.score = 0
        self.score = 0
        self.level = 1
        self.goal = self.level * 5
        self.bottom_count = 0
        self.hard_drop = False
        self.name_location = 0
        self.name = [65, 65, 65]
        self.matrix = [[0 for y in range(self.width)] for x in range(self.height + 1)]
        self.board = [[0 for y in range(self.width)] for x in range(self.height + 1)] # Board matrix
        
        
    def move(self, direction):
        if direction < 0 and not self.is_leftedge(self.dx, self.dy, self.mino_block):
            ui_variables.move_sound.play()
            self.dx += direction
            
        elif direction > 0 and not self.is_rightedge(self.dx, self.dy, self.mino_block, self.rotation):
            ui_variables.move_sound.play()
            self.dx += direction
            
        else:
            pass


    def rotate_clockwise(self, shape):
        return [[shape[y][x]
                 for y in range(len(shape))]
                for x in range(len(shape[0]) - 1, -1, -1)]

    def rotate_counterclockwise(self, shape):
        return [[shape[y][x]
                 for y in range(len(shape)-1, -1, -1)]
                for x in range(len(shape[0]))]

    # Draw block
    def draw_block(self, x, y, color):
        pygame.draw.rect(
            self.screen,
            color,
            Rect(x, y, self.block_size, self.block_size)
        )
        pygame.draw.rect(
            self.screen,
            ui_variables.grey_1,
            Rect(x, y, self.block_size, self.block_size),
            1
        )


    # Draw game screen
    def draw_board(self, grid_n, grid_h, score, level, goal):
        self.screen.fill(ui_variables.grey_1)
        
        pygame.draw.rect(
            self.screen,
            ui_variables.white,
            Rect(408, 0, 192, 748)
        )

        
        for i in range(len(grid_n)):
            for j in range(len(grid_n[0])):
                dx = 440 + self.block_size * j
                dy = 260 + self.block_size * i
                if grid_n[i][j] != 0:
                    pygame.draw.rect(
                        self.screen,
                        ui_variables.t_color[grid_n[i][j]],
                        Rect(dx, dy, self.block_size, self.block_size)
                    )

        
        if self.hold_mino != -1:
            for i in range(len(grid_h)):
                for j in range(len(grid_h[0])):
                    dx = 440 + self.block_size * j
                    dy = 70 + self.block_size * i
                    if grid_h[i][j] != 0:
                        pygame.draw.rect(
                            self.screen,
                            ui_variables.t_color[grid_h[i][j]],
                            Rect(dx, dy, self.block_size, self.block_size)
                        )

        # Set max score
        if self.score > 999999:
            self.score = 999999

        # Draw texts
        text_hold = ui_variables.h5.render("HOLD", 1, ui_variables.black)
        text_next = ui_variables.h5.render("NEXT", 1, ui_variables.black)
        text_score = ui_variables.h5.render("SCORE", 1, ui_variables.black)
        score_value = ui_variables.h4.render(str(self.score), 1, ui_variables.black)
        text_level = ui_variables.h5.render("LEVEL", 1, ui_variables.black)
        level_value = ui_variables.h4.render(str(self.level), 1, ui_variables.black)
        text_goal = ui_variables.h5.render("GOAL", 1, ui_variables.black)
        goal_value = ui_variables.h4.render(str(self.goal), 1, ui_variables.black)
        
        # Place texts
        self.screen.blit(text_hold, (430, 28))
        self.screen.blit(text_next, (430, 218))
        self.screen.blit(text_score, (430, 408))
        self.screen.blit(score_value, (440, 440))
        self.screen.blit(text_level, (430, 528))
        self.screen.blit(level_value, (440, 560))
        self.screen.blit(text_goal, (430, 648))
        self.screen.blit(goal_value, (440, 680))
            
        # Draw board
        for x in range(self.width):
            for y in range(self.height):
                dx = 34 + self.block_size * x
                dy = 34 + self.block_size * y
                self.draw_block(dx, dy, ui_variables.t_color[self.matrix[y + 1][x]])



    # Draw a tetrimino
    def draw_mino(self, x, y, grid):
    
        tx, ty = x, y
        while not self.is_bottom(tx, ty, grid):
            ty += 1
    
        # Draw ghost
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0:
                    self.matrix[ty + i][tx + j] = 8
    
        # Draw mino
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0:
                    self.matrix[y + i][x + j] = grid[i][j]
                



    def build_board(self):
        # Erase ghost
        for j in range(21):
            for i in range(10):
                if self.matrix[j][i] == 8:
                    self.board[j][i] = 0
                else:
                    self.board[j][i] = self.matrix[j][i]
                
                
                
                
    def erase_mino(self, x, y, grid):
        # Erase ghost
        for j in range(21):
            for i in range(10):
                if self.matrix[j][i] == 8:
                    self.matrix[j][i] = 0
    
        # Erase mino
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0:
                    self.matrix[y + i][x + j] = 0



    # Returns true if mino is at bottom
    def is_bottom(self, x, y, grid):
    
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0:
                    if (y + i + 1) > 20:
                        return True
                    elif self.matrix[y + i + 1][x + j] != 0 and self.matrix[y + i + 1][x + j] != 8:
                        return True
    
        return False



    # Returns true if mino is at the left edge
    def is_leftedge(self, x, y, grid):
    
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0:
                    if (x + j - 1) < 0:
                        return True
                    elif self.matrix[y + i][x + j - 1] != 0:
                        return True
    
        return False

    # Returns true if mino is at the right edge
    def is_rightedge(self, x, y, grid, r):
    
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0:
                    if (x + j + 1) > 9:
                        return True
                    elif self.matrix[y + i][x + j + 1] != 0:
                        return True
    
        return False


    # Returns true if turning right is possible
    def is_turnable_r(self, x, y, grid):
    
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0:
                    if (x + j) < 0 or (x + j) > 9 or (y + i) < 0 or (y + i) > 20:
                        return False
                    elif self.matrix[y + i][x + j] != 0:
                        return False
    
        return True


    # Returns true if turning left is possible
    def is_turnable_l(self, x, y, grid):
    
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0:
                    if (x + j) < 0 or (x + j) > 9 or (y + i) < 0 or (y + i) > 20:
                        return False
                    elif self.matrix[y + i][x + j] != 0:
                        return False
    
        return True


    # Returns true if new block is drawable
    def is_stackable(self, grid):
    
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0 and self.matrix[i][3 + j] != 0:
                    return False
    
        return True





    def run(self):
    ###########################################################
    # Loop Start
    ###########################################################
    
        while not self.done:
            # Pause screen
            if self.pause:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.done = True
                    elif event.type == USEREVENT:
                        pygame.time.set_timer(pygame.USEREVENT, 300)
                        
                        self.next_mino_block = self.tetrimino[self.next_mino-1]
                        self.hold_mino_block = self.tetrimino[self.hold_mino-1]
                        self.draw_board(self.next_mino_block, self.hold_mino_block, self.score, self.level, self.goal)
        
                        pause_text = ui_variables.h2_b.render("PAUSED", 1, ui_variables.white)
                        pause_start = ui_variables.h5.render("Press esc to continue", 1, ui_variables.white)
        
                        self.screen.blit(pause_text, (90, 305))
                        if self.blink:
                            self.screen.blit(pause_start, (85, 380))
                            self.blink = False
                        else:
                            self.blink = True
                        pygame.display.update()
                    elif event.type == KEYDOWN:
                        self.mino_block = self.tetrimino[self.mino-1]
                        self.erase_mino(self.dx, self.dy, self.mino_block)
                        
                        if event.key == K_ESCAPE:
                            self.pause = False
                            ui_variables.click_sound.play()
                            pygame.time.set_timer(pygame.USEREVENT, 1)
        
            # Game screen
            elif self.start:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.done = True
                    elif event.type == USEREVENT:
                        # Set speed
                        if not self.game_over:
                            keys_pressed = pygame.key.get_pressed()
                            if keys_pressed[K_DOWN]:
                                pygame.time.set_timer(pygame.USEREVENT, self.framerate * 1)
                            else:
                                pygame.time.set_timer(pygame.USEREVENT, self.framerate * 10)
        
                        # Draw a mino
                        self.draw_mino(self.dx, self.dy, self.mino_block)
                        self.draw_board(self.next_mino_block, self.hold_mino_block, self.score, self.level, self.goal)
                        
                        self.build_board()
        
                        # Erase a mino
                        if not self.game_over:
                            self.erase_mino(self.dx, self.dy, self.mino_block)
        
                        # Move mino down
                        if not self.is_bottom(self.dx, self.dy, self.mino_block):
                            self.dy += 1
        
                        # Create new mino
                        else:
                            if self.hard_drop or self.bottom_count == 6:
                                self.hard_drop = False
                                self.bottom_count = 0
                                self.score += 10 * self.level
                                self.draw_mino(self.dx, self.dy, self.mino_block)
                                self.draw_board(self.next_mino_block, self.hold_mino_block, self.score, self.level, self.goal)
                                
                                self.build_board()
                                
                                if self.is_stackable(self.next_mino_block):
                                    self.mino = self.next_mino
                                    self.next_mino = randint(1, 7)
                                    
                                    self.mino_block = self.tetrimino[self.mino-1]
                                    self.next_mino_block = self.tetrimino[self.next_mino-1]
                                    
                                    self.dx, self.dy = 3, 0
                                    self.rotation = 0
                                    self.hold = False
                                else:
                                    self.start = False
                                    self.game_over = True
                                    pygame.time.set_timer(pygame.USEREVENT, 1)
                            else:
                                self.bottom_count += 1
        
                        # Erase line
                        erase_count = 0
                        for j in range(21):
                            is_full = True
                            for i in range(10):
                                if self.matrix[j][i] == 0:
                                    is_full = False
                            if is_full:
                                erase_count += 1
                                k = j
                                while k > 0:
                                    for i in range(10):
                                        self.matrix[k][i] = self.matrix[k - 1][i]
                                    k -= 1
                        if erase_count == 1:
                            ui_variables.single_sound.play()
                            self.score += 50 * self.level
                        elif erase_count == 2:
                            ui_variables.double_sound.play()
                            self.score += 150 * self.level
                        elif erase_count == 3:
                            ui_variables.triple_sound.play()
                            self.score += 350 * self.level
                        elif erase_count == 4:
                            ui_variables.tetris_sound.play()
                            self.score += 1000 * self.level
        
                        # Increase level
                        self.goal -= erase_count
                        if self.goal < 1 and self.level < 15:
                            self.level += 1
                            self.goal += self.level * 5
                            self.framerate = int(self.framerate * 0.8)
        
                    elif event.type == KEYDOWN:
                                                        
                        self.erase_mino(self.dx, self.dy, self.mino_block)
                        
                        if event.key == K_ESCAPE:
                                                
                            ui_variables.click_sound.play()
                            self.pause = True
                        # Hard drop
                        elif event.key == K_SPACE:
                                                
                            ui_variables.drop_sound.play()
                            while not self.is_bottom(self.dx, self.dy, self.mino_block):
                                self.dy += 1
                            self.hard_drop = True
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                            self.draw_mino(self.dx, self.dy, self.mino_block)
                            self.draw_board(self.next_mino_block, self.hold_mino_block, self.score, self.level, self.goal)

                            self.build_board()
                            
                        # Hold
                        elif event.key == K_LSHIFT or event.key == K_c:
                                                
                            if self.hold == False:
                                ui_variables.move_sound.play()
                                if self.hold_mino == -1:
                                    self.hold_mino = self.mino
                                    self.mino = self.next_mino
                                    self.next_mino = randint(1, 7)
                                    
                                else:
                                    self.hold_mino, self.mino = self.mino, self.hold_mino
                                    
                                self.mino_block = self.tetrimino[self.mino-1]
                                self.hold_mino_block = self.tetrimino[self.hold_mino-1]
                                self.next_mino_block = self.tetrimino[self.next_mino-1]
                                    
                                self.dx, self.dy = 3, 0
                                self.rotation = 0
                                self.hold = True
                                
                            self.draw_mino(self.dx, self.dy, self.mino_block)
                            self.draw_board(self.next_mino_block, self.hold_mino_block, self.score, self.level, self.goal)
 
                            self.build_board()
                            
                        # Turn right
                        elif event.key == K_UP or event.key == K_x:
                                                
                            self.mino_block = self.rotate_clockwise(self.mino_block)
                            
                            
                            if self.is_turnable_r(self.dx, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                            # Kick
                            elif self.is_turnable_r(self.dx, self.dy - 1, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dy -= 1
                            elif self.is_turnable_r(self.dx + 1, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx += 1
                            elif self.is_turnable_r(self.dx - 1, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx -= 1
                            elif self.is_turnable_r(self.dx, self.dy - 2, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dy -= 2
                            elif self.is_turnable_r(self.dx + 2, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx += 2
                            elif self.is_turnable_r(self.dx - 2, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx -= 2
                            elif self.is_turnable_r(self.dx, self.dy - 3, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dy -= 3
                            elif self.is_turnable_r(self.dx + 3, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx += 3
                            elif self.is_turnable_r(self.dx - 3, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx -= 3
                            
                            self.draw_mino(self.dx, self.dy, self.mino_block)
                            self.draw_board(self.next_mino_block, self.hold_mino_block, self.score, self.level, self.goal)

                            self.build_board()
                            
                        # Turn left
                        elif event.key == K_z or event.key == K_LCTRL:
                            
                            self.mino_block = self.rotate_counterclockwise(self.mino_block)
                                                
                            if self.is_turnable_l(self.dx, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                            # Kick
                            elif self.is_turnable_l(self.dx, self.dy - 1, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dy -= 1
                            elif self.is_turnable_l(self.dx + 1, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx += 1
                            elif self.is_turnable_l(self.dx - 1, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx -= 1
                            elif self.is_turnable_l(self.dx, self.dy - 2, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dy -= 2
                            elif self.is_turnable_l(self.dx + 2, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx += 2
                            elif self.is_turnable_l(self.dx - 2, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx -= 2
                            elif self.is_turnable_l(self.dx, self.dy - 3, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dy -= 3
                            elif self.is_turnable_l(self.dx + 3, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx += 3
                            elif self.is_turnable_l(self.dx - 3, self.dy, self.mino_block):
                                ui_variables.move_sound.play()
                                self.dx -= 3
                            
                            self.draw_mino(self.dx, self.dy, self.mino_block)
                            self.draw_board(self.next_mino_block, self.hold_mino_block, self.score, self.level, self.goal)
                            
                            self.build_board()
                            
                        # Move left
                        elif event.key == K_LEFT:
                                                
                            self.move(-1)
                            self.draw_mino(self.dx, self.dy, self.mino_block)
                            self.draw_board(self.next_mino_block, self.hold_mino_block, self.score, self.level, self.goal)

                            self.build_board()
                            
                        # Move right
                        elif event.key == K_RIGHT:
                            
                            self.move(1)
                            self.draw_mino(self.dx, self.dy, self.mino_block)
                            self.draw_board(self.next_mino_block, self.hold_mino_block, self.score, self.level, self.goal)

                            self.build_board()
        
                pygame.display.update()
        
            # Game over screen
            elif self.game_over:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.done = False
                    elif event.type == USEREVENT:
                        pygame.time.set_timer(pygame.USEREVENT, 300)
                        over_text_1 = ui_variables.h2_b.render("GAME", 1, ui_variables.white)
                        over_text_2 = ui_variables.h2_b.render("OVER", 1, ui_variables.white)
                        over_start = ui_variables.h5.render("Press return to continue", 1, ui_variables.white)
        
                        self.next_mino_block = self.tetrimino[self.next_mino-1]
                        self.hold_mino_block = self.tetrimino[self.hold_mino-1]
                        self.draw_board(self.next_mino_block, self.hold_mino_block, self.score, self.level, self.goal)
                        
                        
                        self.screen.blit(over_text_1, (55, 320))
                        self.screen.blit(over_text_2, (220, 320))
        
                        name_1 = ui_variables.h2_i.render(chr(self.name[0]), 1, ui_variables.white)
                        name_2 = ui_variables.h2_i.render(chr(self.name[1]), 1, ui_variables.white)
                        name_3 = ui_variables.h2_i.render(chr(self.name[2]), 1, ui_variables.white)
        
                        underbar_1 = ui_variables.h2.render("_", 1, ui_variables.white)
                        underbar_2 = ui_variables.h2.render("_", 1, ui_variables.white)
                        underbar_3 = ui_variables.h2.render("_", 1, ui_variables.white)
        
                        self.screen.blit(name_1, (160, 430))
                        self.screen.blit(name_2, (190, 430))
                        self.screen.blit(name_3, (220, 430))
        
                        if self.blink:
                            self.screen.blit(over_start, (65, 390))
                            self.blink = False
                        else:
                            if self.name_location == 0:
                                self.screen.blit(underbar_1, (160, 420))
                            elif name_location == 1:
                                self.screen.blit(underbar_2, (190, 420))
                            elif self.name_location == 2:
                                self.screen.blit(underbar_3, (220, 420))
                            self.blink = True
        
                        pygame.display.update()
                    elif event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            ui_variables.click_sound.play()
        
                            outfile = open('leaderboard.txt','a')
                            outfile.write(chr(self.name[0]) + chr(self.name[1]) + chr(self.name[2]) + ' ' + str(self.score) + '\n')
                            outfile.close()
        
                            self.game_over = False
                            self.hold = False
                            self.dx, self.dy = 3, 0
                            self.rotation = 0
                            self.mino = randint(1, 7)
                            self.next_mino = randint(1, 7)
                            self.hold_mino = -1
                            self.framerate = 30
                            self.score = 0
                            self.score = 0
                            self.level = 1
                            self.goal = self.level * 5
                            self.bottom_count = 0
                            self.hard_drop = False
                            self.name_location = 0
                            self.name = [65, 65, 65]
                            self.matrix = [[0 for y in range(self.width)] for x in range(self.height + 1)]
                            self.board = [[0 for y in range(self.width)] for x in range(self.height + 1)] # Board matrix
                            
                            self.reset()
        
                            with open('leaderboard.txt') as f:
                                lines = f.readlines()
                            lines = [line.rstrip('\n') for line in open('leaderboard.txt')]
        
                            self.leaders = {'AAA': 0, 'BBB': 0, 'CCC': 0}
                            for i in lines:
                                self.leaders[i.split(' ')[0]] = int(i.split(' ')[1])
                            self.leaders = sorted(self.leaders.items(), key=operator.itemgetter(1), reverse=True)
        
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                        elif event.key == K_RIGHT:
                            if self.name_location != 2:
                                self.name_location += 1
                            else:
                                self.name_location = 0
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                        elif event.key == K_LEFT:
                            if self.name_location != 0:
                                self.name_location -= 1
                            else:
                                self.name_location = 2
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                        elif event.key == K_UP:
                            ui_variables.click_sound.play()
                            if self.name[self.name_location] != 90:
                                self.name[self.name_location] += 1
                            else:
                                self.name[self.name_location] = 65
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                        elif event.key == K_DOWN:
                            ui_variables.click_sound.play()
                            if self.name[self.name_location] != 65:
                                self.name[self.name_location] -= 1
                            else:
                                self.name[self.name_location] = 90
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                        
                        # self.start = True
        
            # Start screen
            else:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.done = True
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE or not self.start:
                            ui_variables.click_sound.play()
                            self.start = True
                
                self.screen.fill(ui_variables.white)
                pygame.draw.rect(
                    self.screen,
                    ui_variables.grey_1,
                    Rect(0, 374, 600, 374)
                )
        
                title_T = ui_variables.h1.render("T", 1, ui_variables.red)
                title_E = ui_variables.h1.render("E", 1, ui_variables.cyan)
                title_t = ui_variables.h1.render("T", 1, ui_variables.orange)
                title_R = ui_variables.h1.render("R", 1, ui_variables.pink)
                title_I = ui_variables.h1.render("I", 1, ui_variables.blue)
                title_S = ui_variables.h1.render("S", 1, ui_variables.green)
        
                title_start = ui_variables.h5.render("Press space to start", 1, ui_variables.white)
                title_info = ui_variables.h6.render("Copyright (c) 2024 Ali Mahdi All Rights Reserved.", 1, ui_variables.white)
        
                leader_1 = ui_variables.h5_i.render('1st ' + self.leaders[0][0] + ' ' + str(self.leaders[0][1]), 1, ui_variables.grey_1)
                leader_2 = ui_variables.h5_i.render('2nd ' + self.leaders[1][0] + ' ' + str(self.leaders[1][1]), 1, ui_variables.grey_1)
                leader_3 = ui_variables.h5_i.render('3rd ' + self.leaders[2][0] + ' ' + str(self.leaders[2][1]), 1, ui_variables.grey_1)
        
                
                if self.blink:
                    self.screen.blit(title_start, (184, 390))
                    self.blink = False
                else:
                    self.blink = True
        
                
                self.screen.blit(title_T, (110, 240))
                self.screen.blit(title_E, (170, 240))
                self.screen.blit(title_t, (235, 240))
                self.screen.blit(title_R, (295, 240))
                self.screen.blit(title_I, (375, 240))
                self.screen.blit(title_S, (430, 240))
                
                self.screen.blit(title_info, (110, 700))
        
                self.screen.blit(leader_1, (20, 20))
                self.screen.blit(leader_2, (20, 46))
                self.screen.blit(leader_3, (20, 72))
        
                if not self.start:
                    pygame.display.update()
                    self.clock.tick(3)
        
        pygame.quit()
    


game = Tetris()
game.run()
    
    
"""
self.tempState.reset()
self.tempState.board = worldState.board
self.tempState.stone = worldState.stone
self.tempState.stone_x = worldState.stone_x
self.tempState.stone_y = worldState.stone_y
self.tempState.currentStoneId = worldState.currentStoneId
self.tempState.currentRotation = worldState.currentRotation
self.tempState.blockMobile = worldState.blockMobile
self.tempState.nextStoneId = worldState.nextStoneId
self.tempState.next_stone = worldState.next_stone

"""
