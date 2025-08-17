"""
LLM 服務整合模組

功能：
- 整合 OpenAI API 進行策略預測
- 提供策略描述分析和特徵提取
- 計算策略對戰結果預測
- 提供備用預測邏輯（當 API 失敗時）
- 支援不同 prompt 風格的預測

核心功能：
- estimate_payoff(): 主要預測函數，整合 OpenAI API
- call_openai_for_prediction(): OpenAI API 調用
- analyze_strategy(): 策略描述分析
- predict_matchup(): 基於特徵的預測計算
- fallback_prediction(): 備用預測邏輯

支援的 prompt 風格：
- analytical: 詳細分析風格
- default: 簡潔預測風格

配置要求：
- OPENAI_API_KEY: OpenAI API 金鑰
- MODEL_PROVIDER: 模型提供商設定
"""

from ..core.config import settings
from typing import Optional
import random
import openai
import json

# 設定 OpenAI API
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY

def analyze_strategy(description: str) -> dict:
    """分析策略描述，返回策略特徵"""
    description = description.lower()
    
    # 基本策略特徵分析
    features = {
        'rock_freq': 0.33,
        'paper_freq': 0.33, 
        'scissors_freq': 0.33,
        'is_fixed': False,
        'is_random': False,
        'is_reactive': False,
        'aggressive': 0.5
    }
    
    # 檢測固定策略
    if any(word in description for word in ['固定', 'always', 'pure', 'only', '100%']):
        if '石頭' in description or 'rock' in description:
            features.update({'rock_freq': 1.0, 'paper_freq': 0.0, 'scissors_freq': 0.0, 'is_fixed': True})
        elif '布' in description or 'paper' in description:
            features.update({'rock_freq': 0.0, 'paper_freq': 1.0, 'scissors_freq': 0.0, 'is_fixed': True})
        elif '剪刀' in description or 'scissors' in description:
            features.update({'rock_freq': 0.0, 'paper_freq': 0.0, 'scissors_freq': 1.0, 'is_fixed': True})
    
    # 檢測隨機策略
    elif any(word in description for word in ['隨機', 'random', 'randomly']):
        features.update({'is_random': True})
    
    # 檢測反應策略
    elif any(word in description for word in ['反應', 'reactive', 'counter', '回應']):
        features.update({'is_reactive': True, 'aggressive': 0.7})
    
    # 檢測頻率策略
    elif any(word in description for word in ['頻率', 'frequency', 'most', 'common']):
        features.update({'aggressive': 0.6})
    
    # 檢測偏好
    if '偏愛' in description or 'prefer' in description:
        if '石頭' in description or 'rock' in description:
            features.update({'rock_freq': 0.5, 'paper_freq': 0.25, 'scissors_freq': 0.25})
        elif '布' in description or 'paper' in description:
            features.update({'rock_freq': 0.25, 'paper_freq': 0.5, 'scissors_freq': 0.25})
        elif '剪刀' in description or 'scissors' in description:
            features.update({'rock_freq': 0.25, 'paper_freq': 0.25, 'scissors_freq': 0.5})
    
    return features

def predict_matchup(s1_features: dict, s2_features: dict) -> dict:
    """根據兩個策略的特徵預測對戰結果"""
    
    # 計算期望勝率
    s1_win = 0.0
    s1_loss = 0.0
    s1_draw = 0.0
    
    # 石頭剪刀布的勝負矩陣
    # s1_rock vs s2_scissors = s1_win
    # s1_rock vs s2_rock = draw
    # s1_rock vs s2_paper = s1_loss
    # 等等...
    
    s1_win += s1_features['rock_freq'] * s2_features['scissors_freq']  # 石頭勝剪刀
    s1_win += s1_features['paper_freq'] * s2_features['rock_freq']     # 布勝石頭
    s1_win += s1_features['scissors_freq'] * s2_features['paper_freq'] # 剪刀勝布
    
    s1_loss += s1_features['rock_freq'] * s2_features['paper_freq']    # 石頭敗布
    s1_loss += s1_features['paper_freq'] * s2_features['scissors_freq'] # 布敗剪刀
    s1_loss += s1_features['scissors_freq'] * s2_features['rock_freq']  # 剪刀敗石頭
    
    s1_draw += s1_features['rock_freq'] * s2_features['rock_freq']     # 石頭平石頭
    s1_draw += s1_features['paper_freq'] * s2_features['paper_freq']   # 布平布
    s1_draw += s1_features['scissors_freq'] * s2_features['scissors_freq'] # 剪刀平剪刀
    
    # 添加一些隨機性來模擬不確定性
    noise = 0.05
    s1_win = max(0.0, min(1.0, s1_win + random.uniform(-noise, noise)))
    s1_loss = max(0.0, min(1.0, s1_loss + random.uniform(-noise, noise)))
    s1_draw = max(0.0, min(1.0, s1_draw + random.uniform(-noise, noise)))
    
    # 正規化
    total = s1_win + s1_loss + s1_draw
    if total > 0:
        s1_win /= total
        s1_loss /= total
        s1_draw /= total
    
    return {
        'win': round(s1_win, 3),
        'loss': round(s1_loss, 3),
        'draw': round(s1_draw, 3)
    }

