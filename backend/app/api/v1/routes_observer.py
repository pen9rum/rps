"""
觀察者預測 API 路由模組

功能：
- 提供 LLM 策略預測 API
- 支援策略代碼和描述文字輸入
- 整合 OpenAI API 進行預測

API 端點：
- POST /observer/predict - 觀察者預測
"""

from fastapi import APIRouter, HTTPException
from ...schemas.observer import ObserverPredictReq, ObserverPredictResp
from ...services.llm import estimate_payoff
from ...domain.strategies import get_all_strategies

router = APIRouter(prefix="/observer", tags=["observer"])

@router.post("/predict", response_model=ObserverPredictResp)
def observer_predict(req: ObserverPredictReq):
    """觀察者預測端點"""
    # 驗證輸入
    if req.strategy1 and req.strategy2:
        # 使用策略代碼
        all_strategies = get_all_strategies()
        if req.strategy1 not in all_strategies:
            raise HTTPException(status_code=400, detail=f"策略 {req.strategy1} 不存在")
        if req.strategy2 not in all_strategies:
            raise HTTPException(status_code=400, detail=f"策略 {req.strategy2} 不存在")
        
        # 將策略代碼轉換為描述
        description_s1 = all_strategies[req.strategy1]['name']
        description_s2 = all_strategies[req.strategy2]['name']
    elif req.description_s1 and req.description_s2:
        # 使用描述文字
        description_s1 = req.description_s1
        description_s2 = req.description_s2
    else:
        raise HTTPException(
            status_code=400, 
            detail="必須提供策略代碼 (strategy1, strategy2) 或描述文字 (description_s1, description_s2)"
        )
    
    # 調用 LLM 服務進行預測
    try:
        result = estimate_payoff(description_s1, description_s2, req.prompt_style)
        return ObserverPredictResp(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"預測失敗: {str(e)}")
