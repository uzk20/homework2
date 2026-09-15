# main.py
import sys
import pygame

from game_logic import (
    DIRECTION_DELTA, parse_level, can_fly, all_arrows_cleared
)
from levels import LEVELS

# ---------- 常量 ----------
WINDOW_SIZE = 700
GRID_PIXELS = 500          # 棋盘区域大小
MARGIN_TOP = 120           # 棋盘距离顶部留出多少像素放 HUD
GRID_SIZE = 5
CELL = GRID_PIXELS // GRID_SIZE
MAX_MISTAKES = 3

# 颜色
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GRAY   = (200, 200, 200)
BLUE   = (70, 130, 220)
RED    = (220, 70, 70)
GREEN  = (70, 180, 90)
BG     = (245, 245, 245)

# 方向 → 绘制箭头时的旋转角（以“右”为基准）
DIRECTION_ANGLE = {"R": 0, "D": 90, "L": 180, "U": 270}


def draw_arrow(surface, row, col, direction, color=BLUE, offset_y=0):
    """在指定格子中心画一个箭头"""
    cx = col * CELL + CELL // 2
    cy = row * CELL + CELL // 2 + MARGIN_TOP + offset_y
    size = CELL // 3

    # 用一个三角形表示箭头，根据方向旋转
    points = [
        (size, 0),
        (-size, -size),
        (-size, size),
    ]
    # 旋转
    angle = DIRECTION_ANGLE[direction]
    rad = -angle * 3.14159 / 180
    cos_a, sin_a = __import__("math").cos(rad), __import__("math").sin(rad)
    rotated = []
    for (x, y) in points:
        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a
        rotated.append((cx + rx, cy + ry))

    pygame.draw.polygon(surface, color, rotated)


