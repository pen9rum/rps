"""
觀察者預測相關的 Pydantic 模型定義

功能：
- 定義觀察者預測 API 的請求和回應格式
- 支援策略代碼和描述文字輸入
- 提供預測結果和信心度模型
"""

from pydantic import BaseModel
from typing import Optional

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
