# spiderman_bossfight.py
# Spider-Man City Game + Venom Boss Fight
# pip install pygame

import pygame, random, math, sys

# ---------- Constants ----------
WIDTH, HEIGHT = 800, 600
FPS = 60

PLAYER_RADIUS = 20
PLAYER_SPEED = 5
WEB_SPEED = 12
ENEMY_SIZE = 28

ENEMY_BASE_SPEED = 2
ENEMY_SPEED_INC = 0.6
LEVEL_SCORE_THRESHOLD = 60
BOSS_SPAWN_SCORE = 200  # Boss appears after this score

# Colors
BLACK = (0, 0, 0)
WHITE = (240, 240, 240)
SPIDEY_RED = (220, 40, 40)
SPIDEY_BLUE = (20, 60, 150)
WEB_GRAY = (200, 200, 220)
ENEMY_GREEN = (50, 190, 70)
YELLOW = (255, 220, 80)
VENOM_PURPLE = (90, 0, 120)
CITY_SKY = [(30, 30, 40), (20, 40, 70), (10, 30, 60), (0, 20, 40)]

# ---------- Classes ----------
class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = PLAYER_RADIUS
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x - self.radius, y - self.radius,
                                self.radius * 2, self.radius * 2)

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)

    def draw(self, surf):
        pygame.draw.circle(surf, SPIDEY_BLUE, (int(self.x), int(self.y)), self.radius + 2)
        pygame.draw.circle(surf, SPIDEY_RED, (int(self.x), int(self.y)), self.radius)
        eye_w = self.radius // 2
        pygame.draw.ellipse(surf, WHITE, (self.x - eye_w + 4, self.y - eye_w - 2, eye_w, eye_w + 4))
        pygame.draw.ellipse(surf, WHITE, (self.x + 4, self.y - eye_w - 2, eye_w, eye_w + 4))

class Web:
    def __init__(self, x, y, dx, dy):
        mag = math.hypot(dx, dy) or 1
        self.vx = (dx / mag) * WEB_SPEED
        self.vy = (dy / mag) * WEB_SPEED
        self.x, self.y = x, y
        self.alive = True
        self.rect = pygame.Rect(self.x - 4, self.y - 4, 8, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.topleft = (self.x - 4, self.y - 4)
        if not (-50 < self.x < WIDTH + 50 and -50 < self.y < HEIGHT + 50):
            self.alive = False

    def draw(self, surf):
        pygame.draw.line(surf, WEB_GRAY, (int(self.x - self.vx), int(self.y - self.vy)),
                         (int(self.x), int(self.y)), 3)
        pygame.draw.circle(surf, WEB_GRAY, (int(self.x), int(self.y)), 4)

class Enemy:
    def __init__(self, x, y, speed):
        self.x, self.y = x, y
        self.size = ENEMY_SIZE
        self.speed = speed
        self.caught = False
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self):
        if not self.caught:
            self.y += self.speed
        else:
            self.y += 0.6
        self.rect.topleft = (self.x, self.y)

    def draw(self, surf):
        color = (120, 140, 120) if self.caught else ENEMY_GREEN
        pygame.draw.rect(surf, color, (int(self.x), int(self.y), self.size, self.size))
        if not self.caught:
            pygame.draw.rect(surf, BLACK, (int(self.x + 6), int(self.y + 6), 6, 6))
            pygame.draw.rect(surf, BLACK, (int(self.x + self.size - 12), int(self.y + 6), 6, 6))

class VenomBoss:
    def __init__(self):
        self.x, self.y = WIDTH//2 - 60, 100
        self.w, self.h = 120, 120
        self.speed = 3
        self.health = 20
        self.direction = 1
        self.fire_timer = 0
        self.projectiles = []

    def update(self, dt):
        self.x += self.speed * self.direction
        if self.x < 50 or self.x + self.w > WIDTH - 50:
            self.direction *= -1
        self.fire_timer += dt
        if self.fire_timer > 900:  # fire venom ball
            self.fire_timer = 0
            self.projectiles.append(VenomShot(self.x + self.w//2, self.y + self.h))

        for shot in self.projectiles:
            shot.update()
        self.projectiles = [s for s in self.projectiles if s.alive]

    def draw(self, surf):
        # body
        pygame.draw.ellipse(surf, VENOM_PURPLE, (self.x, self.y, self.w, self.h))
        # eyes
        pygame.draw.ellipse(surf, WHITE, (self.x + 25, self.y + 25, 20, 30))
        pygame.draw.ellipse(surf, WHITE, (self.x + self.w - 45, self.y + 25, 20, 30))
        # mouth
        pygame.draw.rect(surf, BLACK, (self.x + 40, self.y + 80, 40, 10))
        # health bar
        pygame.draw.rect(surf, (180, 0, 0), (self.x, self.y - 15, self.w, 8))
        pygame.draw.rect(surf, (0, 220, 0),
                         (self.x, self.y - 15, int(self.w * self.health / 20), 8))
        # projectiles
        for shot in self.projectiles:
            shot.draw(surf)

class VenomShot:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.r = 10
        self.speed = 5
        self.alive = True
        self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r*2, self.r*2)

    def update(self):
        self.y += self.speed
        self.rect.topleft = (self.x - self.r, self.y - self.r)
        if self.y > HEIGHT + 20:
            self.alive = False

    def draw(self, surf):
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), self.r)

