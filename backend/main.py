# main.py
import sys, os
sys.path.append(os.path.dirname(__file__))

import math, json, random
from typing import List

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI

from rps_logic import base_strategies, resolve_dist

# 讀取環境變數（例如 backend/.env）
load_dotenv(dotenv_path="backend/.env")

# ===== 設定 =====
ALL_STRATEGIES = list("ABCDEFGHIJKLMNOPXYZ")  # 模型可用（含 X/Y/Z）
TARGET_STRATEGIES = list("ABCDEFGHIJKLMNOP")  # 對手只在 A~P
LOSS_THRESHOLD = 0.1053  # ≈ -log(0.9)，即 posterior(true) ≥ 0.9 早停
MAX_ROUNDS = 100

# ===== FastAPI =====
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={"detail": str(exc)})

# ===== Schema =====
class LLMPlayInput(BaseModel):
    target_strategy: str
    available_strategies: List[str] = Field(alias="llm_strategies")
    model_config = {"populate_by_name": True}

# （保留：分佈級對比用的端點需要時再加）
# class StrategyInput(BaseModel):
#     actualA: str; actualB: str; predA: str; predB: str

# ===== OpenAI =====
client = OpenAI()  # 自動讀取 OPENAI_API_KEY

# ===== 抽樣與對戰 =====
_rng = random.Random()

def _sample_from_dist(dist, rng=_rng):
    r = rng.random()
    if r < dist["rock"]:
        return "R"
    elif r < dist["rock"] + dist["paper"]:
        return "P"
    return "S"

def _rps_outcome(me, opp):
    if me == opp: return "draw"
    if (me, opp) in [("R","S"), ("S","P"), ("P","R")]: return "win"
    return "loss"

def play_one_round(my_strategy_key, opp_fixed_dist, rng=_rng):
    my_dist   = resolve_dist(my_strategy_key, opp_fixed_dist)  # X/Y/Z 依對手分佈轉換
    my_throw  = _sample_from_dist(my_dist, rng)
    opp_throw = _sample_from_dist(opp_fixed_dist, rng)
    outcome   = _rps_outcome(my_throw, opp_throw)
    return my_throw, opp_throw, outcome

# ===== 後驗推斷（NLL；只用於早停，不給模型）=====
def _throw_prob(throw, dist):
    return {"R": dist["rock"], "P": dist["paper"], "S": dist["scissors"]}[throw]

def _log_likelihood_for_target(history, t):
    opp_dist_t = resolve_dist(t, {"rock":1/3, "paper":1/3, "scissors":1/3})
    ll = 0.0
    for h in history:
        my_strategy = h["my_strategy"]
        my_throw    = h["my_throw"]
        opp_throw   = h["opp_throw"]
        my_dist_t   = resolve_dist(my_strategy, opp_dist_t)
        p_my  = max(_throw_prob(my_throw,  my_dist_t), 1e-12)
        p_opp = max(_throw_prob(opp_throw, opp_dist_t), 1e-12)
        ll += math.log(p_my) + math.log(p_opp)
    return ll

def infer_posterior(history, candidates=TARGET_STRATEGIES):
    if not history:
        p = 1.0 / len(candidates)
        return {t: p for t in candidates}
    lls = {t: _log_likelihood_for_target(history, t) for t in candidates}
    m = max(lls.values())
    exps = {t: math.exp(ll - m) for t, ll in lls.items()}
    Z = sum(exps.values()) or 1.0
    return {t: v / Z for t, v in exps.items()}

def inference_loss(posterior, true_target):
    p = max(posterior.get(true_target, 0.0), 1e-12)
    return -math.log(p)  # 越小越好

# ===== LLM 選策略（無硬性去重；可重複）=====
def _format_strategy_table_full():
    lines = []
    for k in "ABCDEFGHIJKLMNOP":
        s = base_strategies[k]
        lines.append(f"{k}: R={s['rock']}, P={s['paper']}, S={s['scissors']}")
    lines += [
        "X: 反制對手（R=opp.S, P=opp.R, S=opp.P）",
        "Y: 被對手克（R=opp.P, P=opp.S, S=opp.R）",
        "Z: 鏡射對手（R=opp.R, P=opp.P, S=opp.S）",
    ]
    return "\n".join(lines)

def _minimal_history_for_llm(history):
    return [
        {
            "my_strategy": h["my_strategy"],
            "my_throw": h["my_throw"],
            "opp_throw": h["opp_throw"],
            "outcome": h["outcome"],
        } for h in history
    ]

