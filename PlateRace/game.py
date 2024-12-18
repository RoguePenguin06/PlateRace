import pygame
import time
import math
from utilities import resize_image, blit_rotate_center

TRACK = resize_image(pygame.image.load("PlateRace\\assets\Track.png"), 2.5)
CAR = resize_image(pygame.image.load("PlateRace\\assets\SportsCar.png"), 0.5)
GRASS = resize_image(pygame.image.load("PlateRace\\assets\grass.png"), 3)
FINISH = resize_image(pygame.image.load("PlateRace\\assets\Finish.png"), 2.6)

angle_D = [0, 0]
direction = 0


class AbstractCar:
    def __init__(self, max_velocity, player_num):
        self.img = self.IMG
        self.max_velocity = max_velocity
        self.velocity = 0
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.deceleration = 0.5
        self.PLAYER_NUM = player_num
        
        if self.PLAYER_NUM == 1:
            self.controls = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
        elif self.PLAYER_NUM == 2:
            self.controls = [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]
        
    def rotate(self):
        global angle_D
        
        self.angle = angle_D[self.PLAYER_NUM - 1]
        
    def draw(self):
        blit_rotate_center(WIN, self.img, (self.x, self.y), self.angle)

    

    def change_velocity(self):
        global direction
        keys = pygame.key.get_pressed()
        if keys[self.controls[0]]:
            self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
            direction = 1
        elif keys[self.controls[2]]:
            self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
            direction = -0.25
        else:
            self.velocity = max(self.velocity - self.deceleration, 0)
        

class PlayerCar(AbstractCar):
    IMG = CAR
    START_POS = (420, 500)
    
    def move(self):
        global angle_D
        global direction
        
        keys = pygame.key.get_pressed()
        if keys[self.controls[1]]:
            angle_D[self.PLAYER_NUM - 1] += 5
        if keys[self.controls[3]]:
            angle_D[self.PLAYER_NUM - 1] -= 5
        if angle_D[self.PLAYER_NUM - 1] < 0:
            angle_D[self.PLAYER_NUM - 1] += 360
        if angle_D[self.PLAYER_NUM - 1] > 360:
            angle_D[self.PLAYER_NUM - 1] -= 360
        self.rotate()

        self.change_velocity()

        angle_R = angle_D[self.PLAYER_NUM - 1] * (math.pi/180)

        if angle_D[self.PLAYER_NUM - 1] <= 90:
            self.H_velocity = -self.velocity * math.sin(angle_R)
            self.V_velocity = -self.velocity * math.cos(angle_R)

        elif angle_D[self.PLAYER_NUM - 1] <= 180:
            self.H_velocity = -self.velocity * math.cos(angle_R-(math.pi/2))
            self.V_velocity = self.velocity * math.sin(angle_R-(math.pi/2))

        elif angle_D[self.PLAYER_NUM - 1] <= 270:
            self.H_velocity = self.velocity * math.sin(angle_R-math.pi)
            self.V_velocity = self.velocity * math.cos(angle_R-math.pi)

        elif angle_D[self.PLAYER_NUM - 1] <= 360:
            self.H_velocity = self.velocity * math.cos(angle_R-((3*math.pi)/2))
            self.V_velocity = -self.velocity * math.sin(angle_R-((3*math.pi)/2))


        self.x += self.H_velocity * direction
        self.y += self.V_velocity * direction          
    
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
        player_1_car.move()
        player_2_car.move()
        

       
    def _draw(self):
        self.screen.blit(GRASS, (0, 0))
        self.screen.blit(TRACK, (0, 0))
        self.screen.blit(FINISH, (831, 300))
        player_1_car.draw()
        player_2_car.draw()
        pygame.display.update()
        

clock = pygame.time.Clock()

player_1_car = PlayerCar(10, 1)
player_2_car = PlayerCar(10, 2)