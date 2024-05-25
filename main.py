import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale_by(pygame.image.load('./assets/player.png').convert_alpha(), .15)
        self.rect = self.image.get_rect(topleft = (300, 300))
        self.max_health = 3
        self.health = 3
        self.score = 0
        self.speed = 10
        self.damage = 1
        self.max_shadow_cooldown = 5
        self.current_shadow_cooldown = 5
        self.in_shadow = False

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.current_shadow_cooldown <= 0:
            self.in_shadow = not self.in_shadow
            self.current_shadow_cooldown = self.max_shadow_cooldown

    def update(self):
        self.player_input()



pygame.init()


SCREEN_RES = WIDTH, HEIGHT = 1920, 1040
FPS = 60
running = True
screen = pygame.display.set_mode(SCREEN_RES)
pygame.display.set_caption('Raider of Dusk')
clock = pygame.time.Clock()
main_font = pygame.font.Font('./assets/Pixeltype.ttf', 50)

player = pygame.sprite.GroupSingle()
player.add(Player())

player_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/player_heart.png').convert_alpha(), .04)

player_max_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/empty_player_heart.png').convert_alpha(), .04)

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill('#2B2B2F')

    for i in range(player.sprite.max_health):
        player_max_life_rect = player_max_life_surface.get_rect(topleft=(i*50, 0))
        screen.blit(player_max_life_surface, player_max_life_rect)
        
    for i in range(player.sprite.health):
        player_life_rect = player_life_surface.get_rect(topleft=(i * 50, 0))
        screen.blit(player_life_surface, player_life_rect)

    pygame.draw.rect(screen, 'black', (500, 5, (5-player.sprite.current_shadow_cooldown)*200, 30))

    if player.sprite.health <= 0:
        running = False



    player.update()
    player.draw(screen)

    print(player.sprite.in_shadow)

    pygame.display.update()
    player.sprite.current_shadow_cooldown -= 1/FPS
    if player.sprite.current_shadow_cooldown < 0:
        player.sprite.current_shadow_cooldown = 0
    clock.tick(FPS)




print('Game over! You scored ' + str(player.sprite.score))
