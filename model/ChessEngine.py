class GameState():
    def __init__(self):
        '''Inicjalizacja stanu gry: ustawienie planszy, figur, flag, logów'''
        # Plansza 8x8, zapis figur jako "bQ" - czarna hetman, "wp" - biały pion itd.
        self.board = [
           ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]
        # Mapa funkcji odpowiadających za ruchy poszczególnych figur
        self.moveFunctions = {"p":self.getPawnMoves,"R":self.getRookMoves,"N":self.getKnightMoves,
                              "B":self.getBishopMoves,"Q":self.getQueenMoves, "K":self.getKingMoves}
        self.whiteToMove = True # # Flaga: kto ma ruch (True = biały)
        self.movelog = [] # Historia wykonanych ruchów
         # Pozycje królów – używane m.in. przy sprawdzaniu szacha
        self.whiteKingLocation = (7,4) 
        self.blackKingLocation = (0,4)
        # Wartości pozwalające określić czy król jest atakowany 
        self.inCheck = False 
        self.pins = []
        self.checks = []
        # Informacja o możliwym biciu w przelocie
        self.enpassantPossible = () 
        # Prawa do wykonania roszady
        self.currentCastlingRight = CastleRights(True,True,True,True)
        self.castleRightsLog = [self.currentCastlingRight]
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs,self.currentCastlingRight.bqs))



    def makeMove(self,move):
        '''Wykonanie ruchu na planszy, w tym promocji, bicia w przelocie, roszady'''

        # Przesunięcie figury na planszy
        self.board[move.startRow][move.startCol] = "--" # Zastąp pole na krórym stała figura polem "--"
        self.board[move.endRow][move.endCol]= move.pieceMoved # Przesuń figurę na pole docelowe
        self.movelog.append(move) # Dodanie posunięcia do dziennika
        self.whiteToMove = not self.whiteToMove # Możliwość wykonania ruchu przez oponenta

        # Aktualizacja pozycji króla, jeśli się poruszył
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow,move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow,move.endCol)
    
        # Promocja pionka domyślnie hetman
        if move.isPawnPromotion:
            promoteTo = move.promotionChoice or "Q" # Wybór figury
            self.board[move.endRow][move.endCol] = move.pieceMoved[0]+promoteTo # Zastąpienie pionka wybraną figurą
        
        # Bicie w przelocie
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" # Usunięcie zbitego pionka
        # Możliwość przyszłego bicia w przelocie (po ruchu o 2 pola)
        if move.pieceMoved[1]=="p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2,move.startCol)
        else:
            self.enpassantPossible = ()
        # Roszada – przestawienie wieży
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # Krótka roszada
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"
            else: # Długa roszada
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"

        # Aktualizacja praw do roszady
        self.updateCastleRights(move) # Aktualizowanie praw uprawniających do wykonanie roszady
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs,self.currentCastlingRight.bqs))

    

    def undoMove(self):
        '''Cofa ostatni ruch (w tym promocję, bicie w przelocie, roszadę, ruchy króla)'''
        if len(self.movelog) != 0: # Sprawdzenie czy movelog nie jest pusty
            move = self.movelog.pop() # Wyciągnięcie z loga ostatniego ruchu
            # Cofnij ruch na planszy
            self.board[move.startRow][move.startCol] = move.pieceMoved # Cofnięcie ruchu
            self.board[move.endRow][move.endCol] = move.pieceCaptured # Przywrócenie na planszę zbitej figury
            self.whiteToMove = not self.whiteToMove # Zamiana graczy
            # Przywrócenie poprzedniej lokalizacji przesuniętego króla
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow,move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow,move.startCol)
            # Cofnięcie bicia w przelocie
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow,move.endCol)
            # Cofnięcie ustawienia en passant (jeśli ruch był o 2 pola)
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # Cofnięcie wykonanej roszady
            self.castleRightsLog.pop() # Usuń aktualne prawa roszady
            self.currentCastlingRight = self.castleRightsLog[-1] # Przywróć poprzednie

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    # Cofnięcie krótkiej roszady
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:
                    # Cofnięcie długiej roszady
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"
                                

    def updateCastleRights(self,move):
        '''Modyfikuje prawa do roszady na podstawie wykonanego ruchu'''
        # Jeżeli król się poruszył, traci prawa do roszady
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False # Roszada krótka
            self.currentCastlingRight.wqs = False # Roszada długa
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False # tak jak wyżej
            self.currentCastlingRight.bqs = False
        # Jeżeli wieża się poruszyła – traci odpowiednie prawo do roszady
        elif move.pieceMoved == "wR":
            if move.startCol == 0:
                self.currentCastlingRight.wqs = False # roszada długa
            elif move.startCol == 7:
                self.currentCastlingRight.wks = False # Roszada krótka
        elif move.pieceMoved == "bR":
            if move.startCol == 0:
                self.currentCastlingRight.bqs = False # tak jak wyżej
            elif move.startCol == 7:
                self.currentCastlingRight.bks = False

    def getValidMoves(self):
        '''Zwraca listę wszystkich legalnych ruchów (uwzględniając szachy, piny, roszady, en passant)'''
        # Zachowanie aktualnego stanu en passant i roszady
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRight = CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                       self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)
        moves  = []
        # Dodanie roszady tylko wtedy, gdy król nie jest w szachu
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)
        # Sprawdzenie czy król znajduje się pod szachem i określenie pinów
        self.inCheck,self.pins,self.checks = self.checkForPinsAndChecks()
        # Pobierz pozycję króla
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        # Jeśli król jest w szachu
        if self.inCheck:
            if len(self.checks) == 1:
                # Jeśli jeden szach – można albo zbić szachującą figurę, albo zablokować
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                # Jeżeli szachuje skoczek – tylko zbicie
                if pieceChecking[1]=="N":
                    validSquares = [(checkRow,checkCol)]
                else:
                    # Pozostałe figury – można również zablokować
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0]==checkRow and validSquare[1]==checkCol:
                            break
                 # Usunięcie ruchów, które nie zatrzymują szacha
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow,moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                # Jeśli podwójny szach – tylko ruch królem
                self.getKingMoves(kingRow,kingCol,moves)
        else:
            # Jeśli nie ma szacha – wszystkie możliwe ruchy
            moves = self.getAllPossibleMoves()
        # Przywrócenie poprzednich wartości
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRight
        return moves

    def getAllPossibleMoves(self):
        '''Generuje wszystkie możliwe ruchy danej strony (bez sprawdzania szacha)'''
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn =="w" and self.whiteToMove) or (turn=="b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves) # Wywołanie odpowiedniej funkcji do generowania ruchów
        return moves

    def getPawnMoves(self,r,c,moves):
        '''Generuje ruchy pionka z uwzględnieniem promocji, bicia, bicia w przelocie, pinów'''
        piecePinned = False
        pinDirection = ()
        # Sprawdzenie czy figura jest spinnowana
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1]==c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break


        if self.whiteToMove: # Ruch białego piona
            if self.board[r-1][c] == "--": # ruch pionka o 1 pole
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r,c),(r-1,c),self.board))
                    if r==6 and self.board[r-2][c]=="--": # Ruch pionkiem o 2 pola
                        moves.append(Move((r,c),(r-2,c),self.board))
            if c-1 >=0: # Bicie z lewej
                if self.board[r-1][c-1][0] == "b":
                    if not piecePinned or pinDirection == (-1,-1): 
                        moves.append(Move((r,c),(r-1,c-1),self.board)) 
                elif (r-1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board,isEnPassantMove=True))
            if c+1<len(self.board[r]): #Bicie z prawej
                if self.board[r-1][c+1][0] == "b":
                    if not piecePinned or pinDirection == (-1,1):
                        moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board,isEnPassantMove=True))
        else: # Ruch czarnego pionka
            if self.board[r+1][c] == "--":
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((r,c),(r+1,c),self.board))
                    if r==1 and self.board[r+2][c]=="--":
                        moves.append(Move((r,c),(r+2,c),self.board))
            if c-1 >=0:
                if self.board[r+1][c-1][0] == "w":
                    if not piecePinned or pinDirection == (1,-1):
                        moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board,isEnPassantMove=True))
            if c+1<len(self.board[r]):
                if self.board[r+1][c+1][0] == "w":
                    if not piecePinned or pinDirection == (1,1):    
                        moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,isEnPassantMove=True))
    def getRookMoves(self,r,c,moves):
        '''Generuje ruchy wieży w 4 kierunkach, z uwzględnieniem pinów'''
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1]==c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1,0),(0,-1),(1,0),(0,1)) # Góra, lewo, dół, prawo
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r+d[0]*i 
                endCol = c+d[1]*i
                if 0<= endRow < 8 and 0<= endCol<8:
                    if not piecePinned or pinDirection == d or pinDirection ==(-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                else:
                    break
    def getBishopMoves(self,r,c,moves):
        '''Generuje ruchy gońca (na ukos) z uwzględnieniem pinów'''
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break


        directions = ((-1,-1),(-1,1),(1,-1),(1,1)) # Diagonale
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r+d[0]*i 
                endCol = c+d[1]*i
                if 0<= endRow < 8 and 0<= endCol<8:
                    if not piecePinned or pinDirection == d or pinDirection==(-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                else:
                    break
    def getKnightMoves(self,r,c,moves):
        '''Generuje ruchy skoczka – ignoruje piny, chyba że jest przypięty'''
        piecePinned = False

        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1]==c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        directions = ((1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1))
        allyColor = "w" if self.whiteToMove else "b"
        for k in directions:
            endrow=r+k[0]
            endcol = c+k[1]
            if 0<=endrow<8 and 0<= endcol <8:
                if not piecePinned:
                    endPiece = self.board[endrow][endcol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r,c),(endrow,endcol),self.board))
    def getKingMoves(self,r,c,moves):
        '''Ruchy króla na 1 pole w każdą stronę + sprawdzanie szacha'''
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow=r+rowMoves[i]
            endCol = c+colMoves[i]
            if 0<=endRow<8 and 0<= endCol <8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    # Tymczasowa zmiana pozycji króla – by sprawdzić czy będzie szach
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow,endCol)
                    else:
                        self.blackKingLocation = (endRow,endCol)
                    inCheck,pins,check = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    # Przywróć pozycję króla
                    if allyColor == "w":
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)
        # Dodanie ewentualnych roszad
        self.getCastleMoves(r,c,moves)


    def getCastleMoves(self,r,c,moves):
        '''Dodaje możliwe ruchy roszady, jeśli dozwolone i król nie jest w szachu'''
        if self.inCheck:
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r,c,moves)
    def getKingsideCastleMoves(self,r,c,moves):
        '''Sprawdza czy pole wymagane do krótkiej roszady są wolne i nie atakowane'''
        if self.board[r][c+1] == "--" and self.board[r][c+2]=="--":
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove = True))
    def getQueensideCastleMoves(self,r,c,moves):
        '''Sprawdza czy pole wymagane do Długiej roszady są wolne i nie atakowane'''
        if self.board[r][c-1] == "--" and self.board[r][c-2]=="--" and self.board[r][c-3]=="--":
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove = True))

    def getQueenMoves(self,r,c,moves):
        '''Hetman = połączenie ruchów gońca i wieży'''

        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)
    def squareUnderAttack(self, r, c):
        '''Funkcja sprawdzająca czy dane pole jest atakowane przez przeciwnika'''
        # Odwrócenie ruchu na potrzeby wygenerowania ruchów przeciwnika
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        # Sprawdzenie czy którakolwiek figura przeciwnika atakuje dane pole
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def checkForPinsAndChecks(self):
        '''Zwraca: czy król jest w szachu, listę pinów, listę szachów'''
        pins = []
        checks = []
        inCheck = False
        # Ustal kolory w zależności od strony na ruchu
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # Kierunki: pionowo, poziomo, ukośnie
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            posiblePin = ()
            for i in range(1,8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i
                if 0 <= endRow < 8 and 0<=endCol<8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1]!="K":
                        if posiblePin == ():
                            posiblePin = (endRow,endCol,d[0],d[1])
                        else:
                            break
                    elif endPiece[0]==enemyColor:
                        # Szach przez wieżę, gońca, hetmana, piona lub króla
                        type = endPiece[1]
                        if (0<=j <= 3 and type =="R") or (4<=j<=7 and type =="B") or (i== 1 and type == "p" and ((enemyColor =="w" and 6<= j<=7)or (enemyColor=="b" and 4<=j<=5))) or (type=="Q") or (i==1 and type == "K"):
                            if posiblePin == ():
                                inCheck = True
                                checks.append((endRow,endCol,d[0],d[1]))
                                break
                            else:
                                pins.append(posiblePin)
                                break
                        else:
                            break
                else:
                    break
        # Sprawdzenie szacha przez skoczki
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1]=="N":
                    inCheck = True
                    checks.append((endRow,endCol,m[0],m[1]))
        return inCheck, pins,checks
    