# ---------- Utility ----------
def circle_rect_collision(cx, cy, r, rect):
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))
    dx, dy = cx - closest_x, cy - closest_y
    return dx*dx + dy*dy <= r*r

def draw_city_background(screen, level):
    color = CITY_SKY[level % len(CITY_SKY)]
    screen.fill(color)
    pygame.draw.rect(screen, (15, 15, 25), (0, HEIGHT - 100, WIDTH, 100))
    random.seed(level)
    for bx in range(0, WIDTH, 80):
        h = random.randint(40, 80) + level * 5
        pygame.draw.rect(screen, (20, 20, 35), (bx, HEIGHT - 100 - h, 60, h))

# ---------- Main ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spider-Man vs Venom 🕸️")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 56)

    player = Player(WIDTH//2, HEIGHT - 80)
    webs, enemies = [], []
    score, level = 0, 1
    boss = None
    game_over = False
    boss_defeated = False
    spawn_timer = 0

    while True:
        dt = clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and not game_over:
                    mx, my = pygame.mouse.get_pos()
                    webs.append(Web(player.x, player.y - player.radius, mx - player.x, my - player.y))
                if e.key == pygame.K_r and game_over:
                    return main()

        keys = pygame.key.get_pressed()
        if not game_over:
            dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
            if dx and dy:
                dx *= 0.7071; dy *= 0.7071
            player.move(dx, dy)

        # Level-based spawning
        if not boss and not game_over:
            spawn_timer += dt
            if spawn_timer > 800 - level * 60:
                enemies.append(Enemy(random.randint(10, WIDTH - ENEMY_SIZE - 10), -ENEMY_SIZE,
                                     ENEMY_BASE_SPEED + level * ENEMY_SPEED_INC))
                spawn_timer = 0

        # Boss spawn
        if score >= BOSS_SPAWN_SCORE and not boss and not boss_defeated:
            boss = VenomBoss()

        # Updates
        for w in webs: w.update()
        for en in enemies: en.update()
        if boss:
            boss.update(dt)

        # Collisions
        for w in webs:
            if boss and boss.health > 0 and w.rect.colliderect(
                pygame.Rect(boss.x, boss.y, boss.w, boss.h)
            ):
                boss.health -= 1
                w.alive = False
                if boss.health <= 0:
                    boss_defeated = True
                    score += 100
            for en in enemies:
                if not en.caught and w.rect.colliderect(en.rect):
                    en.caught, w.alive = True, False
                    score += 10
                    break

        webs = [w for w in webs if w.alive]
        enemies = [en for en in enemies if en.y < HEIGHT + 80]

        # Player collision
        for en in enemies:
            if circle_rect_collision(player.x, player.y, player.radius, en.rect) and not en.caught:
                game_over = True
        if boss:
            for shot in boss.projectiles:
                if circle_rect_collision(player.x, player.y, player.radius, shot.rect):
                    game_over = True

        # Level progression
        next_level = score // LEVEL_SCORE_THRESHOLD + 1
        if next_level > level and not boss:
            level = next_level
            screen.fill(BLACK)
            txt = big_font.render(f"LEVEL {level}", True, YELLOW)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 20))
            pygame.display.flip()
            pygame.time.wait(1000)

        # Draw
        draw_city_background(screen, level)
        for w in webs: w.draw(screen)
        for en in enemies: en.draw(screen)
        if boss and boss.health > 0:
            boss.draw(screen)
        player.draw(screen)

        # HUD
        screen.blit(font.render(f"Score: {score}", True, YELLOW), (10, 10))
        if boss and boss.health > 0:
            screen.blit(font.render("BOSS: VENOM", True, (255, 50, 255)), (WIDTH - 180, 10))
        if boss_defeated:
            win = big_font.render("VENOM DEFEATED!", True, YELLOW)
            screen.blit(win, (WIDTH//2 - win.get_width()//2, 40))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            go = big_font.render("GAME OVER", True, (255, 70, 70))
            screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//2 - 40))
            sub = font.render("Press R to restart", True, WHITE)
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))

        pygame.display.flip()

if __name__ == "__main__":
    main()
