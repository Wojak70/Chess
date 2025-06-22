import pygame as p
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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

def load_images():
    """Wczytuje obrazy figur i zapisuje je do słownika IMAGES"""
    pieces = ["bp", "bR", "bN", "bB", "bQ", "bK", "wp", "wR", "wN", "wB", "wK", "wQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))

def draw_board(screen):
    """Rysuje szachownicę (naprzemienne kolory pól)"""
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    """Rysuje figury na podstawie aktualnego stanu planszy"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_text(screen, text):
    """Wyświetla tekst na środku planszy (np. komunikat o końcu gry)"""
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_obj = font.render(text, 0, p.Color("green"))
    location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_obj.get_width() / 2, HEIGHT / 2 - text_obj.get_height() / 2)
    screen.blit(text_obj, location)

def highlight_squares(screen, gs, valid_moves, sq_selected):
    """Podświetla wybrane pole i możliwe ruchy z tego pola"""
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color("yellow"))
            for move in valid_moves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))

def draw_game_state(screen, gs, valid_moves, sq_selected):
    """Rysuje całą planszę: pola, figury, podświetlenia"""
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)
def drawPromotionChoice(screen, color):
    """Wyświetla wybór figury przy promocji pionka"""
    font = p.font.SysFont("Helvetica", 24, True, False)
    choices = ["Q", "R", "B", "N"]
    labels = ["Hetman", "Wieża", "Goniec", "Skoczek"]
    rects = []
    # Rysowanie przycisków z wyborem figury
    for i, label in enumerate(labels):
        x = WIDTH // 2 - 100 + i * 50
        y = HEIGHT // 2 - 25
        rect = p.Rect(x, y, 40, 40)
        rects.append((rect, choices[i]))

        p.draw.rect(screen, p.Color("gray"), rect)
        text = font.render(choices[i], True, p.Color("black"))
        screen.blit(text, (x + 10, y + 8))

    p.display.flip()
    # Czekanie na kliknięcie w wybór
    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                exit()
            if e.type == p.MOUSEBUTTONDOWN:
                mx, my = p.mouse.get_pos()
                for rect, choice in rects:
                    if rect.collidepoint(mx, my):
                        return choice
