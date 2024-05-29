import pygame
import random
from math import dist

# Create Player class as a sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        walk_right1 = pygame.transform.scale_by(pygame.image.load('./assets/player.png').convert_alpha(), .15)
        walk_right2 = None
        walk_left1 = None
        walk_left2 = None
        self.player_images = [walk_right1, walk_right2, walk_left1, walk_left2]
        self.animation_index = 0

        self.image = self.player_images[self.animation_index]
        self.rect = self.image.get_rect(topleft = (300, 300))
        self.max_health = 10
        self.health = self.max_health
        self.score = 0
        self.speed = 6
        self.damage = 1
        self.max_shadow_cooldown = 1
        self.current_shadow_cooldown = 1
        self.in_shadow = False
        self.max_invulnerable_time = 4
        self.invulnerable_time = 0

    def player_inputs(self):
        keys = pygame.key.get_pressed()
        x_change = 0
        y_change = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            y_change -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            y_change += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x_change -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            x_change += 1

        if x_change != 0 and y_change != 0:
            x_change /= 2 ** .5
            y_change /= 2 ** .5

        self.rect.x += x_change * self.speed
        self.rect.y += y_change * self.speed

    def take_damage(self):
        if self.invulnerable_time <= 0:
            self.health -= 1
            self.invulnerable_time = self.max_invulnerable_time
            pygame.mixer.Sound('./assets/hit.wav').play()

    def animation_state(self):
        pass

    def check_death(self):
        if self.health <= 0:
            # add death animation
            global running
            running = False

    def check_bounds(self):
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > WIDTH - self.rect.width:
            self.rect.x = WIDTH - self.rect.width
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height

    def space_pressed(self):
        if self.current_shadow_cooldown <= 0:
            if self.in_shadow:
                self.exit_shade()
            else:
                self.enter_shade()
        else:
            self.failed_shade_jump()
        self.current_shadow_cooldown = self.max_shadow_cooldown

    def enter_shade(self):
        self.in_shadow = True
        pygame.mixer.Sound('./assets/warp.wav').play()
        global background_color
        background_color = '#E3E3EA'
        global player_life_surface
        player_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/shadow_heart.png').convert_alpha(), .046)
        self.speed *= .7
        pygame.mixer.Sound('./assets/warp.wav').play()

    def exit_shade(self):
        self.in_shadow = False
        global background_color
        background_color = '#2B2B2F'
        global player_life_surface
        player_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/player_heart.png').convert_alpha(), .04)
        self.speed /= .7
        pygame.mixer.Sound('./assets/warp.wav').play()

    def failed_shade_jump(self):
        self.health -= 1   

    def energy_gun(self):
        if enemies:
            closest_enemy = 0, dist((self.rect.x, self.rect.y), (enemies.sprites()[0].rect.x, enemies.sprites()[0].rect.y))
            for enemy in enumerate(enemies.sprites()):
                enemy_dist = dist((self.rect.x, self.rect.y), (enemy[1].rect.x, enemy[1].rect.y))
                if enemy_dist < closest_enemy[1]:
                    closest_enemy = enemy[0], enemy_dist
            x_change, y_change = find_vel(self.rect, enemies.sprites()[closest_enemy[0]].rect)
            player_projectiles.add(Projectile('musket', self.rect.x, self.rect.y, x_change, y_change))
            pygame.mixer.Sound('./assets/musket-fire.wav').play()

    def get_kill(self, enemy_type):
        if enemy_type == 'Gunner':
            self.score += 5
        else:
            self.score += 10

    def update(self):
        self.player_inputs()
        self.animation_state()
        self.check_death()
        self.check_bounds()


# Create Enemy class and subclasses as sprites
class Enemy:
    def move(self):
        x_distance, y_distance = player.sprite.rect.x - self.rect.x, player.sprite.rect.y - self.rect.y
        total_distance = dist((player.sprite.rect.x, player.sprite.rect.y), (self.rect.x, self.rect.y))
        if total_distance <= self.speed:
            self.rect.x = player.sprite.rect.x
            self.rect.y = player.sprite.rect.y
        else:
            x_change = x_distance / total_distance
            y_change = y_distance / total_distance

            self.rect.x += x_change * self.speed
            self.rect.y += y_change * self.speed

    def take_damage(self):
        self.health -= 50
        if self.health <= 0:
            player.sprite.get_kill('Gunner')
            self.kill()

    def update(self):
        self.move()


