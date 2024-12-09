import pygame
import time
import math

TRACK = pygame.image.load("assests/Track.png")
CAR = pygame.image.load("assets/SportsCar.png")
GRASS = pygame.image.load("assets/grass.png")


class PlateRace:
    def __init__(self):
        pygame.init()

        WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
        pygame.display.set_caption("PlateRace")
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
    def main_loop(self):
        while True:
            self._handle_input()
            self._game_logic()
            self._draw()
            
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                
    def _game_logic(self):
        pass
    
    def _draw(self):
        self.screen.fill((255, 0, 255))
        pygame.display.flip()