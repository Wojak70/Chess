from strategy.BaseStrategy import MoveStrategy
# Wartości punktowe figur (K - król, p - pionek, N - skoczek, B - goniec, R - wieża, Q - hetman)
pieceScore = {"K": 0, "p": 1, "N": 3, "B": 3, "R": 5, "Q": 9}
CHECKMATE = 1000 # Wartość punktowa matu
STALEMATE = 0 # Wartość punktowa patu

class AlphaBetaStrategy(MoveStrategy):
    '''Wybiera ruch na podstawie algorytmu alphaBeta'''
    def __init__(self, depth=3):
        self.depth = depth # Maksymalna głębokość przeszukiwania drzewa ruchów
    
    def select_move(self, gs, valid_moves):
         # Ustal mnożnik dla ruchu: 1 dla białych, -1 dla czarnych
        turnMultiplier = 1 if gs.whiteToMove else -1
        bestMove = None # Najlepszy znaleziony ruch
        maxScore = -CHECKMATE # Najwyższy wynik (inicjalizacja na bardzo niską wartość)
        # Przeszukaj wszystkie możliwe ruchy
        for move in valid_moves:
            gs.makeMove(move)# Wykonaj ruch
            # Oblicz wynik po ruchu, negując, bo zmieniamy stronę na przeciwnika (negamax)

            score = -self.alpha_beta(gs, self.depth - 1, -CHECKMATE, CHECKMATE, -turnMultiplier)
            gs.undoMove() # Cofnij ruch
            # Jeśli znaleziony wynik jest lepszy, zapamiętaj ten ruch
            if score > maxScore:
                maxScore = score
                bestMove = move
        # Zwróć najlepszy ruch, albo pierwszy ruch jeśli lista jest pusta
        return bestMove or (valid_moves[0] if valid_moves else None)

    def alpha_beta(self, gs, depth, alpha, beta, turnMultiplier):
        # Jeśli osiągnięto głębokość 0, ocen planszę
        if depth == 0:
            return turnMultiplier * self.score_board(gs)
        # Pobierz aktualne możliwe ruchy
        valid_moves = gs.getValidMoves()
        # Jeśli brak ruchów: sprawdź czy jest mat lub pat
        if len(valid_moves) == 0:
            return -CHECKMATE + depth if gs.inCheck else STALEMATE
        # Sortuj ruchy, aby priorytet miały bicie (przyspieszenie alfa-beta)
        valid_moves.sort(key=lambda m: m.isCapture, reverse=True)
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.makeMove(move)  # Wykonaj ruch
            # Rekurencyjnie wywołaj algorytm dla ruchu przeciwnika, zmieniając alfa i beta
            score = -self.alpha_beta(gs, depth - 1, -beta, -alpha, -turnMultiplier)
            gs.undoMove() # Cofnij ruch
            # Aktualizuj maksymalny wynik
            if score > max_score:
                max_score = score
             # Aktualizuj alfa - najlepszy wynik dla maksymalizującego gracza
            alpha = max(alpha, score)
            # Jeśli alfa >= beta, można przerwać dalsze przeszukiwanie (cięcie alfa-beta)
            if alpha >= beta:
                break
        return max_score # Zwróć najlepszy wynik

    def score_board(self, gs):
        score = 0 # Suma punktów planszy
        # Iteruj po każdym polu planszy
        for row in gs.board:
            for sq in row:
                if sq != "--": # Jeśli pole nie jest puste
                    val = pieceScore.get(sq[1], 0) # Pobierz wartość figury (drugi znak w stringu)
                    # Dodaj lub odejmij wartość w zależności od koloru figury
                    score += val if sq[0] == "w" else -val

        mobility = len(gs.getValidMoves()) * 0.1 # Premia za mobilność (ilość ruchów * 0.1)
        # Dodaj lub odejmij premię za mobilność w zależności od aktualnego gracza
        score += mobility if gs.whiteToMove else -mobility
        # Kara za bycie w szachu (0.5 pkt)
        if gs.inCheck:
            score -= 0.5 if gs.whiteToMove else -0.5

        return score # Zwróć końcową ocenę planszy
