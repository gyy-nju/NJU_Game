import pygame
from src.config import Scene


class Overworld:
    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return Scene.START  # 按 ESC 回到开始画面
        return None

    def draw(self, screen):
        screen.fill((50, 50, 50))  # 深灰色背景，之后换成地图绘制