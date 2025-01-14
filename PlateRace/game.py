from pathlib import Path
import pygame
import time
import math
import cv2
import boto3
import os
from io import BytesIO

from utilities import resize_image, blit_rotate_center, getDeltaTime
from multi_person_hand_tracker import MultiPersonHandTracker

angle_D = [0, 0]
direction = 0
deltaTime = 0
gamePlaying = True
quitTimer = 3


def load_image_from_s3(bucket_name, key):
    """Load an image from S3 and convert to pygame surface"""
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION"),
    )

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        image_data = response["Body"].read()
        image_file = BytesIO(image_data)
        return pygame.image.load(image_file)
    except Exception as e:
        print(f"Error loading image {key} from S3: {str(e)}")
        return None


class AssetLoader:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def load_game_assets(self):
        """Load all game assets from S3"""
        assets = {
            "TRACK": "assets/track.png",
            "GRASS": "assets/grass.png",
            "FINISH": "assets/finish.png",
            "WALL": "assets/wall.png",
            "CAR_BLUE": "assets/car_blue.png",
            "CAR_RED": "assets/car_red.png",
            "P1WIN": "assets/p1_win.png",
            "P2WIN": "assets/p2_win.png",
            "ANTI_CHEAT_1": "assets/AntiCheat1.png",
            "ANTI_CHEAT_2": "assets/AntiCheat2.png",
        }

        loaded_assets = {}
        for asset_name, asset_path in assets.items():
            loaded_assets[asset_name] = load_image_from_s3(self.bucket_name, asset_path)
            if loaded_assets[asset_name] is None:
                raise RuntimeError(f"Failed to load {asset_name} from S3")

        return loaded_assets


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
                if (
                    self.checkpoint1 and self.checkpoint2 and self.checkpoint3
                ) or self.PLAYER_NUM == 0:
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
    def __init__(self, max_velocity, player_num, start_pos, car_image, game):
        super().__init__(max_velocity, player_num, start_pos)
        self.img = car_image
        self.game = game  # Store reference to game instance

    def move_player(self, hand_gradient):
        # Only add non-None gradients to history
        if hand_gradient is not None:
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
                if smoothed_gradient > 0.2:  # Tilted right
                    angle_D[self.PLAYER_NUM - 1] -= 5
                elif smoothed_gradient < -0.2:  # Tilted left
                    angle_D[self.PLAYER_NUM - 1] += 5

                # Forward movement based on hand being level
                if abs(smoothed_gradient) < 0.3:
                    self.velocity = min(
                        self.velocity + self.acceleration, self.max_velocity
                    )
                    global direction
                    direction = 1
                else:
                    self.velocity = max(self.velocity - self.deceleration, 0)
            else:
                # No valid gradients, slow down
                self.velocity = max(self.velocity - self.deceleration, 0)

    def move(self, person1_gradient, person2_gradient):
        if self.PLAYER_NUM == 1:
            self.move_player(person1_gradient)
        elif self.PLAYER_NUM == 2:
            self.move_player(person2_gradient)

        if angle_D[self.PLAYER_NUM - 1] < 0:
            angle_D[self.PLAYER_NUM - 1] += 360
        if angle_D[self.PLAYER_NUM - 1] > 360:
            angle_D[self.PLAYER_NUM - 1] -= 360

        self.rotate()
        self.onTrack()

        angle_R = angle_D[self.PLAYER_NUM - 1] * (math.pi / 180)

        if angle_D[self.PLAYER_NUM - 1] <= 90:
            self.H_velocity = -self.velocity * math.sin(angle_R)
            self.V_velocity = -self.velocity * math.cos(angle_R)
        elif angle_D[self.PLAYER_NUM - 1] <= 180:
            self.H_velocity = -self.velocity * math.cos(angle_R - (math.pi / 2))
            self.V_velocity = self.velocity * math.sin(angle_R - (math.pi / 2))
        elif angle_D[self.PLAYER_NUM - 1] <= 270:
            self.H_velocity = self.velocity * math.sin(angle_R - math.pi)
            self.V_velocity = self.velocity * math.cos(angle_R - math.pi)
        elif angle_D[self.PLAYER_NUM - 1] <= 360:
            self.H_velocity = self.velocity * math.cos(angle_R - ((3 * math.pi) / 2))
            self.V_velocity = -self.velocity * math.sin(angle_R - ((3 * math.pi) / 2))

        self.x += self.H_velocity * direction
        self.y += self.V_velocity * direction

        self.bounce_on_wall()
        self.antiCheat()

    def rotate(self):
        self.angle = angle_D[self.PLAYER_NUM - 1]

    def bounce_on_wall(self):
        if self.collide(WALL_MASK, *(-25, -25)):
            self.velocity = -self.velocity * 0.5

    def antiCheat(self):
        if self.collide(self.game.ANTI_CHEAT_1_MASK, *(0, 300)):
            self.checkpoint1 = True
        if self.collide(self.game.ANTI_CHEAT_2_MASK, *(450, 0)):
            self.checkpoint2 = True
        if self.collide(self.game.ANTI_CHEAT_2_MASK, *(450, 430)):
            self.checkpoint3 = True