def _extract_strategy_choice(txt: str, pool: list[str]) -> str:
    # 寬鬆解析：優先直接整段；不行就找第一個在 pool 的大寫字母
    s = txt.strip().upper()
    if s in pool:
        return s
    for ch in s:
        if ch in pool:
            return ch
    return pool[0]  # 最終兜底：非硬性去重，只保證字母合法

def llm_guess_strategy(history, available_strategies):
    pool = [s for s in (available_strategies or []) if s in ALL_STRATEGIES] or ALL_STRATEGIES
    rules = _format_strategy_table_full()
    brief = _minimal_history_for_llm(history)

    system_msg = (
        "你在玩剪刀石頭布（R/P/S）的混合策略猜測遊戲。"
        "對手目標固定且只會是 A~P。你知道所有策略（A~P + X/Y/Z）的定義。"
        "歷史只提供：你出的策略、雙方實際出拳（R/P/S）、勝負。"
        "請根據歷史自行推敲與取捨（探索/利用），選出下一步策略。"
        "你可以重複選擇同一策略。只回一個代號（例如 K）。"
    )
    user_msg = (
        "【策略定義】\n" + rules + "\n\n"
        f"【可選策略】{pool}\n"
        f"【歷史】\n{json.dumps(brief, ensure_ascii=False)}\n\n"
        "請只回一個代號（如 A~P 或 X/Y/Z），不要多餘文字。"
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":system_msg},
                  {"role":"user","content":user_msg}],
        max_tokens=8,
        temperature=0.6  # 允許一定探索；不做硬性限制
    )
    guess = _extract_strategy_choice(resp.choices[0].message.content, pool)
    return guess

# ===== 路由 =====
@app.post("/llm-play")
def llm_play(data: LLMPlayInput):
    true_target = data.target_strategy
    if true_target not in TARGET_STRATEGIES:
        raise HTTPException(status_code=400, detail=f"target_strategy 必須為 A~P，其一。收到: {true_target}")

    # 對手（目標）的固定分佈
    true_opp_dist = resolve_dist(true_target, {"rock":1/3, "paper":1/3, "scissors":1/3})

    history = []
    posterior = infer_posterior(history, TARGET_STRATEGIES)

    # 這兩個序列就是你要的「每輪」資訊
    loss_per_round = []                # 每輪的 NLL：-log p(true_target | 歷史至當輪)
    posterior_top5_per_round = []      # （可選）每輪的 top5 後驗，方便你觀察收斂

    for i in range(MAX_ROUNDS):
        # 讓模型決策下一手（模型看不到 loss / posterior）
        guess = llm_guess_strategy(history, data.available_strategies)

        # 實際對戰，歷史只記必要四欄
        my_throw, opp_throw, outcome = play_one_round(guess, true_opp_dist)
        history.append({
            "round": i + 1,
            "my_strategy": guess,
            "my_throw": my_throw,
            "opp_throw": opp_throw,
            "outcome": outcome
        })

        # 伺服端更新後驗 & 當輪 loss（不回饋給模型）
        posterior = infer_posterior(history, TARGET_STRATEGIES)
        loss = inference_loss(posterior, true_target)

        # 記錄到時間序列；也貼到當輪歷史（鍵名以 server_ 開頭避免混淆）
        loss_per_round.append(loss)
        history[-1]["server_loss_after_round"] = loss
        history[-1]["server_posterior_top5_after_round"] = sorted(
            posterior.items(), key=lambda x: x[1], reverse=True
        )[:5]
        posterior_top5_per_round.append(history[-1]["server_posterior_top5_after_round"])

        # 早停
        if loss <= LOSS_THRESHOLD:
            break

    # 最終一次的摘要（與舊版一致）
    final_top5 = sorted(posterior.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "history": history,                 # 每筆都含有 server_loss_after_round
        "target": true_target,
        "rounds": len(history),
        "stopped": (loss_per_round[-1] <= LOSS_THRESHOLD) or (len(history) >= MAX_ROUNDS),
        "server_infer": {
            "posterior_top5": final_top5,
            "loss": loss_per_round[-1],
            "loss_per_round": loss_per_round,                         # ← 你要的重點
            "posterior_top5_per_round": posterior_top5_per_round      # ←（可選）觀察用
        }
    }


@app.get("/")
def root():
    return {"message": "RPS FastAPI backend is running."}
