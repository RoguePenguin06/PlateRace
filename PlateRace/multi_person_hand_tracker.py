import cv2
import mediapipe as mp
import numpy as np

class MultiPersonHandTracker:
    def __init__(self, width=400, height=400, min_detection_confidence=0.7, min_tracking_confidence=0.5):
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

    def calculate_wrist_gradient(self, wrist1, wrist2):
        """
        Calculate the gradient between two wrist points
        Returns: gradient (slope) and angle in degrees
        """
        # Extract x and y coordinates
        x1, y1 = wrist1
        x2, y2 = wrist2
        
        # Avoid division by zero
        if x2 - x1 == 0:
            return float('inf'), 90.0
        
        # Calculate gradient (slope)
        gradient = (y2 - y1) / (x2 - x1)
        
        # Calculate angle in degrees
        angle = np.degrees(np.arctan(gradient))
        
        return gradient, angle

    def assign_hands_to_people(self, hand_landmarks):
        """
        Assign detected hands to different people based on spatial proximity
        """
        current_hands = []
        for landmarks in hand_landmarks:
            # Get wrist position
            wrist_x = landmarks.landmark[0].x
            wrist_y = landmarks.landmark[0].y
            current_hands.append((wrist_x, wrist_y))
        
        # If this is the first detection, split hands based on x-coordinate
        if not self.previous_hands:
            if len(current_hands) >= 2:
                # Sort by x-coordinate and group pairs
                sorted_hands = sorted(current_hands, key=lambda x: x[0])
                person1_hands = sorted_hands[:2]
                person2_hands = sorted_hands[2:4]
                self.previous_hands = person1_hands + person2_hands
                return [(0, h) if i < 2 else (1, h) for i, h in enumerate(sorted_hands)]
            
        # For subsequent frames, assign based on proximity to previous positions
        assignments = []
        for hand in current_hands:
            if not self.previous_hands:
                person_id = 0
            else:
                # Assign to closest previous position
                distances = [np.sqrt((hand[0] - prev[0])**2 + (hand[1] - prev[1])**2) 
                           for prev in self.previous_hands]
                closest_idx = np.argmin(distances)
                person_id = 0 if closest_idx < 2 else 1
            assignments.append((person_id, hand))
        
        self.previous_hands = [hand for _, hand in assignments]
        return assignments
    
    
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
    

    def process_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None
        
        frame = cv2.flip(frame, 1)
        frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_RGB)
        
        # Reset current frame's data
        self.person1_gradient = None
        self.person2_gradient = None
        self.person1_wrist_positions = None
        self.person2_wrist_positions = None
        
        if results.multi_hand_landmarks:
            assignments = self.assign_hands_to_people(results.multi_hand_landmarks)
            
            person1_wrists = []
            person2_wrists = []
            
            for (person_id, _), hand_landmarks in zip(assignments, results.multi_hand_landmarks):
                color = self.person1_color if person_id == 0 else self.person2_color
                
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=color, thickness=2)
                )
                
                # Get wrist position in pixel coordinates
                h, w, _ = frame.shape
                wrist_x = int(hand_landmarks.landmark[0].x * w)
                wrist_y = int(hand_landmarks.landmark[0].y * h)
                
                # Store wrist positions by person
                if person_id == 0:
                    person1_wrists.append((wrist_x, wrist_y))
                else:
                    person2_wrists.append((wrist_x, wrist_y))
                
                # Add person label
                cv2.putText(frame, f"Person {person_id + 1}", 
                        (wrist_x-50, wrist_y-50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Calculate and display gradients if both hands are detected for a person
            if len(person1_wrists) == 2:
                gradient, angle = self.calculate_wrist_gradient(person1_wrists[0], person1_wrists[1])
                # Draw line between wrists
                cv2.line(frame, person1_wrists[0], person1_wrists[1], self.person1_color, 2)
                # Display gradient and angle
                mid_x = (person1_wrists[0][0] + person1_wrists[1][0]) // 2
                mid_y = (person1_wrists[0][1] + person1_wrists[1][1]) // 2
                cv2.putText(frame, f"P1 Gradient: {gradient:.2f}", 
                        (mid_x, mid_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.person1_color, 2)
                cv2.putText(frame, f"P1 Angle: {angle:.1f}°", 
                        (mid_x, mid_y + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.person1_color, 2)
                self.person1_gradient = gradient
                self.person1_wrist_positions = person1_wrists
            
            if len(person2_wrists) == 2:
                gradient, angle = self.calculate_wrist_gradient(person2_wrists[0], person2_wrists[1])
                # Draw line between wrists
                cv2.line(frame, person2_wrists[0], person2_wrists[1], self.person2_color, 2)
                # Display gradient and angle
                mid_x = (person2_wrists[0][0] + person2_wrists[1][0]) // 2
                mid_y = (person2_wrists[0][1] + person2_wrists[1][1]) // 2
                cv2.putText(frame, f"P2 Gradient: {gradient:.2f}", 
                        (mid_x, mid_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.person2_color, 2)
                cv2.putText(frame, f"P2 Angle: {angle:.1f}°", 
                        (mid_x, mid_y + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.person2_color, 2)
                self.person2_gradient = gradient
                self.person2_wrist_positions = person2_wrists
        
        # Add gradient information to top of frame
        if self.person1_gradient is not None:
            cv2.putText(frame, f"Person 1 Gradient: {self.person1_gradient:.2f}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.person1_color, 2)
        if self.person2_gradient is not None:
            cv2.putText(frame, f"Person 2 Gradient: {self.person2_gradient:.2f}", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.person2_color, 2)
        
        return frame, self.person1_wrist_positions, self.person2_wrist_positions

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
