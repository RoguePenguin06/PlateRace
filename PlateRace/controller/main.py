#!/usr/bin/env python3

# https://www.youtube.com/watch?v=RRBXVu5UE-U
# https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker


import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hand = mp_hands.Hands(
    # static_image_mode=False,
    # max_num_hands=2,
    # min_detection_confidence=0.5,
    # min_tracking_confidence=0.5
)


while True:
    success, frame = cap.read()
    if success:
        frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hand.process(frame_RGB)
    
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                    print(hand_landmarks)
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)


        cv2.imshow("Capture Image", frame)
        if cv2.waitKey(1) == ord('q'):
            break


cv2.destroyAllWindows()
