"""
Created on Sun Jun  7 16:09:17 2026

@author: Matin
"""

# -*- coding: utf-8 -*-
"""
hud.py — رندر HUD (اطلاعات بازیکن، نوبت، امتیاز)
"""
import pygame
from core.constants import (
    WIDTH, HEIGHT, HUD_H, WHITE,GOLD,
    RED_HUD, GREEN_HUD, SHADOW_COLOR,THEMES
)


def _fonts():
    from core.constants import FONT_SMALL, FONT_MED, FONT_LARGE, FONT_XLARGE
    return FONT_SMALL, FONT_MED, FONT_LARGE, FONT_XLARGE


class HUDRenderer:
    """کش رندر HUD — فقط در صورت تغییر state دوباره رندر می‌شود."""

    def __init__(self, screen, mode, theme_name, table_diff, ai_level):
        self.screen      = screen
        self.mode        = mode
        self.theme_name  = theme_name
        self.table_diff  = table_diff
        self.ai_level    = ai_level
        self._cache      = {}
        self._prev_state = None

    def draw(self, game):
        FONT_SMALL, FONT_MED, FONT_LARGE, FONT_XLARGE = _fonts()
        cp = game.current_player
        wm = THEMES[self.theme_name]["wood_mid"]

        p0_name = "You"    if self.mode == '1p' else "Player 1"
        p1_name = "CPU"    if self.mode == '1p' else "Player 2"

        state = (
            cp, game.scores[0], game.scores[1],
            game.pocketed_count[0], game.pocketed_count[1],
            game.last_message, self.table_diff, self.theme_name,
            game.table_open, tuple(game.player_type), self.mode,
        )

        if state != self._prev_state:
            self._rebuild_cache(state, cp, p0_name, p1_name,
                                FONT_SMALL, FONT_MED, FONT_LARGE)
            self._prev_state = state

        c = self._cache
        screen = self.screen

        # ── پانل چپ ──────────────────────────────────────────────────────────
        p0_bg = (20,70,20) if cp == 0 else (40,40,40)
        pygame.draw.rect(screen, p0_bg, (8, 8, 250, HUD_H-16), border_radius=8)
        pygame.draw.rect(screen, wm,    (8, 8, 250, HUD_H-16), 2, border_radius=8)
        screen.blit(c['p0_name'],  (18, 10))
        screen.blit(c['p0_score'], (18, 28))
        screen.blit(c['p0_balls'], (18, 50))
        screen.blit(c['p0_type'],  (18, 62))

        # ── پانل راست ─────────────────────────────────────────────────────────
        p1_bg = (20,70,20) if cp == 1 else (40,40,40)
        pygame.draw.rect(screen, p1_bg, (WIDTH-258, 8, 250, HUD_H-16), border_radius=8)
        pygame.draw.rect(screen, wm,    (WIDTH-258, 8, 250, HUD_H-16), 2, border_radius=8)
        screen.blit(c['p1_name'],  (WIDTH-248, 10))
        screen.blit(c['p1_score'], (WIDTH-248, 28))
        screen.blit(c['p1_balls'], (WIDTH-248, 50))
        screen.blit(c['p1_type'],  (WIDTH-248, 62))

        # ── کادر مرکزی ────────────────────────────────────────────────────────
        cx = WIDTH // 2; mid_w = 360; mid_x = cx - mid_w // 2
        pygame.draw.rect(screen, (25,25,55), (mid_x, 8, mid_w, HUD_H-16), border_radius=8)
        pygame.draw.rect(screen, wm,         (mid_x, 8, mid_w, HUD_H-16), 2, border_radius=8)
        screen.blit(c['turn'], c['turn'].get_rect(center=(cx, 22)))
        screen.blit(c['hint'], c['hint'].get_rect(center=(cx, 40)))
        pygame.draw.line(screen, (70,70,100), (mid_x+4, 50), (mid_x+mid_w-4, 50), 1)
        pygame.draw.circle(screen, c['diff_col'], (mid_x+14, 60), 4)
        screen.blit(c['diff'], (mid_x+22, 54))
        felt_col = THEMES[self.theme_name]["felt"]
        pygame.draw.circle(screen, felt_col, (cx+8, 60), 4)
        screen.blit(c['theme_lbl'], (cx+16, 54))
        if c['ai_lbl']:
            screen.blit(c['ai_lbl'],
                        c['ai_lbl'].get_rect(midright=(mid_x+mid_w-8, 60)))

        if c['msg']:
            screen.blit(c['msg'], c['msg'].get_rect(center=(cx, HEIGHT-14)))

    # ── ساخت کش ───────────────────────────────────────────────────────────────
    def _rebuild_cache(self, state, cp, p0_name, p1_name,
                       FONT_SMALL, FONT_MED, FONT_LARGE):
        (_, sc0, sc1, pc0, pc1, last_msg, table_diff,
         theme_name, table_open, player_type, mode) = state
        c = self._cache

        p0_col = GREEN_HUD if cp == 0 else (160,160,160)
        p1_col = GREEN_HUD if cp == 1 else (160,160,160)
        c['p0_name']  = FONT_MED.render(p0_name,  True, p0_col)
        c['p1_name']  = FONT_MED.render(p1_name,  True, p1_col)
        c['p0_score'] = FONT_LARGE.render(f"{sc0:+}", True, WHITE if cp==0 else (130,130,130))
        c['p1_score'] = FONT_LARGE.render(f"{sc1:+}", True, WHITE if cp==1 else (130,130,130))
        c['p0_balls'] = FONT_SMALL.render(f"Balls: {pc0}/7", True, (200,200,150))
        c['p1_balls'] = FONT_SMALL.render(f"Balls: {pc1}/7", True, (200,200,150))

        if table_open:
            ot = FONT_SMALL.render("OPEN TABLE", True, (180,180,100))
            c['p0_type'] = c['p1_type'] = ot
        else:
            pt0, pt1 = player_type[0] or '', player_type[1] or ''
            c['p0_type'] = FONT_SMALL.render(
                pt0.upper(), True, (255,210,60) if pt0=='solid' else (120,200,255))
            c['p1_type'] = FONT_SMALL.render(
                pt1.upper(), True, (255,210,60) if pt1=='solid' else (120,200,255))

        turn_name = p0_name if cp == 0 else p1_name
        c['turn'] = FONT_MED.render(f"{turn_name}'s Turn", True, GOLD)
        n = pc0 if cp == 0 else pc1
        if n >= 7:
            c['hint'] = FONT_SMALL.render("Pocket the 8-ball to WIN!", True, GOLD)
        else:
            c['hint'] = FONT_SMALL.render(
                f"Need {7-n} more before the 8-ball", True, (180,180,180))

        dc_map = {'Easy':(80,200,80), 'Normal':(210,190,60), 'Hard':(220,80,80)}
        dc = dc_map.get(table_diff, WHITE)
        c['diff_col']  = dc
        c['diff']      = FONT_SMALL.render(table_diff,  True, dc)
        c['theme_lbl'] = FONT_SMALL.render(theme_name,  True, (170,170,200))

        if mode == '1p':
            ac_map = {'Easy':(80,200,80), 'Normal':(210,190,60), 'Hard':(220,80,80)}
            ac = ac_map.get(self.ai_level, WHITE)
            c['ai_lbl'] = FONT_SMALL.render(f"CPU: {self.ai_level}", True, ac)
        else:
            c['ai_lbl'] = None

        c['msg'] = (FONT_SMALL.render(last_msg, True, (255,230,100))
                    if last_msg else None)


