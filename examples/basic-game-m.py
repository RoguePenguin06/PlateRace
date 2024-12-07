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

# create screen object
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

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

    screen.fill((255,255,255))
    surf = pygame.Surface((50,50))
    surf.fill((0,0,0))
    rect = surf.get_rect()
    
    surf_centre = (
        (SCREEN_WIDTH-surf.get_width())/2,
        (SCREEN_HEIGHT-surf.get_height())/2
    )
    
    screen.blit(surf,surf_centre)
    pygame.display.flip()   
