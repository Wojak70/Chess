import pygame as p
from view.ChessView import *
from controller.ChessController import ChessController
from strategy.AlphaBetaStrategy import AlphaBetaStrategy
from strategy.RandomStrategy import RandomStrategy
from time import sleep
# Stałe związane z wyświetlaniem
WIDTH = HEIGHT = 512  # Rozmiar okna
DIMENSION = 8 # 8x8 – klasyczna szachownica
SQ_SIZE = HEIGHT // DIMENSION 
MAX_FPS = 15 # Ilość klatek na sekundę
IMAGES = {} # Słownik do przechowywania załadowanych grafik figur

def main():
    """Funkcja główna gry – uruchamia wszystko"""
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    load_images()
# Inicjalizacja kontrolera gry – ustaw, kto gra jaką stroną
    controller = ChessController(
        white_strategy=None,                     # None - Człowiek, inne - odpowiedni algorytm
        # black_strategy=RandomStrategy()          # AI
        black_strategy=AlphaBetaStrategy(3)
    )

    sq_selected = () # Obecnie zaznaczone pole
    player_clicks = [] # Lista kliknięć (maks. 2)
    game_over = False # Flaga końca gry

    while True:
        
        # Określenie, czy teraz jest tura człowieka
        human_turn = (controller.gs.whiteToMove and controller.white_strategy is None) or \
                     (not controller.gs.whiteToMove and controller.black_strategy is None)

        for e in p.event.get():
            if e.type == p.QUIT:
                return
        # Kliknięcie myszy – obsługa ruchu gracza
            elif e.type == p.MOUSEBUTTONDOWN and human_turn and not game_over:
                loc = p.mouse.get_pos()
                col, row = loc[0] // SQ_SIZE, loc[1] // SQ_SIZE
                sq_selected, player_clicks, promotion_move = controller.handle_click(row, col, player_clicks, sq_selected)
                # Jeśli ruch to promocja – pokaż wybór i wykonaj
                if promotion_move and promotion_move.isPawnPromotion:
                    choice = drawPromotionChoice(screen, promotion_move.pieceMoved[0])
                    promotion_move.promotionChoice = choice
                    controller.gs.makeMove(promotion_move)
                    controller.move_made = True
                    controller.animate = True
            # Klawiatura – cofnięcie ruchu lub restart gry
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Cofnij do tury gracza
                    if len(controller.gs.movelog) != 0: 
                        # Cofamy przynajmniej jeden ruch
                        controller.handle_undo()

                        # Cofaj dalej, dopóki nie będzie tury gracza
                        while len(controller.gs.movelog) > 0 and not (
                            (controller.gs.whiteToMove and controller.white_strategy is None) or
                            (not controller.gs.whiteToMove and controller.black_strategy is None)
                        ):
                            controller.handle_undo()

                        # Resetujemy też zaznaczenia i kliknięcia
                        sq_selected = ()
                        player_clicks = []
                        game_over = False
                elif e.key == p.K_r: # Restart gry
                    controller.reset_game()
                    sq_selected = ()
                    player_clicks = []
                    game_over = False
        # Jeśli to tura AI i gra nie jest zakończona
        if not game_over and not human_turn:
            # sleep(1) # Odkomentuj jeśli gra bot z botem
            ai_move = controller.get_ai_move()
            if ai_move:
                controller.gs.makeMove(ai_move)
                controller.move_made = True
                controller.animate = True
        # Po wykonanym ruchu – odśwież legalne ruchy
        if controller.move_made:
            controller.update_after_move()
        # Rysowanie stanu gry
        draw_game_state(screen, controller.gs, controller.valid_moves, sq_selected)
        # Sprawdzenie końca gry (mat lub pat)
        if len(controller.valid_moves) == 0:
            game_over = True
            if controller.gs.inCheck:
                draw_text(screen, "Mat - " + ("Czarne" if controller.gs.whiteToMove else "Białe") + " wygrywają")
            else:
                draw_text(screen, "Pat")

        clock.tick(MAX_FPS)
        p.display.flip()

if __name__ == "__main__":
    main()
