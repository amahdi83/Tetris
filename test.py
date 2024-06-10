#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 00:38:19 2024

@author: alimahdi
"""

import os
import sys
import pygame
import operator
from random import *
from pygame.locals import *
from tetris import Tetris, ui_variables

# Set the working directory to the directory of the executable
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Now the working directory is set correctly, you can proceed with your script...


game = Tetris()



while not game.done:
    # Pause screen
    if game.pause:
        for event in pygame.event.get():
            if event.type == QUIT:
                game.done = True
            elif event.type == USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 300)
                
                game.next_mino_block = game.tetrimino[game.next_mino-1]
                game.hold_mino_block = game.tetrimino[game.hold_mino-1]
                game.draw_board(game.next_mino_block, game.hold_mino_block, game.score, game.level, game.goal)

                pause_text = ui_variables.h2_b.render("PAUSED", 1, ui_variables.white)
                pause_start = ui_variables.h5.render("Press esc to continue", 1, ui_variables.white)

                game.screen.blit(pause_text, (90, 305))
                if game.blink:
                    game.screen.blit(pause_start, (85, 380))
                    game.blink = False
                else:
                    game.blink = True
                pygame.display.update()
            elif event.type == KEYDOWN:
                game.mino_block = game.tetrimino[game.mino-1]
                game.erase_mino(game.dx, game.dy, game.mino_block)
                
                if event.key == K_ESCAPE:
                    game.pause = False
                    ui_variables.click_sound.play()
                    pygame.time.set_timer(pygame.USEREVENT, 1)

    # Game screen
    elif game.start:
        for event in pygame.event.get():
            if event.type == QUIT:
                game.done = True
            elif event.type == USEREVENT:
                # Set speed
                if not game.game_over:
                    keys_pressed = pygame.key.get_pressed()
                    if keys_pressed[K_DOWN]:
                        pygame.time.set_timer(pygame.USEREVENT, game.framerate * 1)
                    else:
                        pygame.time.set_timer(pygame.USEREVENT, game.framerate * 10)

                # Draw a mino
                game.draw_mino(game.dx, game.dy, game.mino_block)
                game.draw_board(game.next_mino_block, game.hold_mino_block, game.score, game.level, game.goal)
                
                game.build_board()

                # Erase a mino
                if not game.game_over:
                    game.erase_mino(game.dx, game.dy, game.mino_block)

                # Move mino down
                if not game.is_bottom(game.dx, game.dy, game.mino_block):
                    game.dy += 1

                # Create new mino
                else:
                    if game.hard_drop or game.bottom_count == 6:
                        game.hard_drop = False
                        game.bottom_count = 0
                        game.score += 10 * game.level
                        game.draw_mino(game.dx, game.dy, game.mino_block)
                        game.draw_board(game.next_mino_block, game.hold_mino_block, game.score, game.level, game.goal)
                        
                        game.build_board()
                        
                        if game.is_stackable(game.next_mino_block):
                            game.mino = game.next_mino
                            game.next_mino = randint(1, 7)
                            
                            game.mino_block = game.tetrimino[game.mino-1]
                            game.next_mino_block = game.tetrimino[game.next_mino-1]
                            
                            game.dx, game.dy = 3, 0
                            game.rotation = 0
                            game.hold = False
                        else:
                            game.start = False
                            game.game_over = True
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                    else:
                        game.bottom_count += 1

                # Erase line
                erase_count = 0
                for j in range(21):
                    is_full = True
                    for i in range(10):
                        if game.matrix[j][i] == 0:
                            is_full = False
                    if is_full:
                        erase_count += 1
                        k = j
                        while k > 0:
                            for i in range(10):
                                game.matrix[k][i] = game.matrix[k - 1][i]
                            k -= 1
                if erase_count == 1:
                    ui_variables.single_sound.play()
                    game.score += 50 * game.level
                elif erase_count == 2:
                    ui_variables.double_sound.play()
                    game.score += 150 * game.level
                elif erase_count == 3:
                    ui_variables.triple_sound.play()
                    game.score += 350 * game.level
                elif erase_count == 4:
                    ui_variables.tetris_sound.play()
                    game.score += 1000 * game.level

                # Increase level
                game.goal -= erase_count
                if game.goal < 1 and game.level < 15:
                    game.level += 1
                    game.goal += game.level * 5
                    game.framerate = int(game.framerate * 0.8)

            elif event.type == KEYDOWN:
                                                
                game.erase_mino(game.dx, game.dy, game.mino_block)
                
                if event.key == K_ESCAPE:
                                        
                    ui_variables.click_sound.play()
                    game.pause = True
                # Hard drop
                elif event.key == K_SPACE:
                                        
                    ui_variables.drop_sound.play()
                    while not game.is_bottom(game.dx, game.dy, game.mino_block):
                        game.dy += 1
                    game.hard_drop = True
                    pygame.time.set_timer(pygame.USEREVENT, 1)
                    game.draw_mino(game.dx, game.dy, game.mino_block)
                    game.draw_board(game.next_mino_block, game.hold_mino_block, game.score, game.level, game.goal)

                    game.build_board()
                    
                # Hold
                elif event.key == K_LSHIFT or event.key == K_c:
                                        
                    if game.hold == False:
                        ui_variables.move_sound.play()
                        if game.hold_mino == -1:
                            game.hold_mino = game.mino
                            game.mino = game.next_mino
                            game.next_mino = randint(1, 7)
                            
                        else:
                            game.hold_mino, game.mino = game.mino, game.hold_mino
                            
                        game.mino_block = game.tetrimino[game.mino-1]
                        game.hold_mino_block = game.tetrimino[game.hold_mino-1]
                        game.next_mino_block = game.tetrimino[game.next_mino-1]
                            
                        game.dx, game.dy = 3, 0
                        game.rotation = 0
                        game.hold = True
                        
                    game.draw_mino(game.dx, game.dy, game.mino_block)
                    game.draw_board(game.next_mino_block, game.hold_mino_block, game.score, game.level, game.goal)

                    game.build_board()
                    
                # Turn right
                elif event.key == K_UP or event.key == K_x:
                                        
                    game.mino_block = game.rotate_clockwise(game.mino_block)
                    
                    
                    if game.is_turnable_r(game.dx, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                    # Kick
                    elif game.is_turnable_r(game.dx, game.dy - 1, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dy -= 1
                    elif game.is_turnable_r(game.dx + 1, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx += 1
                    elif game.is_turnable_r(game.dx - 1, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx -= 1
                    elif game.is_turnable_r(game.dx, game.dy - 2, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dy -= 2
                    elif game.is_turnable_r(game.dx + 2, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx += 2
                    elif game.is_turnable_r(game.dx - 2, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx -= 2
                    elif game.is_turnable_r(game.dx, game.dy - 3, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dy -= 3
                    elif game.is_turnable_r(game.dx + 3, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx += 3
                    elif game.is_turnable_r(game.dx - 3, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx -= 3
                    
                    game.draw_mino(game.dx, game.dy, game.mino_block)
                    game.draw_board(game.next_mino_block, game.hold_mino_block, game.score, game.level, game.goal)

                    game.build_board()
                    
                # Turn left
                elif event.key == K_z or event.key == K_LCTRL:
                    
                    game.mino_block = game.rotate_counterclockwise(game.mino_block)
                                        
                    if game.is_turnable_l(game.dx, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                    # Kick
                    elif game.is_turnable_l(game.dx, game.dy - 1, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dy -= 1
                    elif game.is_turnable_l(game.dx + 1, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx += 1
                    elif game.is_turnable_l(game.dx - 1, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx -= 1
                    elif game.is_turnable_l(game.dx, game.dy - 2, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dy -= 2
                    elif game.is_turnable_l(game.dx + 2, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx += 2
                    elif game.is_turnable_l(game.dx - 2, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx -= 2
                    elif game.is_turnable_l(game.dx, game.dy - 3, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dy -= 3
                    elif game.is_turnable_l(game.dx + 3, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx += 3
                    elif game.is_turnable_l(game.dx - 3, game.dy, game.mino_block):
                        ui_variables.move_sound.play()
                        game.dx -= 3
                    
                    game.draw_mino(game.dx, game.dy, game.mino_block)
                    game.draw_board(game.next_mino_block, game.hold_mino_block, game.score, game.level, game.goal)
                    
                    game.build_board()
                    
                # Move left
                elif event.key == K_LEFT:
                                        
                    game.move(-1)
                    game.draw_mino(game.dx, game.dy, game.mino_block)
                    game.draw_board(game.next_mino_block, game.hold_mino_block, game.score, game.level, game.goal)

                    game.build_board()
                    
                # Move right
                elif event.key == K_RIGHT:
                    
                    game.move(1)
                    game.draw_mino(game.dx, game.dy, game.mino_block)
                    game.draw_board(game.next_mino_block, game.hold_mino_block, game.score, game.level, game.goal)

                    game.build_board()

        pygame.display.update()

    # Game over screen
    elif game.game_over:
        for event in pygame.event.get():
            if event.type == QUIT:
                game.done = False
            elif event.type == USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 300)
                over_text_1 = ui_variables.h2_b.render("GAME", 1, ui_variables.white)
                over_text_2 = ui_variables.h2_b.render("OVER", 1, ui_variables.white)
                over_start = ui_variables.h5.render("Press return to continue", 1, ui_variables.white)

                game.next_mino_block = game.tetrimino[game.next_mino-1]
                game.hold_mino_block = game.tetrimino[game.hold_mino-1]
                game.draw_board(game.next_mino_block, game.hold_mino_block, game.score, game.level, game.goal)
                
                
                game.screen.blit(over_text_1, (55, 320))
                game.screen.blit(over_text_2, (220, 320))

                name_1 = ui_variables.h2_i.render(chr(game.name[0]), 1, ui_variables.white)
                name_2 = ui_variables.h2_i.render(chr(game.name[1]), 1, ui_variables.white)
                name_3 = ui_variables.h2_i.render(chr(game.name[2]), 1, ui_variables.white)

                underbar_1 = ui_variables.h2.render("_", 1, ui_variables.white)
                underbar_2 = ui_variables.h2.render("_", 1, ui_variables.white)
                underbar_3 = ui_variables.h2.render("_", 1, ui_variables.white)

                game.screen.blit(name_1, (160, 430))
                game.screen.blit(name_2, (190, 430))
                game.screen.blit(name_3, (220, 430))

                if game.blink:
                    game.screen.blit(over_start, (65, 390))
                    game.blink = False
                else:
                    if game.name_location == 0:
                        game.screen.blit(underbar_1, (160, 420))
                    elif name_location == 1:
                        game.screen.blit(underbar_2, (190, 420))
                    elif game.name_location == 2:
                        game.screen.blit(underbar_3, (220, 420))
                    game.blink = True

                pygame.display.update()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    ui_variables.click_sound.play()

                    outfile = open('leaderboard.txt','a')
                    outfile.write(chr(game.name[0]) + chr(game.name[1]) + chr(game.name[2]) + ' ' + str(game.score) + '\n')
                    outfile.close()

                    game.game_over = False
                    game.hold = False
                    game.dx, game.dy = 3, 0
                    game.rotation = 0
                    game.mino = randint(1, 7)
                    game.next_mino = randint(1, 7)
                    game.hold_mino = -1
                    game.framerate = 30
                    game.score = 0
                    game.score = 0
                    game.level = 1
                    game.goal = game.level * 5
                    game.bottom_count = 0
                    game.hard_drop = False
                    game.name_location = 0
                    game.name = [65, 65, 65]
                    game.matrix = [[0 for y in range(game.width)] for x in range(game.height + 1)]
                    game.board = [[0 for y in range(game.width)] for x in range(game.height + 1)] # Board matrix
                    
                    game.reset()

                    with open('leaderboard.txt') as f:
                        lines = f.readlines()
                    lines = [line.rstrip('\n') for line in open('leaderboard.txt')]

                    game.leaders = {'AAA': 0, 'BBB': 0, 'CCC': 0}
                    for i in lines:
                        game.leaders[i.split(' ')[0]] = int(i.split(' ')[1])
                    game.leaders = sorted(game.leaders.items(), key=operator.itemgetter(1), reverse=True)

                    pygame.time.set_timer(pygame.USEREVENT, 1)
                elif event.key == K_RIGHT:
                    if game.name_location != 2:
                        game.name_location += 1
                    else:
                        game.name_location = 0
                    pygame.time.set_timer(pygame.USEREVENT, 1)
                elif event.key == K_LEFT:
                    if game.name_location != 0:
                        game.name_location -= 1
                    else:
                        game.name_location = 2
                    pygame.time.set_timer(pygame.USEREVENT, 1)
                elif event.key == K_UP:
                    ui_variables.click_sound.play()
                    if game.name[game.name_location] != 90:
                        game.name[game.name_location] += 1
                    else:
                        game.name[game.name_location] = 65
                    pygame.time.set_timer(pygame.USEREVENT, 1)
                elif event.key == K_DOWN:
                    ui_variables.click_sound.play()
                    if game.name[game.name_location] != 65:
                        game.name[game.name_location] -= 1
                    else:
                        game.name[game.name_location] = 90
                    pygame.time.set_timer(pygame.USEREVENT, 1)
                
                # game.start = True

    # Start screen
    else:
        for event in pygame.event.get():
            if event.type == QUIT:
                game.done = True
            elif event.type == KEYDOWN:
                if event.key == K_SPACE or not game.start:
                    ui_variables.click_sound.play()
                    game.start = True
        
        game.screen.fill(ui_variables.white)
        pygame.draw.rect(
            game.screen,
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

        leader_1 = ui_variables.h5_i.render('1st ' + game.leaders[0][0] + ' ' + str(game.leaders[0][1]), 1, ui_variables.grey_1)
        leader_2 = ui_variables.h5_i.render('2nd ' + game.leaders[1][0] + ' ' + str(game.leaders[1][1]), 1, ui_variables.grey_1)
        leader_3 = ui_variables.h5_i.render('3rd ' + game.leaders[2][0] + ' ' + str(game.leaders[2][1]), 1, ui_variables.grey_1)

        
        if game.blink:
            game.screen.blit(title_start, (184, 390))
            game.blink = False
        else:
            game.blink = True

        
        game.screen.blit(title_T, (110, 240))
        game.screen.blit(title_E, (170, 240))
        game.screen.blit(title_t, (235, 240))
        game.screen.blit(title_R, (295, 240))
        game.screen.blit(title_I, (375, 240))
        game.screen.blit(title_S, (430, 240))
        
        game.screen.blit(title_info, (110, 700))

        game.screen.blit(leader_1, (20, 20))
        game.screen.blit(leader_2, (20, 46))
        game.screen.blit(leader_3, (20, 72))

        if not game.start:
            pygame.display.update()
            game.clock.tick(3)

pygame.quit()