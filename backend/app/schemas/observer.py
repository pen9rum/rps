"""
觀察者預測相關的 Pydantic 模型定義

功能：
- 定義觀察者預測 API 的請求和回應格式
- 支援策略代碼和描述文字輸入
- 提供預測結果和信心度模型
"""

from pydantic import BaseModel
from typing import Optional, List, Dict

class ObserverPredictReq(BaseModel):
    """觀察者預測請求模型"""
    # 支援兩種輸入方式
    description_s1: Optional[str] = None  # 策略1描述
    description_s2: Optional[str] = None  # 策略2描述
    strategy1: Optional[str] = None       # 策略1代碼 (如 'A', 'B', 'X')
    strategy2: Optional[str] = None       # 策略2代碼 (如 'A', 'B', 'X')
    prompt_style: Optional[str] = None    # 提示風格
    model: Optional[str] = None           # 模型名稱（例如 'deepseek', '4o-mini'）

class ObserverPredictResp(BaseModel):
    """觀察者預測回應模型"""
    win: float
    loss: float
    draw: float
    confidence: float
    reasoning: Optional[str] = None  # 推理過程


class ObserverRunReq(BaseModel):
    """觀察者連續觀察請求"""
    true_strategy1: str
    true_strategy2: str
    rounds: int = 50
    k_window: Optional[int] = None
    model: Optional[str] = None  # 'deepseek' | '4o-mini'


class RoundPrediction(BaseModel):
    """單輪預測與結果紀錄"""
    round: int
    win: float
    loss: float
    draw: float
    confidence: float
    move1: int
    move2: int
    result: int  # 1=win, 0=draw, -1=loss（對真實策略1而言）


class ObserverRunResp(BaseModel):
    """觀察者連續觀察回應"""
    model: Optional[str] = None
    true_strategy1: str
    true_strategy2: str
    rounds: int
    k_window: Optional[int] = None
    per_round: List[RoundPrediction]
    summary: Dict[str, float]  # {win, loss, draw, win_rate, loss_rate, draw_rate}
