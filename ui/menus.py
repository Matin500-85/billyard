"""
Created on Sun Jun  7 16:48:11 2026

@author: Matin
"""

# -*- coding: utf-8 -*-
"""
menus.py — منوی انتخاب حالت + منوی تنظیمات
"""
import pygame
from core.constants import (
    WIDTH,WHITE, GOLD,THEME_NAMES,
    THEME_FELT_PREVIEW,
)


def _fonts():
    from core.constants import (
        FONT_SMALL, FONT_MED, FONT_LARGE,
        FONT_XLARGE, FONT_MENU, FONT_TITLE,
    )
    return FONT_SMALL, FONT_MED, FONT_LARGE, FONT_XLARGE, FONT_MENU, FONT_TITLE


# ══════════════════════════════════════════════════════════════════════════════
class ModeMenu:
    def __init__(self, screen):
        self.screen  = screen
        self._btn_2p = pygame.Rect(0, 0, 0, 0)
        self._btn_1p = pygame.Rect(0, 0, 0, 0)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            mx, my = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self._btn_2p.collidepoint(mx, my): return '2p'
                    if self._btn_1p.collidepoint(mx, my): return '1p'
            self._draw(mx, my)
            clock.tick(60)

    def _draw(self, mx, my):
        FS, FM, FL, FX, FMN, FT = _fonts()
        self.screen.fill((12, 10, 6))
        cx = WIDTH // 2
        sh = FT.render("8-Ball Pool", True, (40, 40, 40))
        ti = FT.render("8-Ball Pool", True, GOLD)
        self.screen.blit(sh, sh.get_rect(center=(cx+3, 90)))
        self.screen.blit(ti, ti.get_rect(center=(cx,   87)))
        sub = FM.render("Choose Game Mode", True, (200, 200, 200))
        self.screen.blit(sub, sub.get_rect(center=(cx, 148)))

        btn_w, btn_h, gap = 340, 160, 60
        bx1 = cx - gap//2 - btn_w
        bx2 = cx + gap//2
        self._btn_2p = pygame.Rect(bx1, 200, btn_w, btn_h)
        self._btn_1p = pygame.Rect(bx2, 200, btn_w, btn_h)

        for rect, label, sub_lbl, icon, hov_col in [
            (self._btn_2p, "2 Players",   "Local multiplayer", "", (20,80,20)),
            (self._btn_1p, "Computer", "Single player",     "", (20,40,100)),
        ]:
            hov = rect.collidepoint(mx, my)
            bg  = hov_col if hov else (35,35,35)
            brd = GOLD    if hov else (80,80,80)
            pygame.draw.rect(self.screen, bg,  rect, border_radius=16)
            pygame.draw.rect(self.screen, brd, rect, 2, border_radius=16)
            ico = FX.render(icon,  True, WHITE)
            lbl = FL.render(label, True, WHITE)
            sl  = FS.render(sub_lbl, True, (180,180,180))
            self.screen.blit(ico, ico.get_rect(center=(rect.centerx, rect.top+52)))
            self.screen.blit(lbl, lbl.get_rect(center=(rect.centerx, rect.top+100)))
            self.screen.blit(sl,  sl.get_rect(center=(rect.centerx, rect.top+130)))

        esc = FS.render("ESC = Quit", True, (80,80,80))
        self.screen.blit(esc, esc.get_rect(center=(cx, 400)))
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
class SettingsMenu:
    TABLE_DIFFS = [
        ("Easy",   "Full guide + reflections"),
        ("Normal", "Simple guide, no reflections"),
        ("Hard",   "No guide — balls 1.5× larger"),
    ]
    AI_LEVELS = [
        ("Easy",   "Decent aim, small error"),
        ("Normal", "Accurate — best shot chosen"),
        ("Hard",   "Near-perfect — obstacle aware"),
    ]

    def __init__(self, screen, mode: str):
        self.screen       = screen
        self.mode         = mode
        self.step         = 1
        self.total_steps  = 3 if mode == '1p' else 2
        self.theme_idx    = 0
        self.table_idx    = 0
        self.ai_idx       = 1
        self._theme_rects = []
        self._diff_rects  = []
        self._ai_rects    = []
        self._next_rect   = pygame.Rect(0,0,0,0)
        self._back_rect   = pygame.Rect(0,0,0,0)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            mx, my = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.step > 1: self.step -= 1
                    else: return None
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    result = self._handle_click(mx, my)
                    if result is not None:
                        return result
            self._draw(mx, my)
            clock.tick(60)

    def _handle_click(self, mx, my):
        if self.step == 1:
            for i, r in enumerate(self._theme_rects):
                if r.collidepoint(mx, my): self.theme_idx = i
            if self._next_rect.collidepoint(mx, my): self.step = 2
        elif self.step == 2:
            for i, r in enumerate(self._diff_rects):
                if r.collidepoint(mx, my): self.table_idx = i
            if self._next_rect.collidepoint(mx, my):
                if self.mode == '1p': self.step = 3
                else: return self._result()
            if self._back_rect.collidepoint(mx, my): self.step = 1
        elif self.step == 3:
            for i, r in enumerate(self._ai_rects):
                if r.collidepoint(mx, my): self.ai_idx = i
            if self._next_rect.collidepoint(mx, my): return self._result()
            if self._back_rect.collidepoint(mx, my): self.step = 2

    def _result(self):
        d = {
            'theme':      THEME_NAMES[self.theme_idx],
            'table_diff': self.TABLE_DIFFS[self.table_idx][0],
        }
        if self.mode == '1p':
            d['ai_level'] = self.AI_LEVELS[self.ai_idx][0]
        return d

    # ─── draw ────────────────────────────────────────────────────────────────
    def _draw(self, mx, my):
        FS, FM, FL, FX, FMN, FT = _fonts()
        self.screen.fill((12, 10, 6))
        cx = WIDTH // 2
        ti = FL.render("8-Ball Pool", True, GOLD)
        self.screen.blit(ti, ti.get_rect(center=(cx, 36)))

        step_labels = (["Theme","Table","AI Difficulty"]
                       if self.mode == '1p' else ["Theme","Table"])
        dot_spacing = 120
        dots_x_start = cx - (self.total_steps-1)*dot_spacing//2
        for si in range(self.total_steps):
            sx    = dots_x_start + si*dot_spacing
            done  = (si+1) < self.step
            active= (si+1) == self.step
            col   = GOLD if active else ((100,200,100) if done else (60,60,60))
            pygame.draw.circle(self.screen, col, (sx, 68), 8 if active else 6)
            if si < self.total_steps-1:
                lx = sx+8; rx = dots_x_start+(si+1)*dot_spacing-8
                pygame.draw.line(self.screen,
                                 (100,200,100) if done else (50,50,50),
                                 (lx, 68), (rx, 68), 2)
            slbl = FS.render(step_labels[si], True,
                             WHITE if active else (100,100,100))
            self.screen.blit(slbl, slbl.get_rect(center=(sx, 83)))

        if   self.step == 1: self._draw_theme(cx, mx, my, FS, FM, FL, FMN)
        elif self.step == 2: self._draw_table_diff(cx, mx, my, FS, FM, FL, FMN)
        elif self.step == 3: self._draw_ai(cx, mx, my, FS, FM, FL, FMN)
        pygame.display.flip()

    def _draw_btn_row(self, cx, items, selected_idx, rects_out,
                      by, btn_w, btn_h, gap, FS, FM, FMN, accent_colors=None):
        rects_out.clear()
        total_w = len(items)*btn_w + (len(items)-1)*gap
        sx = cx - total_w//2
        for i, (name, desc) in enumerate(items):
            bx   = sx + i*(btn_w+gap)
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            rects_out.append(rect)
            active = (i == selected_idx)
            hov    = rect.collidepoint(*pygame.mouse.get_pos())
            ac  = (accent_colors[i] if accent_colors else (30,120,30))
            bg  = tuple(c//3 for c in ac) if active else ((50,50,50) if hov else (32,32,32))
            brd = ac if active else ((150,150,150) if hov else (65,65,65))
            pygame.draw.rect(self.screen, bg,  rect, border_radius=12)
            pygame.draw.rect(self.screen, brd, rect, 2, border_radius=12)
            if active:
                pygame.draw.rect(self.screen, ac,
                                 pygame.Rect(bx+2, by+2, btn_w-4, 6), border_radius=8)
            lbl = FMN.render(name, True, WHITE if active else (170,170,170))
            self.screen.blit(lbl, lbl.get_rect(center=(bx+btn_w//2, by+btn_h//2-10)))
            dl  = FS.render(desc,  True, (210,210,130) if active else (90,90,90))
            self.screen.blit(dl,   dl.get_rect(center=(bx+btn_w//2, by+btn_h//2+16)))

    def _draw_nav(self, cx, next_label, show_back, FS, FM, FL, by=430):
        if show_back:
            br  = pygame.Rect(cx-240, by, 160, 48)
            self._back_rect = br
            hov = br.collidepoint(*pygame.mouse.get_pos())
            pygame.draw.rect(self.screen, (60,60,60) if hov else (40,40,40),
                             br, border_radius=10)
            pygame.draw.rect(self.screen, (120,120,120), br, 2, border_radius=10)
            bl = FM.render("Back", True, (200,200,200))
            self.screen.blit(bl, bl.get_rect(center=br.center))
        else:
            self._back_rect = pygame.Rect(0,0,0,0)

        nr = pygame.Rect(cx+80, by, 220, 48)
        self._next_rect = nr
        blink = (pygame.time.get_ticks()//600) % 2
        hov   = nr.collidepoint(*pygame.mouse.get_pos())
        nb    = (30,120,30) if (blink or hov) else (18,80,18)
        pygame.draw.rect(self.screen, nb,   nr, border_radius=12)
        pygame.draw.rect(self.screen, GOLD, nr, 2, border_radius=12)
        nl = FL.render(next_label, True, WHITE)
        self.screen.blit(nl, nl.get_rect(center=nr.center))
        esc = FS.render("ESC = Back", True, (70,70,70))
        self.screen.blit(esc, esc.get_rect(center=(cx, 500)))

    def _draw_theme(self, cx, mx, my, FS, FM, FL, FMN):
        self.screen.blit(FL.render("Step 1 — Table Theme", True, WHITE),
                         FL.render("Step 1 — Table Theme", True, WHITE)
                            .get_rect(center=(cx, 110)))
        self._theme_rects.clear()
        btn_w, btn_h, gap = 300, 120, 28
        total_w = len(THEME_NAMES)*btn_w + (len(THEME_NAMES)-1)*gap
        sx = cx - total_w//2
        for i, tname in enumerate(THEME_NAMES):
            bx = sx + i*(btn_w+gap); by = 145
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            self._theme_rects.append(rect)
            active = (i == self.theme_idx); hov = rect.collidepoint(mx, my)
            bg  = (28,60,28) if active else ((50,50,50) if hov else (32,32,32))
            brd = GOLD       if active else ((150,150,150) if hov else (65,65,65))
            pygame.draw.rect(self.screen, bg,  rect, border_radius=12)
            pygame.draw.rect(self.screen, brd, rect, 2, border_radius=12)
            fc = THEME_FELT_PREVIEW.get(tname, (100,100,100))
            pr = pygame.Rect(bx+14, by+12, btn_w-28, 52)
            pygame.draw.rect(self.screen, fc, pr, border_radius=6)
            pygame.draw.rect(self.screen, WHITE, pr, 1, border_radius=6)
            for xi in range(pr.left+12, pr.right-4, 16):
                pygame.draw.line(self.screen,
                    tuple(max(0, c-8) for c in fc),
                    (xi, pr.top+2), (xi, pr.bottom-2), 1)
            lbl = FMN.render(tname, True, WHITE if active else (180,180,180))
            self.screen.blit(lbl, lbl.get_rect(center=(bx+btn_w//2, by+94)))
        self._draw_nav(cx, "Next", show_back=False, FS=FS, FM=FM, FL=FL, by=300)

    def _draw_table_diff(self, cx, mx, my, FS, FM, FL, FMN):
        self.screen.blit(FL.render("Step 2 — Table Difficulty", True, WHITE),
                         FL.render("Step 2 — Table Difficulty", True, WHITE)
                            .get_rect(center=(cx, 110)))
        tname = THEME_NAMES[self.theme_idx]
        fc    = THEME_FELT_PREVIEW.get(tname, (100,100,100))
        tag   = FS.render(f"Theme: {tname}", True, (170,170,170))
        dr    = pygame.Rect(cx - tag.get_width()//2 - 18, 132, 12, 12)
        pygame.draw.rect(self.screen, fc, dr, border_radius=3)
        self.screen.blit(tag, (cx - tag.get_width()//2, 131))
        accent = [(30,160,60), (180,160,30), (200,50,50)]
        self._draw_btn_row(cx, self.TABLE_DIFFS, self.table_idx,
                           self._diff_rects, 155, 280, 100, 24,
                           FS, FM, FMN, accent)
        next_lbl = "Next" if self.mode == '1p' else "Play!"
        self._draw_nav(cx, next_lbl, show_back=True, FS=FS, FM=FM, FL=FL, by=295)

    def _draw_ai(self, cx, mx, my, FS, FM, FL, FMN):
        self.screen.blit(FL.render("Step 3 — CPU Difficulty", True, WHITE),
                         FL.render("Step 3 — CPU Difficulty", True, WHITE)
                            .get_rect(center=(cx, 110)))
        sub = FS.render("How smart should the computer opponent be?", True, (170,170,170))
        self.screen.blit(sub, sub.get_rect(center=(cx, 133)))
        accent = [(30,160,60), (180,160,30), (200,50,50)]
        self._draw_btn_row(cx, self.AI_LEVELS, self.ai_idx,
                           self._ai_rects, 155, 280, 100, 24,
                           FS, FM, FMN, accent)
        self._draw_nav(cx, "Play!", show_back=True, FS=FS, FM=FM, FL=FL, by=295)
