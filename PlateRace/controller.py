# controller.py
import cv2
from multi_person_hand_tracker import MultiPersonHandTracker

class GameController:
    def __init__(self):
        self.tracker = MultiPersonHandTracker()
        
    def run_game(self):
        while True:
            # Get frame from hand tracker
            frame, _, _ = self.tracker.process_frame()
            
            if frame is None:
                break
            
            # Get the game data (gradients and wrist positions)
            game_data = self.tracker.get_game_data()
            
            # Example game logic using the gradients
            if game_data['person1']['gradient'] is not None:
                if abs(game_data['person1']['gradient']) < 0.1:
                    cv2.putText(frame, "Player 1: Hands are level!", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                              1, (255, 0, 0), 2)
                    
            if game_data['person2']['gradient'] is not None:
                if abs(game_data['person2']['gradient']) < 0.1:
                    cv2.putText(frame, "Player 2: Hands are level!", 
                              (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                              1, (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow("Game Display", frame)
            if cv2.waitKey(1) == ord('q'):
                break
                
        self.tracker.release()

# Run the game
if __name__ == "__main__":
    game = GameController()
    game.run_game()
