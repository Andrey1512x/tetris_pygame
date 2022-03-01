import random
import sys

import pygame
from tetriminos import *

"""
10 x 20 grid
play_height = 2 * play_width

tetriminos:
    0 - S - зеленый
    1 - Z - красный
    2 - I - циановый
    3 - O - желтый
    4 - J - синий
    5 - L - оранжевый
    6 - T - фиолетовый
"""

pygame.font.init()

# Глобальные константы

col = 10
row = 20
s_width = 900
s_height = 750
play_width = 300
play_height = 600
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

# Требуемые файлы
filepath = "highscore.txt"
fontpath = "troubleside.ttf"
fontpath_mario = "mario.ttf"

# ФИгуры
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


# Класс фигуры


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


# инициализация сетки
def create_grid(locked_pos=None):
    if locked_pos is None:
        locked_pos = {}
    grid = [[(0, 0, 0) for x in range(col)] for y in range(row)]

    # Строение словаря
    # (x, y):(r, g, b)
    for y in range(row):
        for x in range(col):
            if (x, y) in locked_pos:
                color = locked_pos[
                    (x, y)]
                grid[y][x] = color

    return grid


def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    '''
    e.g.
       ['.....',
        '.....',
        '..00.',
        '.00..',
        '.....']
    '''
    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(piece, grid):
    # Список возможных позиций
    accepted_pos = [[(x, y) for x in range(col) if grid[y][x] == (0, 0, 0)] for y in range(row)]
    accepted_pos = [x for item in accepted_pos for x in item]

    formatted_shape = convert_shape_format(piece)

    for pos in formatted_shape:
        if pos not in accepted_pos:
            if pos[1] >= 0:
                return False
    return True


# проверка на нахождение фигуры в сетке
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


# выбор фигуры
def get_shape():
    return Piece(5, 0, random.choice(shapes))


# создает текст посередине экрана
def draw_text_middle(text, size, color, surface):
    font = pygame.font.Font(fontpath, size)
    label1 = font.render(text[0], True, color)
    label2 = font.render(text[1], True, color)

    surface.blit(label1, (
        top_left_x + play_width/2 - (label1.get_width()/2), top_left_y + play_height/2 - (label1.get_height()/2)))
    surface.blit(label2, (
        top_left_x + play_width / 2 - (label2.get_width() / 2), top_left_y + play_height / 2 - (label2.get_height() / 2) + 50))


# draws the lines of the grid for the game
def draw_grid(surface):
    r = g = b = 0
    grid_color = (r, g, b)

    for i in range(row):
        pygame.draw.line(surface, grid_color, (top_left_x, top_left_y + i * block_size),
                         (top_left_x + play_width, top_left_y + i * block_size))

        for j in range(col):
            pygame.draw.line(surface, grid_color, (top_left_x + j * block_size, top_left_y),
                             (top_left_x + j * block_size, top_left_y + play_height))


# удаление заполненной линии
def clear_rows(grid, locked):
    # последовательная проверка слоев
    increment = 0
    for i in range(len(grid) - 1, -1, -1):
        grid_row = grid[i]
        if (0, 0, 0) not in grid_row:
            increment += 1
            index = i
            for j in range(len(grid_row)):
                try:
                    del locked[(j, i)]
                except ValueError:
                    continue

    if increment > 0:
        # sort the locked list according to y value in (x,y) and then reverse
        # reversed because otherwise the ones on the top will overwrite the lower ones
        for key in sorted(list(locked), key=lambda a: a[1])[::-1]:
            x, y = key
            if y < index:                       # if the y value is above the removed index
                new_key = (x, y + increment)    # shift position to down
                locked[new_key] = locked.pop(key)

    return increment


# draws the upcoming piece
def draw_next_shape(piece, surface):
    font = pygame.font.Font(fontpath, 30)
    label = font.render('Next shape', 1, (255, 255, 255))

    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100) - 10

    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (start_x + j*block_size, start_y + i*block_size + 20, block_size, block_size), 0)

    surface.blit(label, (start_x, start_y))

    # pygame.display.update()


