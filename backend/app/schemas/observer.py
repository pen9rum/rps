from pydantic import BaseModel
from typing import Optional

class ObserverPredictReq(BaseModel):
    description_s1: str
    description_s2: str
    prompt_style: Optional[str] = None

class ObserverPredictResp(BaseModel):
    win: float
    loss: float
    draw: float
    confidence: float
