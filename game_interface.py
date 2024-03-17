import pygame
import pygame.font
import pygame_menu
import game_connection
import sys
import pickle
import time
import Pyro4
from typing import Optional 
from threading import Thread

BACKGROUND = (17, 20, 69)
WINDOW_SIZE = (960, 720)

BOARD_SIZE = 560, 560
BOARD_DESLOCATION = (40,30)

CHAT_SIZE = (240, 560)
CHAT_DESLOCATION = (660,30)
FONT_SIZE = 18

BOARD_WHITE = (200, 200, 200)
BOARD_BLACK = (40, 41, 35)
RED = (128, 0, 0)
GREEN = (0, 128, 0)

SQUARE_SIZE = 560 // 7

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

FPS = 30

clock: Optional['pygame.time.Clock'] = None

player: Optional['game_connection.Player'] = None

font: Optional['pygame.font.Font'] = None

main_menu: Optional['pygame_menu.Menu'] = None
host_menu: Optional['pygame_menu.Menu'] = None
play_menu: Optional['pygame_menu.Menu'] = None

surface: Optional['pygame.Surface'] = None

default_theme = pygame_menu.Theme(
    background_color=(40, 41, 35),
    cursor_color=(255, 255, 255),
    cursor_selection_color=(80, 80, 80, 120),
    scrollbar_color=(39, 41, 42),
    scrollbar_slider_color=(65, 66, 67),
    scrollbar_slider_hover_color=(90, 89, 88),
    selection_color=(255, 255, 255),
    title_background_color=(47, 48, 51),
    title_font_color=(215, 215, 215),
    widget_font_color=(200, 200, 200),
    widget_font=pygame_menu.font.FONT_NEVIS,
    title_font=pygame_menu.font.FONT_NEVIS
)

