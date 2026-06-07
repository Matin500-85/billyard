"""
Created on Sat Jun  6 13:11:06 2026

@author: Matin
"""

# -*- coding: utf-8 -*-
"""
physics.py — کلاس توپ + فیزیک برخورد
"""
import pygame
from core.constants import (
    FRICTION_RATE, RESTITUTION, STOP_SPEED_SQ,
    POCKET_X, POCKET_Y, NUM_POCKETS, POCKET_NEAR_SQ,
    WALL_LEFT, WALL_RIGHT, WALL_TOP, WALL_BOTTOM,
    BALL_BASE_COLOR, WHITE, BLACK,
)


class Ball:
    def __init__(self, x, y, radius, number=0):
        self.x = float(x); self.y = float(y)
        self.radius = radius; self.number = number
        self.vx = 0.0; self.vy = 0.0

    @property
    def is_stripe(self): return self.number >= 9
    @property
    def is_solid(self):  return 1 <= self.number <= 7
    @property
    def is_eight(self):  return self.number == 8
    @property
    def is_still(self):  return self.vx == 0.0 and self.vy == 0.0
    @property
    def base_color(self):
        return WHITE if self.number == 0 else BALL_BASE_COLOR.get(self.number, (180,180,180))

    def move(self, dt):
    # کاهش سرعت خطی وابسته به زمان
        self.vx *= (1 - FRICTION_RATE * dt)
        self.vy *= (1 - FRICTION_RATE * dt)
        if self.vx*self.vx + self.vy*self.vy < STOP_SPEED_SQ:
            self.vx = self.vy = 0.0
        self.x += self.vx * dt
        self.y += self.vy * dt

    def resolve_wall_collisions(self):
        bx, by = self.x, self.y
        for i in range(NUM_POCKETS):
            ddx = bx - POCKET_X[i]; ddy = by - POCKET_Y[i]
            if ddx*ddx + ddy*ddy < POCKET_NEAR_SQ: return
        r = self.radius
        if   bx - r < WALL_LEFT:    self.x = WALL_LEFT  + r; self.vx = -self.vx * RESTITUTION
        elif bx + r > WALL_RIGHT:   self.x = WALL_RIGHT  - r; self.vx = -self.vx * RESTITUTION
        if   by - r < WALL_TOP:     self.y = WALL_TOP   + r; self.vy = -self.vy * RESTITUTION
        elif by + r > WALL_BOTTOM:  self.y = WALL_BOTTOM - r; self.vy = -self.vy * RESTITUTION

    def draw(self, surface, font_ball):
        ix, iy = int(self.x), int(self.y)
        r = self.radius; col = self.base_color

        if self.number == 0:
            pygame.draw.circle(surface, WHITE, (ix, iy), r)

        elif self.is_stripe:
            bs = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
            cx2 = cy2 = r + 1
            pygame.draw.circle(bs, WHITE, (cx2, cy2), r)
            sh = int(r * 0.58)
            for dy in range(-sh, sh+1):
                csq = r*r - dy*dy
                if csq < 0: continue
                hw = int(csq**0.5)
                pygame.draw.line(bs, col, (cx2-hw, cy2+dy), (cx2+hw, cy2+dy))
            for dy in list(range(-r, -sh)) + list(range(sh+1, r+1)):
                csq = r*r - dy*dy
                if csq < 0: continue
                hw = int(csq**0.5)
                pygame.draw.line(bs, WHITE, (cx2-hw, cy2+dy), (cx2+hw, cy2+dy))
            surface.blit(bs, (ix-r-1, iy-r-1))

        else:
            pygame.draw.circle(surface, col, (ix, iy), r)

        border_col = (80,80,80) if self.number == 0 else BLACK
        pygame.draw.circle(surface, border_col, (ix, iy), r, 1)

        if self.number > 0:
            nr = max(5, int(r * 0.48))
            pygame.draw.circle(surface, WHITE, (ix, iy), nr)
            pygame.draw.circle(surface, (120,120,120), (ix, iy), nr, 1)
            txt = font_ball.render(str(self.number), True, BLACK)
            surface.blit(txt, txt.get_rect(center=(ix, iy)))

        pygame.draw.circle(surface, WHITE,
                           (ix - int(r*0.28), iy - int(r*0.30)),
                           max(2, int(r*0.16)))


def resolve_ball_collision(b1: Ball, b2: Ball, ball_radius: float):
    dx = b2.x - b1.x; dy = b2.y - b1.y
    dist_sq = dx*dx + dy*dy
    min_sq  = (ball_radius * 2) ** 2
    if dist_sq >= min_sq or dist_sq == 0: return
    dist = dist_sq ** 0.5; overlap = ball_radius * 2 - dist
    inv = 1.0 / dist; nx, ny = dx * inv, dy * inv
    half = overlap * 0.5
    b1.x -= nx * half; b1.y -= ny * half
    b2.x += nx * half; b2.y += ny * half
    tx, ty = -ny, nx
    v1n = b1.vx*nx + b1.vy*ny; v1t = b1.vx*tx + b1.vy*ty
    v2n = b2.vx*nx + b2.vy*ny; v2t = b2.vx*tx + b2.vy*ty
    b1.vx = v2n*nx + v1t*tx; b1.vy = v2n*ny + v1t*ty
    b2.vx = v1n*nx + v2t*tx; b2.vy = v1n*ny + v2t*ty
