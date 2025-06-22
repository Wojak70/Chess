from abc import ABC, abstractmethod

class MoveStrategy(ABC):
    @abstractmethod
    def select_move(self, gs, valid_moves):
        pass