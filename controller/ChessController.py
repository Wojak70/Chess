from model.ChessEngine import *
from strategy.RandomStrategy import MoveStrategy

class ChessController:
    """
    Inicjalizacja kontrolera gry:
    - tworzy nowy stan gry (GameState),
    - ustawia strategię AI (jeśli podano),
    - generuje początkową listę legalnych ruchów.
    """
    def __init__(self, white_strategy: MoveStrategy = None, black_strategy: MoveStrategy = None):
        self.gs = GameState()
        self.white_strategy = white_strategy
        self.black_strategy = black_strategy
        self.valid_moves = self.gs.getValidMoves()
        self.move_made = False # Flaga: czy wykonano ruch
        self.animate = False # Flaga: czy należy animować ruch

    def reset_game(self):
        """
        Resetuje stan gry, zachowując strategię AI.
        """
        self.__init__(self.white_strategy, self.black_strategy)

    def handle_click(self, row, col, player_clicks, sq_selected):
        """
        Obsługuje kliknięcia użytkownika na planszy.
        Zwraca:
        - nowy wybrany kwadrat (sq_selected),
        - zaktualizowaną listę kliknięć (player_clicks),
        - ewentualny ruch z promocją (do potwierdzenia przez gracza).
        """
        if sq_selected == (row, col):
            # Ponowne kliknięcie tego samego pola – cofnięcie wyboru
            return (), [], None
        else:
            # Zaznacz nowe pole i zapisz wybór
            sq_selected = (row, col)
            player_clicks.append(sq_selected)
            if len(player_clicks) == 2:
                # Próba wykonania ruchu
                move = Move(player_clicks[0], player_clicks[1], self.gs.board)
                for valid_move in self.valid_moves:
                    if move == valid_move:
                        # Jeśli ruch to promocja pionka – nie wykonuj jeszcze, zapytaj gracza
                        if valid_move.isPawnPromotion:
                            return (), [], valid_move  # NIE wykonujemy jeszcze
                        # Wykonanie zwykłego ruchu
                        self.gs.makeMove(valid_move)
                        self.move_made = True
                        self.animate = True
                        return (), [], None
                # Nielegalny ruch – zresetuj do ostatniego wyboru
                return sq_selected, [sq_selected], None
            return sq_selected, player_clicks, None

    def handle_undo(self):
        """
        Cofa ostatni ruch w grze.
        """
        self.gs.undoMove()
        self.move_made = True
        self.animate = False

    def update_after_move(self):
        """
        Aktualizuje listę legalnych ruchów po wykonaniu ruchu.
        Resetuje flagi.
        """
        if self.move_made:
            self.valid_moves = self.gs.getValidMoves()
            self.move_made = False
            self.animate = False

    def get_ai_move(self):
        """
        Jeśli obecny gracz ma przypisaną strategię AI – wybiera ruch.
        Zwraca wybrany ruch lub None.
        """
        current_strategy = self.white_strategy if self.gs.whiteToMove else self.black_strategy
        if current_strategy:
            return current_strategy.select_move(self.gs, self.valid_moves)
        return None
