# rps_logic.py
# RPS 策略定義與分佈工具

base_strategies = {
    'A': {'name': 'A (纯剪刀)', 'rock': 0, 'paper': 0, 'scissors': 1},
    'B': {'name': 'B (纯石头)', 'rock': 1, 'paper': 0, 'scissors': 0},
    'C': {'name': 'C (纯布)', 'rock': 0, 'paper': 1, 'scissors': 0},
    'D': {'name': 'D (随机)', 'rock': 0.333, 'paper': 0.333, 'scissors': 0.334},
    'E': {'name': 'E (石头+布)', 'rock': 0.5, 'paper': 0.5, 'scissors': 0},
    'F': {'name': 'F (石头+剪刀)', 'rock': 0.5, 'paper': 0, 'scissors': 0.5},
    'G': {'name': 'G (布+剪刀)', 'rock': 0, 'paper': 0.5, 'scissors': 0.5},
    'H': {'name': 'H (偏爱石头)', 'rock': 0.5, 'paper': 0.25, 'scissors': 0.25},
    'I': {'name': 'I (偏爱布)', 'rock': 0.25, 'paper': 0.5, 'scissors': 0.25},
    'J': {'name': 'J (偏爱剪刀)', 'rock': 0.25, 'paper': 0.25, 'scissors': 0.5},
    'K': {'name': 'K (石头主布次)', 'rock': 0.5, 'paper': 0.333, 'scissors': 0.167},
    'L': {'name': 'L (石头主剪次)', 'rock': 0.5, 'paper': 0.167, 'scissors': 0.333},
    'M': {'name': 'M (布主石次)', 'rock': 0.333, 'paper': 0.5, 'scissors': 0.167},
    'N': {'name': 'N (布主剪次)', 'rock': 0.167, 'paper': 0.5, 'scissors': 0.333},
    'O': {'name': 'O (剪主石次)', 'rock': 0.333, 'paper': 0.167, 'scissors': 0.5},
    'P': {'name': 'P (剪主布次)', 'rock': 0.167, 'paper': 0.333, 'scissors': 0.5},
}

def resolve_dist(key, opp_dist):
    """回傳策略 key 的出拳分佈。
    - A~P：固定分佈（忽略 opp_dist）
    - X：反制對手（R=opp.S, P=opp.R, S=opp.P）
    - Y：被對手克（R=opp.P, P=opp.S, S=opp.R）
    - Z：鏡射對手（R=opp.R, P=opp.P, S=opp.S）
    """
    if key in base_strategies:
        return base_strategies[key]
    if key == 'X':
        return {'rock': opp_dist['scissors'], 'paper': opp_dist['rock'], 'scissors': opp_dist['paper']}
    if key == 'Y':
        return {'rock': opp_dist['paper'], 'paper': opp_dist['scissors'], 'scissors': opp_dist['rock']}
    if key == 'Z':
        return {'rock': opp_dist['rock'], 'paper': opp_dist['paper'], 'scissors': opp_dist['scissors']}
    return {'rock': 0, 'paper': 0, 'scissors': 0}

def calculate_matchup(k1, k2):
    """計算 k1 對 k2 的勝/負/和 百分比（%）"""
    opp1 = base_strategies.get(k2, {'rock': 1/3, 'paper': 1/3, 'scissors': 1/3})
    opp2 = base_strategies.get(k1, {'rock': 1/3, 'paper': 1/3, 'scissors': 1/3})
    s1 = resolve_dist(k1, opp1)
    s2 = resolve_dist(k2, opp2)
    wins = s1['rock'] * s2['scissors'] + s1['scissors'] * s2['paper'] + s1['paper'] * s2['rock']
    losses = s1['scissors'] * s2['rock'] + s1['paper'] * s2['scissors'] + s1['rock'] * s2['paper']
    draws = s1['rock'] * s2['rock'] + s1['paper'] * s2['paper'] + s1['scissors'] * s2['scissors']
    return {'wins': wins * 100, 'losses': losses * 100, 'draws': draws * 100}
