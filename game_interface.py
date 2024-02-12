import pygame
import pygame_menu
import resta1
from typing import Optional 

BACKGROUND = (17, 20, 69)
BTN_BACKGROUND=(75, 79, 81)

BOARD_SIZE = resta1.WIDTH, resta1.HEIGHT
BOARD_DESLOCATION = (40,30)

CHAT_SIZE = (240, 560)
CHAT_DESLOCATION = (660,30)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

FPS = 60
WINDOW_SIZE = (960, 720)

clock: Optional['pygame.time.Clock'] = None

main_menu: Optional['pygame_menu.Menu'] = None
search_menu: Optional['pygame_menu.Menu'] = None
play_menu: Optional['pygame_menu.Menu'] = None

surface: Optional['pygame.Surface'] = None

theme = pygame_menu.Theme(
            background_color=pygame_menu.themes.TRANSPARENT_COLOR,
            title=False,
            widget_font=pygame_menu.font.FONT_FIRACODE,
            widget_font_color=(255, 255, 255),
            widget_margin=(0, 15),
            widget_selection_effect=pygame_menu.widgets.NoneSelection()
)

def pos_on_board(pos):
    return BOARD_DESLOCATION[1] <= pos[1] < BOARD_SIZE[1] + BOARD_DESLOCATION[1] and \
           BOARD_DESLOCATION[0] <= pos[0] < BOARD_SIZE[0] + BOARD_DESLOCATION[0]

def draw_background():
    global surface
    surface.fill((BACKGROUND))

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

    search_theme = pygame_menu.themes.THEME_DARK.copy()

    search_theme.widget_font=pygame_menu.font.FONT_NEVIS
    search_theme.title_font=pygame_menu.font.FONT_NEVIS

    search_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.6,
        theme=search_theme,
        title='Procurar Partida',
        width=WINDOW_SIZE[0] * 0.6,
        mouse_motion_selection=True
    )

    search_menu.add.text_input(
        'IP do Host: ', 
        maxchar=15,
        align=pygame_menu.locals.ALIGN_LEFT, 
        margin=(20,0), 
        cursor=pygame_menu.locals.CURSOR_HAND
        )
    search_menu.add.vertical_margin(20)
    search_menu.add.text_input(
        'Porta do Host: ', 
        maxchar=5,
        align=pygame_menu.locals.ALIGN_LEFT, 
        margin=(20,0), 
        cursor=pygame_menu.locals.CURSOR_HAND
        )
    search_menu.add.vertical_margin(40)
    search_menu.add.button(
        'Entrar', 
        play_function,
        cursor=pygame_menu.locals.CURSOR_HAND
        )
    
    search_menu.enable()

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
                    search_menu.disable()
                    search_menu.full_reset()

                    return
                
        # Continue playing
        draw_background()

        search_menu.update(events)
        search_menu.draw(surface)
        pygame.display.flip()

def play_function():

    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------

    global main_menu
    global search_menu
    global clock

    board = [[-1, -1,  1,  1,  1, -1, -1],
            [-1, -1,  1,  1,  1, -1, -1],
            [ 1,  1,  1,  1,  1,  1,  1],
            [ 1,  1,  1,  0,  1,  1,  1],
            [ 1,  1,  1,  1,  1,  1,  1],
            [-1, -1,  1,  1,  1, -1, -1],
            [-1, -1,  1,  1,  1, -1, -1]]

    board_surface = pygame.Surface(BOARD_SIZE)
    chat_surface = pygame.Surface(CHAT_SIZE)
    selected_piece = None

    search_menu.disable()
    search_menu.full_reset()

    while True:

        clock.tick(60)

        # Application events
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    search_menu.enable()

                    return
            elif e.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if(pos_on_board(pos)):
                    row = (pos[1] - BOARD_DESLOCATION[1]) // resta1.SQUARE_SIZE
                    col = (pos[0] - BOARD_DESLOCATION[0]) // resta1.SQUARE_SIZE

                    if selected_piece is None:
                        if board[row][col] == 1:
                            selected_piece = (row, col)
                    else:
                        if resta1.is_valid_move(board, selected_piece, (row, col)):
                            board[selected_piece[0]][selected_piece[1]] = 0
                            board[(selected_piece[0] + row) // 2][(selected_piece[1] + col) // 2] = 0
                            board[row][col] = 1
                            if resta1.game_over(board):
                                print("Fim de Jogo")

                                search_menu.enable()
                                return
                        selected_piece = None
        
        # Continue playing
        draw_background()

        surface.blit(board_surface, (BOARD_DESLOCATION))

        chat_surface.fill(WHITE)
        surface.blit(chat_surface, (CHAT_DESLOCATION))
        resta1.draw_board(board_surface, board, selected_piece)

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

    main_theme = pygame_menu.themes.THEME_DARK.copy()

    main_theme.widget_font=pygame_menu.font.FONT_NEVIS
    main_theme.title_font=pygame_menu.font.FONT_NEVIS

    main_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.5,
        theme=main_theme,
        title='Menu Principal',
        width=WINDOW_SIZE[0] * 0.5,
        mouse_motion_selection=True
    )

    main_menu.add.button(
        'Criar um Jogo', 
        pygame_menu.events.NONE, 
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

        # Tick
        clock.tick(FPS)

        # Paint background
        draw_background()

        # Application events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        # Main menu
        if main_menu.is_enabled():
            main_menu.mainloop(surface, draw_background, fps_limit=FPS)

        # Flip surface
        pygame.display.flip()
