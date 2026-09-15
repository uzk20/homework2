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

def can_fly(arrows, row, col, rows, cols):
    """
    判断 (row, col) 处的箭头能否飞出棋盘。
    rows, cols 是棋盘的尺寸，用于边界判断。
    """
    direction = arrows[(row, col)]
    dr, dc = DIRECTION_DELTA[direction]
    r, c = row + dr, col + dc

    # 同时判断上下界
    while 0 <= r < rows and 0 <= c < cols:
        if (r, c) in arrows:
            return False
        r += dr
        c += dc

    return True

def all_arrows_cleared(arrows):
    """棋盘上还有没有箭头？空字典表示全部清除"""
    return len(arrows) == 0