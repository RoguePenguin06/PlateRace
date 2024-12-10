import pygame
import time
import math
from utilities import resize_image, blit_rotate_center

TRACK = resize_image(pygame.image.load("PlateRace\\assets\Track.png"), 2.5)
CAR = resize_image(pygame.image.load("PlateRace\\assets\SportsCar.png"), 0.5)
GRASS = resize_image(pygame.image.load("PlateRace\\assets\grass.png"), 3)
FINISH = resize_image(pygame.image.load("PlateRace\\assets\Finish.png"), 2.6)

angle = 0


class AbstractCar:
    def __init__(self, max_velocity):
        self.img = self.IMG
        self.max_velocity = max_velocity
        self.velocity = 0
        self.angle = 90
        self.x, self.y = self.START_POS
        
    def rotate(self):
        global angle
        
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            angle += 5
        if keys[pygame.K_d]:
            angle -= 5


        self.angle = angle
        
    def draw(self):
        blit_rotate_center(WIN, self.img, (self.x, self.y), self.angle)
        

class PlayerCar(AbstractCar):
    IMG = CAR
    START_POS = (420, 500)
    
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()        

def window():
    global WIN
    pygame.display.set_caption("PlateRace")
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    return WIN
    

class PlateRace:
    def __init__(self):
        pygame.init()
        
        self.screen = window()
        
    def main_loop(self):
        while True:
            clock.tick(60)
            self._handle_input()
            self._game_logic()
            self._draw()
            
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                
    def _game_logic(self):
        player_car.rotate()
        

        
    
    def _draw(self):
        self.screen.blit(GRASS, (0, 0))
        self.screen.blit(TRACK, (0, 0))
        self.screen.blit(FINISH, (831, 300))
        player_car.draw()
        #pygame.display.flip()
        pygame.display.update()
        


clock = pygame.time.Clock()

player_car = PlayerCar(10)