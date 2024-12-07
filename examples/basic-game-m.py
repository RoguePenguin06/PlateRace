# Simple pygame program from RealPython

import pygame

# Import pygame.locals for easier access to key coordinates
from pygame.locals import ( 
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Define a Player Object by etending pygame.sprite.Sprite.
# The surface drawn on the screen is now an atrribute of 'player'
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((75,75))
        self.surf.fill((255,255,255))
        self.rect = self.surf.get_rect()

# create screen object
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

player = Player()

# Every game has a gameplay loop that does 4 important things:
#    - Processes user input
#    - Updates the state of all the game objects
#    - Updates tej display and audio output
#    - Maintains the speed of the game
# Each cycle of the loop is a frame and frames continue to occur until an exit condition is met e.g player collides with obstacle, player closes window.


# Processing events
# All user input results in an event being generated.

running = True

# Main loop
while running:
    # Look for event in the queue
    for event in pygame.event.get():
        # Did the user hit a key
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

        # Did the user click the close window button
        elif event.type == QUIT:
            running = False

    screen.fill((0,0,0))
    
    screen.blit(player.surf,player.rect)
    pygame.display.flip()   
