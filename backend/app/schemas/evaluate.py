from pydantic import BaseModel
from typing import List, Optional

class EvalReq(BaseModel):
    pred: List[float]
    gt: List[float]

class EvalResp(BaseModel):
    mae: float
    rmse: float
    brier: float
    pearson: Optional[float] = None
    kendall: Optional[float] = None
