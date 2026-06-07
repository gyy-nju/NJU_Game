import pygame
from src.config import Scene
from src.start_screen import StartScreen
from src.character_select import CharacterSelect
from src.overworld import Overworld
from src.building_scene import BuildingScene


class SceneManager:
    def __init__(self):
        self.current_scene = Scene.START
        self.scenes = {
            Scene.START: StartScreen(),
            Scene.SELECT: CharacterSelect(),
            Scene.OVERWORLD: None,
            Scene.BUILDING: BuildingScene()
        }

    def switch_to(self, scene_name):
        if scene_name in self.scenes:
            self.current_scene = scene_name

    def update(self, events):
        next_scene = self.scenes[self.current_scene].update(events)

        if next_scene:
            if next_scene == Scene.OVERWORLD and self.current_scene == Scene.SELECT:
                gender = self.scenes[Scene.SELECT].selected_gender
                self.scenes[Scene.OVERWORLD] = Overworld(gender)

            if next_scene == Scene.BUILDING and self.current_scene == Scene.OVERWORLD:
                nearby = self.scenes[Scene.OVERWORLD].nearby_building
                if nearby:
                    self.scenes[Scene.BUILDING].enter(nearby)

            self.switch_to(next_scene)

    def draw(self, screen):
        self.scenes[self.current_scene].draw(screen)