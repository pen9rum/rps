from fastapi import APIRouter
from ...schemas.observer import ObserverPredictReq, ObserverPredictResp
from ...services.llm import estimate_payoff

router = APIRouter(prefix="/observer", tags=["observer"])

@router.post("/predict", response_model=ObserverPredictResp)
def observer_predict(req: ObserverPredictReq):
    res = estimate_payoff(req.description_s1, req.description_s2, req.prompt_style)
    return ObserverPredictResp(**res)
