import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale_by(pygame.image.load('./assets/player.png').convert_alpha(), .15)
        self.rect = self.image.get_rect(topleft = (300, 300))
        self.health = 3
        self.score = 0
        self.speed = 10
        self.damage = 1
        self.in_shadow = False

    def player_input(self):
        keys = pygame.key.get_pressed()

    def update(self):
        self.player_input()



pygame.init()


SCREEN_RES = WIDTH, HEIGHT = 1920, 1040
running = True
screen = pygame.display.set_mode(SCREEN_RES)
pygame.display.set_caption('Raider of Dusk')
clock = pygame.time.Clock()
main_font = pygame.font.Font('./assets/Pixeltype.ttf', 50)

player = pygame.sprite.GroupSingle()
player.add(Player())

player_life_surface = pygame.transform.scale_by(pygame.image.load('./assets/player_heart.png').convert_alpha(), .04)
player_life_rect = player_life_surface.get_rect(topleft = (0, 0))


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    screen.fill('#2B2B2F')

    player_life_rect.x = 0
    for i in range(player.sprite.health):
        screen.blit(player_life_surface, player_life_rect)
        player_life_rect.x += 50



    player.update()
    player.draw(screen)

    pygame.display.update()
    clock.tick(15)




print('Game over! You scored ' + str(player.sprite.score))
