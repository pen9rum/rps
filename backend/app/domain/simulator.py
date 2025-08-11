import numpy as np
from .strategies import beats

def play_round(s1, s2, history, k_window=None):
    h = history[-k_window:] if k_window else history
    m1 = s1.next(history=h)
    m2 = s2.next(history=[(b,a) for a,b in h])
    return m1, m2, beats(m1, m2)

def simulate(s1, s2, rounds=1000, k_window=None):
    history = []
    results = []
    for _ in range(rounds):
        m1, m2, r = play_round(s1, s2, history, k_window=k_window)
        history.append((m1, m2))
        results.append(r)
    arr = np.array(results)
    wins  = float((arr == 1).mean())
    losses= float((arr == -1).mean())
    draws = float((arr == 0).mean())
    return {"win": wins, "loss": losses, "draw": draws}
