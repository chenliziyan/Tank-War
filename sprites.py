# sprites.py
# (版本 13 - 实现了玩家重生(vs Enemy)和秒杀(vs Player)逻辑)

import pygame
import os
import random
import settings as s

# --- 辅助函数 (无改动) ---

def load_image(filename):
    path = os.path.join(s.IMAGE_DIR, filename)
    try:
        image = pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError) as e: 
        print(f"Error: Unable to load image '{filename}' at path '{path}'.")
        print(f"Details: {e}")
        placeholder = pygame.Surface((s.TILE_SIZE, s.TILE_SIZE))
        placeholder.fill(s.YELLOW) 
        return placeholder
    image = pygame.transform.scale(image, (s.TILE_SIZE, s.TILE_SIZE))
    return image

def load_sound(filename):
    path = os.path.join(s.SOUND_DIR, filename)
    try:
        sound = pygame.mixer.Sound(path)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error: Unable to load sound '{filename}' at path '{path}'.")
        print(f"Details: {e}")
        sound = pygame.mixer.Sound(buffer=b'') 
    return sound

def draw_text(surface, text, size, x, y, color, font_name):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def draw_health_bar(surface, x, y, hp, max_hp):
    if hp < 0: hp = 0
    BAR_LENGTH = s.TILE_SIZE
    BAR_HEIGHT = 7
    fill_pct = (hp / max_hp) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill_pct, BAR_HEIGHT)
    if fill_pct > BAR_LENGTH * 0.6: fill_color = s.GREEN
    elif fill_pct > BAR_LENGTH * 0.3: fill_color = s.YELLOW
    else: fill_color = s.RED
    pygame.draw.rect(surface, s.BLACK, outline_rect)
    pygame.draw.rect(surface, fill_color, fill_rect)
    pygame.draw.rect(surface, s.WHITE, outline_rect, 1)

# ----------------------------------------
# 1. 墙壁 (Wall) 和 树叶 (Bush) 类 (无改动)
# ----------------------------------------
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, wall_type):
        pygame.sprite.Sprite.__init__(self)
        self.wall_type = wall_type
        if self.wall_type == s.MAP_TILE_RED_WALL:
            self.image = load_image(s.IMG_WALL_RED); self.health = 1
        elif self.wall_type == s.MAP_TILE_IRON_WALL:
            self.image = load_image(s.IMG_WALL_IRON); self.health = float('inf')
        elif self.wall_type == s.MAP_TILE_BOSS:
            self.image = load_image(s.IMG_BOSS); self.health = 1
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * s.TILE_SIZE, y * s.TILE_SIZE)

class Bush(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(s.IMG_BUSH)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * s.TILE_SIZE, y * s.TILE_SIZE)

# ----------------------------------------
# 2. 子弹 (Bullet) 类 (无改动)
# ----------------------------------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(s.IMG_BULLET)
        bullet_size = (s.TILE_SIZE // 4, s.TILE_SIZE // 4)
        self.image = pygame.transform.scale(self.image, bullet_size)
        self.rect = self.image.get_rect()
        self.owner = owner
        self.direction = direction
        self.speed = s.BULLET_SPEED
        if self.direction == 'UP':
            self.rect.centerx = x; self.rect.bottom = y
        elif self.direction == 'DOWN':
            self.rect.centerx = x; self.rect.top = y
        elif self.direction == 'LEFT':
            self.rect.right = x; self.rect.centery = y
        elif self.direction == 'RIGHT':
            self.rect.left = x; self.rect.centery = y

    def update(self):
        if self.direction == 'UP': self.rect.y -= self.speed
        elif self.direction == 'DOWN': self.rect.y += self.speed
        elif self.direction == 'LEFT': self.rect.x -= self.speed
        elif self.direction == 'RIGHT': self.rect.x += self.speed
        if not pygame.Rect(0, 0, s.SCREEN_WIDTH, s.SCREEN_HEIGHT).colliderect(self.rect):
            self.kill()

# ----------------------------------------
# 3. 坦克 (Tank) - 基类 (已修改)
# ----------------------------------------
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, initial_image_surface, hp):
        pygame.sprite.Sprite.__init__(self)
        self.image = initial_image_surface
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * s.TILE_SIZE, y * s.TILE_SIZE)
        self.speed = 0
        self.vel = pygame.math.Vector2(0, 0)
        self.hp = hp

    def update(self, walls_group):
        if self.direction == 'UP':
            self.vel.x = 0; self.vel.y = -self.speed
        elif self.direction == 'DOWN':
            self.vel.x = 0; self.vel.y = self.speed
        elif self.direction == 'LEFT':
            self.vel.x = -self.speed; self.vel.y = 0
        elif self.direction == 'RIGHT':
            self.vel.x = self.speed; self.vel.y = 0
        
        self.rect.x += self.vel.x
        self.check_collision(walls_group, 'x')
        self.rect.y += self.vel.y
        self.check_collision(walls_group, 'y')
        
    def check_collision(self, walls_group, axis):
        hits = pygame.sprite.spritecollide(self, walls_group, False)
        if hits:
            if axis == 'x':
                if self.vel.x > 0: self.rect.right = hits[0].rect.left
                if self.vel.x < 0: self.rect.left = hits[0].rect.right
            if axis == 'y':
                if self.vel.y > 0: self.rect.bottom = hits[0].rect.top
                if self.vel.y < 0: self.rect.top = hits[0].rect.bottom
            self.vel.x = 0
            self.vel.y = 0
            
    def take_damage(self, amount, owner):
        """(新) take_damage 现在需要一个 owner"""
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
        return None

