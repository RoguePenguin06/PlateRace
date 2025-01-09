
import cv2

from hand_tracker import HandTracker


class GameController:
    def __init__(self):
        self.tracker = HandTracker()
        
    def run_game(self):
        while True:
            # Get frame and data from hand tracker
            frame, gradient, wrist_positions = self.tracker.process_frame()
            
            if frame is None:
                break
            
            # Use the gradient and wrist positions in your game logic
            if gradient is not None:
                # Example: Check if hands are level
                if abs(gradient) < 0.1:
                    print("Hands are level!")
                    
                # Example: Check if hands form a diagonal
                if abs(gradient) > 0.8 and abs(gradient) < 1.2:
                    print("Hands form a diagonal!")
            
            # Display the frame
            cv2.imshow("Game Display", frame)
            if cv2.waitKey(1) == ord('q'):
                break
                
        self.tracker.release()

# Run the game
if __name__ == "__main__":
    game = GameController()
    game.run_game()
