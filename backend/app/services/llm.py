from ..core.config import settings
from typing import Optional

# Stub service; replace with real provider (OpenAI, Anthropic, local model, etc.)
def estimate_payoff(description_s1: str, description_s2: str, prompt_style: Optional[str] = None):
    # Return a naive uniform guess + moderate confidence; replace with real call
    return {"win": 0.34, "loss": 0.33, "draw": 0.33, "confidence": 0.6}

def decide_next_move(history, k_window=5, belief=None):
    # Simple heuristic placeholder; replace with real LLM policy
    if not history: return 0, "No history; default ROCK."
    opp_moves = [opp for _, opp in history[-(k_window or len(history)):]]
    top = max(set(opp_moves), key=opp_moves.count)
    move = (top + 1) % 3
    return move, "Counter most frequent opponent move."
