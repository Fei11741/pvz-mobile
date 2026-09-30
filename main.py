<< << << < SEARCH
== == == =
# -*- coding: utf-8 -*-
"""
植物大战僵尸 - Kivy 移动端入口
负责窗口、触摸事件、Canvas 绘制。
"""

import math

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel

import game as G

# 颜色定义（0-1 浮点）
C_BG = (0.13, 0.55, 0.13)
C_GRASS_A = (0.24, 0.70, 0.44)
C_GRASS_B = (0.18, 0.55, 0.34)
C_LINE = (0.08, 0.35, 0.16)
C_TOPBAR = (0.55, 0.27, 0.07)
C_SUN = (1.0, 0.84, 0.0)
C_SUNFLOWER = (1.0, 0.78, 0.0)
C_SUNFLOWER_C = (0.55, 0.27, 0.07)
C_PEASHOOTER = (0.0, 0.78, 0.0)
C_PEASHOOTER_H = (0.0, 0.59, 0.0)
C_BULLET = (0.20, 1.0, 0.20)
C_ZOMBIE = (0.47, 0.47, 0.51)
C_ZOMBIE_HEAD = (0.71, 0.78, 0.63)
C_HP_BG = (0.78, 0.0, 0.0)
C_HP_FG = (0.0, 1.0, 0.0)
C_SELECT = (1.0, 1.0, 0.0)
C_TEXT = (1.0, 1.0, 1.0)
C_BLACK = (0.0, 0.0, 0.0)
C_RED = (1.0, 0.0, 0.0)


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = G.Game()
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self._labels = {}
        Clock.schedule_interval(self.tick, 1.0 / 60.0)

    def on_size(self, *args):
        self._recalc_transform()

    def _recalc_transform(self):
        sx = self.width / G.WINDOW_WIDTH
        sy = self.height / G.WINDOW_HEIGHT
        self.scale = min(sx, sy)
        self.offset_x = (self.width - G.WINDOW_WIDTH * self.scale) / 2.0
        self.offset_y = (self.height - G.WINDOW_HEIGHT * self.scale) / 2.0

    def to_screen(self, x, y):
        """逻辑坐标 -> 屏幕坐标（Kivy 原点在左下）"""
        sx = self.offset_x + x * self.scale
        sy = self.offset_y + (G.WINDOW_HEIGHT - y) * self.scale
        return sx, sy

    def to_logic(self, sx, sy):
        """屏幕坐标 -> 逻辑坐标"""
        x = (sx - self.offset_x) / self.scale
        y = G.WINDOW_HEIGHT - (sy - self.offset_y) / self.scale
        return x, y

    def _label(self, text, size=20, color=C_TEXT):
        key = (text, size, color)
        if key not in self._labels:
            lbl = CoreLabel(text=text, font_size=size, color=color)
            lbl.refresh()
            self._labels[key] = lbl
        return self._labels[key]

    def _draw_text(self, text, lx, ly, size=20, color=C_TEXT, center=False):
        lbl = self._label(text, size, color)
        tex = lbl.texture
        sx, sy = self.to_screen(lx, ly)
        w = tex.width * self.scale
        h = tex.height * self.scale
        if center:
            sx -= w / 2.0
            sy -= h / 2.0
        Rectangle(texture=tex, pos=(sx, sy), size=(w, h))

    def tick(self, dt):
        self.game.update(dt)
        self.redraw()

    def on_touch_down(self, touch):
        lx, ly = self.to_logic(touch.x, touch.y)
        if self.game.game_over:
            self.game.reset()
        else:
            self.game.handle_click((lx, ly))
        return True

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            # 背景
            Color(*C_BG)
            Rectangle(pos=self.pos, size=self.size)

            # 草坪
            for row in range(G.GRID_ROWS):
                for col in range(G.GRID_COLS):
                    lx = G.GRID_LEFT + col * G.CELL_WIDTH
                    ly = G.GRID_TOP + row * G.CELL_HEIGHT
                    sx, sy = self.to_screen(lx, ly + G.CELL_HEIGHT)
                    w = G.CELL_WIDTH * self.scale
                    h = G.CELL_HEIGHT * self.scale
                    Color(*(C_GRASS_A if (row + col) % 2 == 0 else C_GRASS_B))
                    Rectangle(pos=(sx, sy), size=(w, h))
                    Color(*C_LINE)
                    Line(rectangle=(sx, sy, w, h), width=1)

            # 顶部栏
            sx, sy = self.to_screen(0, G.TOP_BAR_HEIGHT)
            Color(*C_TOPBAR)
            Rectangle(pos=(sx, sy),
                      size=(G.WINDOW_WIDTH * self.scale,
                            G.TOP_BAR_HEIGHT * self.scale))

            # 卡片
            self._draw_card(20, 10, 120, 60, C_SUNFLOWER, C_SUNFLOWER_C,
                            f"向日葵 {G.SUNFLOWER_COST}",
                            self.game.selected == "sunflower")
            self._draw_card(160, 10, 140, 60, C_PEASHOOTER, C_PEASHOOTER_H,
                            f"豌豆射手 {G.PEASHOOTER_COST}",
                            self.game.selected == "peashooter")

            # 阳光数量
            self._draw_text(f"阳光: {self.game.sun_count}",
                            G.WINDOW_WIDTH - 150, 30, 20, C_TEXT)

            # 植物
            for p in self.game.plants:
                self._draw_plant(p)
            # 子弹
            for b in self.game.bullets:
                self._draw_circle(b.x, b.y, b.radius, C_BULLET)
            # 僵尸
            for z in self.game.zombies:
                self._draw_zombie(z)
            # 阳光
            for s in self.game.suns:
                self._draw_circle(s.x, s.y, s.radius, C_SUN)

            # 游戏结束
            if self.game.game_over:
                self._draw_text("游戏结束！僵尸吃掉了你的脑子",
                                G.WINDOW_WIDTH / 2, G.WINDOW_HEIGHT / 2,
                                40, C_RED, center=True)

    def _draw_card(self, lx, ly, w, h, color, icon_color, text, selected):
        sx, sy = self.to_screen(lx, ly + h)
        sw = w * self.scale
        sh = h * self.scale
        Color(*color)
        Rectangle(pos=(sx, sy), size=(sw, sh))
        # 图标
        cx, cy = self.to_screen(lx + 30, ly + h / 2)
        Color(*icon_color)
        Ellipse(pos=(cx - 15 * self.scale, cy - 15 * self.scale),
                size=(30 * self.scale, 30 * self.scale))
        # 文字
        self._draw_text(text, lx + 50, ly + 20, 20, C_BLACK)
        # 选中边框
        if selected:
            Color(*C_SELECT)
            Line(rectangle=(sx, sy, sw, sh), width=3)

    def _draw_circle(self, lx, ly, r, color):
        sx, sy = self.to_screen(lx, ly)
        Color(*color)
        Ellipse(pos=(sx - r * self.scale, sy - r * self.scale),
                size=(2 * r * self.scale, 2 * r * self.scale))

    def _draw_plant(self, p):
        if isinstance(p, G.Sunflower):
            for i in range(8):
                angle = i * math.pi / 4
                px = p.x + 28 * math.cos(angle)
                py = p.y + 28 * math.sin(angle)
                self._draw_circle(px, py, 12, C_SUNFLOWER)
            self._draw_circle(p.x, p.y, 16, C_SUNFLOWER_C)
        elif isinstance(p, G.Peashooter):
            sx, sy = self.to_screen(p.x - 5, p.y + 30)
            Color(*C_PEASHOOTER)
            Rectangle(pos=(sx, sy),
                      size=(10 * self.scale, 30 * self.scale))
            self._draw_circle(p.x, p.y, 22, C_PEASHOOTER_H)
            self._draw_circle(p.x + 20, p.y, 8, C_PEASHOOTER)

    def _draw_zombie(self, z):
        sx, sy = self.to_screen(z.x - 18, z.y + 40)
        Color(*C_ZOMBIE)
        Rectangle(pos=(sx, sy),
                  size=(36 * self.scale, 50 * self.scale))
        self._draw_circle(z.x, z.y - 25, 18, C_ZOMBIE_HEAD)
        self._draw_circle(z.x - 6, z.y - 28, 3, C_BLACK)
        self._draw_circle(z.x + 6, z.y - 28, 3, C_BLACK)
        # 血条
        bar_w = 40
        bx, by = self.to_screen(z.x - bar_w / 2, z.y - 55 + 6)
        Color(*C_HP_BG)
        Rectangle(pos=(bx, by),
                  size=(bar_w * self.scale, 6 * self.scale))
        ratio = max(0.0, z.hp / z.max_hp)
        Color(*C_HP_FG)
        Rectangle(pos=(bx, by),
                  size=(bar_w * ratio * self.scale, 6 * self.scale))


class PVZApp(App):
    def build(self):
        Window.clearcolor = C_BG
        return GameWidget()


if __name__ == "__main__":
    PVZApp().run()
>> >> >> > REPLACE