class PlateRace:
    def __init__(self):
        pygame.init()

        # Load assets from S3
        asset_loader = AssetLoader("your-bucket-name")
        game_assets = asset_loader.load_game_assets()

        # Assign loaded assets to class attributes
        self.TRACK = game_assets["TRACK"]
        self.GRASS = game_assets["GRASS"]
        self.FINISH = game_assets["FINISH"]
        self.WALL = game_assets["WALL"]
        self.CAR_BLUE = game_assets["CAR_BLUE"]
        self.CAR_RED = game_assets["CAR_RED"]
        self.P1WIN = game_assets["P1WIN"]
        self.P2WIN = game_assets["P2WIN"]
        self.ANTI_CHEAT_1 = game_assets["ANTI_CHEAT_1"]
        self.ANTI_CHEAT_2 = game_assets["ANTI_CHEAT_2"]

        # Create masks after loading images
        self.TRACK_MASK = pygame.mask.from_surface(self.TRACK)
        self.FINISH_MASK = pygame.mask.from_surface(self.FINISH)
        self.WALL_MASK = pygame.mask.from_surface(self.WALL)
        self.ANTI_CHEAT_1_MASK = pygame.mask.from_surface(self.ANTI_CHEAT_1)
        self.ANTI_CHEAT_2_MASK = pygame.mask.from_surface(self.ANTI_CHEAT_2)

        self.WIDTH, self.HEIGHT = self.TRACK.get_width(), self.TRACK.get_height()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("PlateRace")
        self.clock = pygame.time.Clock()
        self.hand_tracker = MultiPersonHandTracker()

        # Initialize players with loaded assets
        self.player_1_car = PlayerCar(10, 1, (845, 350), self.CAR_BLUE, self)
        self.player_2_car = PlayerCar(10, 2, (910, 350), self.CAR_RED, self)

    def main_loop(self):
        global gamePlaying, quitTimer, deltaTime

        while True:
            self.clock.tick(60)
            self._handle_input()

            if gamePlaying:
                try:
                    # Get hand tracking data
                    result = self.hand_tracker.process_frame()
                    if result is None:
                        continue

                    player_frame, person1_gradient, person2_gradient = result

                    # Update game state if we have a valid frame
                    if player_frame is not None:
                        cv2.imshow("Multi-Person Hand Tracking", player_frame)
                        self._game_logic(person1_gradient, person2_gradient)
                        self._draw()

                except Exception as e:
                    print(f"Error in main loop: {str(e)}")
                    continue

            else:
                quitTimer -= getDeltaTime()
                if quitTimer <= 0:
                    if hasattr(self.hand_tracker, "release"):
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


if __name__ == "__main__":
    game = PlateRace()
    game.main_loop()
