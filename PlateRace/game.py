import pygame
import time
import math
from utilities import resize_image, blit_rotate_center, getDeltaTime

TRACK = resize_image(pygame.image.load("PlateRace\\assets\Track.png"), 2.5)
TRACK_MASK = pygame.mask.from_surface(TRACK)

WALL = resize_image(pygame.image.load("PlateRace\\assets\wall.png"), 2.5)
WALL_MASK = pygame.mask.from_surface(WALL)

CAR_BLUE = resize_image(pygame.image.load("PlateRace\\assets\SportsCar(Blue).png"), 0.5)
CAR_RED = resize_image(pygame.image.load("PlateRace\\assets\SportsCar(Red).png"), 0.5)

GRASS = resize_image(pygame.image.load("PlateRace\\assets\grass.png"), 3)
FINISH = resize_image(pygame.image.load("PlateRace\\assets\Finish.png"), 2.6)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POS = (831, 300)

P1WIN = resize_image(pygame.image.load("PlateRace\\assets\P1Win.png"), 2.5)
P2WIN = resize_image(pygame.image.load("PlateRace\\assets\P2Win.png"), 2.5)


ANTI_CHEAT_1 = resize_image(pygame.image.load("PlateRace\\assets\AntiCheat1.png"), 2.5)
ANTI_CHEAT_1_MASK = pygame.mask.from_surface(ANTI_CHEAT_1)

ANTI_CHEAT_2 = resize_image(pygame.image.load("PlateRace\\assets\AntiCheat2.png"), 2.5)
ANTI_CHEAT_2_MASK = pygame.mask.from_surface(ANTI_CHEAT_2)


angle_D = [0, 0]
direction = 0
deltaTime = 0
gamePlaying = True
quitTimer = 3


class AbstractCar:
    def __init__(self, max_velocity, player_num, start_pos):
        self.max_velocity_onTrack = max_velocity
        self.max_velocity = max_velocity
        self.velocity = 0
        self.angle = 0
        self.x, self.y = start_pos
        self.acceleration = 0.1
        self.deceleration = 0.5
        self.lap = 0
        self.finish_timer = 2
        
        if player_num != 0:
            self.PLAYER_NUM = player_num
            
            self.checkpoint1 = True
            self.checkpoint2 = True
            self.checkpoint3 = True
        
            if self.PLAYER_NUM == 1:
                self.controls = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
                self.img = CAR_BLUE
            elif self.PLAYER_NUM == 2:
                self.controls = [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]
                self.img = CAR_RED
        
    def draw(self):
        blit_rotate_center(WIN, self.img, (self.x, self.y), self.angle)
        
    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi
        
    def onTrack(self):
        if self.collide(TRACK_MASK):
            self.max_velocity = self.max_velocity_onTrack
        else:
            self.max_velocity = self.max_velocity_onTrack * 0.25
    
    def finish_line_check(self):
        global deltaTime
        self.finish_timer += deltaTime
        if self.finish_timer >= 2:
            if self.collide(FINISH_MASK, *FINISH_POS):
                if (self.checkpoint1 and self.checkpoint2 and self.checkpoint3) or self.PLAYER_NUM == 0:
                    self.lap += 1
                    self.checkpoint1 = False
                    self.checkpoint2 = False
                    self.checkpoint3 = False
                    self.finish_timer = 0
                else:
                    self.max_velocity_onTrack *= 0.5
                    self.finish_timer = -3
     
    def raceEnd(self):
        if self.lap > 3:
            return True
        

class PlayerCar(AbstractCar):
    
    def move(self):
        global angle_D
        global direction
        
        keys = pygame.key.get_pressed()
        
        # turning left
        if keys[self.controls[1]]:
            angle_D[self.PLAYER_NUM - 1] += 5
        elif keys[self.controls[1]]:
            angle_D[self.PLAYER_NUM - 1] += 10
            
        # turning right
        if keys[self.controls[3]]:
            angle_D[self.PLAYER_NUM - 1] -= 5
        elif keys[self.controls[3]]:
            angle_D[self.PLAYER_NUM - 1] -= 10
            
        
        if angle_D[self.PLAYER_NUM - 1] < 0:
            angle_D[self.PLAYER_NUM - 1] += 360
        if angle_D[self.PLAYER_NUM - 1] > 360:
            angle_D[self.PLAYER_NUM - 1] -= 360
        self.rotate()

        self.onTrack()
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
        
        self.bounce_on_wall()
        self.antiCheat()
            
        
    def rotate(self):
        global angle_D
        
        self.angle = angle_D[self.PLAYER_NUM - 1]
        
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
         
    def bounce_on_wall(self):
        if self.collide(WALL_MASK, *(-25, -25)):
            self.velocity = -self.velocity * 0.5
            self.draw()
            
    def antiCheat(self):
        if self.collide(ANTI_CHEAT_1_MASK, *(0, 300)):
            self.checkpoint1 = True
        if self.collide(ANTI_CHEAT_2_MASK, *(450, 0)):
            self.checkpoint2 = True
        if self.collide(ANTI_CHEAT_2_MASK, *(450, 430)):
            self.checkpoint3 = True
            
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
        global gamePlaying
        global quitTimer
        while True:
            clock.tick(60)
            self._handle_input()
            if gamePlaying == True:
                self._draw()
                self._game_logic()
            else:
                quitTimer -= getDeltaTime()
                if quitTimer <= 0:
                    quit()
            
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                
    def _game_logic(self):
        global deltaTime
        global gamePlaying
        player_1_car.move()
        player_2_car.move()

        player_1_car.finish_line_check()
        player_2_car.finish_line_check()
        
        if player_1_car.raceEnd():
            gamePlaying = False
            self.screen.blit(P1WIN, (0, 0))
            pygame.display.update()
        if player_2_car.raceEnd():
            gamePlaying = False
            self.screen.blit(P2WIN, (0, 0))
            pygame.display.update()
       
           
        deltaTime = getDeltaTime()

       
    def _draw(self):
        self.screen.blit(GRASS, (0, 0))
        self.screen.blit(TRACK, (0, 0))
        self.screen.blit(FINISH, FINISH_POS)
        self.screen.blit(WALL, (-25, -25))
      
        player_1_car.draw()
        player_2_car.draw()
        pygame.display.update()
        

clock = pygame.time.Clock()

player_1_car = PlayerCar(10, 1, (845, 350))
player_2_car = PlayerCar(10, 2, (910, 350))