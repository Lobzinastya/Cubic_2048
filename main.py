from ursina import *
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from logic import Game


# Цвета текста
color_text = {
    2: (117, 100, 82, 255),
    4: (154, 134, 117, 255),
}

# Цвета кубиков
color_back = {
    2: color.rgb(238 / 255, 228 / 255, 218 / 255),
    4: color.rgb(235 / 255, 216 / 255, 182 / 255),
    8: color.rgb(241 / 255, 174 / 255, 114 / 255),
    16: color.rgb(245 / 255, 143 / 255, 90 / 255),
    32: color.rgb(245 / 255, 118 / 255, 88 / 255),
    64: color.rgb(245 / 255, 91 / 255, 55 / 255),
    128: color.rgb(242 / 255, 207 / 255, 85 / 255),
    256: color.rgb(242 / 255, 210 / 255, 98 / 255),
    512: color.rgb(246 / 255, 209 / 255, 69 / 255),
    1024: color.rgb(249 / 255, 196 / 255, 44 / 255),
    2048: color.rgb(255 / 255, 184 / 255, 0 / 255),
}


def generate_texture(n):
    """Создание текстуры с цифрой"""
    texture_path = f'textures/{n}.png'
    if not os.path.exists(texture_path):
        img_size = 256
        img = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font_size = 160

        while True:
            try:
                font = ImageFont.truetype('arial.ttf', font_size)
            except:
                font = ImageFont.load_default()
                break

            text = str(n)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

            if text_width <= img_size * 0.9 and text_height <= img_size * 0.9:
                break
            else:
                font_size -= 2

        x, y = (img_size - text_width) // 2, (img_size - text_height) // 2
        draw.text((x, y), text, font=font, fill=color_text.get(n, (255, 255, 255, 255)))
        img.save(texture_path)

    return texture_path


class NumberCube(Entity):
    """Кубик с числом"""
    def __init__(self, number, position=(0, 0, 0), scale=1, **kwargs):
        super().__init__(**kwargs)
        texture_path = generate_texture(number)

        self.cube = Entity(
            parent=self,
            model='cube',
            color=color_back.get(number, color.black),
            scale=scale,
            texture='white_cube',
            alpha=0.666
        )
        self.number = Entity(
            parent=self,
            model='quad',
            texture=load_texture(texture_path),
            scale=scale * 1,
            position=(0, 0, 0),
            always_face_camera=True,
            alpha=1
        )
        self.position = position


def create_3d_grid(values, rows=3, cols=3, depth=3, spacing=1.2, scale=1):
    """Создание 3D-сетки кубов"""
    cubes = []
    for x in range(rows):
        for y in range(cols):
            for z in range(depth):
                num = values[z, depth - 1 - y, x]
                pos = (x * spacing, y * spacing, z * spacing)

                if num != 0:
                    cube = NumberCube(num, position=pos, scale=scale)
                    cubes.append(cube)
    return cubes


# ✅ **Настройка приложения**
app = Ursina()
window.color = color.rgb(189 / 255, 172 / 255, 151 / 255)

# ✅ **Инициализация игры**
d = 3
my_game = Game(d)
my_game.pretty()
cubes = create_3d_grid(values=my_game.values, rows=d, cols=d, depth=d, spacing=1.1)

# ✅ **Настройка камеры**
EditorCamera()
camera.position = (6, 6, -10)
camera.look_at((1.5, 1.5, 1.5))  # Смотрим в центр сетки

game_over_text = None  # Текст для окончания игры


def update_cubes():

    global cubes
    for cube in cubes:
        destroy(cube)
    cubes.clear()
    cubes = create_3d_grid(values=my_game.values, rows=d, cols=d, depth=d, spacing=1.2)


def input(key):
    """Обрабатываем ввод WASDQE"""
    global game_over_text

    if key in ['w', 'a', 's', 'd', 'q', 'e']:  # Только нужные клавиши
        my_game.update(key)
        my_game.is_finished()
        my_game.pretty()
        update_cubes()

        if my_game.values.max() == 2048:
            game_over_text = Text(
                text=f"YOU GOT 2048\nScore: {my_game.score}",
                position=(-0.25, 0.1),
                scale=2,
                color=color.green
            )

        if my_game.end:
            game_over_text = Text(
                text=f"GAME OVER\nScore: {my_game.score}",
                position=(-0.25, 0.1),
                scale=2,
                color=color.red
            )


app.run()
