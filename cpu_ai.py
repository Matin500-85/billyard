"""
Created on Sun Jun  7 15:49:46 2026

@author: Matin
"""


# -*- coding: utf-8 -*-
"""
cpu_ai.py — هوش مصنوعی CPU

الگوریتم مشترک همه سطوح:
  1. Ghost Ball: برای هر (ball, pocket) نقطه تماس دقیق محاسبه می‌شود
  2. Line-of-sight check: بررسی عدم وجود مانع بین cue و ghost_pos
  3. Power calibration: سرعت بر اساس فاصله واقعی محاسبه می‌شود
  4. Cut angle filter: زوایای بیشتر از حد مجاز کنار گذاشته می‌شوند
"""

import math
import random
import time
from core.constants import (
    POCKET_X, POCKET_Y, NUM_POCKETS, FPS
)


# ─── تنظیمات هر سطح ──────────────────────────────────────────────────────────
_LEVEL_CFG = {
    #            err_sd  max_cut  candidates  blind_chance  speed_jitter  think_f
    'Easy':   (0.055,   55,      4,           0.08,         0.12,         55),
    'Normal': (0.018,   70,      8,           0.01,         0.05,         70),
    'Hard':   (0.004,   80,      999,         0.00,         0.01,         85),
}

# فاصله‌ای که CPU قبل از شوت "فکر می‌کند" (فریم)
_THINK_FRAMES_DEFAULT = 70


def _dist(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)


def _unit(dx, dy):
    d = math.hypot(dx, dy)
    if d == 0:
        return 0.0, 1.0
    return dx / d, dy / d


def _ghost_pos(ball_x, ball_y, pocket_x, pocket_y, R):
    """
    نقطه‌ای که توپ سفید باید در آن با توپ هدف تماس بگیرد
    تا توپ هدف دقیقاً به سمت pocket برود.
    """
    dx = ball_x - pocket_x
    dy = ball_y - pocket_y
    d  = math.hypot(dx, dy)
    if d == 0:
        return ball_x, ball_y
    inv = 1.0 / d
    return ball_x + dx * inv * R * 2, ball_y + dy * inv * R * 2


def _cut_angle_deg(cue_x, cue_y, ghost_x, ghost_y, ball_x, ball_y):
    """
    زاویه بریدن (cut angle) بین خط cue→ghost و ghost→ball.
    هرچه بزرگتر، شات سخت‌تر.
    """
    ux1, uy1 = _unit(ghost_x - cue_x, ghost_y - cue_y)
    ux2, uy2 = _unit(ball_x - ghost_x, ball_y - ghost_y)
    dot = max(-1.0, min(1.0, ux1*ux2 + uy1*uy2))
    return math.degrees(math.acos(dot))


def _los_clear(cue_x, cue_y, gx, gy, balls, target_ball, R):
    """
    بررسی آزاد بودن مسیر cue → ghost_pos از توپ‌های دیگر.
    اگر توپی در این مسیر باشد، امتیاز منفی (شات مسدود).
    """
    dx, dy = gx - cue_x, gy - cue_y
    total   = math.hypot(dx, dy)
    if total < 1:
        return True
    ux, uy = dx / total, dy / total

    for ball in balls:
        if ball is target_ball:
            continue
        # فاصله عمودی توپ از خط cue→ghost
        ex = ball.x - cue_x; ey = ball.y - cue_y
        proj = ex * ux + ey * uy
        if proj < R or proj > total - R:
            continue
        perp = abs(ex * uy - ey * ux)
        if perp < R * 1.8:   # با کمی حاشیه اطمینان
            return False
    return True


def _score_shot(cue_x, cue_y, ball, pk, R, balls):
    """
    امتیاز کیفیت شات (کمتر = بهتر).
    ترکیبی از:
      - فاصله cue تا ghost (هرچه دورتر، سخت‌تر)
      - فاصله ball تا pocket
      - cut angle (زاویه بریدن)
      - مانع در مسیر
    """
    gx, gy = _ghost_pos(ball.x, ball.y, POCKET_X[pk], POCKET_Y[pk], R)
    d_cue  = _dist(cue_x, cue_y, gx, gy)
    d_ball = _dist(ball.x, ball.y, POCKET_X[pk], POCKET_Y[pk])
    cut    = _cut_angle_deg(cue_x, cue_y, gx, gy, ball.x, ball.y)

    blocked = 0 if _los_clear(cue_x, cue_y, gx, gy, balls, ball, R) else 8000

    return d_cue * 0.4 + d_ball * 0.6 + cut * 18 + blocked


def _calibrate_speed(d_cue, d_ball, jitter):
    """
    سرعت شات متناسب با فاصله واقعی.
    کافی باشه که توپ هدف به سوراخ برسه + کمی اضافه.
    """
    # فاصله کل مسیر cue->ghost + ghost->ball (تقریب)
    total_path = d_cue + d_ball
    # سرعت پایه: حداقل 14، حداکثر 26
    base = max(14.0, min(26.0, 9.0 + total_path * 0.022))
    return base * (1.0 + random.gauss(0, jitter))


