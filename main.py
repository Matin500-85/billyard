"""
Created on Sun Jun  7 23:31:56 2026

@author: Matin
"""

# -*- coding: utf-8 -*-
"""
main.py — نقطه ورود بازی بیلیارد
"""
import pygame
import sys
import os


sys.path.insert(0, os.path.dirname(__file__))

pygame.init()
pygame.font.init()

from core.constants import WIDTH, HEIGHT, init_fonts
from ui.menus import ModeMenu, SettingsMenu
from game     import BilliardGame

init_fonts()


def main():
    info  = pygame.display.Info()
    win_w = min(WIDTH,  info.current_w)
    win_h = min(HEIGHT, info.current_h - 60)
    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption("8-Ball Pool")

    while True:
        mode = ModeMenu(screen).run()
        if mode is None: break

        settings = SettingsMenu(screen, mode).run()
        if settings is None: continue

        result = BilliardGame(screen, settings, mode).run()
        if result == 'quit': break

    pygame.quit()


if __name__ == "__main__":
    main()
