import pygame
import sys
import random
import settings as s
import map as m
from sprites import HeroTank, Wall, Bush, Bullet, EnemyTank, load_sound, draw_text


class Game:
    """Main Game Class — controls the entire game loop and state"""

    def __init__(self):
        # Initialize pygame and mixer (for sounds)
        pygame.init()
        pygame.mixer.init()

        # Set up the main window
        self.screen = pygame.display.set_mode(s.SCREEN_SIZE)
        pygame.display.set_caption(s.TITLE)

        # Game clock for controlling FPS
        self.clock = pygame.time.Clock()
        self.running = True

        # Load font (fallback to default if Consolas not found)
        self.font_name = pygame.font.match_font('consolas')
        if not self.font_name:
            self.font_name = pygame.font.get_default_font()

        # Load game resources (sounds, etc.)
        self.load_data()


    # Load sound and other resources
    def load_data(self):
        self.sound_fire = load_sound(s.SND_FIRE)
        self.sound_hit_iron = load_sound(s.SND_HIT_IRON)
        self.sound_bang_enemy = load_sound(s.SND_BANG_ENEMY)
        self.sound_bang_player = load_sound(s.SND_BANG_PLAYER)


    # Start a new game session
    def new_game(self):
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.bushes = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.boss_group = pygame.sprite.Group()
        self.enemy_spawn_tiles = []

        # Game state flags
        self.game_over = False
        self.game_victory = False
        self.winner = None  # Used for instant-death (boss kill) situations

        # Build the map by reading data from m.MAP_DATA
        for row_index, row in enumerate(m.MAP_DATA):
            for col_index, tile in enumerate(row):
                if tile == s.MAP_TILE_RED_WALL or tile == s.MAP_TILE_IRON_WALL:
                    # Create normal or iron walls
                    wall = Wall(col_index, row_index, tile)
                    self.all_sprites.add(wall);
                    self.walls.add(wall)
                elif tile == s.MAP_TILE_BOSS:
                    # Create boss tile (special wall)
                    wall = Wall(col_index, row_index, tile)
                    self.all_sprites.add(wall);
                    self.walls.add(wall)
                    self.boss_group.add(wall)
                elif tile == s.MAP_TILE_BUSH:
                    # Create bush (transparent terrain)
                    bush = Bush(col_index, row_index)
                    self.all_sprites.add(bush);
                    self.bushes.add(bush)
                elif tile == s.MAP_TILE_EMPTY:
                    # Empty tile — may be used for enemy spawn
                    if row_index > 2 and row_index < 22:
                        self.enemy_spawn_tiles.append((col_index, row_index))

        # Spawn players
        self.player1 = HeroTank(m.PLAYER1_SPAWN[0], m.PLAYER1_SPAWN[1], 1, self)
        self.player2 = HeroTank(m.PLAYER2_SPAWN[0], m.PLAYER2_SPAWN[1], 2, self)
        self.all_sprites.add(self.player1);
        self.all_sprites.add(self.player2)
        self.players.add(self.player1);
        self.players.add(self.player2)

        # Enemy spawn management
        self.enemies_spawned = 0
        self.total_enemies_to_spawn = s.ENEMY_TOTAL_COUNT
        for _ in range(s.ENEMY_START_COUNT):
            self.spawn_enemy()

    # Spawn a new enemy if conditions allow
    def spawn_enemy(self):
        if self.enemies_spawned >= self.total_enemies_to_spawn: return
        if len(self.enemies) >= s.ENEMY_MAX_ON_SCREEN: return
        if not self.enemy_spawn_tiles: return

        spawn_pos = random.choice(self.enemy_spawn_tiles)
        enemy = EnemyTank(spawn_pos[0], spawn_pos[1], self)
        self.all_sprites.add(enemy);
        self.enemies.add(enemy)
        self.enemies_spawned += 1


    # Main game loop
    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(s.FPS)  # Maintain frame rate
            self.events()  # Handle inputs/events
            self.update()  # Update game logic
            self.draw()  # Render everything

        if not self.running:
            return

        self.show_game_over_screen()

    # Event handling (keyboard, quit, etc.)
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing: self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == s.P1_SHOOT: self.player1.shoot()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.player2.shoot()

        # Get player movement input continuously
        self.player1.get_input()
        self.player2.get_input()

    # Update game logic (collision, status, etc.)
    def update(self):
        # Update movement and interactions
        self.players.update(self.walls)
        self.enemies.update(self.walls)
        self.bullets.update()

        # (1) Bullet vs Wall collisions
        hits = pygame.sprite.groupcollide(self.bullets, self.walls, False, False)
        for bullet, hit_walls in hits.items():
            wall = hit_walls[0]
            if wall.wall_type == s.MAP_TILE_IRON_WALL:
                # Iron walls are indestructible
                bullet.kill();
                self.sound_hit_iron.play()
            elif wall.wall_type == s.MAP_TILE_RED_WALL:
                # Red walls take damage and can be destroyed
                bullet.kill();
                wall.health -= 1
                if wall.health <= 0: wall.kill()
            elif wall.wall_type == s.MAP_TILE_BOSS:
                # (New) Boss instant-death rule
                if bullet.owner == 'Enemy':
                    bullet.kill()  # Enemy bullets don't affect boss
                elif bullet.owner == 'P1':
                    print("Player 1 shot the boss! Player 2 wins!")
                    self.game_over = True;
                    self.playing = False
                    self.winner = 'P2'
                    bullet.kill();
                    wall.kill();
                    self.boss_group.empty()
                    return
                elif bullet.owner == 'P2':
                    print("Player 2 shot the boss! Player 1 wins!")
                    self.game_over = True;
                    self.playing = False
                    self.winner = 'P1'
                    bullet.kill();
                    wall.kill();
                    self.boss_group.empty()
                    return

        # (2) Bullet vs Player
        hits = pygame.sprite.groupcollide(self.players, self.bullets, False, False)
        for player, bullets_hit in hits.items():
            for bullet in bullets_hit:
                if bullet.owner != f"P{player.player_num}":
                    player.take_damage(1, bullet.owner)
                    bullet.kill()

        # (3) Bullet vs Enemy
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, False)
        for enemy, bullets_hit in hits.items():
            for bullet in bullets_hit:
                if bullet.owner != 'Enemy':
                    killer = enemy.take_damage(1, bullet.owner)
                    bullet.kill()
                    if killer:
                        self.sound_bang_enemy.play()
                        # Reward player with score and heal
                        if killer == 'P1':
                            self.player1.score += 1
                            self.player1.heal(s.PLAYER_HEAL_ON_KILL)
                        elif killer == 'P2':
                            self.player2.score += 1
                            self.player2.heal(s.PLAYER_HEAL_ON_KILL)
                        self.spawn_enemy()

        # (4) Check victory condition
        if self.enemies_spawned == self.total_enemies_to_spawn and not self.enemies:
            self.game_victory = True
            self.playing = False


    # Draw all visual elements

    def draw(self):
        self.screen.fill(s.BLACK)

        # Draw sprites except bushes (draw them later to layer on top)
        for sprite in self.all_sprites:
            if sprite not in self.bushes:
                self.screen.blit(sprite.image, sprite.rect)

        # Draw player UI (health, score, etc.)
        if self.player1.alive():
            self.player1.draw_ui(self.screen)
        if self.player2.alive():
            self.player2.draw_ui(self.screen)

        # Draw bushes last for visual cover effect
        for bush in self.bushes:
            self.screen.blit(bush.image, bush.rect)

        # On-screen text UI
        draw_text(self.screen, f"P1 Score: {self.player1.score}", 24, 100, 35, s.WHITE, self.font_name)
        draw_text(self.screen, f"P2 Score: {self.player2.score}", 24, s.SCREEN_WIDTH / 2, 35, s.WHITE, self.font_name)
        enemies_left = self.total_enemies_to_spawn - self.enemies_spawned + len(self.enemies)
        draw_text(self.screen, f"Enemies: {enemies_left}", 24, s.SCREEN_WIDTH - 100, 35, s.WHITE, self.font_name)

        pygame.display.flip()


    # Game Over / Victory screen

    def show_game_over_screen(self):
        """Display the end screen (either Game Over or Victory)"""
        self.screen.fill(s.BLACK)

        title_text = ""
        title_color = s.WHITE
        winner_text = ""

        # Case 1: Victory (PVE win)
        if self.game_victory:
            title_text = "VICTORY!"
            title_color = s.GREEN
            p1_score = self.player1.score
            p2_score = self.player2.score
            # Determine winner by score
            if p1_score > p2_score:
                winner_text = "Player 1 Wins!"
            elif p2_score > p1_score:
                winner_text = "Player 2 Wins!"
            else:
                winner_text = "It's a Tie!"

        # Case 2: Boss shot or player death
        elif self.game_over:
            title_text = "GAME OVER"
            title_color = s.RED
            if self.winner == 'P1':
                winner_text = "Player 1 Wins!"
            elif self.winner == 'P2':
                winner_text = "Player 2 Wins!"

        # (5) Collision: Player vs Enemy
        for enemy in self.enemies:
            # Player 1 collision
            if pygame.sprite.collide_rect(enemy, self.player1):
                self.player1.take_damage(1, 'Enemy')
                enemy.take_damage(1, 'P1')

            # Player 2 collision
            if pygame.sprite.collide_rect(enemy, self.player2):
                self.player2.take_damage(1, 'Enemy')
                enemy.take_damage(1, 'P2')

        # Draw title and scores
        draw_text(self.screen, title_text, 64, s.SCREEN_WIDTH / 2, s.SCREEN_HEIGHT / 4, title_color, self.font_name)
        draw_text(self.screen, f"Player 1 Score: {self.player1.score}", 32, s.SCREEN_WIDTH / 2, s.SCREEN_HEIGHT / 2,
                  s.WHITE, self.font_name)
        draw_text(self.screen, f"Player 2 Score: {self.player2.score}", 32, s.SCREEN_WIDTH / 2,
                  s.SCREEN_HEIGHT / 2 + 50, s.WHITE, self.font_name)
        if winner_text:
            draw_text(self.screen, winner_text, 40, s.SCREEN_WIDTH / 2, s.SCREEN_HEIGHT / 2 + 120, s.YELLOW,
                      self.font_name)
        draw_text(self.screen, "Press any key to play again", 20, s.SCREEN_WIDTH / 2, s.SCREEN_HEIGHT * 3 / 4, s.WHITE,
                  self.font_name)

        pygame.display.flip()

        # Wait for user to press a key before restarting
        waiting = True
        while waiting:
            self.clock.tick(s.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False



# Game launcher (entry point)

g = Game()
while g.running:
    g.new_game()
    g.run()

pygame.quit()
sys.exit()
