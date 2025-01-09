import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, width=600, height=400, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        # Initialize camera settings
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Initialize mediapipe hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Define colors
        self.left_hand_color = (255, 0, 0)  # Blue for left hand
        self.right_hand_color = (0, 0, 255)  # Red for right hand
        self.line_color = (0, 255, 0)  # Green for the line
        
        # Initialize gradient
        self.current_gradient = None
        self.wrist_positions = []
    
    def process_frame(self):
        """
        Process a single frame and return both the frame and gradient
        Returns:
            tuple: (frame, gradient, wrist_positions) or (None, None, None) if no frame
        """
        success, frame = self.cap.read()
        if not success:
            return None, None, None
        
        frame = cv2.flip(frame, 1)
        frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(frame_RGB)
        
        self.wrist_positions = []
        self.current_gradient = None
        
        if result.multi_hand_landmarks:
            self.wrist_positions = self._process_hands(frame, result)
            
        if len(self.wrist_positions) == 2:
            self.current_gradient = self._draw_line_and_gradient(frame, self.wrist_positions)
            
        return frame, self.current_gradient, self.wrist_positions
    
    def _process_hands(self, frame, result):
        wrist_positions = []
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            hand_type = handedness.classification[0].label
            color = self.left_hand_color if hand_type == "Left" else self.right_hand_color
            
            # Draw landmarks
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=color, thickness=2)
            )
            
            # Get wrist position
            h, w, _ = frame.shape
            wrist_x = int(hand_landmarks.landmark[0].x * w)
            wrist_y = int(hand_landmarks.landmark[0].y * h)
            wrist_positions.append((wrist_x, wrist_y, hand_type))
            
            # Display hand type
            cv2.putText(frame, f"{hand_type} Hand", (wrist_x-50, wrist_y+50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                       
        return wrist_positions
    
    def _draw_line_and_gradient(self, frame, wrist_positions):
        # Sort positions so left hand is first
        wrist_positions.sort(key=lambda x: x[2] == "Left", reverse=True)
        
        # Draw line between wrists
        cv2.line(frame, 
                (wrist_positions[0][0], wrist_positions[0][1]),
                (wrist_positions[1][0], wrist_positions[1][1]),
                self.line_color, 2)
        
        # Calculate gradient
        dx = wrist_positions[1][0] - wrist_positions[0][0]
        dy = wrist_positions[1][1] - wrist_positions[0][1]
        
        # Avoid division by zero
        gradient = float('inf') if dx == 0 else dy/dx
        
        # Display gradient
        cv2.putText(frame, f"Gradient: {gradient:.2f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return gradient
    
    def get_current_gradient(self):
        """
        Returns the current gradient between hands
        Returns:
            float or None: Current gradient if both hands are detected, None otherwise
        """
        return self.current_gradient
    
    def get_wrist_positions(self):
        """
        Returns the current wrist positions
        Returns:
            list: List of tuples containing (x, y, hand_type) for each detected hand
        """
        return self.wrist_positions
    
    def release(self):
        """Release camera and destroy windows"""
        self.cap.release()
        cv2.destroyAllWindows()

# Example usage:
if __name__ == "__main__":
    tracker = HandTracker()
    while True:
        frame, gradient, wrist_positions = tracker.process_frame()
        if frame is None:
            break
            
        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) == ord('q'):
            break
    
    tracker.release()
