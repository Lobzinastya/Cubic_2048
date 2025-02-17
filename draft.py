from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from logic import Game
from panda3d.core import CardMaker, TransparencyAttrib
from panda3d.core import TextNode

from panda3d.core import AmbientLight, DirectionalLight, PointLight, Spotlight
import math


class ThreeD2048(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Инициализация игры
        self.d = 3
        self.game = Game(self.d)
        self.game.pretty()
        self.spacing = 1.1
        self.cube_scale = 0.5
        self.cubes = []

        # Настройка сцены
        self.disableMouse()
        self.setup_camera()

        self.setup_lighting()

        self.setup_gui()
        self.generate_all_textures()
        self.setup_controls()

        # Первоначальное отображение
        self.update_visuals()


    # def setup_camera(self):
    #     self.camera.setPos(5, -15, 3)
    #     self.camera.lookAt(0,0,0)

    def setup_camera(self):
        """✅ Настраивает камеру с зумом колесиком и вращением ЛКМ"""

        self.camera.setPos(self.d/2 * self.cube_scale -1, self.d/2 * self.cube_scale, 1 +self.d/2 * self.cube_scale )

        self.camera_radius = 12  # ✅ Начальная дистанция камеры
        self.camera_angle_x = 170  # ✅ Горизонтальный угол (вращение)
        self.camera_angle_y = 10  # ✅ Вертикальный угол (наклон)

        self.min_zoom = 10  # ✅ Минимальное приближение
        self.max_zoom = 50  # ✅ Максимальное удаление

        self.mouse_active = False  # ✅ По умолчанию камера не двигается

        # ✅ Начальная позиция (без проблем со спиралью)

        self.update_camera_position()

        # ✅ Управление колесиком (ЗУМ)
        self.accept("wheel_up", self.zoom_camera, [-2])  # Приблизить
        self.accept("wheel_down", self.zoom_camera, [2])  # Отдалить

        # ✅ Управление ЛКМ (вращение)
        self.accept("mouse1", self.start_mouse_control)  # ЛКМ зажата → начинаем вращение
        self.accept("mouse1-up", self.stop_mouse_control)  # ЛКМ отпущена → останавливаем

        # ✅ Обновление камеры каждый кадр
        taskMgr.add(self.update_camera, "update_camera")

    def update_camera_position(self):
        """✅ Обновляет позицию камеры (без спирали)"""
        x = self.camera_radius * math.sin(math.radians(self.camera_angle_x))
        y = self.camera_radius * math.cos(math.radians(self.camera_angle_x))
        z = math.sin(math.radians(self.camera_angle_y)) * self.camera_radius + 3.8161

        self.camera.setPos(x, y, z)  # ✅ Камера двигается без спирали
        self.camera.lookAt(0, 0, 0,)  # ✅ Камера всегда смотрит на центр

    def zoom_camera(self, delta):
        """✅ Приближение и отдаление камеры"""
        self.camera_radius = max(self.min_zoom, min(self.max_zoom, self.camera_radius + delta))
        self.update_camera_position()

    def start_mouse_control(self):
        """✅ Начинаем вращение камеры при зажатии ЛКМ"""
        self.mouse_active = True
        md = base.win.getPointer(0)
        self.last_mouse_x = md.getX()
        self.last_mouse_y = md.getY()

    def stop_mouse_control(self):
        """✅ Останавливаем вращение камеры при отпускании ЛКМ"""
        self.mouse_active = False

    def update_camera(self, task):
        """✅ Обновляет камеру при движении мыши, если ЛКМ зажата"""
        if self.mouse_active and base.mouseWatcherNode.hasMouse():
            md = base.win.getPointer(0)
            mouse_x = md.getX()
            mouse_y = md.getY()

            dx = (mouse_x - self.last_mouse_x) * 0.3  # ✅ Вращение влево/вправо
            dy = (mouse_y - self.last_mouse_y) * 0.3  # ✅ Вращение вверх/вниз

            self.last_mouse_x = mouse_x
            self.last_mouse_y = mouse_y

            self.camera_angle_x -= dx  # ✅ Вращаем камеру вокруг центра
            self.camera_angle_y = max(-50, min(50, self.camera_angle_y - dy))  # ✅ Ограничиваем наклон

            self.update_camera_position()

        return task.cont  # ✅ Продолжаем обновлять камеру

    def setup_lighting(self):
        """Настраивает красивое освещение"""


        ambient_light = AmbientLight("ambient")
        ambient_light.setColor((1.2, 1.2, 1.2, 1))  # Светлее
        self.render.setLight(self.render.attachNewNode(ambient_light))


        directional_light = DirectionalLight("directional")
        directional_light.setColor((1.2, 1.2, 1.2, 1))
        dlnp = self.render.attachNewNode(directional_light)
        dlnp.setHpr(45, -60, 0)
        self.render.setLight(dlnp)


        point_light = PointLight("point")
        point_light.setColor((1.0, 1.0, 1.0, 1))
        plnp = self.render.attachNewNode(point_light)
        plnp.setPos(3, 3, 5)
        self.render.setLight(plnp)


        spotlight = Spotlight("spot")
        spotlight.setColor((1.5, 1.3, 1.1, 1))
        slnp = self.render.attachNewNode(spotlight)
        slnp.setPos(2, -4, 6)
        slnp.lookAt(0, 0, 0)
        self.render.setLight(slnp)

        base.setBackgroundColor(246/255,242/255,233/255)

    def setup_gui(self):
        self.score_text = OnscreenText(
            text="Score: 0",
            pos=(-0.9, 0.85),
            scale=0.12,
            fg=(0, 0, 0, 1),
            align=TextNode.ALeft
        )

        self.description_text = OnscreenText(
            text="Control:\nW/S - up/down\nA/D - left/right\nQ/E - front/rear",
            pos=(-0.9, -0.45),
            scale=0.05,
            fg=(0, 0, 0, 1),
            align=TextNode.ALeft
        )

    def generate_all_textures(self):
        os.makedirs("textures", exist_ok=True)
        for n in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
            self.generate_number_texture(n)

    def generate_number_texture(self, n):
        path = f"textures/{n}.png"
        if os.path.exists(path): return

        img = Image.new('RGBA', (256, 256))
        draw = ImageDraw.Draw(img)
        font_size = 160

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text = str(n)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        while text_w > 230 or text_h > 230:
            font_size -= 5
            font = ImageFont.truetype("arial.ttf", font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

        x = (256 - text_w) // 2
        y = (256 - text_h) // 2
        draw.text((x, y), text, font=font, fill=(119, 110, 101, 255))
        img.save(path)

    def create_cube(self, number, pos):
        # Загрузка GLB модели
        cube = self.loader.loadModel("models/cube.glb")
        cube.setScale(self.cube_scale)
        cube.setPos(pos)
        cube.clearTexture()
        # Настройка материала
        color = self.get_color(number)
        cube.setColorScale(color)
        cube.setTransparency(TransparencyAttrib.MAlpha)


        # ✅ Добавляем текст прямо на куб
        self.create_text_on_cube(cube, number)

        return cube

    def create_text_on_cube(self, cube, number):
        """Создаёт текст и прикрепляет к кубу"""
        text_node = TextNode("number_text")
        text_node.setText(str(number))  # Устанавливаем цифру
        text_node.setTextColor(1, 1, 1, 1)  # Белый цвет текста
        text_node.setAlign(TextNode.ACenter)  # Центрирование

        text_node_path = cube.attachNewNode(text_node)  # Прикрепляем текст к кубу
        text_node_path.setScale(1)  # Размер текста
        text_node_path.setPos(0, 1, 0)  # ✅ Вынести текст ВПЕРЁД

        return text_node_path

    def get_color(self, number):
        colors = {
            2: (238 / 255, 228 / 255, 218 / 255, 0.8),
            4: (235 / 255, 216 / 255, 182 / 255, 0.8),
            8: (241 / 255, 174 / 255, 114 / 255, 0.8),
            16: (245 / 255, 143 / 255, 90 / 255, 0.8),
            32: (245 / 255, 118 / 255, 88 / 255, 0.8),
            64: (245 / 255, 91 / 255, 55 / 255, 0.8),
            128: (242 / 255, 207 / 255, 85 / 255, 0.8),
            256: (242 / 255, 210 / 255, 98 / 255, 0.8),
            512: (246 / 255, 209 / 255, 69 / 255, 0.8),
            1024: (249 / 255, 196 / 255, 44 / 255, 0.8),
            2048: (255 / 255, 184 / 255, 0 / 255, 0.8)
        }


        return colors.get(number, (0,0,0, 1))

    # def create_text_plane(self, texture):
    #     plane = self.loader.loadModel("models/plane.glb")
    #     plane.setBillboardPointEye()
    #     plane.setTransparency(TransparencyAttrib.MAlpha)
    #     plane.setTexture(texture, 1)
    #     plane.setScale(0.8)
    #     return plane




    def update_visuals(self):
        # Удаление старых кубов
        for cube in self.cubes:
            cube.removeNode()
        self.cubes = []

        # Создание новых кубов
        for x in range(self.d):
            for y in range(self.d):
                for z in range(self.d):
                    num = self.game.values[y, self.d-1-z, x]
                    if num != 0:
                        pos = (
                            x * self.spacing ,
                            y * self.spacing ,
                            z * self.spacing
                        )
                        cube = self.create_cube(num, pos)
                        cube.reparentTo(self.render)
                        self.cubes.append(cube)

        self.score_text.setText(f"Score: {self.game.score}")

    def setup_controls(self):
        controls = {
            'w': 'w',
            's': 's',
            'a': 'a',
            'd': 'd',
            'q': 'q',
            'e': 'e'
        }

        for key, action in controls.items():
            self.accept(key, self.handle_input, [action])  # ✅ Теперь вызываем handle_input()

    def handle_input(self, direction):
        self.game.update(direction)
        self.game.is_finished()
        self.game.pretty()
        self.update_visuals()

        if self.game.values.max() == 2048:
            self.show_game_over("YOU WIN!", (0, 1, 0, 1))
        elif self.game.end:
            self.show_game_over("GAME OVER!", (1, 0, 0, 1))

    def show_game_over(self, text, color):
        OnscreenText(
            text=text + f"\nScore: {self.game.score}",
            pos=(-0.25, 0.1),
            scale=0.1,
            fg=color,
            align=TextNode.ACenter
        )
        self.game_over = True


if __name__ == "__main__":
    game = ThreeD2048()
    game.run()


