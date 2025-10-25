# main.py
# (版本 9 - 最终版：UI 位置, 重生, PVP秒杀, Boss秒杀)

import pygame
import sys
import random
import settings as s
import map as m
from sprites import HeroTank, Wall, Bush, Bullet, EnemyTank, load_sound, draw_text

class Game:
    """游戏主类"""
    def __init__(self):
        pygame.init()
        pygame.mixer.init() 
        self.screen = pygame.display.set_mode(s.SCREEN_SIZE)
        pygame.display.set_caption(s.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_name = pygame.font.match_font('consolas')
        if not self.font_name:
            self.font_name = pygame.font.get_default_font()
        self.load_data() 

    def load_data(self):
        self.sound_fire = load_sound(s.SND_FIRE)
        self.sound_hit_iron = load_sound(s.SND_HIT_IRON)
        self.sound_bang_enemy = load_sound(s.SND_BANG_ENEMY)
        self.sound_bang_player = load_sound(s.SND_BANG_PLAYER)

    def new_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.bushes = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.boss_group = pygame.sprite.Group()
        self.enemy_spawn_tiles = []
        
        # (新) 游戏状态
        self.game_over = False
        self.game_victory = False
        self.winner = None # 用于秒杀
        
        for row_index, row in enumerate(m.MAP_DATA):
            for col_index, tile in enumerate(row):
                if tile == s.MAP_TILE_RED_WALL or \
                   tile == s.MAP_TILE_IRON_WALL:
                    wall = Wall(col_index, row_index, tile)
                    self.all_sprites.add(wall); self.walls.add(wall)
                elif tile == s.MAP_TILE_BOSS:
                    wall = Wall(col_index, row_index, tile)
                    self.all_sprites.add(wall); self.walls.add(wall)
                    self.boss_group.add(wall)
                elif tile == s.MAP_TILE_BUSH:
                    bush = Bush(col_index, row_index)
                    self.all_sprites.add(bush); self.bushes.add(bush)
                elif tile == s.MAP_TILE_EMPTY:
                    if row_index > 2 and row_index < 22:
                        self.enemy_spawn_tiles.append((col_index, row_index))

        self.player1 = HeroTank(m.PLAYER1_SPAWN[0], m.PLAYER1_SPAWN[1], 1, self)
        self.player2 = HeroTank(m.PLAYER2_SPAWN[0], m.PLAYER2_SPAWN[1], 2, self)
        self.all_sprites.add(self.player1); self.all_sprites.add(self.player2)
        self.players.add(self.player1); self.players.add(self.player2)
        
        self.enemies_spawned = 0
        self.total_enemies_to_spawn = s.ENEMY_TOTAL_COUNT
        for _ in range(s.ENEMY_START_COUNT):
            self.spawn_enemy()

    def spawn_enemy(self):
        if self.enemies_spawned >= self.total_enemies_to_spawn: return
        if len(self.enemies) >= s.ENEMY_MAX_ON_SCREEN: return
        if not self.enemy_spawn_tiles: return
            
        spawn_pos = random.choice(self.enemy_spawn_tiles)
        enemy = EnemyTank(spawn_pos[0], spawn_pos[1], self)
        self.all_sprites.add(enemy); self.enemies.add(enemy)
        self.enemies_spawned += 1

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(s.FPS)
            self.events()
            self.update()
            self.draw()
            
        if not self.running:
            return
        
        self.show_game_over_screen()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing: self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == s.P1_SHOOT: self.player1.shoot()
                if event.key == s.P2_SHOOT: self.player2.shoot()
        
        self.player1.get_input()
        self.player2.get_input()

    def update(self):
        self.players.update(self.walls)
        self.enemies.update(self.walls)
        self.bullets.update()

        # 1. 碰撞: 子弹 vs 墙壁
        hits = pygame.sprite.groupcollide(self.bullets, self.walls, False, False)
        for bullet, hit_walls in hits.items():
            wall = hit_walls[0] 
            if wall.wall_type == s.MAP_TILE_IRON_WALL:
                bullet.kill(); self.sound_hit_iron.play()
            elif wall.wall_type == s.MAP_TILE_RED_WALL:
                bullet.kill(); wall.health -= 1
                if wall.health <= 0: wall.kill()
                
            # --- (新) Boss 秒杀逻辑 ---
            elif wall.wall_type == s.MAP_TILE_BOSS:
                if bullet.owner == 'Enemy':
                    bullet.kill() # 敌人子弹无效
                elif bullet.owner == 'P1':
                    # P1 射中 Boss, P1 输
                    print("Player 1 shot the boss! Player 2 wins!")
                    self.game_over = True; self.playing = False
                    self.winner = 'P2' # P2 获胜
                    bullet.kill(); wall.kill(); self.boss_group.empty()
                    return
                elif bullet.owner == 'P2':
                    # P2 射中 Boss, P2 输
                    print("Player 2 shot the boss! Player 1 wins!")
                    self.game_over = True; self.playing = False
                    self.winner = 'P1' # P1 获胜
                    bullet.kill(); wall.kill(); self.boss_group.empty()
                    return
            # --------------------------

        # 2. 碰撞: 子弹 vs 玩家 (包含重生和秒杀)
        hits = pygame.sprite.groupcollide(self.players, self.bullets, False, False)
        for player, bullets_hit in hits.items():
            for bullet in bullets_hit:
                if bullet.owner != f"P{player.player_num}":
                    # 调用 HeroTank.take_damage, 它会处理重生或游戏结束
                    player.take_damage(1, bullet.owner)
                    bullet.kill()

        # 3. 碰撞: 子弹 vs 敌人
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, False)
        for enemy, bullets_hit in hits.items():
            for bullet in bullets_hit:
                if bullet.owner != 'Enemy':
                    killer = enemy.take_damage(1, bullet.owner)
                    bullet.kill()
                    if killer:
                        self.sound_bang_enemy.play()
                        if killer == 'P1':
                            self.player1.score += 1
                            self.player1.heal(s.PLAYER_HEAL_ON_KILL)
                        elif killer == 'P2':
                            self.player2.score += 1
                            self.player2.heal(s.PLAYER_HEAL_ON_KILL)
                        self.spawn_enemy()

        # 4. 检查游戏结束条件 (只剩 "胜利" 条件)
        if self.enemies_spawned == self.total_enemies_to_spawn and not self.enemies:
            self.game_victory = True # 游戏胜利
            self.playing = False

    def draw(self):
        self.screen.fill(s.BLACK)
        
        for sprite in self.all_sprites:
            if sprite not in self.bushes:
                self.screen.blit(sprite.image, sprite.rect)
        
        if self.player1.alive():
            self.player1.draw_ui(self.screen)
        if self.player2.alive():
            self.player2.draw_ui(self.screen)
            
        for bush in self.bushes:
            self.screen.blit(bush.image, bush.rect)
            
        # --- (新) 绘制 UI 文本 (Y 坐标已修改) ---
        
        # P1 分数 (Y=35)
        draw_text(self.screen, f"P1 Score: {self.player1.score}", 24, 
                  100, 35, s.WHITE, self.font_name)
        
        # P2 分数 (Y=35)
        draw_text(self.screen, f"P2 Score: {self.player2.score}", 24, 
                  s.SCREEN_WIDTH / 2, 35, s.WHITE, self.font_name)
                  
        # 敌人剩余 (Y=35)
        enemies_left = self.total_enemies_to_spawn - self.enemies_spawned + len(self.enemies)
        draw_text(self.screen, f"Enemies: {enemies_left}", 24, 
                  s.SCREEN_WIDTH - 100, 35, s.WHITE, self.font_name)
            
        pygame.display.flip()

    def show_game_over_screen(self):
        """(新) 游戏结束/胜利画面 (已重写)"""
        self.screen.fill(s.BLACK)
        
        title_text = ""
        title_color = s.WHITE
        winner_text = "" # (用于 PVE 胜利)
        
        if self.game_victory:
            # 1. PVE 胜利 (敌人清空)
            title_text = "VICTORY!"
            title_color = s.GREEN
            # 按分数决胜负
            p1_score = self.player1.score
            p2_score = self.player2.score
            if p1_score > p2_score:
                winner_text = "Player 1 Wins!"
            elif p2_score > p1_score:
                winner_text = "Player 2 Wins!"
            else:
                winner_text = "It's a Tie!"
                
        elif self.game_over:
            # 2. PVP/Boss 秒杀
            title_text = "GAME OVER"
            title_color = s.RED
            # 根据 self.winner 显示获胜者
            if self.winner == 'P1':
                winner_text = "Player 1 Wins!"
            elif self.winner == 'P2':
                winner_text = "Player 2 Wins!"
        
        # 绘制标题
        draw_text(self.screen, title_text, 64, 
                  s.SCREEN_WIDTH / 2, s.SCREEN_HEIGHT / 4, title_color, self.font_name)
                  
        # 绘制最终得分
        draw_text(self.screen, f"Player 1 Score: {self.player1.score}", 32, 
                  s.SCREEN_WIDTH / 2, s.SCREEN_HEIGHT / 2, s.WHITE, self.font_name)
        draw_text(self.screen, f"Player 2 Score: {self.player2.score}", 32, 
                  s.SCREEN_WIDTH / 2, s.SCREEN_HEIGHT / 2 + 50, s.WHITE, self.font_name)
        
        # 绘制获胜者
        if winner_text:
            draw_text(self.screen, winner_text, 40, 
                      s.SCREEN_WIDTH / 2, s.SCREEN_HEIGHT / 2 + 120, s.YELLOW, self.font_name)

        draw_text(self.screen, "Press any key to play again", 20, 
                  s.SCREEN_WIDTH / 2, s.SCREEN_HEIGHT * 3 / 4, s.WHITE, self.font_name)
                  
        pygame.display.flip()
        
        # 等待玩家按键
        waiting = True
        while waiting:
            self.clock.tick(s.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

# --- Gmae 启动 ---
g = Game()
while g.running:
    g.new_game()
    g.run()
    
pygame.quit()
sys.exit()