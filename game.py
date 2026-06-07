"""
Created on Sat Jun  6 22:14:40 2026

@author: Matin
"""

# -*- coding: utf-8 -*-
"""
game.py — منطق اصلی بازی (BilliardGame)
"""
import pygame
import time
from core.constants import (
    WIDTH, HEIGHT, FPS, TABLE_MID_Y,
    POCKET_X, POCKET_Y, NUM_POCKETS, POCKET_RADIUS_SQ,
    SCORE_OWN_BALL, SCORE_OPP_BALL,
    THEMES,
)
from core.physics import Ball, resolve_ball_collision
from ai.cpu_ai    import CPUPlayer
from ui.table     import build_table_cache
from ui.hud       import HUDRenderer, GameOverRenderer
from ui.aim       import draw_aim


class BilliardGame:
    def __init__(self, screen, settings: dict, mode: str):
        self.screen     = screen
        self.mode       = mode
        self.theme_name = settings['theme']
        self.theme      = THEMES[self.theme_name]
        self.table_diff = settings['table_diff']
        self.ai_level   = settings.get('ai_level', 'Normal')
        self.ball_radius= 25 if self.table_diff == 'Hard' else 17
        self.cpu        = CPUPlayer(self.ai_level) if mode == '1p' else None
        self._game_surf = pygame.Surface((WIDTH, HEIGHT))

        self._hud      = HUDRenderer(screen, mode, self.theme_name,
                                     self.table_diff, self.ai_level)
        self._go_rend  = GameOverRenderer(screen)
        self._reset()

    # ─── ریست ────────────────────────────────────────────────────────────────
    def _reset(self):
        R = self.ball_radius
        self.balls: list[Ball] = []
        self.cue_ball = Ball(WIDTH//4, TABLE_MID_Y, R, 0)
        self.balls.append(self.cue_ball)

        ORDER = [1,9,2,3,8,10,4,11,5,12,6,13,7,14,15]
        apex_x = int(WIDTH*0.67); apex_y = TABLE_MID_Y; idx = 0
        for row in range(5):
            for col in range(row+1):
                x = apex_x + row*int(R*2*0.866)
                y = apex_y + (col - row/2.0)*(R*2+1)
                self.balls.append(Ball(x, y, R, ORDER[idx])); idx += 1

        self.scores             = [0, 0]
        self.pocketed_count     = [0, 0]
        self.current_player     = 0
        self.ball_pocketed_turn = False
        self.foul_occurred      = False
        self.was_moving         = False
        self.game_over          = False
        self.winner             = None
        self.lose_reason        = ""
        self.last_message       = ""
        self.is_aiming          = False
        self.mouse_start        = (0, 0)
        self.table_open         = True
        self.player_type        = [None, None]

        if self.cpu: self.cpu.reset_turn()
        self._table_cache = build_table_cache(self.theme_name)
        self._hud._prev_state = None

        fs = 20 if self.table_diff == 'Hard' else 12
        self._font_ball = pygame.font.SysFont('Arial', fs, bold=True)

    # ─── ویژگی‌ها ─────────────────────────────────────────────────────────────
    @property
    def table_is_silent(self):
        return all(b.is_still for b in self.balls)

    def _my_ball(self, ball):
        if ball.is_eight: return False
        if self.table_open: return True
        pt = self.player_type[self.current_player]
        if pt == 'solid':  return ball.is_solid
        if pt == 'stripe': return ball.is_stripe
        return False

    # ─── رویدادها ─────────────────────────────────────────────────────────────
    def handle_events(self, events):
        is_human_turn = (self.mode == '2p') or (self.current_player == 0)
        for event in events:
            if event.type == pygame.QUIT: return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if is_human_turn and self.table_is_silent and not self.game_over:
                    self.is_aiming = True; self.mouse_start = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                if self.is_aiming:
                    self.is_aiming = False
                    dx = self.mouse_start[0] - event.pos[0]
                    dy = self.mouse_start[1] - event.pos[1]
                    self.cue_ball.vx = dx * 0.12 * FPS
                    self.cue_ball.vy = dy * 0.12 * FPS
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE:    self._reset()
                    elif event.key == pygame.K_ESCAPE: return 'menu'
                else:
                    if event.key == pygame.K_ESCAPE: return 'menu'
        return 'ok'

    # ─── CPU ──────────────────────────────────────────────────────────────────
    def update_cpu(self):
        if not self.cpu or self.game_over: return
        if self.current_player != 1: return
        if not self.table_is_silent: return
        if self.cpu.update(self):
            vx, vy = self.cpu.get_shot()
            self.cue_ball.vx = vx; self.cue_ball.vy = vy

    # ─── فیزیک ───────────────────────────────────────────────────────────────
    def update_physics(self, dt):
        R = self.ball_radius
        for b in self.balls:
            b.move(dt)
            b.resolve_wall_collisions()
        n = len(self.balls)
        for i in range(n):
            for j in range(i+1, n):
                resolve_ball_collision(self.balls[i], self.balls[j], R)

    # ─── پاکت شدن ────────────────────────────────────────────────────────────
    def check_pocketing(self):
        if self.game_over: return
        cp, op = self.current_player, 1-self.current_player
        i = len(self.balls) - 1
        while i >= 0:
            ball = self.balls[i]; pocketed = False
            for k in range(NUM_POCKETS):
                ddx = ball.x - POCKET_X[k]; ddy = ball.y - POCKET_Y[k]
                if ddx*ddx + ddy*ddy < POCKET_RADIUS_SQ:
                    pocketed = True; break
            if pocketed:
                self._handle_pocketed(ball, i, cp, op)
            i -= 1

    def _handle_pocketed(self, ball, idx, cp, op):
        if ball.number == 0:
            self.foul_occurred = True
            ball.x, ball.y = float(WIDTH//4), float(TABLE_MID_Y)
            ball.vx = ball.vy = 0.0
            self.last_message = "Foul! Cue ball pocketed — turn passes"

        elif ball.is_eight:
            self.balls.pop(idx)
            if self.pocketed_count[cp] < 7:
                self.game_over = True; self.winner = op
                n = 'You' if cp==0 and self.mode=='1p' else f'Player {cp+1}'
                self.lose_reason = f"{n} pocketed the 8-ball early!"
            else:
                self.game_over = True; self.winner = cp
                self.lose_reason = ""

        elif ball.is_solid or ball.is_stripe:
            self.balls.pop(idx)
            if self.table_open:
                self._assign_types(ball, cp, op)
            elif self._my_ball(ball):
                self.scores[cp] += SCORE_OWN_BALL
                self.pocketed_count[cp] += 1
                self.ball_pocketed_turn = True
                pn = 'You' if cp==0 and self.mode=='1p' else f'Player {cp+1}'
                self.last_message = f"+{SCORE_OWN_BALL}  {pn}"
            else:
                self.scores[cp] += SCORE_OPP_BALL
                self.pocketed_count[op] += 1
                self.foul_occurred = True
                on = 'CPU' if op==1 and self.mode=='1p' else f'P{op+1}'
                self.last_message = (f"{SCORE_OPP_BALL}  opponent's ball!  "
                                     f"({on}: {self.pocketed_count[op]}/7)")

    def _assign_types(self, ball, cp, op):
        self.table_open = False
        if ball.is_solid:
            self.player_type[cp] = 'solid';  self.player_type[op] = 'stripe'
        else:
            self.player_type[cp] = 'stripe'; self.player_type[op] = 'solid'
        self.scores[cp] += SCORE_OWN_BALL
        self.pocketed_count[cp] += 1
        self.ball_pocketed_turn = True
        pn = 'You' if cp==0 and self.mode=='1p' else f'P{cp+1}'
        on = 'CPU' if op==1 and self.mode=='1p' else f'P{op+1}'
        pt_cp = self.player_type[cp]; pt_op = self.player_type[op]
        self.last_message = (f"Table closed!  "
                             f"{pn}={pt_cp.upper()}  {on}={pt_op.upper()}")
        self._hud._prev_state = None

    # ─── مدیریت نوبت ──────────────────────────────────────────────────────────
    def manage_turns(self):
        any_moving = any(not b.is_still for b in self.balls)
        if any_moving: self.was_moving = True
        if self.was_moving and not any_moving:
            if self.foul_occurred:
                self.current_player     = 1 - self.current_player
                self.foul_occurred      = False
                self.ball_pocketed_turn = False
            elif not self.ball_pocketed_turn:
                self.current_player = 1 - self.current_player
            self.ball_pocketed_turn = False
            self.was_moving         = False
            self._hud._prev_state   = None
            if self.cpu and self.current_player == 1:
                self.cpu.reset_turn()

    # ─── رندر ────────────────────────────────────────────────────────────────
    def render(self, mouse_pos):
        surf = self._game_surf
        surf.blit(self._table_cache, (0, 0))

        # نشانه‌گیری
        if self.is_aiming:
            is_cpu = (self.mode == '1p' and self.current_player == 1)
            draw_aim(
                surf, self.cue_ball, self.mouse_start, mouse_pos,
                self.table_diff, self.balls, self.ball_radius,
                self.current_player, self.pocketed_count,
                self.table_open, self.player_type, self._my_ball,
                is_cpu_turn=is_cpu,
            )

        for ball in self.balls:
            ball.draw(surf, self._font_ball)

        # HUD روی screen اصلی
        real = self.screen
        win_w, win_h = real.get_size()
        if win_w != WIDTH or win_h != HEIGHT:
            real.blit(pygame.transform.scale(surf, (win_w, win_h)), (0, 0))
        else:
            real.blit(surf, (0, 0))

        self._hud.screen = real
        self._hud.draw(self)
        if self.game_over:
            self._go_rend.screen = real
            self._go_rend.draw(self, self.mode)

        pygame.display.flip()

    # ─── حلقه اصلی ───────────────────────────────────────────────────────────
    def run(self):
        last_time = time.perf_counter()
        while True:
            now = time.perf_counter()
            dt = now - last_time
            if dt > 0.03:   # جلوگیری از پرش ناگهانی
                dt = 0.03
            last_time = now
            events    = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()
            result    = self.handle_events(events)
            if result == 'quit': return 'quit'
            if result == 'menu': return 'menu'
            self.update_cpu()
            self.update_physics(dt)
            self.check_pocketing()
            self.manage_turns()
            self.render(mouse_pos)
