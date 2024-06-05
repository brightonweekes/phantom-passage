import pygame
import random
from math import dist, ceil

# Create Player class as a sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale_by(pygame.image.load('./assets/player.png').convert_alpha(), .15)
        self.rect = self.image.get_rect(topleft = (300, 300))
        self.max_health = 5
        self.health = self.max_health
        self.score = 0
        self.gold = 0
        self.speed = 6
        self.damage = 1
        self.max_shadow_cooldown = 15
        self.current_shadow_cooldown = self.max_shadow_cooldown
        self.in_shade = False
        self.max_shadow_duration = 8
        self.shadow_duration = self.max_shadow_duration
        self.max_invulnerable_time = 3
        self.invulnerable_time = 0
        self.damage_modifier = 1
        self.firerate_modifier = 1
        self.range_modifier = 1
        self.max_energy_gun_cooldown = .4
        self.energy_gun_cooldown = self.max_energy_gun_cooldown
        self.max_shotgun_cooldown = 1
        self.shotgun_cooldown = self.max_shotgun_cooldown
        self.projectile_speed = 8

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

    def check_death(self):
        if self.health <= 0:
            # add death animation
            global game_state
            game_state = 'game-over'

    def update_timers(self):
        if game_state == 'fighting':
            self.invulnerable_time -= 1 / FPS
            self.energy_gun_cooldown -= 1 / FPS
            self.shotgun_cooldown -= 1 / FPS
            if self.current_shadow_cooldown < 0:
                self.current_shadow_cooldown = 0
            if self.in_shade:
                self.shadow_duration -= 1 / FPS
                if self.shadow_duration <= 0:
                    self.exit_shade()
            else:
                self.current_shadow_cooldown -= 1 / FPS

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
            if self.in_shade:
                self.exit_shade()
            else:
                self.enter_shade()
        else:
            self.failed_shade_jump()
        self.current_shadow_cooldown = self.max_shadow_cooldown

    def enter_shade(self):
        global bg_color, player_life_surface
        self.in_shade = True
        self.shadow_duration = self.max_shadow_duration
        pygame.mixer.Sound('./assets/warp.wav').play()
        bg_color = '#BABDC3'
        player_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/shadow_heart.png').convert_alpha(), .046)
        self.speed *= .7
        pygame.mixer.Sound('./assets/warp.wav').play()

    def exit_shade(self):
        global bg_color, player_life_surface
        self.in_shade = False
        bg_color = '#2B2B2F'
        player_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/player_heart.png').convert_alpha(), .04)
        self.speed /= .7
        pygame.mixer.Sound('./assets/warp.wav').play()

    def failed_shade_jump(self):
        self.health -= 1   

    def energy_gun(self):
        if enemies and self.energy_gun_cooldown <= 0:
            self.energy_gun_cooldown = self.max_energy_gun_cooldown * self.firerate_modifier
            x_change, y_change = self.find_closest_enemy_distance()
            player_projectiles.add(Projectile(self.rect.x, self.rect.y, x_change, y_change, self.projectile_speed, pygame.transform.scale_by(pygame.image.load('./assets/bullet-snowball.png').convert_alpha(), .2), 1400 * self.range_modifier))
            pygame.mixer.Sound('./assets/pew.wav').play()

    def shotgun(self):
        if enemies and self.shotgun_cooldown <= 0:
            self.shotgun_cooldown = self.max_shotgun_cooldown * self.firerate_modifier
            x_change, y_change = self.find_closest_enemy_distance()
            for i in range(6):
                player_projectiles.add(Projectile(self.rect.x, self.rect.y, x_change+random.uniform(-.5, .5), y_change+random.uniform(-.5, .5), self.projectile_speed, pygame.image.load('./assets/Musket_Ball.webp').convert_alpha(), 600 * self.range_modifier))
            pygame.mixer.Sound('./assets/musket.wav').play()

    def find_closest_enemy_distance(self):
        closest_enemy = 0, dist((self.rect.x, self.rect.y), (enemies.sprites()[0].rect.x, enemies.sprites()[0].rect.y))
        for enemy in enumerate(enemies.sprites()):
            enemy_dist = dist((self.rect.x, self.rect.y), (enemy[1].rect.x, enemy[1].rect.y))
            if enemy_dist < closest_enemy[1]:
                closest_enemy = enemy[0], enemy_dist
        x_change, y_change = find_vel(self.rect, enemies.sprites()[closest_enemy[0]].rect)
        return x_change, y_change


    def get_kill(self, enemy):
        self.score += enemy.value
        self.gold += enemy.value

    def upgrade(self, stat, factor, cost):
        self.gold -= cost
        setattr(self, stat, getattr(self, stat) * factor)
        if stat == 'max_health':
            self.max_health += 1
            self.health += 1

    def reset_defaults(self):
        global round
        round = 1
        self.max_health = 5
        self.health = self.max_health
        self.score = 0
        self.gold = 0
        self.speed = 6
        self.damage = 1
        self.max_shadow_cooldown = 15
        self.current_shadow_cooldown = self.max_shadow_cooldown
        if self.in_shade:
            self.exit_shade()
        self.max_shadow_duration = 8
        self.shadow_duration = self.max_shadow_duration
        self.max_invulnerable_time = 3
        self.invulnerable_time = 0
        self.damage_modifier = 1
        self.firerate_modifier = 1
        self.max_energy_gun_cooldown = .4
        self.energy_gun_cooldown = self.max_energy_gun_cooldown
        self.max_shotgun_cooldown = 1
        self.shotgun_cooldown = self.max_shotgun_cooldown
        self.projectile_speed = 8

    def update(self):
        self.player_inputs()
        self.check_death()
        self.check_bounds()
        self.energy_gun()
        self.shotgun()
        self.update_timers()


