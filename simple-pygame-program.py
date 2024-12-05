# Simple pygame program from RealPython

import pygame
pygame.init()

# set up the drawing window
screen = pygame.display.set_mode([500,500])

# run until the user asks to quit
running = True
while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fill the background with white
    screen.fill((255,255,255))
    #Draw a solid blue circle in the centre
    pygame.draw.circle(screen, (0, 0,255), (250,250),75)
    # flip the display
    pygame.display.flip()

pygame.quit()
