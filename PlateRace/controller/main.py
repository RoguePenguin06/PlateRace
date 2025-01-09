import cv2
import mediapipe as mp
import numpy as np
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Variables to track hand position and time
last_position = None
last_time = time.time()
movement_vector = np.zeros(2)  # Changed to 2D (x,y only)

def get_hand_position(hand_landmarks):
    # Get only X and Y of the wrist point (point 0)
    return np.array([
        hand_landmarks.landmark[0].x,
        hand_landmarks.landmark[0].y
    ])

def calculate_movement(current_pos, last_pos):
    if last_pos is None:
        return np.zeros(2)
    return current_pos - last_pos

while True:
    success, frame = cap.read()
    if success:
        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)
        
        frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_RGB)
        
        current_time = time.time()
    
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw landmarks
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Get current hand position (x,y only)
                current_position = get_hand_position(hand_landmarks)
                
                # Calculate movement vector every 0.5 seconds
                if current_time - last_time >= 0.5:
                    movement_vector = calculate_movement(current_position, last_position)
                    last_position = current_position.copy()
                    last_time = current_time
                
                # Display the movement vector components
                cv2.putText(frame, f"X Movement: {movement_vector[0]:.4f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(frame, f"Y Movement: {movement_vector[1]:.4f}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

                # Draw arrow to visualize movement
                frame_height, frame_width = frame.shape[:2]
                center_x = int(frame_width/2)
                center_y = int(frame_height/2)
                
                # Scale the movement vector for visualization
                scale = 500  # Adjust this value to make the arrow more/less visible
                end_x = center_x + int(movement_vector[0] * scale)
                end_y = center_y + int(movement_vector[1] * scale)
                
                # Draw arrow
                cv2.arrowedLine(frame, (center_x, center_y), (end_x, end_y), 
                               (0, 255, 0), 2)

        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