# Create Enemy class and subclasses as sprites
class Enemy:
    def move(self):
        short_distance = False
        if not player.sprite.in_shade:
            x_distance, y_distance, total_distance = find_distances(self.rect.x, self.rect.y, player.sprite.rect.x, player.sprite.rect.y)
            if total_distance <= self.speed:
                short_distance = True
                self.rect.x = player.sprite.rect.x
                self.rect.y = player.sprite.rect.y
        else:
            x_distance, y_distance, total_distance = find_distances(self.rect.x, self.rect.y, shade_pos[0], shade_pos[1])
            if total_distance <= self.speed:
                short_distance = True
                self.rect.x = shade_pos[0]
                self.rect.y = shade_pos[1]
        
        if not short_distance:
            x_change = x_distance / total_distance
            y_change = y_distance / total_distance

            self.rect.x += x_change * self.speed
            self.rect.y += y_change * self.speed

    def take_damage(self):
        self.health -= 50 * player.sprite.damage_modifier
        if self.health <= 0:
            player.sprite.get_kill(self)
            self.kill()

    def update(self):
        self.move()


class Gunner(Enemy, pygame.sprite.Sprite):
    value = 20

    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale_by(pygame.image.load('./assets/enemy-bird.gif').convert_alpha(), .5)
        self.rect = self.image.get_rect(topleft = (random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.health = 100
        self.speed = 3
        self.max_shoot_timer = 1.5
        self.shoot_timer = .5

    def check_shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = self.max_shoot_timer
            x_change, y_change = find_vel(self.rect, player.sprite.rect)
            projectiles.add(Projectile(self.rect.x, self.rect.y, x_change, y_change, 4, pygame.transform.scale_by(pygame.image.load('./assets/bullet-energy.png').convert_alpha(), .2), 2000))
            pygame.mixer.Sound('./assets/pew.wav').play()

    def update(self):
        super().update()
        self.check_shoot()


class Bomber(Enemy, pygame.sprite.Sprite):
    value = 25

    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale_by(pygame.image.load('./assets/enemy-bomb.gif'), .4).convert_alpha()
        self.rect = self.image.get_rect(topleft = (random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.health = 200
        self.speed = 3

    def check_explode(self):
        if dist((self.rect.x, self.rect.y), (player.sprite.rect.x, player.sprite.rect.y)) < 50:
            self.kill()
            player.sprite.take_damage()

    def update(self):
        super().update()
        self.check_explode()


class Prism(Enemy, pygame.sprite.Sprite):
    value = 50

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('./assets/enemy-prism.gif').convert_alpha()
        self.rect = self.image.get_rect(topleft = (random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.health = 500
        self.speed = 1

# Create Projectile class as a sprite
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, x_change, y_change, speed, image, range):
        super().__init__()
        self.x_change = x_change
        self.y_change = y_change
        self.speed = speed
        self.image = image
        self.rect = self.image.get_rect(topleft = (x, y))
        self.range = range

    def move(self):
        self.range -= (abs(self.x_change) + abs(self.y_change)) * self.speed
        self.rect.x += self.x_change * self.speed
        self.rect.y += self.y_change * self.speed
        if self.range <= 0:
            self.kill()

    def update(self):
        self.move()


# Create collison functions
def detect_collision(target_group, object_group, do_destroy_object):
    collision_list = pygame.sprite.spritecollide(target_group, object_group, do_destroy_object)
    if collision_list:
        target_group.take_damage()
    return collision_list


def find_vel(point1, point2):
    x_distance, y_distance, total_distance = find_distances(point1.x, point1.y, point2.x, point2.y)
    if total_distance != 0:
        x_change = x_distance / total_distance
        y_change = y_distance / total_distance
    else:
        x_change = 0
        y_change = 0
    return x_change, y_change


def draw_sprites(sprite_groups):
    for group in sprite_groups:
        group.update()
        group.draw(screen)


def find_round_enemies():
    round_value = round ** 3 + 80
    enemy_spawn_list = []
    enemy_spawn_chance = [.6, .3, .1]
    while round_value > 19:
        choice = random.choices(Enemy.__subclasses__(), enemy_spawn_chance)
        enemy_spawn_list.append(choice[0]())
        round_value -= choice[0]().value
    return enemy_spawn_list


def clear_sprites():
    enemies.empty()
    projectiles.empty()
    player_projectiles.empty()
    

def advance_round():
    global round, max_round_time, round_timer
    round += 1
    max_round_time += 2
    round_timer = max_round_time
    if player.sprite.health < player.sprite.max_health:
        player.sprite.health += 1
    clear_sprites()


def begin_fighting():
    global game_state, round, max_round_time, round_timer
    clear_sprites()
    player.sprite.reset_defaults()
    game_state = 'fighting'
    round = 1
    max_round_time = 20
    round_timer = max_round_time


def draw_ui():
    for i in range(player.sprite.max_health):
        player_max_life_rect = player_max_life_surface.get_rect(topleft=(i*50, 0))
        screen.blit(player_max_life_surface, player_max_life_rect)
        
    for i in range(player.sprite.health):
        player_life_rect = player_life_surface.get_rect(topleft=(i * 50, 0))
        screen.blit(player_life_surface, player_life_rect)

    if player.sprite.in_shade:
        pygame.draw.rect(screen, 'black', (500, 5, player.sprite.shadow_duration * 100, 30))
    else:
        pygame.draw.rect(screen, 'black', (500, 5, (player.sprite.max_shadow_cooldown-player.sprite.current_shadow_cooldown) * 100, 30))

    round_time_surface = main_font.render('Time remaining: ' + str(ceil(round_timer)), False, 'white')
    round_time_rect = round_time_surface.get_rect(topleft = (1120, 0))
    screen.blit(round_time_surface, round_time_rect)

    gold_surface = pygame.transform.scale_by(pygame.image.load('./assets/gold_coin.gif').convert_alpha(), 1.5)
    gold_rect = gold_surface.get_rect(topleft = (1500, 0))
    screen.blit(gold_surface, gold_rect)

    gold_number = main_font.render(str(player.sprite.gold), False, 'white')
    gold_number_rect = gold_number.get_rect(topleft = (1530, 0))
    screen.blit(gold_number, gold_number_rect)

    score_surface = main_font.render('Score:  ' + str(player.sprite.score), False, 'white')
    score_rect = score_surface.get_rect(topright=(WIDTH, 0))
    screen.blit(score_surface, score_rect)
    

def find_distances(x1, y1, x2, y2):
    x_distance, y_distance = x2 - x1, y2 - y1
    total_distance = dist((x2, y2), (x1, y1))
    return x_distance, y_distance, total_distance


# Initialize pygame and global variables
pygame.init()
SCREEN_RES = WIDTH, HEIGHT = 1920, 1040
FPS = 60
running = True
screen = pygame.display.set_mode(SCREEN_RES)
pygame.display.set_caption('Phantom Passage')
clock = pygame.time.Clock()
main_font = pygame.font.Font('./assets/Pixeltype.ttf', 50)
round = 1
max_round_time = 20
round_timer = max_round_time
bg_color = '#2B2B2F'
bg_music = pygame.mixer.Sound('./assets/main_audio.mp3')
bg_music.set_volume(.5)
bg_music.play(loops=-1)
game_state = 'fighting'
upgrades = [
    {"name": "Increase Max Health", "stat": "max_health", "factor": 1, "cost": 130},
    {"name": "Increase Attack", "stat": "damage_modifier", "factor": 1.5, "cost": 120},
    {"name": "Increase Speed", "stat": "speed", "factor": 1.3, "cost": 160},
    {"name": "Decrease Shadow Cooldown", "stat": "max_shadow_cooldown", "factor": .7, "cost": 100},
    {"name": "Increase Firerate", "stat": "firerate_modifier", "factor": .8, "cost": 180},
    {"name": "Increase Shadow Duration", "stat": "max_shadow_duration", "factor": 1.5, "cost": 80},
    {"name": "Increase Projectile Speed", "stat": "projectile_speed", "factor": 1.5, "cost": 120},
]
available_upgrades = []
reroll_num = 0
shade_pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))

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
enemy_spawn = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_spawn, 3000)

shade_player_pos = pygame.USEREVENT + 3
pygame.time.set_timer(shade_player_pos, 2000)

# Create UI element surfaces
player_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/player_heart.png').convert_alpha(), .04)

player_max_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/empty_player_heart.png').convert_alpha(), .04)


# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == 'fighting':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.sprite.space_pressed()
            
            if event.type == enemy_spawn:
                for enemy in find_round_enemies():
                    enemies.add(enemy)

            if event.type == shade_player_pos:
                shade_pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))

    if game_state == 'fighting' or game_state == 'shopping':
        screen.fill(bg_color)

        draw_ui()

        detect_collision(player.sprite, enemies, False)
        detect_collision(player.sprite, projectiles, True)
        for enemy in enemies:
            detect_collision(enemy, player_projectiles, True)

        draw_sprites((player, enemies, projectiles, player_projectiles))

        if game_state == 'shopping':
            fight_prompt = main_font.render('Press Enter to continue...', False, 'white')
            screen.blit(fight_prompt, fight_prompt.get_rect(topleft = (300, 200)))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            y = 400
            upgrades_empty = True
            for upgrade in available_upgrades:
                if upgrade != None:
                    upgrades_empty = False
                    upgrade_label = main_font.render(f"{upgrade['name']} (+{upgrade['factor']}) - Cost: {upgrade['cost']} Gold", False, 'white')
                    upgrade_label_rect = upgrade_label.get_rect(topleft=(200, y))
                    screen.blit(upgrade_label, upgrade_label_rect)

                    if upgrade_label_rect.collidepoint(mouse_pos) and mouse_click[0] and player.sprite.gold >= upgrade['cost']:
                        player.sprite.upgrade(upgrade['stat'], upgrade['factor'], upgrade['cost'])
                        available_upgrades[available_upgrades.index(upgrade)] = None
                        pygame.time.delay(200)

                y += 100
            
            reroll_cost = (reroll_num + 1) * 10
                
            reroll_label = main_font.render(f'Reroll       {reroll_cost}', False, 'white')
            reroll_label_rect = reroll_label.get_rect(topleft = (800, 650))
            screen.blit(reroll_label, reroll_label_rect)

            reroll_coin = pygame.transform.scale_by(pygame.image.load('./assets/gold_coin.gif').convert_alpha(), 1.5)
            reroll_coin_rect = reroll_label.get_rect(topleft = (900, 650))
            screen.blit(reroll_coin, reroll_coin_rect)

            if upgrades_empty or (reroll_label_rect.collidepoint(mouse_pos) and mouse_click[0]):
                if upgrades_empty:
                    reroll_cost = 0
                if player.sprite.gold >= reroll_cost:
                    available_upgrades = random.sample(upgrades, 3)
                    player.sprite.gold -= reroll_cost
                    if not upgrades_empty:
                        reroll_num += 1
                pygame.time.delay(100)

            if pygame.key.get_pressed()[pygame.K_RETURN]:
                game_state = 'fighting'
        
        elif game_state == 'fighting':
            round_timer -= 1 / FPS

            if round_timer <= 0:
                game_state = 'shopping'
                available_upgrades = random.sample(upgrades, 3)
                advance_round()
                reroll_num = 0

            for sprite in enemies:
                if hasattr(sprite, 'shoot_timer'):
                    sprite.shoot_timer -= 1 / FPS


    elif game_state == 'game-over':
        screen.fill(bg_color)

        death_text = main_font.render('You have been sent to the shadow realm...', False, 'white')
        death_text_rect = death_text.get_rect(topleft = (300, 300))
        screen.blit(death_text, death_text_rect)

        score_text = main_font.render(f'You scored {str(player.sprite.score)} points. Press enter to continue', False, 'white')
        score_text_rect = score_text.get_rect(topleft = (500, 700))
        screen.blit(score_text, score_text_rect)

        if pygame.key.get_pressed()[pygame.K_RETURN]:
            begin_fighting()


    pygame.display.update()
    clock.tick(FPS)