# ----------------------------------------
# 4. 玩家坦克 (HeroTank) 类 (已修改)
# ----------------------------------------
class HeroTank(Tank):
    def __init__(self, x, y, player_num, game):
        self.player_num = player_num
        self.player_speed = s.PLAYER_SPEED
        self.game = game 
        self.images = {}
        if self.player_num == 1:
            self.images['UP'] = load_image(s.IMG_P1_UP)
            self.images['DOWN'] = load_image(s.IMG_P1_DOWN)
            self.images['LEFT'] = load_image(s.IMG_P1_LEFT)
            self.images['RIGHT'] = load_image(s.IMG_P1_RIGHT)
        else:
            self.images['UP'] = load_image(s.IMG_P2_UP)
            self.images['DOWN'] = load_image(s.IMG_P2_DOWN)
            self.images['LEFT'] = load_image(s.IMG_P2_LEFT)
            self.images['RIGHT'] = load_image(s.IMG_P2_RIGHT)
        self.last_shot_time = pygame.time.get_ticks()
        self.shoot_cooldown = s.BULLET_COOLDOWN
        self.score = 0
        
        # (新) 记住出生点 (图块坐标)
        self.spawn_x_tile = x
        self.spawn_y_tile = y
        
        super().__init__(x, y, self.images['UP'], s.PLAYER_HP)
        self.direction = 'UP'

    def get_input(self):
        self.speed = 0
        keys = pygame.key.get_pressed()
        if self.player_num == 1:
            if keys[s.P1_UP]:
                self.speed = self.player_speed; self.direction = 'UP'; self.image = self.images['UP']
            elif keys[s.P1_DOWN]:
                self.speed = self.player_speed; self.direction = 'DOWN'; self.image = self.images['DOWN']
            elif keys[s.P1_LEFT]:
                self.speed = self.player_speed; self.direction = 'LEFT'; self.image = self.images['LEFT']
            elif keys[s.P1_RIGHT]:
                self.speed = self.player_speed; self.direction = 'RIGHT'; self.image = self.images['RIGHT']
        elif self.player_num == 2:
            if keys[s.P2_UP]:
                self.speed = self.player_speed; self.direction = 'UP'; self.image = self.images['UP']
            elif keys[s.P2_DOWN]:
                self.speed = self.player_speed; self.direction = 'DOWN'; self.image = self.images['DOWN']
            elif keys[s.P2_LEFT]:
                self.speed = self.player_speed; self.direction = 'LEFT'; self.image = self.images['LEFT']
            elif keys[s.P2_RIGHT]:
                self.speed = self.player_speed; self.direction = 'RIGHT'; self.image = self.images['RIGHT']

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_cooldown:
            self.last_shot_time = now
            self.game.sound_fire.play()
            owner = f"P{self.player_num}"
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, owner)
            self.game.all_sprites.add(bullet)
            self.game.bullets.add(bullet)

    def heal(self, amount):
        self.hp = min(s.PLAYER_HP, self.hp + amount)
        
    def respawn(self):
        """(新) 玩家重生方法"""
        print(f"Player {self.player_num} respawned!")
        self.hp = s.PLAYER_HP
        self.rect.topleft = (self.spawn_x_tile * s.TILE_SIZE, self.spawn_y_tile * s.TILE_SIZE)
        self.direction = 'UP'
        self.image = self.images['UP']
        
    def take_damage(self, amount, owner):
        """(新) 重写 take_damage 以实现新逻辑"""
        if not self.alive(): # 防止 "已死" 坦克再次中弹
            return
            
        self.hp -= amount
        
        if self.hp <= 0:
            # 检查是被谁击杀的
            if owner == 'Enemy':
                # 被敌人击杀：重生
                self.game.sound_bang_player.play()
                self.respawn()
            else:
                # 被其他玩家 (P1 or P2) 击杀：游戏结束
                print(f"Player {self.player_num} was killed by {owner}!")
                self.game.sound_bang_player.play()
                self.game.game_over = True
                self.game.playing = False
                self.game.winner = owner # 'owner' 是击杀者 (e.g., 'P1')
                self.kill() # 玩家死亡

    def draw_ui(self, surface):
        draw_health_bar(surface, self.rect.x, self.rect.y - 10, self.hp, s.PLAYER_HP)

