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
        self.max_health = 3
        self.health = 3
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

        if keys[pygame.K_w]:
            y_change -= 1
        if keys[pygame.K_s]:
            y_change += 1
        if keys[pygame.K_a]:
            x_change -= 1
        if keys[pygame.K_d]:
            x_change += 1

        if x_change != 0 and y_change != 0:
            x_change /= 2 ** .5
            y_change /= 2 ** .5

        self.rect.x += x_change * self.speed
        self.rect.y += y_change * self.speed

    def collision(self):
        if self.invulnerable_time <= 0:
            self.health -= 1
            self.invulnerable_time = self.max_invulnerable_time

    def animation_state(self):
        pass

    def check_death(self):
        if self.health <= 0:
            # add death animation
            global running
            running = False

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
        global background_color
        background_color = '#E3E3EA'
        global player_life_surface
        player_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/shadow_heart.png').convert_alpha(), .046)
        self.speed *= .7


    def exit_shade(self):
        self.in_shadow = False
        global background_color
        background_color = '#2B2B2F'
        global player_life_surface
        player_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/player_heart.png').convert_alpha(), .04)
        self.speed /= .7

    def failed_shade_jump(self):
        self.health -= 1        

    def update(self):
        self.player_inputs()
        self.animation_state()
        self.check_death()


# Create Enemy class as a sprite
class Gunner(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('./assets/enemy-bird.gif').convert_alpha()
        self.rect = self.image.get_rect(topleft = (random.randint(0, 1000), random.randint(0, 1000)))
        self.health = 100
        self.speed = 3

    def destroy(self):
        if self.health <= 0:
            self.kill()

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


    def update(self):
        self.move()
        self.destroy()


# Create collison functions
def detect_collison(object_group, destroy_object):
    collision_list = pygame.sprite.spritecollide(player.sprite, object_group, destroy_object)
    if collision_list:
        player.sprite.collision()
    return collision_list


# Initialize pygame, screen, clock
pygame.init()
SCREEN_RES = WIDTH, HEIGHT = 1920, 1040
FPS = 60
running = True
screen = pygame.display.set_mode(SCREEN_RES)
pygame.display.set_caption('Raider of Dusk')
clock = pygame.time.Clock()
main_font = pygame.font.Font('./assets/Pixeltype.ttf', 50)
round = 1
background_color = '#2B2B2F'
background_music = pygame.mixer.Sound('./assets/slow_descent.mp3')
background_music.set_volume(0)
background_music.play(loops=-1)

# Create the player sprite group
player = pygame.sprite.GroupSingle()
player.add(Player())

# Create the enemy sprite group
enemies = pygame.sprite.Group()
enemies.add(Gunner())

# Create the projectile sprite group

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

    screen.fill(background_color)

    for i in range(player.sprite.max_health):
        player_max_life_rect = player_max_life_surface.get_rect(topleft=(i*50, 0))
        screen.blit(player_max_life_surface, player_max_life_rect)
        
    for i in range(player.sprite.health):
        player_life_rect = player_life_surface.get_rect(topleft=(i * 50, 0))
        screen.blit(player_life_surface, player_life_rect)

    screen.blit(score_surface, score_rect)

    pygame.draw.rect(screen, 'black', (500, 5, (player.sprite.max_shadow_cooldown-player.sprite.current_shadow_cooldown)*200, 30))

    detect_collison(enemies, False)
    # detect_collision(projectiles, True)

    player.update()
    player.draw(screen)

    enemies.update()
    enemies.draw(screen)

    pygame.display.update()
    player.sprite.invulnerable_time -= 1 / FPS
    player.sprite.current_shadow_cooldown -= 1/FPS
    if player.sprite.current_shadow_cooldown < 0:
        player.sprite.current_shadow_cooldown = 0
    clock.tick(FPS)




print('Game over! You scored ' + str(player.sprite.score))
