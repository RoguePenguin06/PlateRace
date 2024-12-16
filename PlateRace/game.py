import pygame
import time
import math
from utilities import resize_image, blit_rotate_center

TRACK = resize_image(pygame.image.load("PlateRace\\assets\Track.png"), 2.5)
CAR = resize_image(pygame.image.load("PlateRace\\assets\SportsCar.png"), 0.5)
GRASS = resize_image(pygame.image.load("PlateRace\\assets\grass.png"), 3)
FINISH = resize_image(pygame.image.load("PlateRace\\assets\Finish.png"), 2.6)

angle_D = 0


class AbstractCar:
    def __init__(self, max_velocity):
        self.img = self.IMG
        self.max_velocity = max_velocity
        self.velocity = 0
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        
    def rotate(self):
        global angle_D
        
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            angle_D += 5
        if keys[pygame.K_d]:
            angle_D -= 5
        if angle_D < 0:
            angle_D += 360
        if angle_D > 360:
            angle_D -= 360

        self.angle = angle_D
        
    def draw(self):
        blit_rotate_center(WIN, self.img, (self.x, self.y), self.angle)

    def move(self):
        self.change_velocity()

        angle_R = angle_D * (math.pi/180)

        if angle_D <= 90:
            self.H_velocity = -self.velocity * math.sin(angle_R)
            self.V_velocity = -self.velocity * math.cos(angle_R)

        elif angle_D <= 180:
            self.H_velocity = -self.velocity * math.cos(angle_R-(math.pi/2))
            self.V_velocity = self.velocity * math.sin(angle_R-(math.pi/2))

        elif angle_D <= 270:
            self.H_velocity = self.velocity * math.sin(angle_R-math.pi)
            self.V_velocity = self.velocity * math.cos(angle_R-math.pi)

        elif angle_D <= 360:
            self.H_velocity = self.velocity * math.cos(angle_R-((3*math.pi)/2))
            self.V_velocity = -self.velocity * math.sin(angle_R-((3*math.pi)/2))


        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.x += self.H_velocity
            self.y += self.V_velocity

    def change_velocity(self):
        self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
        

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
        player_car.move()
        

       
    def _draw(self):
        self.screen.blit(GRASS, (0, 0))
        self.screen.blit(TRACK, (0, 0))
        self.screen.blit(FINISH, (831, 300))
        player_car.draw()
        pygame.display.update()
        

clock = pygame.time.Clock()

player_car = PlayerCar(10)