# draws the content of the window
def draw_window(surface, grid, score=0, last_score=0):
    surface.fill((0, 0, 0))  # fill the surface with black

    pygame.font.init()  # initialise font
    font = pygame.font.Font(fontpath_mario, 65, bold=True)
    label = font.render('TETRIS', 1, (255, 255, 255))  # initialise 'Tetris' text with white

    surface.blit(label, ((top_left_x + play_width / 2) - (label.get_width() / 2), 30))  # put surface on the center of the window

    # current score
    font = pygame.font.Font(fontpath, 30)
    label = font.render("SCORE", 1, (255, 255, 255))

    start_x = top_left_x - 280
    start_y = top_left_y + 250
    surface.blit(label, (start_x, start_y + 200))

    label = font.render(str(score), 1, (255, 255, 255))

    start_x = top_left_x - 280
    start_y = top_left_y + 290

    surface.blit(label, (start_x, start_y + 200))

    # last score
    label_hi = font.render("HIGHSCORE", 1, (255, 255, 255))

    start_x_hi = top_left_x - 280
    start_y_hi = top_left_y + (play_height / 2 - 100) - 10
    surface.blit(label_hi, (start_x_hi, start_y_hi))

    label_hi = font.render(str(last_score), 1, (255, 255, 255))

    start_x_hi = top_left_x - 280
    start_y_hi = top_left_y + 240
    surface.blit(label_hi, (start_x_hi, start_y_hi))

    # controls

    label = font.render("PRESS <R>", 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100) + 160

    surface.blit(label, (start_x, start_y))

    label = font.render("FOR RESTART", 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100) + 200

    surface.blit(label, (start_x, start_y))

    label = font.render("PRESS <ESC>", 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100) + 240

    surface.blit(label, (start_x, start_y))

    label = font.render("FOR EXIT", 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100) + 280

    surface.blit(label, (start_x, start_y))

    # draw content of the grid
    for i in range(row):
        for j in range(col):
            # pygame.draw.rect()
            # draw a rectangle shape
            # rect(Surface, color, Rect, width=0) -> Rect
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # draw vertical and horizontal grid lines
    draw_grid(surface)

    # draw rectangular border around play area
    border_color = (255, 255, 255)
    pygame.draw.rect(surface, border_color, (top_left_x, top_left_y, play_width, play_height), 4)

    # pygame.display.update()


# update the score txt file with high score
def update_score(new_score):
    score = get_max_score()

    with open(filepath, 'w') as file:
        if new_score > score:
            file.write(str(new_score))
        else:
            file.write(str(score))


# get the high score from the file
def get_max_score():
    with open(filepath, 'r') as file:
        lines = file.readlines()        # reads all the lines and puts in a list
        score = int(lines[0].strip())   # remove \n

    return score


def main(window):
    locked_positions = {}
    create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.35
    level_time = 0
    score = 0
    last_score = get_max_score()

    while run:
        # need to constantly make new grid as locked positions always change
        grid = create_grid(locked_positions)

        # helps run the same on every computer
        # add time since last tick() to fall_time
        fall_time += clock.get_rawtime()  # returns in milliseconds
        level_time += clock.get_rawtime()

        clock.tick()  # updates clock

        if level_time/1000 > 5:    # make the difficulty harder every 10 seconds
            level_time = 0
            if fall_speed > 0.15:   # until fall speed is 0.15
                fall_speed -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                # since only checking for down - either reached bottom or hit another piece
                # need to lock the piece position
                # need to generate new piece
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1  # move x position left
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1  # move x position right
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1

                elif event.key == pygame.K_DOWN:
                    # move shape down
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                elif event.key == pygame.K_UP:
                    # rotate shape
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)
                elif event.key == pygame.K_r:
                    main(screen)
                elif event.key == pygame.K_ESCAPE:
                    sys.exit(1)

        piece_pos = convert_shape_format(current_piece)

        # draw the piece on the grid by giving color in the piece locations
        for i in range(len(piece_pos)):
            x, y = piece_pos[i]
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:  # if the piece is locked
            for pos in piece_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color       # add the key and value in the dictionary
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10    # increment score by 10 for every row cleared
            update_score(score)

            if last_score < score:
                last_score = score

        draw_window(window, grid, score, last_score)
        draw_next_shape(next_piece, window)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    draw_text_middle(("You Lost", ""), 40, (255, 255, 255), window)
    pygame.display.update()
    pygame.time.delay(2000)  # wait for 2 seconds
    pygame.quit()


def main_menu(screen):
    run = True
    while run:
        draw_text_middle((" Для продолжения", "нажмите любую кнопку"), 40, (255, 255, 255), screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                main(screen)

    pygame.quit()


if __name__ == "__main__":
    screen = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption("Тетрис")

    main_menu(screen)
