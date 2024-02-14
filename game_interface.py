import pygame
import pygame_menu
import game_connection
import game_logic
import threading
from typing import Optional 

BACKGROUND = (17, 20, 69)
WINDOW_SIZE = (960, 720)

BOARD_SIZE = game_logic.WIDTH, game_logic.HEIGHT
BOARD_DESLOCATION = (40,30)

CHAT_SIZE = (240, 560)
CHAT_DESLOCATION = (660,30)
FONT_SIZE = 18

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

FPS = 60

IP = None
PORT = None

clock: Optional['pygame.time.Clock'] = None

client: Optional['game_connection.Client_2'] = None
server: Optional['game_connection.Client_2'] = None

main_menu: Optional['pygame_menu.Menu'] = None
host_menu: Optional['pygame_menu.Menu'] = None
search_menu: Optional['pygame_menu.Menu'] = None
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

font = pygame.font.Font(None, FONT_SIZE)

def draw_text(surface, text, color, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

def receive_messages(client, chat_window):
    while True:
        try:
            message = client.receive_message()
            chat_window.add_message(f'Oponente: {message}')
        except Exception as e:
            print("Erro ao receber mensagem:", e)
            break

class ChatWindow:
    def __init__(self, client, surface):
        self.client = client
        self.surface = surface
        self.messages = []
        self.input_box = pygame.Rect(10, CHAT_SIZE[1] - FONT_SIZE - 10, CHAT_SIZE[0] - 20, FONT_SIZE)
        self.text = ''

    def add_message(self, message):
        self.messages.append(message)

    def send_message(self):
        if self.text:
            self.client.send_message(self.text)
            self.add_message(f'Você: {self.text}')
            self.text = ''

    def draw(self):
        self.surface.fill(WHITE)
        for i, message in enumerate(self.messages):
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

def get_host_ip(host_ip):
    global IP
    IP = host_ip

def get_host_port(host_port):
    global PORT
    PORT = host_port

def challenger_screen_play():

    global search_menu

    # -------------------------------------------------------------------------
    # Client Socket
    # -------------------------------------------------------------------------

    client = game_connection.Client_2()
    client.join_room(IP, int(PORT))

    search_menu.disable()
    search_menu.full_reset()
    play_function(client)

def host_screen_play(server):

    global host_menu

    host_menu.disable()
    host_menu.full_reset()
    play_function(server)

def host_match():
    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------

    global main_menu
    global host_menu
    global server

    # -------------------------------------------------------------------------
    # Server Socket
    # -------------------------------------------------------------------------

    server = game_connection.Client_2()
    server.create_room()

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
        f'Compartilhe seu IP e Porta: {server.ip}:{server.port}',
        font_size=20
    )
    host_menu.add.vertical_margin(20)
    host_menu.add.label(
        f'Aguardando...',
        font_size=20
    )

    host_menu.enable()

    main_menu.disable()
    main_menu.full_reset()

    while True:

        clock.tick(60)

        # Application events
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    main_menu.enable()
                    host_menu.disable()
                    host_menu.full_reset()

                    return
        
        if server.client_connected:
            host_screen_play(server)
                
        # Continue playing
        draw_background()

        host_menu.update(events)
        host_menu.draw(surface)
        pygame.display.flip()

        server.wait_connection()

def search_match():

    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------

    global main_menu
    global search_menu
    global clock

    # -------------------------------------------------------------------------
    # Create menu: Search Menu
    # -------------------------------------------------------------------------

    search_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.6,
        theme=default_theme,
        title='Procurar Partida',
        width=WINDOW_SIZE[0] * 0.6,
        mouse_motion_selection=True
    )

    search_menu.add.text_input(
        'IP do Host: ', 
        maxchar=15,
        align=pygame_menu.locals.ALIGN_LEFT, 
        margin=(20,0), 
        cursor=pygame_menu.locals.CURSOR_HAND,
        onchange=get_host_ip
        )
    search_menu.add.vertical_margin(20)
    search_menu.add.text_input(
        'Porta do Host: ', 
        maxchar=5,
        align=pygame_menu.locals.ALIGN_LEFT, 
        margin=(20,0), 
        cursor=pygame_menu.locals.CURSOR_HAND,
        onchange=get_host_port
        )
    search_menu.add.vertical_margin(40)
    search_menu.add.button(
        'Entrar', 
        challenger_screen_play,
        cursor=pygame_menu.locals.CURSOR_HAND
        )
    
    search_menu.enable()

    main_menu.disable()
    main_menu.full_reset()

    while True:

        clock.tick(60)

        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    main_menu.enable()
                    search_menu.disable()
                    search_menu.full_reset()

                    return
                
        # Continue playing
        draw_background()

        search_menu.update(events)
        search_menu.draw(surface)
        pygame.display.flip()

def play_function(player):

    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------

    global main_menu
    global search_menu
    global clock
    global IP
    global PORT

    board = [[-1, -1,  1,  1,  1, -1, -1],
            [-1, -1,  1,  1,  1, -1, -1],
            [ 1,  1,  1,  1,  1,  1,  1],
            [ 1,  1,  1,  0,  1,  1,  1],
            [ 1,  1,  1,  1,  1,  1,  1],
            [-1, -1,  1,  1,  1, -1, -1],
            [-1, -1,  1,  1,  1, -1, -1]]

    board_surface = pygame.Surface(BOARD_SIZE)
    chat_surface = pygame.Surface(CHAT_SIZE)
    chat_window = ChatWindow(player, chat_surface)
    threading.Thread(target=receive_messages, args=(player, chat_window)).start()
    selected_piece = None

    while True:

        clock.tick(30)

        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                exit()
            
            elif e.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if(pos_on_board(pos)):
                    row = (pos[1] - BOARD_DESLOCATION[1]) // game_logic.SQUARE_SIZE
                    col = (pos[0] - BOARD_DESLOCATION[0]) // game_logic.SQUARE_SIZE

                    if selected_piece is None:
                        if board[row][col] == 1:
                            selected_piece = (row, col)
                    else:
                        if game_logic.is_valid_move(board, selected_piece, (row, col)):
                            board[selected_piece[0]][selected_piece[1]] = 0
                            board[(selected_piece[0] + row) // 2][(selected_piece[1] + col) // 2] = 0
                            board[row][col] = 1
                            if game_logic.game_over(board):
                                print("Fim de Jogo")
                                
                                #return
                        selected_piece = None
            chat_window.handle_event(e)
        
        # Continue playing
        draw_background()

        surface.blit(chat_surface, (CHAT_DESLOCATION))
        surface.blit(board_surface, (BOARD_DESLOCATION))

        chat_window.draw()
        game_logic.draw_board(board_surface, board, selected_piece)

        pygame.display.flip()


def draw_interface():

    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------
    global clock
    global main_menu
    global surface

    pygame.init()

    # -------------------------------------------------------------------------
    # Create window
    # -------------------------------------------------------------------------
    surface = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

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
        search_match, 
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
                exit()

        if main_menu.is_enabled():
            main_menu.mainloop(surface, draw_background, fps_limit=FPS)

        pygame.display.flip()
