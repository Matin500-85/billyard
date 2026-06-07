"""
Created on Sun Jun  7 15:49:46 2026

@author: Matin
"""

# -*- coding: utf-8 -*-
"""
aim.py — رسم چوب بیلیارد، خط نشانه‌گیری و ray casting
"""
import pygame
from core.constants import (
    WALL_LEFT, WALL_RIGHT, WALL_TOP, WALL_BOTTOM,
    POCKET_X, POCKET_Y, NUM_POCKETS, POCKET_RADIUS_SQ,
)


def cast_ray(ox, oy, ux, uy, balls, cue_ball, ball_radius, current_player,
             pocketed_count, table_open, player_type, my_ball_fn):
    R = ball_radius
    MAX = 1400.0; STEP = 1.5; d = float(R) + 2.0
    hit_sq = (R * 2 - 1) ** 2

    while d < MAX:
        cx = ox + ux*d; cy = oy + uy*d

        for k in range(NUM_POCKETS):
            ddx = cx - POCKET_X[k]; ddy = cy - POCKET_Y[k]
            if ddx*ddx + ddy*ddy < POCKET_RADIUS_SQ:
                return cx, cy, 'pocket', None, 0.0, 0.0

        if cx - R <= WALL_LEFT or cx + R >= WALL_RIGHT:
            return cx, cy, 'wall', None, 0.0, 0.0
        if cy - R <= WALL_TOP  or cy + R >= WALL_BOTTOM:
            return cx, cy, 'wall', None, 0.0, 0.0

        for ball in balls:
            if ball is cue_ball: continue
            ddx = cx - ball.x; ddy = cy - ball.y
            if ddx*ddx + ddy*ddy < hit_sq:
                if ball.is_eight:
                    btype = 'eight_ok' if pocketed_count[current_player] >= 7 else 'eight_bad'
                elif table_open or my_ball_fn(ball):
                    btype = 'own'
                else:
                    btype = 'enemy'
                ndx = ball.x - cx; ndy = ball.y - cy
                nd  = (ndx*ndx + ndy*ndy) ** 0.5
                if nd > 0:
                    inv = 1.0 / nd
                    return cx, cy, btype, ball, ndx*inv, ndy*inv
                return cx, cy, btype, ball, ux, uy

        d += STEP

    return ox + ux*MAX, oy + uy*MAX, 'wall', None, 0.0, 0.0


def draw_aim(surface, cue_ball, mouse_start, mouse_pos, table_diff,
             balls, ball_radius, current_player, pocketed_count,
             table_open, player_type, my_ball_fn, is_cpu_turn=False):
    if is_cpu_turn: return
    dx = mouse_start[0] - mouse_pos[0]; dy = mouse_start[1] - mouse_pos[1]
    dist_sq = dx*dx + dy*dy
    if dist_sq == 0: return
    dist = dist_sq ** 0.5; inv = 1.0 / dist
    ux, uy = dx * inv, dy * inv
    R = ball_radius

    # چوب بیلیارد
    shift  = dist * 0.4; s_dist = R + 8 + shift; e_dist = R + 230 + shift
    ss = (cue_ball.x - ux*s_dist,      cue_ball.y - uy*s_dist)
    se = (cue_ball.x - ux*e_dist,      cue_ball.y - uy*e_dist)
    te = (cue_ball.x - ux*(s_dist+14), cue_ball.y - uy*(s_dist+14))
    pygame.draw.line(surface, (150,100,50), ss, se, 7)
    pygame.draw.line(surface, (100,70,30),  ss, se, 3)
    pygame.draw.line(surface, (240,230,190), ss, te, 7)

    if table_diff == 'Hard': return

    hit_x, hit_y, hit_type, hit_ball, nx, ny = cast_ray(
        cue_ball.x, cue_ball.y, ux, uy,
        balls, cue_ball, R, current_player,
        pocketed_count, table_open, player_type, my_ball_fn
    )

    COLOR_AIM = {
        'wall':     (220,220,220), 'pocket':   (220,220,220),
        'own':      (50,230,80),   'eight_ok': (50,230,80),
        'enemy':    (230,50,50),   'eight_bad':(230,50,50),
    }
    line_color = COLOR_AIM.get(hit_type, (220,220,220))

    # خط‌چین اصلی
    start_d = float(R) + 4
    hdx = hit_x - cue_ball.x; hdy = hit_y - cue_ball.y
    total_d = (hdx*hdx + hdy*hdy) ** 0.5
    dash, gap = 9, 7; d = start_d
    while d < total_d:
        t2 = min(d + dash, total_d)
        sx = int(cue_ball.x + ux*d);  sy = int(cue_ball.y + uy*d)
        ex = int(cue_ball.x + ux*t2); ey = int(cue_ball.y + uy*t2)
        pygame.draw.line(surface, line_color, (sx, sy), (ex, ey), 2)
        d += dash + gap

    pygame.draw.circle(surface, line_color, (int(hit_x), int(hit_y)), 5, 2)
    if hit_ball is not None:
        pygame.draw.circle(surface, line_color,
                           (int(hit_ball.x), int(hit_ball.y)), R + 4, 2)

    # بازتاب (فقط Easy)
    if table_diff == 'Easy' and hit_ball is not None:
        _draw_reflections(surface, hit_x, hit_y, hit_ball, ux, uy, nx, ny, R, line_color)


def _draw_reflections(surface, hit_x, hit_y, hit_ball, ux, uy, nx, ny, R, line_color):
    RL = 55; RD = 6; RG = 5
    v1n = ux*nx + uy*ny; v1t = ux*(-ny) + uy*nx

    # جهت توپ هدف
    t_vx = v1n * nx; t_vy = v1n * ny
    t_sq = t_vx*t_vx + t_vy*t_vy
    if t_sq > 0.0001:
        ts  = t_sq**0.5; tux = t_vx/ts; tuy = t_vy/ts
        sx0 = hit_ball.x + tux*(R+3); sy0 = hit_ball.y + tuy*(R+3)
        ex0 = hit_ball.x + tux*(R+3+RL); ey0 = hit_ball.y + tuy*(R+3+RL)
        if WALL_LEFT <= ex0 <= WALL_RIGHT and WALL_TOP <= ey0 <= WALL_BOTTOM:
            d = 0.0
            while d < RL:
                t2 = min(d+RD, RL)
                pygame.draw.line(surface, line_color,
                    (int(sx0+tux*d), int(sy0+tuy*d)),
                    (int(sx0+tux*t2), int(sy0+tuy*t2)), 2)
                d += RD + RG

    # جهت انحراف توپ سفید
    c_vx = v1t * (-ny); c_vy = v1t * nx
    c_sq = c_vx*c_vx + c_vy*c_vy
    if c_sq > 0.0001:
        cs  = c_sq**0.5; cux = c_vx/cs; cuy = c_vy/cs
        sx0 = hit_x + cux*(R+3); sy0 = hit_y + cuy*(R+3)
        ex0 = hit_x + cux*(R+3+RL); ey0 = hit_y + cuy*(R+3+RL)
        if WALL_LEFT <= ex0 <= WALL_RIGHT and WALL_TOP <= ey0 <= WALL_BOTTOM:
            d = 0.0
            while d < RL:
                t2 = min(d+RD, RL)
                pygame.draw.line(surface, (180,180,255),
                    (int(sx0+cux*d), int(sy0+cuy*d)),
                    (int(sx0+cux*t2), int(sy0+cuy*t2)), 2)
                d += RD + RG