def estimate_confidence(s1_features: dict, s2_features: dict, prediction: dict) -> float:
    """估計預測的信心度"""
    base_confidence = 0.6
    
    # 如果策略很明確，提高信心度
    if s1_features['is_fixed'] or s2_features['is_fixed']:
        base_confidence += 0.2
    
    # 如果預測很極端（高勝率或高敗率），提高信心度
    max_prob = max(prediction['win'], prediction['loss'], prediction['draw'])
    if max_prob > 0.7:
        base_confidence += 0.1
    
    # 如果兩個策略相似，降低信心度
    if (abs(s1_features['rock_freq'] - s2_features['rock_freq']) < 0.1 and
        abs(s1_features['paper_freq'] - s2_features['paper_freq']) < 0.1):
        base_confidence -= 0.1
    
    return min(0.95, max(0.3, base_confidence))

def call_openai_for_prediction(description_s1: str, description_s2: str, prompt_style: Optional[str] = None) -> dict:
    """使用 OpenAI API 進行預測"""
    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key not configured")
    
    # 構建 prompt
    if prompt_style == "analytical":
        prompt = f"""
你是一個石頭剪刀布遊戲的專家分析師。請分析以下兩個策略的對戰結果：

策略1: {description_s1}
策略2: {description_s2}

請分析這兩個策略的特徵，並預測策略1對戰策略2的結果。
請以JSON格式回答，包含以下欄位：
- win: 策略1獲勝的機率 (0-1之間的小數)
- loss: 策略1失敗的機率 (0-1之間的小數)  
- draw: 平手的機率 (0-1之間的小數)
- confidence: 你對這個預測的信心度 (0-1之間的小數)
- reasoning: 簡短的推理過程

請確保 win + loss + draw = 1
"""
    else:
        prompt = f"""
在石頭剪刀布遊戲中，策略1是"{description_s1}"，策略2是"{description_s2}"。

請預測策略1對戰策略2的結果，並以JSON格式回答：
{{
  "win": 策略1獲勝機率,
  "loss": 策略1失敗機率,
  "draw": 平手機率,
  "confidence": 預測信心度,
  "reasoning": "推理過程"
}}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個石頭剪刀布遊戲分析專家。請提供準確的預測和清晰的推理。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # 解析回應
        content = response.choices[0].message.content
        # 嘗試提取 JSON
        try:
            # 尋找 JSON 部分
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                result = json.loads(json_str)
                
                # 驗證和正規化結果
                total = result.get('win', 0) + result.get('loss', 0) + result.get('draw', 0)
                if total > 0:
                    result['win'] = round(result.get('win', 0) / total, 3)
                    result['loss'] = round(result.get('loss', 0) / total, 3)
                    result['draw'] = round(result.get('draw', 0) / total, 3)
                
                result['confidence'] = min(1.0, max(0.0, result.get('confidence', 0.6)))
                return result
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError):
            # 如果 JSON 解析失敗，使用 fallback
            return fallback_prediction(description_s1, description_s2)
            
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return fallback_prediction(description_s1, description_s2)

def fallback_prediction(description_s1: str, description_s2: str) -> dict:
    """當 OpenAI API 失敗時的備用預測"""
    # 使用原有的邏輯作為備用
    s1_features = analyze_strategy(description_s1)
    s2_features = analyze_strategy(description_s2)
    prediction = predict_matchup(s1_features, s2_features)
    confidence = estimate_confidence(s1_features, s2_features, prediction)
    
    return {
        "win": prediction['win'],
        "loss": prediction['loss'], 
        "draw": prediction['draw'],
        "confidence": round(confidence, 3),
        "reasoning": "使用備用分析邏輯"
    }

# 主要的預測函數
def estimate_payoff(description_s1: str, description_s2: str, prompt_style: Optional[str] = None):
    """根據策略描述預測對戰結果"""
    
    # 檢查是否有 OpenAI API 配置
    if not settings.OPENAI_API_KEY:
        print("⚠️ 警告: 未設定 OPENAI_API_KEY，使用備用預測邏輯")
        return fallback_prediction(description_s1, description_s2)
    
    # 檢查是否啟用 OpenAI
    if settings.MODEL_PROVIDER != "openai":
        print(f"⚠️ 警告: MODEL_PROVIDER 設定為 '{settings.MODEL_PROVIDER}'，使用備用預測邏輯")
        return fallback_prediction(description_s1, description_s2)
    
    # 嘗試使用 OpenAI API
    try:
        return call_openai_for_prediction(description_s1, description_s2, prompt_style)
    except Exception as e:
        print(f"❌ OpenAI API 失敗，使用備用邏輯: {e}")
        return fallback_prediction(description_s1, description_s2)

def decide_next_move(history, k_window=5, belief=None):
    # Simple heuristic placeholder; replace with real LLM policy
    if not history: return 0, "No history; default ROCK."
    opp_moves = [opp for _, opp in history[-(k_window or len(history)):]]
    top = max(set(opp_moves), key=opp_moves.count)
    move = (top + 1) % 3
    return move, "Counter most frequent opponent move."
