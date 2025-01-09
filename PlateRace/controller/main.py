import cv2
import mediapipe as mp
import numpy as np
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

left_hand_color = (255, 0, 0)  # Blue for left hand
right_hand_color = (0, 0, 255)  # Red for right hand

while True:
    success, frame = cap.read()
    if success:
        frame = cv2.flip(frame, 1)
        frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_RGB)
        
        # Store wrist positions
        wrist_positions = []
        
        if result.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                hand_type = handedness.classification[0].label
                color = left_hand_color if hand_type == "Left" else right_hand_color
                
                # Draw landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=color, thickness=2)
                )
                
                # Get wrist position
                h, w, _ = frame.shape
                wrist_x = int(hand_landmarks.landmark[0].x * w)
                wrist_y = int(hand_landmarks.landmark[0].y * h)
                wrist_positions.append((wrist_x, wrist_y, hand_type))
                
                # Display hand type
                cv2.putText(frame, f"{hand_type} Hand", (wrist_x-50, wrist_y-20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # If we detect both hands, draw line and calculate gradient
        if len(wrist_positions) == 2:
            # Sort positions so left hand is first
            wrist_positions.sort(key=lambda x: x[2] == "Left", reverse=True)
            
            # Draw line between wrists
            cv2.line(frame, 
                    (wrist_positions[0][0], wrist_positions[0][1]),
                    (wrist_positions[1][0], wrist_positions[1][1]),
                    (0, 255, 0), 2)  # Green line
            
            # Calculate gradient
            dx = wrist_positions[1][0] - wrist_positions[0][0]
            dy = wrist_positions[1][1] - wrist_positions[0][1]
            
            # Avoid division by zero
            if dx != 0:
                gradient = dy/dx
            else:
                gradient = float('inf')
            
            # Display gradient
            cv2.putText(frame, f"Gradient: {gradient:.2f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
