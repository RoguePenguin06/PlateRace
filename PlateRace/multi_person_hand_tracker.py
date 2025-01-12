import cv2
import mediapipe as mp
import numpy as np
import math

class MultiPersonHandTracker:
    def __init__(self, width=400, height=150, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Initialize mediapipe hands with max_num_hands=4 (2 hands per person)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            max_num_hands=4  # Allow detection of up to 4 hands
        )
        
        # Define colors for different people
        self.person1_color = (255, 0, 0)  # Blue for person 1
        self.person2_color = (0, 255, 0)  # Green for person 2
        
        self.previous_hands = []  # Store previous hand positions for tracking
        self.debug =True  # Flag to enable/disable debug mode

    def calculate_wrist_gradient(self, hand1, hand2):
        """Calculate gradient between two hands using wrist positions"""
        try:
            # Get wrist landmarks from the hand landmark objects
            if isinstance(hand1, tuple) or isinstance(hand2, tuple):
                return None
                
            wrist1 = hand1.landmark[self.mp_hands.HandLandmark.WRIST]
            wrist2 = hand2.landmark[self.mp_hands.HandLandmark.WRIST]
            
            # Convert to pixel coordinates
            frame_height, frame_width = self.frame.shape[:2]
            x1 = wrist1.x * frame_width
            y1 = wrist1.y * frame_height
            x2 = wrist2.x * frame_width
            y2 = wrist2.y * frame_height
            
            # Calculate gradient, avoiding division by zero
            dx = x2 - x1
            if abs(dx) < 1e-6:  # Avoid division by zero
                return None
                
            gradient = (y2 - y1) / dx
            return gradient
            
        except Exception as e:
            print(f"Error calculating gradient: {str(e)}")
            return None

    def assign_hands_to_people(self, hands):
        """
        Assign hands to people based on their position in the divided camera view
        Left side is for Person 1, Right side is for Person 2
        """
        try:
            MAX_HAND_DISTANCE = 300  # Maximum pixel distance between a person's hands
            
            person1_hands = []
            person2_hands = []
            
            if not hands or len(hands) < 2:
                return [], []
            
            # Get frame dimensions
            frame_height, frame_width = self.frame.shape[:2]
            middle_x = frame_width // 2
            
            # Draw division line for debugging
            if self.debug:
                cv2.line(self.frame, (middle_x, 0), (middle_x, frame_height), (0, 0, 255), 2)
                cv2.putText(self.frame, "Player 1", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(self.frame, "Player 2", (middle_x + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Sort hands into left and right sides
            left_hands = []
            right_hands = []
            
            for hand_landmarks in hands:
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                x = int(wrist.x * frame_width)
                y = int(wrist.y * frame_height)
                
                if x < middle_x:  # Left side - Player 1
                    left_hands.append((x, y, hand_landmarks))
                else:  # Right side - Player 2
                    right_hands.append((x, y, hand_landmarks))
            
            # Process left side (Player 1)
            if len(left_hands) >= 2:
                # Find closest pair of hands on left side
                min_distance = float('inf')
                best_pair = None
                
                for i in range(len(left_hands)):
                    for j in range(i + 1, len(left_hands)):
                        x1, y1, _ = left_hands[i]
                        x2, y2, _ = left_hands[j]
                        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                        
                        if distance < min_distance and distance <= MAX_HAND_DISTANCE:
                            min_distance = distance
                            best_pair = (left_hands[i][2], left_hands[j][2])
                
                if best_pair:
                    person1_hands = list(best_pair)
            
            # Process right side (Player 2)
            if len(right_hands) >= 2:
                # Find closest pair of hands on right side
                min_distance = float('inf')
                best_pair = None
                
                for i in range(len(right_hands)):
                    for j in range(i + 1, len(right_hands)):
                        x1, y1, _ = right_hands[i]
                        x2, y2, _ = right_hands[j]
                        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                        
                        if distance < min_distance and distance <= MAX_HAND_DISTANCE:
                            min_distance = distance
                            best_pair = (right_hands[i][2], right_hands[j][2])
                
                if best_pair:
                    person2_hands = list(best_pair)
            
            return person1_hands, person2_hands
            
        except Exception as e:
            print(f"Error assigning hands: {str(e)}")
            return [], []

    
    
    def get_game_data(self):
        """
        Returns the current gradients and wrist positions for both players
        """
        return {
            'person1': {
                'gradient': self.person1_gradient,
                'wrist_positions': self.person1_wrist_positions
            },
            'person2': {
                'gradient': self.person2_gradient,
                'wrist_positions': self.person2_wrist_positions
            }
        }
    

    # In multi_person_hand_tracker.py
    def process_frame(self):
        try:
            success, self.frame = self.cap.read()
            if not success:
                print("Failed to capture frame")
                return (None, None, None)  # Return tuple of None values

            # Flip the frame horizontally for a later selfie-view display
            self.frame = cv2.flip(self.frame, 1)
            
            # Convert the BGR image to RGB
            image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image)

            # Reset gradients
            person1_gradient = None
            person2_gradient = None

            if results.multi_hand_landmarks:
                # Get hand assignments
                person1_hands, person2_hands = self.assign_hands_to_people(results.multi_hand_landmarks)
                
                # Calculate and draw for person 1
                if person1_hands and len(person1_hands) == 2:
                    for hand in person1_hands:
                        self.mp_drawing.draw_landmarks(
                            self.frame,
                            hand,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
                            self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                        )
                    person1_gradient = self.calculate_wrist_gradient(person1_hands[0], person1_hands[1])

                # Calculate and draw for person 2
                if person2_hands and len(person2_hands) == 2:
                    for hand in person2_hands:
                        self.mp_drawing.draw_landmarks(
                            self.frame,
                            hand,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                        )
                    person2_gradient = self.calculate_wrist_gradient(person2_hands[0], person2_hands[1])

            # Always return a tuple
            return (self.frame, person1_gradient, person2_gradient)
    
        except Exception as e:
            print(f"Error in process_frame: {str(e)}")
            return (None, None, None)


    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

# Example usage:
if __name__ == "__main__":
    tracker = MultiPersonHandTracker()
    while True:
        frame, person1_wrist_positions, person2_wrist_positions = tracker.process_frame()
        if frame is None:
            break
            
        cv2.imshow("Multi-Person Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    tracker.release()
