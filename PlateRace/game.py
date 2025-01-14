from pathlib import Path
import pygame
import time
import math
import cv2

from utilities import resize_image, blit_rotate_center, getDeltaTime
from multi_person_hand_tracker import MultiPersonHandTracker

# Define base assets directory
ASSETS_DIR = Path("PlateRace/assets")

# Update image loading to use pathlib
TRACK = resize_image(pygame.image.load(ASSETS_DIR / "Track.png"), 2.5)
TRACK_MASK = pygame.mask.from_surface(TRACK)

WALL = resize_image(pygame.image.load(ASSETS_DIR / "wall.png"), 2.5)
WALL_MASK = pygame.mask.from_surface(WALL)

CAR_BLUE = resize_image(pygame.image.load(ASSETS_DIR / "SportsCar(Blue).png"), 0.5)
CAR_RED = resize_image(pygame.image.load(ASSETS_DIR / "SportsCar(Red).png"), 0.5)

GRASS = resize_image(pygame.image.load(ASSETS_DIR / "grass.png"), 3)
FINISH = resize_image(pygame.image.load(ASSETS_DIR / "Finish.png"), 2.6)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POS = (831, 300)

P1WIN = resize_image(pygame.image.load(ASSETS_DIR / "P1Win.png"), 2.5)
P2WIN = resize_image(pygame.image.load(ASSETS_DIR / "P2Win.png"), 2.5)

ANTI_CHEAT_1 = resize_image(pygame.image.load(ASSETS_DIR / "AntiCheat1.png"), 2.5)
ANTI_CHEAT_1_MASK = pygame.mask.from_surface(ANTI_CHEAT_1)

ANTI_CHEAT_2 = resize_image(pygame.image.load(ASSETS_DIR / "AntiCheat2.png"), 2.5)
ANTI_CHEAT_2_MASK = pygame.mask.from_surface(ANTI_CHEAT_2)

angle_D = [0, 0]
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
        self.gradient_history = []  # For smoothing hand tracking input
        
        if player_num != 0:
            self.PLAYER_NUM = player_num
            self.checkpoint1 = True
            self.checkpoint2 = True
            self.checkpoint3 = True
        
            if self.PLAYER_NUM == 1:
                self.img = CAR_BLUE
            elif self.PLAYER_NUM == 2:
                self.img = CAR_RED

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
        
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
    def move_player(self, hand_gradient):
        # Only add non-None gradients to history
        if (hand_gradient is not None) and (abs(hand_gradient) < 2):
            self.gradient_history.append(hand_gradient)
        
        # Keep history at max length
        if len(self.gradient_history) > 5:
            self.gradient_history.pop(0)
        
        # Only process if we have valid gradients
        if self.gradient_history and any(g is not None for g in self.gradient_history):
            # Filter out None values and calculate average
            valid_gradients = [g for g in self.gradient_history if g is not None]
            if valid_gradients:  # Check if we have any valid gradients
                smoothed_gradient = sum(valid_gradients) / len(valid_gradients)
                
                # Dead zone
                DEAD_ZONE = 0.1
                if abs(smoothed_gradient) < DEAD_ZONE:
                    smoothed_gradient = 0
                
                # Convert gradient to angle change
                if smoothed_gradient > 0:  # Tilted right
                    angle_D[self.PLAYER_NUM - 1] -= 5 * smoothed_gradient
                elif smoothed_gradient < 0:  # Tilted left
                    angle_D[self.PLAYER_NUM - 1] -= 5 * smoothed_gradient
                   
        

    def move(self, person1_gradient, person2_gradient):
        if self.PLAYER_NUM == 1:
            self.move_player(person1_gradient)
        elif self.PLAYER_NUM == 2:
            self.move_player(person2_gradient)
            
        self.rotate()

        if angle_D[self.PLAYER_NUM - 1] < 0:
            angle_D[self.PLAYER_NUM - 1] += 360
        if angle_D[self.PLAYER_NUM - 1] > 360:
            angle_D[self.PLAYER_NUM - 1] -= 360
            
        
        self.onTrack()

        angle_R = angle_D[self.PLAYER_NUM - 1] * (math.pi/180)

        self.velocity = min(self.velocity + self.acceleration, self.max_velocity)

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

        self.x += self.H_velocity
        self.y += self.V_velocity
        
        self.bounce_on_wall()
        self.antiCheat()
            
    def rotate(self):
        self.angle = angle_D[self.PLAYER_NUM - 1]
            
    def bounce_on_wall(self):
        if self.collide(WALL_MASK, *(-25, -25)):
            self.velocity = -self.velocity * 0.5
            
    def antiCheat(self):
        if self.collide(ANTI_CHEAT_1_MASK, *(0, 300)):
            self.checkpoint1 = True
        if self.collide(ANTI_CHEAT_2_MASK, *(450, 0)):
            self.checkpoint2 = True
        if self.collide(ANTI_CHEAT_2_MASK, *(450, 430)):
            self.checkpoint3 = True

class PlateRace:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = TRACK.get_width(), TRACK.get_height()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("PlateRace")
        self.clock = pygame.time.Clock()
        self.hand_tracker = MultiPersonHandTracker()
        
        # Initialize players
        self.player_1_car = PlayerCar(10, 1, (845, 350))
        self.player_2_car = PlayerCar(10, 2, (910, 350))
        
    def main_loop(self):
        tick = 10
        global gamePlaying, quitTimer, deltaTime
        
        while True:
            self.clock.tick(60)
            self._handle_input()
            
            if gamePlaying:
                tick += 1
                if tick >= 10:
                    try:
                        tick = 0

                        # Get hand tracking data
                        result = self.hand_tracker.process_frame()
                        #if result is None:
                            #continue
                        
                        player_frame, person1_gradient, person2_gradient = result
                    
                        # Update game state if we have a valid frame
                        if player_frame is not None:
                            cv2.imshow("Multi-Person Hand Tracking", player_frame)
                    
                    except Exception as e:
                        print(f"Error in main loop: {str(e)}")
                        continue

                self._draw()
                self._game_logic(person1_gradient, person2_gradient)
                    
            else:
                quitTimer -= getDeltaTime()
                if quitTimer <= 0:
                    if hasattr(self.hand_tracker, 'release'):
                        self.hand_tracker.release()
                    quit()

            
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                
    def _game_logic(self, person1_gradient, person2_gradient):
        global deltaTime
        global gamePlaying
        self.player_1_car.move(person1_gradient, person2_gradient)
        self.player_2_car.move(person1_gradient, person2_gradient)

        self.player_1_car.finish_line_check()
        self.player_2_car.finish_line_check()
        
        if self.player_1_car.raceEnd():
            gamePlaying = False
            self.screen.blit(P1WIN, (0, 0))
            pygame.display.update()
        if self.player_2_car.raceEnd():
            gamePlaying = False
            self.screen.blit(P2WIN, (0, 0))
            pygame.display.update()
        
        deltaTime = getDeltaTime()
       
    def _draw(self):
        self.screen.blit(GRASS, (0, 0))
        self.screen.blit(TRACK, (0, 0))
        self.screen.blit(FINISH, FINISH_POS)
        self.screen.blit(WALL, (-25, -25))
      
        self.player_1_car.draw(self.screen)
        self.player_2_car.draw(self.screen)
        pygame.display.update()