class Game:
    """游戏状态机：start / playing / success / failed"""
    def __init__(self):
        self.state = "start"
        self.level_index = 0
        self.arrows = {}
        self.mistakes = 0
        self.mistake_flash = None   # (row, col, 剩余帧数) 用于碰撞反馈
        self.animations = []        # [(row, col, direction, progress)] 飞出动画

    # ----- 关卡控制 -----
    def load_level(self, index):
        self.level_index = index
        self.arrows = parse_level(LEVELS[index])
        self.mistakes = 0
        self.mistake_flash = None
        self.animations = []

    def restart(self):
        self.load_level(self.level_index)

    # ----- 点击处理 -----
    def handle_click(self, mx, my):
        # 转换成棋盘行列
        col = mx // CELL
        row = (my - MARGIN_TOP) // CELL
        if (row, col) not in self.arrows:
            return

        if can_fly(self.arrows, row, col, GRID_SIZE, GRID_SIZE):
            direction = self.arrows.pop((row, col))
            self.animations.append([row, col, direction, 0])
        else:
            # 碰撞：失误 +1，并记录反馈
            self.mistakes += 1
            self.mistake_flash = [row, col, 20]
            if self.mistakes >= MAX_MISTAKES:
                self.state = "failed"

    # ----- 每帧更新 -----
    def update(self):
        # 飞出动画
        for a in self.animations[:]:
            a[3] += 1
            if a[3] > 30:           # 动画结束
                self.animations.remove(a)

        # 碰撞闪烁计时
        if self.mistake_flash:
            self.mistake_flash[2] -= 1
            if self.mistake_flash[2] <= 0:
                self.mistake_flash = None

        # 通关判定
        if self.state == "playing" and all_arrows_cleared(self.arrows):
            if self.level_index + 1 < len(LEVELS):
                self.state = "success"
            else:
                self.state = "all_clear"

    # ----- 绘制 -----
    def draw(self, screen, font_big, font_small):
        screen.fill(BG)

        if self.state == "start":
            self._draw_start(screen, font_big, font_small)
        elif self.state == "playing":
            self._draw_playing(screen, font_small)
        elif self.state == "success":
            self._draw_center_text(screen, font_big,
                f"第 {self.level_index + 1} 关通过！",
                "按 空格 进入下一关")
        elif self.state == "failed":
            self._draw_center_text(screen, font_big, "游戏失败",
                "按 R 重新开始本关")
        elif self.state == "all_clear":
            self._draw_center_text(screen, font_big, "全部通关！",
                "按 R 再玩一次")

    def _draw_start(self, screen, font_big, font_small):
        title = font_big.render("一箭又一箭", True, BLACK)
        screen.blit(title, (WINDOW_SIZE // 2 - title.get_width() // 2, 200))
        tip = font_small.render("点击方向箭头，让它飞出棋盘", True, GRAY)
        screen.blit(tip, (WINDOW_SIZE // 2 - tip.get_width() // 2, 280))
        start = font_big.render("按 空格 开始游戏", True, BLUE)
        screen.blit(start, (WINDOW_SIZE // 2 - start.get_width() // 2, 380))

    def _draw_playing(self, screen, font_small):
        # HUD
        info = font_small.render(
            f"关卡 {self.level_index + 1}    剩余箭头 {len(self.arrows)}"
            f"    失误 {self.mistakes}/{MAX_MISTAKES}",
            True, BLACK)
        screen.blit(info, (20, 20))

        # 重新开始按钮
        btn = pygame.Rect(WINDOW_SIZE - 150, 15, 130, 40)
        pygame.draw.rect(screen, GRAY, btn, border_radius=8)
        txt = font_small.render("重新开始", True, BLACK)
        screen.blit(txt, (btn.x + 20, btn.y + 10))
        self.restart_btn = btn

        # 网格
        for i in range(GRID_SIZE + 1):
            x = i * CELL
            y = i * CELL + MARGIN_TOP
            pygame.draw.line(screen, GRAY, (x, MARGIN_TOP), (x, MARGIN_TOP + GRID_PIXELS), 1)
            pygame.draw.line(screen, GRAY, (0, y), (GRID_PIXELS, y), 1)

        # 静态箭头
        for (r, c), d in self.arrows.items():
            color = BLUE
            offset = 0
            if self.mistake_flash and self.mistake_flash[0] == r and self.mistake_flash[1] == c:
                color = RED
                # 左右晃动
                import math
                offset = int(math.sin(self.mistake_flash[2] * 1.5) * 6)
            draw_arrow(screen, r, c, d, color, offset_y=offset)

        # 飞出动画
        for (r, c, d, prog) in self.animations:
            dr, dc = DIRECTION_DELTA[d]
            offset_px = prog * 12
            draw_arrow(screen, r, c, d, GREEN,
                       offset_y=offset_px * dr + (offset_px * dc and 0) if False else offset_px * dr)
            # 水平方向的动画简单处理：用 x 方向偏移
            if dc != 0:
                # 重画一次水平偏移版本
                pass

    def _draw_center_text(self, screen, font_big, line1, line2):
        t1 = font_big.render(line1, True, BLACK)
        screen.blit(t1, (WINDOW_SIZE // 2 - t1.get_width() // 2, 250))
        t2 = font_big.render(line2, True, GRAY)
        screen.blit(t2, (WINDOW_SIZE // 2 - t2.get_width() // 2, 330))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("一箭又一箭")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("simhei", 40)
    font_small = pygame.font.SysFont("simhei", 22)

    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game.state == "start" and event.key == pygame.K_SPACE:
                    game.load_level(0)
                    game.state = "playing"
                elif game.state == "success" and event.key == pygame.K_SPACE:
                    game.load_level(game.level_index + 1)
                    game.state = "playing"
                elif game.state in ("failed", "all_clear") and event.key == pygame.K_r:
                    if game.state == "all_clear":
                        game.load_level(0)
                    else:
                        game.restart()
                    game.state = "playing"

            if event.type == pygame.MOUSEBUTTONDOWN and game.state == "playing":
                mx, my = event.pos
                # 先判断是否点中“重新开始”按钮
                if hasattr(game, "restart_btn") and game.restart_btn.collidepoint(mx, my):
                    game.restart()
                else:
                    game.handle_click(mx, my)

        game.update()
        game.draw(screen, font_big, font_small)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()