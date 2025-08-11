from fastapi import APIRouter
from ...schemas.evaluate import EvalReq, EvalResp
from ...domain.metrics import mae, rmse, brier, corr_pearson, corr_kendall

router = APIRouter(prefix="/evaluate", tags=["evaluate"])

@router.post("", response_model=EvalResp)
def eval_metrics(req: EvalReq):
    return EvalResp(
        mae=mae(req.pred, req.gt),
        rmse=rmse(req.pred, req.gt),
        brier=brier(req.pred, req.gt),
        pearson=corr_pearson(req.pred, req.gt),
        kendall=corr_kendall(req.pred, req.gt),
    )
