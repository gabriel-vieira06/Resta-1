import pygame
import sys

# Inicialização do Pygame
pygame.init()

# Definição de algumas constantes
WIDTH, HEIGHT = 560, 560
ROW_COUNT, COL_COUNT = 7, 7
SQUARE_SIZE = WIDTH // COL_COUNT

# Definição das cores
WHITE = (200, 200, 200)
BLACK = (40, 41, 35)
RED = (128, 0, 0)
GREEN = (0, 128, 0)

# Função para desenhar o tabuleiro
def draw_board(screen, board, selected_piece):

    screen.fill(WHITE)
    for row in range(ROW_COUNT):
        for col in range(COL_COUNT):
            pygame.draw.rect(screen, BLACK, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 1)
            if selected_piece != None and row == selected_piece[0] and col == selected_piece[1]:
                pygame.draw.circle(screen, GREEN, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 3)
            elif board[row][col] == 1:
                pygame.draw.circle(screen, RED, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 3)
            elif board[row][col] == -1:
                pygame.draw.rect(screen, BLACK, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Função para validar movimentos
def is_valid_move(board, start_pos, end_pos):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    if board[start_row][start_col] == 1 and board[end_row][end_col] == 0:
        if abs(start_row - end_row) == 2 and abs(start_col - end_col) == 0:
            if board[(start_row + end_row) // 2][start_col] == 1:
                return True
        elif abs(start_col - end_col) == 2 and abs(start_row - end_row) == 0:
            if board[start_row][(start_col + end_col) // 2] == 1:
                return True
    return False

# Função para verificar se o jogo acabou
def game_over(board, my_turn):

    piece_count = sum(row.count(1) for row in board)

    if piece_count == 1 and my_turn == True:
        return 1    # Venceu
    elif piece_count == 1 and my_turn == False:
        return 0    # Perdeu

    for row in range(ROW_COUNT):
        for col in range(COL_COUNT):
            if board[row][col] == 1:
                if (row >= 2 and board[row-1][col] == 1 and board[row-2][col] == 0) or \
                   (row <= ROW_COUNT-3 and board[row+1][col] == 1 and board[row+2][col] == 0) or \
                   (col >= 2 and board[row][col-1] == 1 and board[row][col-2] == 0) or \
                   (col <= COL_COUNT-3 and board[row][col+1] == 1 and board[row][col+2] == 0):
                    return -1   # Continua

    return 2    # Empate