def draw_text(surface, text, color, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

def end_game(game_state):

    global font
    global surface

    counter = pygame.time.Clock()

    seconds = 10

    # -------------------------------------------------------------------------
    # Create menu: End Menu
    # -------------------------------------------------------------------------

    end_menu = pygame_menu.Menu (
        height=WINDOW_SIZE[1] * 0.6,
        theme=default_theme,
        title='Fim do jogo',
        width=WINDOW_SIZE[0] * 0.6
    )

    time_label = end_menu.add.label(
        f"Encerrando em {seconds} segundos...",
        font_size=FONT_SIZE
    )
    end_menu.add.vertical_margin(20)
    end_menu.add.label(
        f"Resultado da partida: {game_state}",
        font_size=FONT_SIZE
    )

    while seconds > 0:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_background()
        end_menu.update(events)
        end_menu.draw(surface)
        pygame.display.flip()

        counter.tick(1)
        seconds -= 1
        time_label.set_title(f"Encerrando em {seconds} segundos...")
    
    pygame.quit()
    sys.exit()

class ChatWindow:
    def __init__(self, player, surface):
        self.player = player
        self.surface = surface
        self.input_box = pygame.Rect(10, CHAT_SIZE[1] - FONT_SIZE - 10, CHAT_SIZE[0] - 20, FONT_SIZE)
        self.text = ''

    def add_message(self, message):
        self.player.match.register_message(message)

    def send_message(self):
        if self.text:
            self.add_message(f'{self.player.name}: {self.text}')
            self.text = ''

    def draw(self):
        self.surface.fill(WHITE)
        for i, message in enumerate(self.player.match.get_messages()):
            draw_text(self.surface, message, BLACK, 10, i * FONT_SIZE)
        pygame.draw.rect(self.surface, BLACK, self.input_box, 2)
        draw_text(self.surface, self.text, BLACK, self.input_box.x + 5, self.input_box.y + 5)
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.send_message()
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

def pos_on_board(pos):
    return BOARD_DESLOCATION[1] <= pos[1] < BOARD_SIZE[1] + BOARD_DESLOCATION[1] and \
           BOARD_DESLOCATION[0] <= pos[0] < BOARD_SIZE[0] + BOARD_DESLOCATION[0]

def draw_background():
    global surface
    surface.fill((BACKGROUND))

def challenger_screen_play():

    global main_menu

    # -------------------------------------------------------------------------
    # Second Player
    # -------------------------------------------------------------------------

    server = Pyro4.Proxy("PYRONAME:match.server")
    player = game_connection.Player("Second", server)
    server.register_player(player.name)

    main_menu.disable()
    main_menu.full_reset()
    play_function(player)

def host_screen_play(player):

    global host_menu

    host_menu.disable()
    host_menu.full_reset()
    play_function(player)

def host_match():
    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------

    global main_menu
    global host_menu
    global first_player
    global surface

    # -------------------------------------------------------------------------
    # First Player
    # -------------------------------------------------------------------------

    #game_connection.start_server()
    server = Pyro4.Proxy("PYRONAME:match.server")
    player = game_connection.Player("First", server)
    server.register_player(player.name)

    # -------------------------------------------------------------------------
    # Create menu: Host Menu
    # -------------------------------------------------------------------------

    host_menu = pygame_menu.Menu (
        height=WINDOW_SIZE[1] * 0.6,
        theme=default_theme,
        title='Criando Partida',
        width=WINDOW_SIZE[0] * 0.6
    )

    host_menu.add.label(
        f'Aguardando outro jogador...',
        font_size=20
    )

    host_menu.enable()

    main_menu.disable()
    main_menu.full_reset()

    while True:

        clock.tick(FPS)

        # Application events
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    main_menu.enable()
                    host_menu.disable()
                    host_menu.full_reset()
                    return
        
        if player.match.get_players_len() == 2:
            host_screen_play(player)
                
        # Continue playing
        draw_background()

        host_menu.update(events)
        host_menu.draw(surface)
        pygame.display.flip()

def play_function(player):

    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------

    global main_menu
    global clock
    global board
    global turn_order
    global surrender_flag

    board_surface = pygame.Surface(BOARD_SIZE)
    chat_surface = pygame.Surface(CHAT_SIZE)
    chat_window = ChatWindow(player, chat_surface)

    server = player.match

    selected_piece = None

    surrender_btn = pygame.Rect(380, 650, 100, 50)
    surrender_txt = pygame.font.Font(None, 36).render("Desistir", True, BLACK)
    surrender_txt_rect = surrender_txt.get_rect(center=surrender_btn.center)

    while True:

        clock.tick(FPS)

        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                server.register_surrender()
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if surrender_btn.collidepoint(e.pos):
                    server.register_surrender()
                    end_game('Desistiu')
                elif server.get_current_player() == player.name:
                    if(pos_on_board(pos)):
                        row = (pos[1] - BOARD_DESLOCATION[1]) // SQUARE_SIZE
                        col = (pos[0] - BOARD_DESLOCATION[0]) // SQUARE_SIZE

                        if selected_piece is None:
                            if server.get_board()[row][col] == 1:
                                selected_piece = (row, col)
                        else:
                            server.make_move(selected_piece, (row,col))
                            selected_piece = None

            if server.check_winner(player.name) == 2:
                end_game('Empate')
            elif server.check_winner(player.name) == 1:
                end_game('Voce venceu')
            elif server.check_winner(player.name) == 0:
                end_game('Voce perdeu')
            
            if server.get_surrender_player() != None:
                end_game('Seu oponente desistiu')

            chat_window.handle_event(e)
        
        # Continue playing
        draw_background()

        surface.blit(chat_surface, (CHAT_DESLOCATION))
        surface.blit(board_surface, (BOARD_DESLOCATION))
        pygame.draw.rect(surface, WHITE, surrender_btn)
        surface.blit(surrender_txt, surrender_txt_rect)

        chat_window.draw()
        draw_board(board_surface, selected_piece, server.get_board())

        pygame.display.flip()

def draw_board(screen, selected_piece, board):
        screen.fill(BOARD_WHITE)
        for row in range(7):
            for col in range(7):
                pygame.draw.rect(screen, BOARD_BLACK, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 1)
                if selected_piece != None and row == selected_piece[0] and col == selected_piece[1]:
                    pygame.draw.circle(screen, GREEN, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 3)
                elif board[row][col] == 1:
                    pygame.draw.circle(screen, RED, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 3)
                elif board[row][col] == -1:
                    pygame.draw.rect(screen, BOARD_BLACK, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_interface():

    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------
    global clock
    global main_menu
    global surface
    global font

    pygame.init()

    # -------------------------------------------------------------------------
    # Create window
    # -------------------------------------------------------------------------
    surface = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, FONT_SIZE)

    # -------------------------------------------------------------------------
    # Create menu: Main Menu
    # -------------------------------------------------------------------------

    main_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.5,
        theme=default_theme,
        title='Menu Principal',
        width=WINDOW_SIZE[0] * 0.5,
        mouse_motion_selection=True
    )

    main_menu.add.button(
        'Criar um Jogo', 
        host_match, 
        align=pygame_menu.locals.ALIGN_LEFT, 
        margin=(20,0), 
        cursor=pygame_menu.locals.CURSOR_HAND
    )
    main_menu.add.vertical_margin(20)
    main_menu.add.button(
        'Entrar em um Jogo', 
        challenger_screen_play, 
        align=pygame_menu.locals.ALIGN_LEFT,
        margin=(20,0), 
        cursor=pygame_menu.locals.CURSOR_HAND
    )
    main_menu.add.vertical_margin(20)
    main_menu.add.button(
        'Sair do Jogo',
        pygame_menu.events.EXIT, 
        align=pygame_menu.locals.ALIGN_LEFT, 
        margin=(20,0), 
        cursor=pygame_menu.locals.CURSOR_HAND
    )

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------

    while True:

        clock.tick(FPS)

        draw_background()

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if main_menu.is_enabled():
            main_menu.mainloop(surface, draw_background, fps_limit=FPS)

        pygame.display.flip()
