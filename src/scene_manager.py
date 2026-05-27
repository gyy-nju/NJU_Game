import pygame
from src.config import Scene
from src.start_screen import StartScreen
from src.overworld import Overworld


class SceneManager:
    def __init__(self):
        self.current_scene = Scene.START
        self.scenes = {
            Scene.START: StartScreen(),
            Scene.OVERWORLD: Overworld()
        }

    def switch_to(self, scene_name):
        """切换到指定场景"""
        if scene_name in self.scenes:
            self.current_scene = scene_name

    def update(self, events):
        """处理当前场景的逻辑，并接收可能返回的下一个场景名"""
        next_scene = self.scenes[self.current_scene].update(events)
        if next_scene:
            self.switch_to(next_scene)

    def draw(self, screen):
        """绘制当前场景"""
        self.scenes[self.current_scene].draw(screen)