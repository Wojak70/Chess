import random
from strategy.BaseStrategy import MoveStrategy

class RandomStrategy(MoveStrategy):
    '''Wybiera losowy ruch z możliwych'''
    def select_move(self, gs, valid_moves):
        return random.choice(valid_moves) if valid_moves else None