class Gunner(Enemy, pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale_by(pygame.image.load('./assets/enemy-bird.gif').convert_alpha(), .5)
        self.rect = self.image.get_rect(topleft = (random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.health = 100
        self.speed = 3
        self.max_shoot_timer = 5
        self.shoot_timer = self.max_shoot_timer

    def check_shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = self.max_shoot_timer
            x_change, y_change = find_vel(self.rect, player.sprite.rect)
            projectiles.add(Projectile('energy', self.rect.x, self.rect.y, x_change, y_change))
            pygame.mixer.Sound('./assets/pew.wav').play()

    def update(self):
        super().update()
        self.check_shoot()


class Bomber(Enemy, pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('./assets/enemy-bomb.gif').convert_alpha()
        self.rect = self.image.get_rect()
        self.health = 200
        self.speed = 3

    def explode(self):
        pass


# Create Projectile class as a sprite
class Projectile(pygame.sprite.Sprite):
    def __init__(self, type, x, y, x_change, y_change):
        super().__init__()
        self.x_change = x_change
        self.y_change = y_change

        if type == 'energy':
            image = pygame.transform.scale_by(pygame.image.load('./assets/bullet-energy.png').convert_alpha(), .2)
            self.speed = 4
        elif type == 'musket':
            image = pygame.transform.scale_by(pygame.image.load('./assets/bullet-snowball.png').convert_alpha(), .2)
            self.speed = 20

        self.image = image
        self.rect = self.image.get_rect(topleft = (x, y))

    def move(self):
        self.rect.x += self.x_change * self.speed
        self.rect.y += self.y_change * self.speed

    def update(self):
        self.move()


# Create Timer class
class Timer:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.start_time = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        if elapsed_time >= self.interval:
            self.action()
            self.start_time = current_time  # Reset timer


# Create collison functions
def detect_collision(target_group, object_group, do_destroy_object):
    collision_list = pygame.sprite.spritecollide(target_group, object_group, do_destroy_object)
    if collision_list:
        target_group.take_damage()
    return collision_list


def find_vel(point1, point2):
    x_distance, y_distance = point2.x - point1.x, point2.y - point1.y
    total_distance = dist((point2.x, point2.y), (point1.x, point1.y))
    if total_distance != 0:
        x_change = x_distance / total_distance
        y_change = y_distance / total_distance
    else:
        x_change = 0
        y_change = 0
    return x_change, y_change


# Initialize pygame, screen, clock
pygame.init()
SCREEN_RES = WIDTH, HEIGHT = 1920, 1040
FPS = 60
running = True
screen = pygame.display.set_mode(SCREEN_RES)
pygame.display.set_caption('Phantom Passage')
clock = pygame.time.Clock()
main_font = pygame.font.Font('./assets/Pixeltype.ttf', 50)
round = 1
background_color = '#2B2B2F'
background_music = pygame.mixer.Sound('./assets/main_audio.mp3')
background_music.set_volume(1)
background_music.play(loops=-1)

# Create the player sprite group
player = pygame.sprite.GroupSingle()
player.add(Player())

# Create the enemy sprite group
enemies = pygame.sprite.Group()

# Create the projectile sprite group
projectiles = pygame.sprite.Group()

# Create the player projectiles sprite group
player_projectiles = pygame.sprite.Group()

# Create enemy spawn event timers
gunner_spawn = pygame.USEREVENT + 1
pygame.time.set_timer(gunner_spawn, 1000)

player_shoot = pygame.USEREVENT + 2
pygame.time.set_timer(player_shoot, 800)

# Create UI element surfaces
player_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/player_heart.png').convert_alpha(), .04)

player_max_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/empty_player_heart.png').convert_alpha(), .04)

score_surface = main_font.render('Score:  '+ str(player.sprite.score), False, 'white')
score_rect = score_surface.get_rect(topright=(WIDTH, 0))


# Main loop
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.sprite.space_pressed()
        
        if event.type == gunner_spawn:
            enemies.add(Gunner())

        if event.type == player_shoot:
            player.sprite.energy_gun()

    screen.fill(background_color)

    for i in range(player.sprite.max_health):
        player_max_life_rect = player_max_life_surface.get_rect(topleft=(i*50, 0))
        screen.blit(player_max_life_surface, player_max_life_rect)
        
    for i in range(player.sprite.health):
        player_life_rect = player_life_surface.get_rect(topleft=(i * 50, 0))
        screen.blit(player_life_surface, player_life_rect)

    screen.blit(score_surface, score_rect)

    pygame.draw.rect(screen, 'black', (500, 5, (player.sprite.max_shadow_cooldown-player.sprite.current_shadow_cooldown)*200, 30))

    detect_collision(player.sprite, enemies, False)
    detect_collision(player.sprite, projectiles, True)
    for enemy in enemies:
        detect_collision(enemy, player_projectiles, True)

    player.update()
    player.draw(screen)

    enemies.update()
    enemies.draw(screen)

    projectiles.update()
    projectiles.draw(screen)

    player_projectiles.update()
    player_projectiles.draw(screen)

    score_surface = main_font.render('Score:  '+ str(player.sprite.score), False, 'white')
    score_rect = score_surface.get_rect(topright=(WIDTH, 0))

    pygame.display.update()
    player.sprite.invulnerable_time -= 1 / FPS
    player.sprite.current_shadow_cooldown -= 1 / FPS
    if player.sprite.current_shadow_cooldown < 0:
        player.sprite.current_shadow_cooldown = 0
    for sprite in enemies:
        sprite.shoot_timer -= 1 / FPS
    clock.tick(FPS)




print('Game over! You scored ' + str(player.sprite.score))