# ----------------------------------------
# 5. 敌人坦克 (EnemyTank) 类 (无改动)
# ----------------------------------------
class EnemyTank(Tank):
    def __init__(self, x, y, game):
        self.game = game
        self.images = {}
        self.type = random.choice(['white', 'green'])
        if self.type == 'white':
            hp = s.ENEMY_HP_WHITE
            self.images['UP'] = load_image(s.IMG_ENEMY_WHITE_UP)
            self.images['DOWN'] = load_image(s.IMG_ENEMY_WHITE_DOWN)
            self.images['LEFT'] = load_image(s.IMG_ENEMY_WHITE_LEFT)
            self.images['RIGHT'] = load_image(s.IMG_ENEMY_WHITE_RIGHT)
        else:
            hp = s.ENEMY_HP_GREEN
            self.images['UP'] = load_image(s.IMG_ENEMY_GREEN_UP)
            self.images['DOWN'] = load_image(s.IMG_ENEMY_GREEN_DOWN)
            self.images['LEFT'] = load_image(s.IMG_ENEMY_GREEN_LEFT)
            self.images['RIGHT'] = load_image(s.IMG_ENEMY_GREEN_RIGHT)
        self.move_timer = pygame.time.get_ticks()
        self.move_cooldown = random.randint(1000, 3000)
        self.shoot_timer = pygame.time.get_ticks()
        self.shoot_cooldown = s.ENEMY_SHOOT_COOLDOWN
        self.direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
        super().__init__(x, y, self.images[self.direction], hp)
        self.speed = s.ENEMY_SPEED 

    def update(self, walls_group):
        self.ai_move()
        self.ai_shoot()
        super().update(walls_group)

    def ai_move(self):
        now = pygame.time.get_ticks()
        if now - self.move_timer > self.move_cooldown:
            self.move_timer = now
            self.move_cooldown = random.randint(1000, 3000)
            self.direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
            self.image = self.images[self.direction]
            self.speed = s.ENEMY_SPEED 

    def ai_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer > self.shoot_cooldown:
            self.shoot_timer = now
            self.shoot()

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, 'Enemy')
        self.game.all_sprites.add(bullet)
        self.game.bullets.add(bullet)

    def take_damage(self, amount, owner):
        self.hp -= amount
        if self.hp <= 0:
            self.kill(); return owner
        if self.type == 'green' and self.hp == 1:
            print("Enemy changed from Green to White!")
            self.type = 'white'
            self.images['UP'] = load_image(s.IMG_ENEMY_WHITE_UP)
            self.images['DOWN'] = load_image(s.IMG_ENEMY_WHITE_DOWN)
            self.images['LEFT'] = load_image(s.IMG_ENEMY_WHITE_LEFT)
            self.images['RIGHT'] = load_image(s.IMG_ENEMY_WHITE_RIGHT)
            self.image = self.images[self.direction]
        return None