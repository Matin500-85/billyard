"""
Created on Sat Jun  6 23:18:12 2026

@author: Matin
"""

# -*- coding: utf-8 -*-
"""
table.py — رندر میز بیلیارد (کش)
"""
import pygame
from core.constants import (
    WIDTH, HEIGHT, HUD_H,
    WALL_LEFT, WALL_RIGHT, WALL_TOP, WALL_BOTTOM, TABLE_MID_Y,
    POCKET_X, POCKET_Y, NUM_POCKETS, POCKET_RADIUS,THEMES
)


def build_table_cache(theme_name: str) -> pygame.Surface:
    """
    یک‌بار ساخته می‌شود و در هر فریم روی صفحه کپی می‌شود.
    شامل: پس‌زمینه، چوب، نمد، کوسن‌ها، سوراخ‌ها.
    """
    T    = THEMES[theme_name]
    surf = pygame.Surface((WIDTH, HEIGHT))

    surf.fill(T["bg"])

    # HUD bar
    pygame.draw.rect(surf, T["hud_bg"],   (0, 0, WIDTH, HUD_H))
    pygame.draw.line(surf, T["wood_mid"], (0, HUD_H-1), (WIDTH, HUD_H-1), 2)

    # چوب (لایه‌های متحد‌المرکز)
    pygame.draw.rect(surf, T["wood_dark"],  (0, HUD_H, WIDTH, HEIGHT - HUD_H))
    pygame.draw.rect(surf, T["wood_mid"],   (8,  HUD_H+8,  WIDTH-16, HEIGHT-HUD_H-16))
    pygame.draw.rect(surf, T["wood_light"], (18, HUD_H+18, WIDTH-36, HEIGHT-HUD_H-36))

    # نمد اصلی
    felt_rect = pygame.Rect(WALL_LEFT, WALL_TOP,
                            WALL_RIGHT - WALL_LEFT, WALL_BOTTOM - WALL_TOP)
    pygame.draw.rect(surf, T["felt"], felt_rect)

    # خطوط نمد
    lc = tuple(max(0, T["felt_line"][k]) for k in range(3))
    x = WALL_LEFT
    while x < WALL_RIGHT:
        pygame.draw.line(surf, lc, (x, WALL_TOP), (x, WALL_BOTTOM), 1)
        x += 18

    # خط میانی و نشانه‌های میز
    mid_x  = WIDTH // 2
    foot_x = int(WIDTH * 0.67)
    head_x = WIDTH // 4
    pygame.draw.line(surf, T["felt_shadow"],
                     (mid_x, WALL_TOP+10), (mid_x, WALL_BOTTOM-10), 1)
    for mx, my in [(foot_x, TABLE_MID_Y), (head_x, TABLE_MID_Y)]:
        pygame.draw.circle(surf, T["felt_shadow"], (mx, my), 4)
    pygame.draw.circle(surf, T["felt_shadow"], (head_x, TABLE_MID_Y), 60, 1)

    # کوسن‌های گوشه
    WL, WR, WT, WB = WALL_LEFT, WALL_RIGHT, WALL_TOP, WALL_BOTTOM
    for pts in [
        [(WL, WT), (WL+45, WT), (WL+22, WT+20)],
        [(WR, WT), (WR-45, WT), (WR-22, WT+20)],
        [(WL, WB), (WL+45, WB), (WL+22, WB-20)],
        [(WR, WB), (WR-45, WB), (WR-22, WB-20)],
    ]:
        pygame.draw.polygon(surf, T["cushion"], pts)

    pygame.draw.rect(surf, T["felt_shadow"], felt_rect, 3)

    # سوراخ‌ها
    for i in range(NUM_POCKETS):
        px, py = int(POCKET_X[i]), int(POCKET_Y[i])
        pygame.draw.circle(surf, T["wood_dark"], (px, py), POCKET_RADIUS + 10)
        pygame.draw.circle(surf, (8, 8, 8),      (px, py), POCKET_RADIUS + 2)
        pygame.draw.circle(surf, (0, 0, 0),      (px, py), POCKET_RADIUS)

    return surf