class CPUPlayer:
    def __init__(self, ai_level: str):
        self.ai_level    = ai_level
        cfg              = _LEVEL_CFG.get(ai_level, _LEVEL_CFG['Normal'])
        self._err_sd     = cfg[0]
        self._max_cut    = cfg[1]
        self._candidates = cfg[2]
        self._blind_ch   = cfg[3]
        self._spd_jitter = cfg[4]
        think_frames = cfg[5]
        self.think_delay = think_frames / 60.0   # مثلاً 70/60 ≈ 1.17 ثانیه
        self._time_remaining = 0.0
        self._last_time = None
        self.shot_ready  = False
        self._vx = 0.0
        self._vy = 0.0

    def reset_turn(self):
        self._time_remaining = self.think_delay
        self.shot_ready = False
        self._last_time = None   # برای محاسبه dt در اولین فریم
        

    def update(self, game) -> bool:
        if self.shot_ready:
            return False
        
        now = time.perf_counter()
        if self._last_time is None:
            self._last_time = now
            return False
        
        dt = now - self._last_time
        self._last_time = now
        if dt > 0.03:   # جلوگیری از پرش ناگهانی
            dt = 0.03
        
        self._time_remaining -= dt
        if self._time_remaining > 0:
            return False
        
        self._plan_shot(game)
        self.shot_ready = True
        return True

    def get_shot(self):
        return self._vx, self._vy

    # ─────────────────────────────────────────────────────────────────────────
    def _get_targets(self, game):
        cp  = 1
        cue = game.cue_ball
        if game.pocketed_count[cp] >= 7:
            return [b for b in game.balls if b.is_eight]
        if game.table_open:
            return [b for b in game.balls if b is not cue and not b.is_eight]
        pt = game.player_type[cp]
        if pt == 'solid':  return [b for b in game.balls if b.is_solid]
        if pt == 'stripe': return [b for b in game.balls if b.is_stripe]
        return []

    # ─────────────────────────────────────────────────────────────────────────
    def _plan_shot(self, game):
        cue     = game.cue_ball
        R       = game.ball_radius
        targets = self._get_targets(game)

        # هیچ هدفی نیست -> شوت تصادفی ضعیف
        if not targets:
            angle    = random.uniform(0, 2 * math.pi)
            self._vx = math.cos(angle) * 10.0 * FPS
            self._vy = math.sin(angle) * 10.0 * FPS
            return

        # ── شانس شوت کور (فقط Easy) ─────────────────────────────────────────
        if self._blind_ch > 0 and random.random() < self._blind_ch:
            target = random.choice(targets)
            dx = target.x - cue.x; dy = target.y - cue.y
            d  = math.hypot(dx, dy) or 1.0
            err = random.gauss(0, 0.35)
            angle    = math.atan2(dy/d, dx/d) + err
            spd      = random.uniform(10, 16)
            self._vx = math.cos(angle) * spd * FPS
            self._vy = math.sin(angle) * spd * FPS
            return

        # ── جمع‌آوری و امتیازدهی کاندیداها ─────────────────────────────────
        scored = []
        for ball in targets:
            for pk in range(NUM_POCKETS):
                gx, gy = _ghost_pos(ball.x, ball.y, POCKET_X[pk], POCKET_Y[pk], R)
                cut = _cut_angle_deg(cue.x, cue.y, gx, gy, ball.x, ball.y)
                if cut > self._max_cut:
                    continue     # زاویه غیر قابل اجرا
                s = _score_shot(cue.x, cue.y, ball, pk, R, game.balls)
                scored.append((s, ball, pk, gx, gy))

        if not scored:
            # هیچ شات قابل قبولی نیست -> ضعیف‌ترین شوت ممکن
            scored = []
            for ball in targets:
                for pk in range(NUM_POCKETS):
                    gx, gy = _ghost_pos(ball.x, ball.y, POCKET_X[pk], POCKET_Y[pk], R)
                    s = _score_shot(cue.x, cue.y, ball, pk, R, game.balls)
                    scored.append((s, ball, pk, gx, gy))

        scored.sort(key=lambda x: x[0])

        # ── انتخاب شات ───────────────────────────────────────────────────────
        pool = scored[:max(1, min(self._candidates, len(scored)))]
        pick = pool[0]   # همیشه بهترین از pool
        if self.ai_level == 'Easy' and len(pool) > 1:
            # Easy: از ۴ تا بهترین، یکی تصادفی
            pick = random.choice(pool[:4])

        _, target, pk, gx, gy = pick

        # ── محاسبه جهت و سرعت شوت ───────────────────────────────────────────
        dx = gx - cue.x; dy = gy - cue.y
        dist_cue_ghost = math.hypot(dx, dy)
        dist_ball_pock = _dist(target.x, target.y, POCKET_X[pk], POCKET_Y[pk])

        if dist_cue_ghost < 1:
            # توپ سفید روی ghost pos → مستقیم به سوراخ
            dx = POCKET_X[pk] - cue.x
            dy = POCKET_Y[pk] - cue.y
            dist_cue_ghost = math.hypot(dx, dy) or 1.0

        ux, uy = dx / dist_cue_ghost, dy / dist_cue_ghost

        speed = _calibrate_speed(dist_cue_ghost, dist_ball_pock, self._spd_jitter)
        speed *=FPS

        # ── اضافه کردن خطای زاویه ────────────────────────────────────────────
        err   = random.gauss(0, self._err_sd)
        angle = math.atan2(uy, ux) + err

        self._vx = math.cos(angle) * speed
        self._vy = math.sin(angle) * speed