class GameOverRenderer:
    """اورلی پایان بازی."""

    def __init__(self, screen):
        self.screen = screen
        self._overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 185))

    def draw(self, game, mode):
        FONT_SMALL, FONT_MED, FONT_LARGE, FONT_XLARGE = _fonts()
        self.screen.blit(self._overlay, (0, 0))
        blink = (pygame.time.get_ticks() // 500) % 2
        w_col = GOLD if blink == 0 else WHITE
        cx = WIDTH // 2; my = (HUD_H + HEIGHT) // 2

        win_txt = (("You WIN!" if game.winner == 0 else "CPU Wins!")
                   if mode == '1p' else f"PLAYER {game.winner+1}  WINS!")
        sh = FONT_XLARGE.render(win_txt, True, SHADOW_COLOR)
        mn = FONT_XLARGE.render(win_txt, True, w_col)
        self.screen.blit(sh, sh.get_rect(center=(cx+3, my-55)))
        self.screen.blit(mn, mn.get_rect(center=(cx,   my-58)))

        if game.lose_reason:
            r = FONT_MED.render(game.lose_reason, True, RED_HUD)
            self.screen.blit(r, r.get_rect(center=(cx, my)))

        f0_lbl = "You"    if mode == '1p' else "Player 1"
        f1_lbl = "CPU"    if mode == '1p' else "Player 2"
        f0 = FONT_MED.render(f"{f0_lbl}: {game.scores[0]:+}", True, WHITE)
        f1 = FONT_MED.render(f"{f1_lbl}: {game.scores[1]:+}", True, WHITE)
        self.screen.blit(f0, f0.get_rect(center=(cx-110, my+35)))
        self.screen.blit(f1, f1.get_rect(center=(cx+110, my+35)))

        if blink == 0:
            rst = FONT_SMALL.render(
                "SPACE = Play Again    ESC = Main Menu", True, (220,220,220))
            self.screen.blit(rst, rst.get_rect(center=(cx, my+68)))
