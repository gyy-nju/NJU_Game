import os
import random
import pygame
from src.config import font2_path

class MinigameCrossroad:
    def __init__(self):
        self.font_large = pygame.font.Font(font2_path, 48)
        self.font_normal = pygame.font.Font(font2_path, 24)
        self.font_small = pygame.font.Font(font2_path, 20)
        self.load_resources()
        self.reset()
        self.result_buttons = []

    def load_resources(self):
        # 背景图
        self.road_bg = None
        bg_path = "assets/images/road.png"
        if os.path.exists(bg_path):
            self.road_bg = pygame.image.load(bg_path).convert()
            self.road_bg = pygame.transform.scale(self.road_bg, (800, 600))

        # 车辆图片
        self.car_images = []
        car_files = ["bus_left.png", "pinkcar_left.png", "taxi_left.png", "bluecar_left.png"]
        for f in car_files:
            path = os.path.join("assets/images", f)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.car_images.append(img)

        # 玩家动画
        self.player_animations = None
        self.gender = None
        self.load_player_animation("男")

    def load_player_animation(self, gender):
        if self.gender == gender and self.player_animations is not None:
            return
        self.gender = gender
        filename = "girl_walk.png" if gender == "女" else "boy_walk.png"
        frame_size = 256 if gender == "女" else 313
        path = os.path.join("assets", "images", filename)
        if not os.path.exists(path):
            self.player_animations = None
            return
        sprite_sheet = pygame.image.load(path).convert_alpha()
        directions = {"down": 0, "right": 1, "left": 2, "up": 3}
        self.player_animations = {}
        for direction, row in directions.items():
            frames = []
            for col in range(4):
                frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
                frame.blit(sprite_sheet, (0, 0), (col * frame_size, row * frame_size, frame_size, frame_size))
                frame = pygame.transform.scale(frame, (80, 80))
                frames.append(frame)
            self.player_animations[direction] = frames

    def reset(self):
        self.player_x = 360
        self.player_y = 512
        self.player_width = 80
        self.player_height = 80
        self.player_speed = 6
        self.lives = 3
        self.invincible_timer = 0
        self.game_state = "playing"
        self.cars = []
        self.spawn_timer = 0
        self.frame_count = 0
        self.show_result = False
        self.result_message = ""
        self.return_building = "南园校门"
        self.return_info = ""
        self.player_direction = "down"
        self.player_frame_index = 0
        self.player_frame_timer = 0
        self.player_frame_delay = 8
        self.player_moving = False
        self.result_buttons = []

    def enter(self, building_data=None, player_data=None, return_building="南园校门"):
        self.building_data = building_data
        self.player_data = player_data
        self.return_building = return_building
        if player_data:
            self.load_player_animation(player_data.gender)
        else:
            self.load_player_animation("男")
        self.reset()
        for _ in range(4):
            self.spawn_car()

    def spawn_car(self):
        lane_centers = [177, 271, 364, 458]
        lane = random.randint(0, 3)
        # 检查该车道是否有车在 650px 范围内（避免新生车与现有车立即重叠）
        too_close = False
        for car in self.cars:
            if abs(car['y'] - lane_centers[lane]) < 20:  # 同一车道
                if car['x'] > 650:
                    too_close = True
                    break
        if too_close:
            return  # 放弃生成本次车辆
        car = {
            'x': 850 + random.randint(0, 300),
            'y': lane_centers[lane] - random.randint(30, 45),
            'speed': random.uniform(3.0, 6.0),
            'width': random.randint(120, 160),
            'height': random.randint(80, 100),
            'image': random.choice(self.car_images) if self.car_images else None
        }
        self.cars.append(car)

    def update(self, events):
        self.frame_count += 1
        if self.game_state == "playing":
            # 玩家移动
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]:
                dx = -self.player_speed
                self.player_direction = "left"
            elif keys[pygame.K_RIGHT]:
                dx = self.player_speed
                self.player_direction = "right"
            elif keys[pygame.K_UP]:
                dy = -self.player_speed
                self.player_direction = "up"
            elif keys[pygame.K_DOWN]:
                dy = self.player_speed
                self.player_direction = "down"

            self.player_moving = dx != 0 or dy != 0
            self.player_x += dx
            self.player_y += dy
            self.player_x = max(40, min(self.player_x, 760 - self.player_width))
            self.player_y = max(0, min(self.player_y, 600 - self.player_height))

            # 动画更新
            if self.player_moving and self.player_animations:
                self.player_frame_timer += 1
                if self.player_frame_timer >= self.player_frame_delay:
                    self.player_frame_timer = 0
                    self.player_frame_index = (self.player_frame_index + 1) % 4
            else:
                self.player_frame_index = 0
                self.player_frame_timer = 0

            # 无敌帧递减
            if self.invincible_timer > 0:
                self.invincible_timer -= 1

            # 生成车辆
            self.spawn_timer += 1
            if self.spawn_timer >= random.randint(40, 70):
                self.spawn_timer = 0
                self.spawn_car()

            # 1. 移动车辆（只做一次！）
            for car in self.cars[:]:
                car['x'] -= car['speed']
                if car['x'] < -100:
                    self.cars.remove(car)

            # 2. 避免同车道车辆重叠
            for i in range(len(self.cars)):
                for j in range(i + 1, len(self.cars)):
                    car_a = self.cars[i]
                    car_b = self.cars[j]
                    if abs(car_a['y'] - car_b['y']) < 20:
                        if car_a['x'] > car_b['x']:
                            car_a, car_b = car_b, car_a
                        if car_a['x'] + car_a['width'] > car_b['x']:
                            car_b['x'] = car_a['x'] + car_a['width'] + 5

            # 3. 碰撞检测（仅在非无敌时）
            if self.invincible_timer <= 0:
                player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)
                player_shrink_w = int(self.player_width * 0.15)
                player_shrink_h = int(self.player_height * 0.15)
                player_rect = player_rect.inflate(-player_shrink_w, -player_shrink_h)

                for car in self.cars[:]:
                    car_rect = pygame.Rect(car['x'], car['y'], car['width'], car['height'])
                    car_shrink_w = int(car['width'] * 0.35)
                    car_shrink_h = int(car['height'] * 0.35)
                    car_rect = car_rect.inflate(-car_shrink_w, -car_shrink_h)

                    if player_rect.colliderect(car_rect):
                        self.lives -= 1
                        self.invincible_timer = 60
                        self.cars.remove(car)
                        if self.lives <= 0:
                            self.game_state = "lose"
                            self.result_message = "平时过马路要注意交通安全~"
                            self.show_result = True
                            return
                        break

            # 4. 胜利判定
            if self.player_y + self.player_height <= 130:
                self.game_state = "win"
                self.cars.clear()
                self.result_message = "挑战成功！"
                self.return_building = "汉口路校门"
                self.return_info = "按 Q 返回汉口路校门"
                self.show_result = True

        # 事件处理（保持不变）
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.show_result:
                    for action, rect in self.result_buttons:
                        if rect.collidepoint(event.pos):
                            if action == "retry":
                                self.reset()
                                self.enter(self.building_data, self.player_data, "南园校门")
                            elif action in ("win_exit", "lose_exit"):
                                if action == "win_exit":
                                    return ("exit_minigame", "汉口路校门")
                                else:
                                    return ("exit_minigame", "南园校门")
                            return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    if not self.show_result:
                        self.return_building = "南园校门"
                    return ("exit_minigame", self.return_building)
                if self.show_result and self.game_state == "lose":
                    if event.key == pygame.K_r:
                        self.reset()
                        self.enter(self.building_data, self.player_data, "南园校门")
                    elif event.key == pygame.K_e or event.key == pygame.K_q:
                        return ("exit_minigame", "南园校门")
                if self.show_result and self.game_state == "win":
                    if event.key == pygame.K_q:
                        return ("exit_minigame", self.return_building)
        return None

    def draw(self, screen):
        if self.road_bg:
            screen.blit(self.road_bg, (0, 0))
        else:
            # 备用绘制（按新比例）
            screen.fill((100, 100, 100))
            # 车道线
            for lane_y in [224, 318, 412]:  # 车道分隔线
                pygame.draw.line(screen, (255, 255, 200), (0, lane_y), (800, lane_y), 2)
            pygame.draw.rect(screen, (180, 180, 180), (0, 0, 800, 130))       # 上安全区
            pygame.draw.rect(screen, (180, 180, 180), (0, 505, 800, 95))      # 下安全区

        for car in self.cars:
            if car['image']:
                img = pygame.transform.scale(car['image'], (car['width'], car['height']))
                screen.blit(img, (car['x'], car['y']))
            else:
                pygame.draw.rect(screen, (200, 50, 50), (car['x'], car['y'], car['width'], car['height']))

        if self.player_animations and self.player_direction in self.player_animations:
            if self.invincible_timer % 10 < 5 or self.invincible_timer <= 0:
                frame = self.player_animations[self.player_direction][self.player_frame_index]
                screen.blit(frame, (self.player_x, self.player_y))
        else:
            if self.invincible_timer % 10 < 5 or self.invincible_timer <= 0:
                pygame.draw.rect(screen, (0, 255, 0), (self.player_x, self.player_y, self.player_width, self.player_height))

        if not self.show_result:
        # 生命值框（左上角）
            lives_text = self.font_normal.render(f"生命值: {self.lives}", True, (255, 255, 255))
            lives_padding = 12
            lives_box_w = lives_text.get_width() + lives_padding * 2
            lives_box_h = lives_text.get_height() + lives_padding
            lives_box = pygame.Rect(20, 20, lives_box_w, lives_box_h)
            # 半透明背景
            lives_bg = pygame.Surface((lives_box_w, lives_box_h), pygame.SRCALPHA)
            lives_bg.fill((0, 0, 0, 160))
            screen.blit(lives_bg, lives_box.topleft)
            # 边框
            pygame.draw.rect(screen, (100, 100, 100), lives_box, 1)
            screen.blit(lives_text, (lives_box.x + lives_padding, lives_box.y + lives_padding // 2))

            # 提示框（顶部居中）
            tip_text = "按 Q 退出"
            tip_surf = self.font_small.render(tip_text, True, (255, 255, 255))
            tip_padding = 10
            tip_box_w = tip_surf.get_width() + tip_padding * 2
            tip_box_h = tip_surf.get_height() + tip_padding
            tip_box_x = (800 - tip_box_w) // 2
            tip_box_y = 20
            tip_box = pygame.Rect(tip_box_x, tip_box_y, tip_box_w, tip_box_h)
            tip_bg = pygame.Surface((tip_box_w, tip_box_h), pygame.SRCALPHA)
            tip_bg.fill((0, 0, 0, 160))
            screen.blit(tip_bg, tip_box.topleft)
            pygame.draw.rect(screen, (100, 100, 100), tip_box, 1)
            screen.blit(tip_surf, (tip_box.x + tip_padding, tip_box.y + tip_padding // 2))

        # 6. 结果界面（菜单风格）
        if self.show_result:
            # 半透明遮罩
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            if self.game_state == "win":
                self._draw_result_win(screen)
            else:
                self._draw_result_lose(screen)

    def _draw_button(self, screen, rect, text):
        """画一个与菜单风格一致的按钮"""
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        bg_color = (88, 58, 120) if hovered else (60, 70, 110)
        border_color = (245, 230, 160) if hovered else (230, 230, 230)
        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, border_color, rect, 2)
        text_surf = self.font_small.render(text, True, (255, 255, 255))
        screen.blit(text_surf, (
            rect.centerx - text_surf.get_width() // 2,
            rect.centery - text_surf.get_height() // 2
        ))

    def _draw_result_win(self, screen):
        """胜利界面——对称简洁"""
        panel_w, panel_h = 360, 220
        panel_x = (800 - panel_w) // 2
        panel_y = (600 - panel_h) // 2
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (34, 38, 52), panel)
        pygame.draw.rect(screen, (230, 230, 230), panel, 2)

        # 标题
        title = self.font_large.render("挑战成功!", True, (255, 255, 255))
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 30))

        # 按钮
        btn_w, btn_h = 200, 44
        btn_y = panel.y + 150
        btn = pygame.Rect(panel.centerx - btn_w // 2, btn_y, btn_w, btn_h)
        self.result_buttons = [("win_exit", btn)]
        self._draw_button(screen, btn, "返回汉口路校门")

        # 键盘提示（紧贴按钮上方4像素）
        tip = self.font_small.render("按 Q 返回", True, (180, 180, 180))
        screen.blit(tip, (panel.centerx - tip.get_width() // 2, btn.y - 40))

    def _draw_result_lose(self, screen):
        """失败界面——对称简洁"""
        panel_w, panel_h = 400, 260
        panel_x = (800 - panel_w) // 2
        panel_y = (600 - panel_h) // 2
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (34, 38, 52), panel)
        pygame.draw.rect(screen, (230, 230, 230), panel, 2)

        # 标题
        title = self.font_large.render("挑战失败!", True, (255, 255, 255))
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 35))

        # 提示语
        tip = self.font_normal.render(self.result_message, True, (200, 200, 200))
        screen.blit(tip, (panel.centerx - tip.get_width() // 2, panel.y + 100))

        # 按钮
        btn_w, btn_h = 140, 44
        gap = 30
        btn_y = panel.y + 180
        left_btn = pygame.Rect(panel.centerx - btn_w - gap // 2, btn_y, btn_w, btn_h)
        right_btn = pygame.Rect(panel.centerx + gap // 2, btn_y, btn_w, btn_h)
        self.result_buttons = [("retry", left_btn), ("lose_exit", right_btn)]
        self._draw_button(screen, left_btn, "重新挑战")
        self._draw_button(screen, right_btn, "退出")

        # 键盘提示
        key_tip = self.font_small.render("按 R 重新挑战 / 按 Q 退出", True, (180, 180, 180))
        screen.blit(key_tip, (panel.centerx - key_tip.get_width() // 2, btn_y - 40))