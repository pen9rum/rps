import numpy as np
from enum import IntEnum

class Move(IntEnum):
    ROCK = 0; PAPER = 1; SCISSORS = 2

def beats(a: int, b: int) -> int:
    if a == b: return 0
    return 1 if (a - b) % 3 == 1 else -1

class FixedStrategy:
    def __init__(self, move: int): self.move = move
    def next(self, **kwargs): return self.move

class RandomStrategy:
    def next(self, **kwargs): return int(np.random.choice([0,1,2]))

class ReactiveStrategy:
    def __init__(self, on_win=0, on_loss=1, on_draw=2):
        self.on_win, self.on_loss, self.on_draw = on_win, on_loss, on_draw
    def next(self, history):
        if not history: return int(np.random.choice([0,1,2]))
        my, opp = history[-1]
        res = beats(my, opp)
        return [self.on_draw, self.on_win, self.on_loss][res] if res in (-1,0,1) else 0

class FrequencyStrategy:
    def next(self, history):
        if not history: return int(np.random.choice([0,1,2]))
        opp_moves = [opp for _, opp in history]
        counts = np.bincount(opp_moves, minlength=3)
        top = int(np.argmax(counts))
        return (top + 1) % 3
