import Pyro4

@Pyro4.expose
class Player:
    def __init__(self, name, server):
        self.name = name
        self.match = server

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Match:
    def __init__(self):
        self.board = [[-1, -1,  1,  1,  1, -1, -1],
                      [-1, -1,  1,  1,  1, -1, -1],
                      [ 1,  1,  1,  1,  1,  1,  1],
                      [ 1,  1,  1,  0,  1,  1,  1],
                      [ 1,  1,  1,  1,  1,  1,  1],
                      [-1, -1,  1,  1,  1, -1, -1],
                      [-1, -1,  1,  1,  1, -1, -1]]
        self.players = []
        self.messages = []
        self.current_player = None
        self.surrender_player = None

    def get_board(self):
        return self.board

    def get_current_player(self):
        return self.current_player
    
    def get_players_len(self):
        return len(self.players)

    def get_surrender_player(self):
        return self.surrender_player
    
    def get_messages(self):
        return self.messages

    def register_message(self, message):
        self.messages.append(message)

    def register_surrender(self):
        self.surrender_player = self.current_player

    def register_player(self, player_id):
        self.players.append(player_id)
        self.current_player = self.players[0]
    
    def is_valid_move(self, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        if self.board[start_row][start_col] == 1 and self.board[end_row][end_col] == 0:
            if abs(start_row - end_row) == 2 and abs(start_col - end_col) == 0:
                if self.board[(start_row + end_row) // 2][start_col] == 1:
                    return True
            elif abs(start_col - end_col) == 2 and abs(start_row - end_row) == 0:
                if self.board[start_row][(start_col + end_col) // 2] == 1:
                    return True
        return False

    def check_winner(self, player_id):
        piece_count = sum(row.count(1) for row in self.board)
        if piece_count == 1 and player_id != self.current_player:
            return 1    # Venceu
        elif piece_count == 1 and player_id != self.current_player:
            return 0    # Perdeu
        for row in range(7):
            for col in range(7):
                if self.board[row][col] == 1:
                    if (row >= 2 and self.board[row-1][col] == 1 and self.board[row-2][col] == 0) or \
                    (row <= 4 and self.board[row+1][col] == 1 and self.board[row+2][col] == 0) or \
                    (col >= 2 and self.board[row][col-1] == 1 and self.board[row][col-2] == 0) or \
                    (col <= 4 and self.board[row][col+1] == 1 and self.board[row][col+2] == 0):
                        return -1   # Continua
        return 2    # Empate

    def make_move(self, start_pos, end_pos):
        if self.is_valid_move(start_pos, end_pos):
            start_row, start_col = start_pos
            end_row, end_col = end_pos

            self.board[start_row][start_col] = 0
            self.board[(start_row + end_row) // 2][(start_col + end_col) // 2] = 0
            self.board[end_row][end_col] = 1

            self.current_player = self.players[0] if self.current_player == self.players[1] else self.players[1]

def start_server():
    daemon = Pyro4.Daemon()
    uri = daemon.register(Match)
    Pyro4.locateNS().register("match.server", uri)
    print("Aguardando conexões...")
    daemon.requestLoop()
    