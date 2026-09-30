# -*- coding: utf-8 -*-
"""
植物大战僵尸 - 游戏逻辑层（无渲染依赖）
坐标系统使用逻辑坐标，渲染层负责缩放到实际屏幕。
"""

import random

# ---------------- 逻辑坐标配置 ----------------
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
TOP_BAR_HEIGHT = 80

GRID_COLS = 9
GRID_ROWS = 5
CELL_WIDTH = 90
CELL_HEIGHT = 100
GRID_LEFT = 30
GRID_TOP = TOP_BAR_HEIGHT + 10

# ---------------- 游戏参数 ----------------
SUNFLOWER_COST = 50
PEASHOOTER_COST = 100
START_SUN = 150

SUNFLOWER_INTERVAL = 8.0
PEASHOOTER_INTERVAL = 1.5
BULLET_SPEED = 8
BULLET_DAMAGE = 20

ZOMBIE_SPEED = 0.4
ZOMBIE_HP = 100
ZOMBIE_SPAWN_INTERVAL = 3.0


def cell_center(row, col):
    x = GRID_LEFT + col * CELL_WIDTH + CELL_WIDTH // 2
    y = GRID_TOP + row * CELL_HEIGHT + CELL_HEIGHT // 2
    return x, y


class Sun:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 18
        self.life = 10.0
        self.collected = False

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.collected = True

    def contains(self, pos):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return dx * dx + dy * dy <= self.radius * self.radius


class Plant:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x, self.y = cell_center(row, col)
        self.hp = 100

    def update(self, dt, game):
        pass


class Sunflower(Plant):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.timer = SUNFLOWER_INTERVAL

    def update(self, dt, game):
        self.timer -= dt
        if self.timer <= 0:
            self.timer = SUNFLOWER_INTERVAL
            game.suns.append(Sun(self.x, self.y))


class Peashooter(Plant):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.timer = 0.0

    def update(self, dt, game):
        self.timer -= dt
        if self.timer > 0:
            return
        has_target = any(
            z.row == self.row and z.x > self.x and z.alive
            for z in game.zombies
        )
        if has_target:
            self.timer = PEASHOOTER_INTERVAL
            game.bullets.append(Bullet(self.x + 20, self.y, self.row))


class Bullet:
    def __init__(self, x, y, row):
        self.x = x
        self.y = y
        self.row = row
        self.radius = 7
        self.alive = True

    def update(self, dt, game):
        self.x += BULLET_SPEED
        if self.x > WINDOW_WIDTH:
            self.alive = False
            return
        for z in game.zombies:
            if not z.alive or z.row != self.row:
                continue
            if abs(z.x - self.x) < 25:
                z.hp -= BULLET_DAMAGE
                self.alive = False
                if z.hp <= 0:
                    z.alive = False
                break


class Zombie:
    def __init__(self, row):
        self.row = row
        self.x = WINDOW_WIDTH + 30
        self.y = cell_center(row, 0)[1]
        self.hp = ZOMBIE_HP
        self.max_hp = ZOMBIE_HP
        self.alive = True
        self.attack_timer = 0.0

    def update(self, dt, game):
        blocked = None
        for p in game.plants:
            if p.row == self.row and abs(p.x - self.x) < 40 and p.x < self.x:
                blocked = p
                break

        if blocked is not None:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attack_timer = 0.5
                blocked.hp -= 20
                if blocked.hp <= 0:
                    game.plants.remove(blocked)
        else:
            self.x -= ZOMBIE_SPEED

        if self.x < GRID_LEFT - 20:
            game.game_over = True


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.plants = []
        self.zombies = []
        self.bullets = []
        self.suns = []
        self.sun_count = START_SUN
        self.selected = None
        self.zombie_timer = 2.0
        self.game_over = False

    def handle_click(self, pos):
        x, y = pos

        for s in self.suns:
            if s.contains(pos):
                s.collected = True
                self.sun_count += 25
                return

        if y < TOP_BAR_HEIGHT:
            if 20 <= x <= 140:
                self.selected = "sunflower"
            elif 160 <= x <= 300:
                self.selected = "peashooter"
            return

        if self.selected is None:
            return
        col = int((x - GRID_LEFT) // CELL_WIDTH)
        row = int((y - GRID_TOP) // CELL_HEIGHT)
        if not (0 <= row < GRID_ROWS and 0 <= col < GRID_COLS):
            return
        for p in self.plants:
            if p.row == row and p.col == col:
                return

        if self.selected == "sunflower" and self.sun_count >= SUNFLOWER_COST:
            self.plants.append(Sunflower(row, col))
            self.sun_count -= SUNFLOWER_COST
        elif (self.selected == "peashooter"
              and self.sun_count >= PEASHOOTER_COST):
            self.plants.append(Peashooter(row, col))
            self.sun_count -= PEASHOOTER_COST

    def update(self, dt):
        if self.game_over:
            return

        self.zombie_timer -= dt
        if self.zombie_timer <= 0:
            self.zombie_timer = ZOMBIE_SPAWN_INTERVAL
            self.zombies.append(Zombie(random.randint(0, GRID_ROWS - 1)))

        for p in self.plants:
            p.update(dt, self)
        for b in self.bullets:
            b.update(dt, self)
        for z in self.zombies:
            z.update(dt, self)
        for s in self.suns:
            s.update(dt)

        self.bullets = [b for b in self.bullets if b.alive]
        self.zombies = [z for z in self.zombies if z.alive]
        self.suns = [s for s in self.suns if not s.collected]
