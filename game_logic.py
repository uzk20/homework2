# game_logic.py
# 纯逻辑模块：不依赖 pygame，方便单独测试

# 方向 → (行增量, 列增量)
DIRECTION_DELTA = {
    "U": (-1, 0),
    "D": (1, 0),
    "L": (0, -1),
    "R": (0, 1),
}

def parse_level(level_str_tuple):
    """把字符串关卡解析成 {(row, col): direction} 字典"""
    arrows = {}
    for r, line in enumerate(level_str_tuple):
        for c, ch in enumerate(line):
            if ch in DIRECTION_DELTA:
                arrows[(r, c)] = ch
    return arrows

def can_fly(arrows, row, col):
    """
    判断 (row, col) 处的箭头能否飞出棋盘。
    规则：沿箭头方向，从下一格开始逐格前进，直到出界。
          途中遇到任何其他箭头 → 不能飞。
    """
    direction = arrows[(row, col)]
    dr, dc = DIRECTION_DELTA[direction]
    r, c = row + dr, col + dc

    # 只要还在棋盘范围内（行/列都 >= 0）就继续检查
    while r >= 0 and c >= 0:
        if (r, c) in arrows:
            return False   # 前方有阻挡
        r += dr
        c += dc

    return True            # 前方畅通，可以飞出

def all_arrows_cleared(arrows):
    """棋盘上还有没有箭头？空字典表示全部清除"""
    return len(arrows) == 0