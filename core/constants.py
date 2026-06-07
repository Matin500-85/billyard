"""
Created on Sat Jun  6 12:36:38 2026

@author: Matin
"""

# -*- coding: utf-8 -*-
"""
constants.py — تمام ثابت‌های بازی
"""
import pygame

# ─── صفحه ───────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1140, 720
HUD_H         = 80
FPS           = 60

# ─── دیوارها ─────────────────────────────────────────────────────────────────
WALL_LEFT   = 72
WALL_RIGHT  = WIDTH  - 72
WALL_TOP    = HUD_H  + 72
WALL_BOTTOM = HEIGHT - 40
TABLE_MID_Y = (WALL_TOP + WALL_BOTTOM) // 2

# ─── فیزیک ───────────────────────────────────────────────────────────────────
FRICTION_RATE      = 0.9
RESTITUTION        = 0.96
POCKET_RADIUS      = 30
POCKET_RADIUS_SQ   = POCKET_RADIUS * POCKET_RADIUS
POCKET_NEAR_SQ     = (POCKET_RADIUS + 10) ** 2
STOP_SPEED_SQ      = 0.1 * 0.1

# ─── امتیاز ──────────────────────────────────────────────────────────────────
SCORE_OWN_BALL  = 100
SCORE_OPP_BALL  = -25

# ─── سوراخ‌ها ─────────────────────────────────────────────────────────────────
POCKETS = [
    (WALL_LEFT,  WALL_TOP),
    (WIDTH//2,   WALL_TOP - 4),
    (WALL_RIGHT, WALL_TOP),
    (WALL_LEFT,  WALL_BOTTOM),
    (WIDTH//2,   WALL_BOTTOM + 4),
    (WALL_RIGHT, WALL_BOTTOM),
]
POCKET_X    = tuple(p[0] for p in POCKETS)
POCKET_Y    = tuple(p[1] for p in POCKETS)
NUM_POCKETS = len(POCKETS)

# ─── رنگ توپ‌ها ───────────────────────────────────────────────────────────────
BALL_BASE_COLOR = {
    1:(255,215,0),  2:(30,80,200),   3:(210,30,30),
    4:(130,0,130),  5:(230,90,10),   6:(20,130,20),
    7:(160,60,20),  8:(20,20,20),
    9:(255,215,0),  10:(30,80,200),  11:(210,30,30),
    12:(130,0,130), 13:(230,90,10),  14:(20,130,20),
    15:(160,60,20),
}

# ─── رنگ‌های عمومی ───────────────────────────────────────────────────────────
WHITE        = (255,255,255)
BLACK        = (0,0,0)
GOLD         = (255,215,0)
SHADOW_COLOR = (40,40,40)
RED_HUD      = (220,60,60)
GREEN_HUD    = (60,200,90)

# ─── تم‌ها ────────────────────────────────────────────────────────────────────
THEMES = {
    "Classic Green": {
        "felt":(22,105,50),   "felt_shadow":(15,75,35),  "felt_line":(18,101,46),
        "cushion":(18,90,42), "wood_dark":(90,50,15),    "wood_mid":(130,80,25),
        "wood_light":(175,115,50), "bg":(25,20,10),      "hud_bg":(18,18,18),
    },
    "Midnight Blue": {
        "felt":(20,40,110),   "felt_shadow":(12,25,80),  "felt_line":(17,36,106),
        "cushion":(15,32,95), "wood_dark":(30,25,60),    "wood_mid":(55,45,100),
        "wood_light":(90,75,145), "bg":(10,8,30),        "hud_bg":(12,10,30),
    },
    "Desert Sand": {
        "felt":(185,145,70),  "felt_shadow":(150,112,48),"felt_line":(179,140,66),
        "cushion":(160,120,50),"wood_dark":(100,55,10),  "wood_mid":(145,90,25),
        "wood_light":(190,130,55),"bg":(60,38,12),       "hud_bg":(40,26,8),
    },
}
THEME_NAMES = list(THEMES.keys())
THEME_FELT_PREVIEW = {
    "Classic Green": (22,105,50),
    "Midnight Blue": (20,40,110),
    "Desert Sand":   (185,145,70),
}

# ─── فونت‌ها (بعد از pygame.init) ────────────────────────────────────────────
def init_fonts():
    global FONT_SMALL, FONT_MED, FONT_LARGE, FONT_XLARGE, FONT_MENU, FONT_TITLE
    FONT_SMALL  = pygame.font.SysFont('Arial', 12, bold=True)
    FONT_MED    = pygame.font.SysFont('Arial', 17, bold=True)
    FONT_LARGE  = pygame.font.SysFont('Arial', 26, bold=True)
    FONT_XLARGE = pygame.font.SysFont('Arial', 42, bold=True)
    FONT_MENU   = pygame.font.SysFont('Arial', 22, bold=True)
    FONT_TITLE  = pygame.font.SysFont('Arial', 52, bold=True)

FONT_SMALL = FONT_MED = FONT_LARGE = FONT_XLARGE = FONT_MENU = FONT_TITLE = None
