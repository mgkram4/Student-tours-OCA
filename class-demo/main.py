import os
import random
import sys

import pygame

pygame.init()
pygame.mixer.init()

# Improved dimensions for better gameplay
WIDTH, HEIGHT = 1024, 768
FPS = 60
WHITE, BLACK, RED, GREEN, BLUE = (255,)*3, (0,)*3, (220,40,40), (0,210,0), (40,120,255)
BG = (10, 10, 20)
PLAYER_SPEED, BULLET_SPEED, ENEMY_BULLET_SPEED = 8, 12, 5
ENEMY_MOVE_TIME = 600     # ms between horizontal steps (will speed up)
ENEMY_DESCEND = 28
FONT = pygame.font.SysFont("consolas", 28)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def load_sound(name):
    path = os.path.join("sounds", name)
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None

def load_music(name):
    path = os.path.join("sounds", name)
    if os.path.exists(path):
        return path
    return None

# Load sound effects
snd_player_shoot = load_sound("shoot.wav")
snd_enemy_shoot  = load_sound("invader_shoot.wav")
snd_hit          = load_sound("hit.wav")
snd_explosion    = load_sound("explosion.wav")
snd_game_over    = load_sound("game_over.wav")

# Load background music
bg_music = load_music("background_music.wav")
if bg_music:
    pygame.mixer.music.load(bg_music)
    pygame.mixer.music.set_volume(0.3)

# ───────── Sprites ─────────
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load the player image
        try:
            self.image = pygame.image.load("player.png").convert_alpha()
            # Scale the image to a reasonable size for gameplay
            self.image = pygame.transform.scale(self.image, (80, 60))
        except:
            # Fallback to green rectangle if image loading fails
            self.image = pygame.Surface((80, 60))
            self.image.fill(GREEN)
        self.rect  = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT-40))
        self.lives = 3

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left>0:         self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right<WIDTH:   self.rect.x += PLAYER_SPEED

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x,y, speed, color=WHITE):
        super().__init__()
        self.image = pygame.Surface((6,18)); self.image.fill(color)
        self.rect  = self.image.get_rect(midbottom=(x,y))
        self.speed = speed
    def update(self): 
        self.rect.y += self.speed
        if self.rect.bottom<0 or self.rect.top>HEIGHT: self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x,y,row):
        super().__init__()
        # Load the enemy image
        try:
            self.image = pygame.image.load("bad.png").convert_alpha()
            # Scale the image to a reasonable size for gameplay
            self.image = pygame.transform.scale(self.image, (60, 50))
        except:
            # Fallback to colored rectangles if image loading fails
            w,h = 60,50
            self.image = pygame.Surface((w,h))
            colors = [BLUE,WHITE,RED]             # 3 point tiers
            self.tier  = row//2                   # 0,1,2
            self.points= (3-self.tier)*10
            self.image.fill(colors[self.tier])
        
        self.tier  = row//2                   # 0,1,2
        self.points= (3-self.tier)*10
        self.rect = self.image.get_rect(topleft=(x,y))

