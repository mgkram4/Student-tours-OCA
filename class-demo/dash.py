import math  # New: Import math for sine wave movement
import random
import sys

import pygame

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 50
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Player settings
PLAYER_SIZE = 50
PLAYER_X = 150
JUMP_VELOCITY = -18
GRAVITY = 0.9
BOOST_DURATION = 500  # milliseconds
BOOST_COOLDOWN = 3000  # milliseconds
BOOST_SPEED = 20

# Flying Enemy settings
FLYING_ENEMY_SIZE = 40
FLYING_ENEMY_SPEED = 7
FLYING_ENEMY_AMPLITUDE = 100 # How high up and down it moves
FLYING_ENEMY_FREQUENCY = 0.02 # How fast it moves up and down

# Obstacle settings
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 70
OBSTACLE_SPEED = 10
OBSTACLE_SPAWN_TIME = 1300  # milliseconds

class Player:
    def __init__(self):
        self.size = PLAYER_SIZE
        self.x = PLAYER_X
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.size
        self.velocity_y = 0
        self.is_jumping = False
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        
        # Boost attributes
        self.is_boosting = False
        self.boost_start_time = 0
        self.last_boost_time = -BOOST_COOLDOWN  # Allow boost from start
        self.boost_trail = []  # For visual effect
        self.image = pygame.image.load('player1.png').convert_alpha() # Load player image
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
    
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = JUMP_VELOCITY
            self.is_jumping = True
            pygame.mixer.Sound('sounds/shoot.wav').play() # Play jump sound
    
    def boost(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_boost_time >= BOOST_COOLDOWN and not self.is_boosting:
            self.is_boosting = True
            self.boost_start_time = current_time
            self.last_boost_time = current_time
            pygame.mixer.Sound('sounds/invader_shoot.wav').play() # Play boost sound
    
    def update(self):
        # Handle boost
        if self.is_boosting:
            current_time = pygame.time.get_ticks()
            if current_time - self.boost_start_time < BOOST_DURATION:
                # Add to trail for visual effect
                self.boost_trail.append((self.x, self.y))
                if len(self.boost_trail) > 10:
                    self.boost_trail.pop(0)
                
                # Move forward during boost
                self.x += BOOST_SPEED
                if self.x > PLAYER_X + 200:  # Limit forward movement
                    self.x = PLAYER_X + 200
            else:
                self.is_boosting = False
                self.boost_trail.clear()
                # Return to normal position
                if self.x > PLAYER_X:
                    self.x = max(PLAYER_X, self.x - 5)
        else:
            # Return to normal position when not boosting
            if self.x > PLAYER_X:
                self.x = max(PLAYER_X, self.x - 5)
        
        # Apply gravity
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        
        # Check ground collision
        if self.y >= SCREEN_HEIGHT - GROUND_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.size
            self.velocity_y = 0
            self.is_jumping = False
        
        # Update rect position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, screen):
        # Draw boost trail
        for i, (trail_x, trail_y) in enumerate(self.boost_trail):
            alpha = i * 25  # Fade effect
            trail_color = (*BLUE, alpha) if self.is_boosting else (*WHITE, alpha)
            trail_rect = pygame.Rect(trail_x, trail_y, self.size, self.size)
            # Draw faded trail images
            trail_image = self.image.copy()
            trail_image.set_alpha(alpha)
            screen.blit(trail_image, trail_rect)
        
        # Draw player (different color when boosting)
        # color = BLUE if self.is_boosting else WHITE # No longer needed with image
        # pygame.draw.rect(screen, color, self.rect) # No longer needed with image
        screen.blit(self.image, self.rect) # Draw player image
        
        # Draw boost effect
        if self.is_boosting:
            pygame.draw.rect(screen, YELLOW, self.rect, 3)

class Obstacle:
    def __init__(self, type='block'):
        self.type = type
        self.width = OBSTACLE_WIDTH if type == 'block' else 70  # Wider for holes
        self.height = OBSTACLE_HEIGHT
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height if type == 'block' else SCREEN_HEIGHT - GROUND_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.image = pygame.image.load('bad.png').convert_alpha() # Load obstacle image
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
    
    def update(self):
        self.x -= OBSTACLE_SPEED
        self.rect.x = self.x
    
    def draw(self, screen):
        if self.type == 'block':
            screen.blit(self.image, self.rect) # Draw obstacle image
        # Holes are represented by not drawing anything in their rect, but the ground below it
        # will be black instead of gray. The hole itself is a "lack" of ground.
    
    def is_off_screen(self):
        return self.x + self.width < 0

class FlyingEnemy:
    def __init__(self):
        self.size = FLYING_ENEMY_SIZE
        self.x = SCREEN_WIDTH
        self.initial_y = random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT // 2) # Random starting height
        self.y = self.initial_y
        self.velocity_x = FLYING_ENEMY_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.time = 0 # For sine wave movement
        self.image = pygame.image.load('bad.png').convert_alpha() # Load flying enemy image
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
    
    def update(self):
        self.x -= self.velocity_x
        # Sine wave movement for y-coordinate
        self.time += FLYING_ENEMY_FREQUENCY
        self.y = self.initial_y + FLYING_ENEMY_AMPLITUDE * math.sin(self.time) # Use sine for smooth up and down movement
        
        # Ensure the enemy stays within vertical bounds, for instance, not going below ground or too high
        self.y = max(SCREEN_HEIGHT // 4, min(self.y, SCREEN_HEIGHT // 2 + FLYING_ENEMY_AMPLITUDE))

        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, screen):
        screen.blit(self.image, self.rect) # Draw flying enemy image
    
    def is_off_screen(self):
        return self.x + self.size < 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Endless Runner - Speed Boost Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()
        pygame.mixer.music.load('sounds/background_music.wav') # Load background music
        pygame.mixer.music.play(-1) # Play in a loop
        self.background_image = pygame.image.load('background.png').convert() # Load background image
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.flying_enemies = [] # New: List to hold flying enemies
        self.score = 0
        self.game_over = False
        self.last_obstacle_spawn = pygame.time.get_ticks()
        self.last_flying_enemy_spawn = pygame.time.get_ticks() # New: Track last enemy spawn
        self.start_time = pygame.time.get_ticks()
    
    def spawn_obstacle(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_obstacle_spawn > OBSTACLE_SPAWN_TIME:
            # Randomly spawn a block or a hole
            if random.random() < 0.3:  # 30% chance for a hole
                self.obstacles.append(Obstacle(type='hole'))
            else:
                self.obstacles.append(Obstacle(type='block'))
            self.last_obstacle_spawn = current_time
    
    def spawn_flying_enemy(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_flying_enemy_spawn > 4000:  # Spawn every 4 seconds
            self.flying_enemies.append(FlyingEnemy())
            self.last_flying_enemy_spawn = current_time
    
    def update_score(self):
        if not self.game_over:
            # Update score based on time (100 points per second)
            current_time = pygame.time.get_ticks()
            self.score = (current_time - self.start_time) // 10
    
    def check_collisions(self):
        # No collision during boost (invincibility)
        if self.player.is_boosting:
            return
        
        for obstacle in self.obstacles:
            # Collision with blocks only, not holes
            if obstacle.type == 'block' and self.player.rect.colliderect(obstacle.rect):
                pygame.mixer.Sound('sounds/hit.wav').play() # Play hit sound
                self.game_over = True
                return # End collision check if game is over
        
        # Check collisions with flying enemies
        for enemy in self.flying_enemies:
            if self.player.rect.colliderect(enemy.rect):
                pygame.mixer.Sound('sounds/hit.wav').play() # Play hit sound
                self.game_over = True
                return # End collision check if game is over
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_over:
                        self.player.jump()
                    else:
                        self.reset_game()
                
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    if not self.game_over:
                        self.player.boost()
        
        return True
    
    def update(self):
        if not self.game_over:
            self.player.update()
            self.spawn_obstacle()
            self.spawn_flying_enemy() # New: Spawn flying enemies
            
            # Update obstacles
            for obstacle in self.obstacles[:]:
                obstacle.update()
                if obstacle.is_off_screen():
                    self.obstacles.remove(obstacle)
            
            # Update flying enemies
            for enemy in self.flying_enemies[:]: # New: Update flying enemies
                enemy.update()
                if enemy.is_off_screen():
                    self.flying_enemies.remove(enemy)
            
            self.check_collisions()
            self.update_score()
    
    def draw_boost_indicator(self):
        current_time = pygame.time.get_ticks()
        cooldown_remaining = max(0, BOOST_COOLDOWN - (current_time - self.player.last_boost_time))
        
        # Draw boost bar background
        bar_width = 200
        bar_height = 20
        bar_x = SCREEN_WIDTH - bar_width - 20
        bar_y = 20
        
        pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Draw boost bar fill
        if cooldown_remaining == 0:
            fill_color = GREEN
            fill_width = bar_width
            status_text = "BOOST READY!"
        else:
            fill_color = RED
            fill_width = int((1 - cooldown_remaining / BOOST_COOLDOWN) * bar_width)
            status_text = f"BOOST: {cooldown_remaining // 1000 + 1}s"
        
        pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_width, bar_height))
        
        # Draw border
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Draw text
        boost_text = self.small_font.render(status_text, True, WHITE)
        self.screen.blit(boost_text, (bar_x, bar_y + bar_height + 5))
    
    def draw(self):
        # Clear screen
        # self.screen.fill(BLACK) # Replaced by background image
        self.screen.blit(self.background_image, (0,0)) # Draw background image
        
        # Draw ground
        pygame.draw.rect(self.screen, GRAY, 
                        (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # Draw holes as black sections on the ground
        for obstacle in self.obstacles:
            if obstacle.type == 'hole':
                pygame.draw.rect(self.screen, BLACK, obstacle.rect)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            if obstacle.type == 'block': # Only draw blocks here, holes handled above
                obstacle.draw(self.screen)
        
        # Draw flying enemies
        for enemy in self.flying_enemies: # New: Draw flying enemies
            enemy.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw controls
        controls_text = self.small_font.render("SPACE: Jump | SHIFT: Boost", True, WHITE)
        self.screen.blit(controls_text, (10, 50))
        
        # Draw boost indicator
        self.draw_boost_indicator()
        
        # Draw game over message
        if self.game_over:
            game_over_text = self.font.render("GAME OVER! Press SPACE to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
            pygame.mixer.music.stop() # Stop background music
            pygame.mixer.Sound('sounds/game_over.wav').play() # Play game over sound
            
            final_score_text = self.font.render(f"Final Score: {self.score}", True, YELLOW)
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(final_score_text, score_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()