class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks # white kingside
        self.bks = bks # black kingside
        self.wqs = wqs # white queenside
        self.bqs = bqs # black queenside


class Move():
    ranksToRows = {"1":7,"2":6,"3":5,"4":4,
                   "5":3,"6":2,"7":1,8:0}
    rowsToRanks= {v: k for k,v in ranksToRows.items()}
    filesToCols = {"a":0,"b":1,"c":2,"d":3,
                   "e":4,"f":5,"g":6,"h":7}
    colsToFiles = {v: k for k,v in filesToCols.items()}
    def __init__ (self,startSq,endSq,board,isEnPassantMove = False, isCastleMove = False,promotionChoice=None):
        self.startRow = startSq[0]
        self.startCol = startSq[1]  
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]

        # Ruchy specjalne 
        if isEnPassantMove:
            self.pieceCaptured = board[self.startRow][self.endCol]
        else:
            self.pieceCaptured = board[self.endRow][self.endCol]
        self.isEnpassantMove = isEnPassantMove
        self.isCastleMove = isCastleMove
        # Promocja pionka
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved=="bp" and self.endRow==7)
        self.promotionChoice = promotionChoice
        # Czy był zbity przeciwnik
        self.isCapture = True if self.pieceCaptured != "--" else False
        # Unikalny ID dla ruchu
        self.moveId = self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol
   

        


    def __eq__(self,other):
        '''Ruchy są równe, jeśli mają taki sam ID'''
        if isinstance(other,Move):
            return self.moveId == other.moveId
        return False
    def getChessNotation(self):
            '''Zwraca zapis algebraiczny ruchu, np. e2e4'''
            return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,r,c):
        '''Konwertuje współrzędne na notację (np. 6,4 => e2)'''
        return self.colsToFiles[c] + self.rowsToRanks[r]