class Shield(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.Surface((10,10)); self.image.fill((50,200,50))
        self.rect  = self.image.get_rect(topleft=(x,y))

class Explosion(pygame.sprite.Sprite):
    def __init__(self,pos,color,size=8):
        super().__init__()
        self.image = pygame.Surface((size,size)); self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.timer= 180   # ms
    def update(self):
        self.timer -= clock.get_time()
        if self.timer<=0: self.kill()

# ───────── build stage ─────────
def build_enemies():
    g = pygame.sprite.Group()
    rows, cols = 5, 12
    x_off, y_off = 70, 60
    for r in range(rows):
        for c in range(cols):
            x = 100 + c*x_off
            y = 80 + r*y_off
            g.add(Enemy(x,y,r))
    return g

def build_shields():
    g = pygame.sprite.Group()
    start_x = 150
    for bunker in range(4):
        for row in range(8):
            for col in range(12):
                if row<3 and 3<col<8: continue               # carve top arch
                x = start_x + bunker* (WIDTH//4) + col*10
                y = HEIGHT-200 + row*10
                g.add(Shield(x,y))
    return g

# ───────── helpers ─────────
def draw_hud(score, lives):
    txt = FONT.render(f"Score {score:04d}", True, WHITE); screen.blit(txt,(30,15))
    for i in range(lives):
        pygame.draw.rect(screen, GREEN, pygame.Rect(WIDTH-150+i*35,15,25,15))

def maybe_fire_enemy_bullet():
    global enemy_bullets
    if len(enemies)==0 or len(enemy_bullets): return
    if random.random()<0.02:                    # 2 % chance per frame
        shooter = random.choice(enemies.sprites())
        bullet = Bullet(shooter.rect.centerx, shooter.rect.bottom, ENEMY_BULLET_SPEED, RED)
        enemy_bullets.add(bullet)
        if snd_enemy_shoot: snd_enemy_shoot.play()

# ───────── game objects ─────────
state = "TITLE"
player  = Player()
player_grp = pygame.sprite.GroupSingle(player)
bullets, enemy_bullets = pygame.sprite.Group(), pygame.sprite.Group()
enemies  = build_enemies()
shields  = build_shields()
explodes = pygame.sprite.Group()

enemy_dir, enemy_timer, level_speedup = 1, 0, 0
score = 0

# Load background image
try:
    bg_image = pygame.image.load("background.png").convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
except:
    bg_image = None

def reset():
    global player, player_grp, bullets, enemy_bullets, enemies, shields, explodes
    global enemy_dir, enemy_timer, level_speedup, score, state
    player  = Player(); player_grp = pygame.sprite.GroupSingle(player)
    bullets, enemy_bullets = pygame.sprite.Group(), pygame.sprite.Group()
    enemies, shields = build_enemies(), build_shields()
    explodes.empty()
    enemy_dir, enemy_timer, level_speedup = 1, 0, 0
    score   = 0
    state   = "PLAYING"
    # Start background music
    if bg_music:
        pygame.mixer.music.play(-1)  # Loop indefinitely

# ───────── main loop ─────────
while True:
    dt = clock.tick(FPS)
    keys = pygame.key.get_pressed()
    for e in pygame.event.get():
        if e.type==pygame.QUIT: pygame.quit(); sys.exit()
        if state=="PLAYING" and e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE and len(bullets)<3:
            bullets.add(Bullet(player.rect.centerx, player.rect.top, -BULLET_SPEED))
            if snd_player_shoot: snd_player_shoot.play()
        if state in ("TITLE","GAME_OVER") and e.type==pygame.KEYDOWN:
            reset()

    # ─── Update world ───
    if state=="PLAYING":
        player_grp.update(keys)
        bullets.update(); enemy_bullets.update(); explodes.update()

        # Enemy block movement
        enemy_timer += dt
        step_time = max(80, ENEMY_MOVE_TIME - level_speedup*12)   # speeds up
        if enemy_timer >= step_time:
            enemy_timer = 0
            hit_edge = any((enemy.rect.right>=WIDTH-10 and enemy_dir==1) or
                           (enemy.rect.left<=10 and enemy_dir==-1) for enemy in enemies)
            if hit_edge:
                enemy_dir *= -1
                for en in enemies: en.rect.y += ENEMY_DESCEND
            else:
                for en in enemies: en.rect.x += 10*enemy_dir
            level_speedup = (60 - len(enemies))                   # fewer invaders → faster

        maybe_fire_enemy_bullet()

        # Collisions
        # Player bullet hits
        for bullet in bullets:
            hit_inv = pygame.sprite.spritecollide(bullet,enemies,True)
            if hit_inv:
                score += hit_inv[0].points
                bullet.kill()
                explodes.add(Explosion(hit_inv[0].rect.center, WHITE))
                if snd_hit: snd_hit.play()
        # Enemy bullet hits player
        if pygame.sprite.spritecollide(player,enemy_bullets,True):
            player.lives -=1
            explodes.add(Explosion(player.rect.center, RED,12))
            if snd_explosion: snd_explosion.play()
            if player.lives<=0: 
                state="GAME_OVER"
                if bg_music: pygame.mixer.music.stop()
                if snd_game_over: snd_game_over.play()
        # Bullets vs shields
        for grp in (bullets, enemy_bullets):
            hit_shield = pygame.sprite.groupcollide(grp, shields, True, True)
            if hit_shield: 
                # Fix: Get the bullet object from the dictionary
                bullet = list(hit_shield.keys())[0]
                explodes.add(Explosion(bullet.rect.center, GREEN,6))

        # Invader reaches bottom / shield
        if any(enemy.rect.bottom >= player.rect.top for enemy in enemies):
            state="GAME_OVER"
            if bg_music: pygame.mixer.music.stop()
            if snd_game_over: snd_game_over.play()

        # Win?
        if not enemies:
            state="GAME_OVER"
            if bg_music: pygame.mixer.music.stop()

    # ─── Draw ───
    # Draw background
    if bg_image:
        screen.blit(bg_image, (0, 0))
    else:
        screen.fill(BG)
    if state=="TITLE":
        t1 = FONT.render("SPACE INVADERS  –  PRESS ANY KEY", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(WIDTH//2, HEIGHT//2)))
    elif state=="GAME_OVER":
        t1 = FONT.render("GAME  OVER  –  PRESS ANY KEY", True, RED)
        t2 = FONT.render(f"FINAL SCORE: {score}", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(WIDTH//2, HEIGHT//2-20)))
        screen.blit(t2, t2.get_rect(center=(WIDTH//2, HEIGHT//2+20)))
    else:   # PLAYING
        player_grp.draw(screen)
        enemies.draw(screen)
        shields.draw(screen)
        bullets.draw(screen); enemy_bullets.draw(screen)
        explodes.draw(screen)
        draw_hud(score, player.lives)

    pygame.display.flip()