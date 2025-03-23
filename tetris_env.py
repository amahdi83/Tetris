import pygame
import random
import sys
import copy
import numpy as np
from pygame import Rect
from tetris import Tetris


class TetrisEnv(Tetris):
    def __init__(self):
        super().__init__()
        

    def reset(self):
        self.initialize_game_variables()
        return np.array(self.get_possible_states(), dtype=object)

    
    def get_possible_states(self):
        """Returns all possible states of the board with the corresponding action tuple.
    
        Tries out every possible way to turn and move the current piece.
        The action taken and the state of the board is combined into a tuple and added to the returning list.
        After every try, the board is reset to its original state.
    
        :rtype: A list with a tuple of (action, state).
        action = (column, rotation)
        state = return value of `get_info`
        """
        if self.current_tetromino is None:
            return []
    
        states = []
        
        # Store the current tetromino's position and rotation
        original_tetromino = copy.deepcopy(self.current_tetromino)
        original_dx = self.tetromino_dx
        original_dy = self.tetromino_dy
    
        for rotation in range(4):  # Assuming at most 4 possible rotations
            # Rotate the piece and restore original position
            rotated_tetromino = copy.deepcopy(self.current_tetromino)
            for _ in range(rotation):
                rotated_tetromino = list(zip(*rotated_tetromino[::-1]))  # Rotate clockwise
    
            for column in range(self.GRID_WIDTH):
                # Reset the position
                self.current_tetromino = copy.deepcopy(rotated_tetromino)
                self.tetromino_dx = column
                self.tetromino_dy = 0
    
                # Move and drop the piece
                if not self.check_collision(self.current_tetromino, self.tetromino_dx, self.tetromino_dy):
                    self.insta_drop()
    
                    # Simulate placing the piece and capture the board state
                    temp_board = copy.deepcopy(self.board)
                    for row in range(len(self.current_tetromino)):
                        for col in range(len(self.current_tetromino[row])):
                            if self.current_tetromino[row][col]:
                                temp_board[self.tetromino_dy + row][self.tetromino_dx + col] = self.current_tetromino[row][col]
    
                    # Check lines cleared
                    rows_cleared = self.get_cleared_rows()
                    cleared_lines = len(rows_cleared)
    
                    # Get board statistics
                    state_info = self.get_info(rows_cleared, temp_board)
    
                    # Save the state-action pair
                    states.append(((column, rotation), state_info))
    
            # Restore original state before testing the next rotation
            self.current_tetromino = copy.deepcopy(original_tetromino)
            self.tetromino_dx = original_dx
            self.tetromino_dy = original_dy
    
        return states
    
    def get_info(self, rows_cleared, board):
        """Returns the state of the board using statistics.
    
        0: Rows cleared
        1: Bumpiness
        2: Holes
        3: Landing height
        4: Row transitions
        5: Column transitions
        6: Cumulative wells
        7: Eroded piece cells
        8: Aggregate height
    
        :rtype: Integer array
        """
        last_piece_coords = [(self.tetromino_dx + col, self.tetromino_dy + row)
                             for row in range(len(self.current_tetromino))
                             for col in range(len(self.current_tetromino[row]))
                             if self.current_tetromino[row][col]]
    
        eroded_piece_cells = len(rows_cleared) * sum(y in rows_cleared for x, y in last_piece_coords)
        landing_height = self.GRID_HEIGHT - max(y for x, y in last_piece_coords)
    
        return [
            len(rows_cleared),
            self.get_bumpiness(board),
            self.get_hole_count(board),
            landing_height,
            self.get_row_transitions(board),
            self.get_column_transitions(board),
            self.get_cumulative_wells(board),
            eroded_piece_cells,
            self.get_aggregate_height(board),
        ]
    
    def get_cleared_rows(self):
        """Returns the rows that will be cleared."""
        return [i for i, row in enumerate(self.board) if all(row)]
    
    def get_row_transitions(self, board):
        """Returns the number of horizontal cell transitions."""
        total = 0
        for row in board:
            row_count = 0
            last_empty = True
            for cell in row:
                empty = cell == 0
                if last_empty != empty:
                    row_count += 1
                    last_empty = empty
            total += row_count
        return total
    
    def get_column_transitions(self, board):
        """Returns the number of vertical cell transitions."""
        total = 0
        for x in range(self.GRID_WIDTH):
            last_empty = True
            column_count = 0
            for y in range(self.GRID_HEIGHT):
                empty = board[y][x] == 0
                if last_empty != empty:
                    column_count += 1
                last_empty = empty
            total += column_count
        return total
    
    def get_bumpiness(self, board):
        """Returns the total of the difference between the height of each column."""
        heights = [next((self.GRID_HEIGHT - y for y in range(self.GRID_HEIGHT) if board[y][x] != 0), 0)
                   for x in range(self.GRID_WIDTH)]
        return sum(abs(heights[i] - heights[i+1]) for i in range(len(heights)-1))
    
    def get_cumulative_wells(self, board):
        """Returns the sum of all wells."""
        wells = [0] * self.GRID_WIDTH
        for x in range(self.GRID_WIDTH):
            for y in range(self.GRID_HEIGHT):
                if board[y][x] == 0:
                    left_filled = x == 0 or board[y][x - 1] != 0
                    right_filled = x == self.GRID_WIDTH - 1 or board[y][x + 1] != 0
                    if left_filled and right_filled:
                        wells[x] += 1
        return sum(wells)
    
    def get_aggregate_height(self, board):
        """Returns the sum of the heights of each column."""
        return sum(next((self.GRID_HEIGHT - y for y in range(self.GRID_HEIGHT) if board[y][x] != 0), 0)
                   for x in range(self.GRID_WIDTH))
    
    def get_hole_count(self, board):
        """Returns the number of empty cells covered by a full cell."""
        hole_count = 0
        for x in range(self.GRID_WIDTH):
            seen_block = False
            for y in range(self.GRID_HEIGHT):
                if board[y][x] != 0:
                    seen_block = True
                elif seen_block:
                    hole_count += 1
        return hole_count
    
    
    def step(self, action, render=False):
        """Performs one step/frame in the game and returns the observation, reward, and if the game is over."""
        
        
        x, rotation = action  # Extract x-position and rotation
    
        # Rotate to the correct position
        for _ in range(rotation):
            if not self.check_collision(self.current_tetromino, self.tetromino_dx, self.tetromino_dy):
                self.rotate_tetromino(self.current_tetromino, 1)  # Rotate right
        
        # if not self.check_collision(self.current_tetromino, self.tetromino_dx, self.tetromino_dy):
        #     self.rotate_tetromino(self.current_tetromino, 1)  # 
    
    
        # Move the piece horizontally to x
        move_attempts = 0
        max_moves = self.GRID_WIDTH  # Safety limit to prevent infinite loops
        while self.tetromino_dx < x and move_attempts < max_moves:
            if not self.check_collision(self.current_tetromino, self.tetromino_dx + 1, self.tetromino_dy):
                self.move(1)  # Move right
  
            move_attempts += 1
    
        move_attempts = 0
        while self.tetromino_dx > x and move_attempts < max_moves:
            if not self.check_collision(self.current_tetromino, self.tetromino_dx - 1, self.tetromino_dy):
                self.move(-1)  # Move left

            move_attempts += 1
    
    
        # Drop the piece to the lowest possible position
        drop_attempts = 0
        max_drop = self.GRID_HEIGHT  # Prevent infinite drop loop
        while not self.check_collision(self.current_tetromino, self.tetromino_dx, self.tetromino_dy + 1) and drop_attempts < max_drop:
            self.tetromino_dy += 1
            drop_attempts += 1

    
        # Update game state
        self.update()
        
        if render:
            self.draw_grid()
            pygame.display.update()
    
        done = self.game_over        
        lines_cleared = self.cl
    
        reward = 1
    
        if lines_cleared == 1:
            reward += 40
        elif lines_cleared == 2:
            reward += 100
        elif lines_cleared == 3:
            reward += 300
        elif lines_cleared == 4:
            reward += 1200
            
        
        # # **Penalize Height Increase (to prevent stacking too high)**
        # aggregate_height = self.get_aggregate_height(self.board)
        # reward -= 0.1 * aggregate_height
        
        # # **Penalize Holes in the Board (to encourage compact placement)**
        # hole_count = self.get_hole_count(self.board)
        # reward -= 0.2 * hole_count
    
        if done:
            reward -= 5
            # reward -= 100
    
    
        return np.array(self.get_possible_states(), dtype=object), reward, done, {}