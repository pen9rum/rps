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
from ...schemas.observer import (
    ObserverPredictReq, ObserverPredictResp,
    ObserverRunReq, ObserverRunResp, RoundPrediction
)
from ...services.llm import estimate_payoff
from ...domain.strategies import (
    get_all_strategies, beats,
    BASE_STRATEGIES, DYNAMIC_STRATEGIES,
    resolve_dist, iterate_dists
)

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
        result = estimate_payoff(description_s1, description_s2, req.prompt_style, req.model)
        return ObserverPredictResp(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"預測失敗: {str(e)}")


@router.post("/run", response_model=ObserverRunResp)
def observer_run(req: ObserverRunReq):
    """連續多輪觀察：
    - 真實策略以代碼表示（如 'A' / 'B'）
    - 每輪先用模型對當前對戰做勝負平預測，再用簡易模擬器跑一輪實際結果
    - 回傳逐輪紀錄與彙總
    """
    strategies = get_all_strategies()
    if req.true_strategy1 not in strategies or req.true_strategy2 not in strategies:
        raise HTTPException(status_code=400, detail="真實策略不存在")

    # 名稱描述供 LLM 預測
    desc1 = strategies[req.true_strategy1]['name']
    desc2 = strategies[req.true_strategy2]['name']

    history = []
    per_round = []
    wins = 0
    losses = 0
    draws = 0

    for r in range(1, int(req.rounds) + 1):
        # LLM/備用模型預測
        pred = estimate_payoff(desc1, desc2, model=req.model)

        # 實際對戰一回合（依策略組合計算當前拳分佈後抽樣）
        import random
        def sample_move(dist):
            return random.choices([0,1,2], weights=[dist['rock'], dist['paper'], dist['scissors']])[0]

        # 依真實策略取得當前回合使用的分佈
        k1 = req.true_strategy1
        k2 = req.true_strategy2
        is_base1 = k1 in BASE_STRATEGIES
        is_base2 = k2 in BASE_STRATEGIES

        if is_base1 and is_base2:
            dist1 = BASE_STRATEGIES[k1]
            dist2 = BASE_STRATEGIES[k2]
        elif is_base1 and not is_base2:
            dist1 = BASE_STRATEGIES[k1]
            dist2 = resolve_dist(k2, dist1)
        elif not is_base1 and is_base2:
            dist2 = BASE_STRATEGIES[k2]
            dist1 = resolve_dist(k1, dist2)
        else:
            # 雙動態：使用穩態分佈
            it = iterate_dists(k1, k2, 50)
            dist1, dist2 = it['s1'], it['s2']

        m1 = sample_move(dist1)
        m2 = sample_move(dist2)
        res = beats(m1, m2)
        history.append((m1, m2))

        if res == 1: wins += 1
        elif res == -1: losses += 1
        else: draws += 1

        per_round.append(RoundPrediction(
            round=r,
            win=pred.get('win', 0.0),
            loss=pred.get('loss', 0.0),
            draw=pred.get('draw', 0.0),
            confidence=pred.get('confidence', 0.0),
            move1=m1,
            move2=m2,
            result=res,
        ))

    total = float(req.rounds) if req.rounds else 1.0
    summary = {
        'win': wins,
        'loss': losses,
        'draw': draws,
        'win_rate': wins / total,
        'loss_rate': losses / total,
        'draw_rate': draws / total,
    }

    return ObserverRunResp(
        model=req.model,
        true_strategy1=req.true_strategy1,
        true_strategy2=req.true_strategy2,
        rounds=req.rounds,
        k_window=req.k_window,
        per_round=per_round,
        summary=summary,
    )
