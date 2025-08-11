from pydantic import BaseModel
from typing import Literal, Optional

class StrategySpec(BaseModel):
    kind: Literal["fixed","random","reactive","frequency"]
    param: Optional[int] = None

class SimulateRequest(BaseModel):
    s1: StrategySpec
    s2: StrategySpec
    rounds: int = 10000
    k_window: Optional[int] = None

class SimulateResponse(BaseModel):
    win: float
    loss: float
    draw: float
