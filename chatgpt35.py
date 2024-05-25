import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shadow Realm Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Player properties
player_size = 50
player_color = BLACK
player_x = 50
player_y = HEIGHT - player_size * 2
player_speed = 5

# Platform properties
platform_width = 100
platform_height = 20
platform_color = GRAY
platforms = [(0, HEIGHT - platform_height, WIDTH, platform_height),
             (WIDTH // 2 - platform_width // 2, HEIGHT * 3 // 4, platform_width, platform_height)]

# Shadow realm flag
in_shadow_realm = False

# Main game loop
while True:
    SCREEN.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle shadow realm
                in_shadow_realm = not in_shadow_realm

    # Move player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(SCREEN, platform_color, platform)

    # Draw player
    pygame.draw.rect(SCREEN, player_color, (player_x, player_y, player_size, player_size))

    # Update display
    pygame.display.flip()
