import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt
import time

# MQTT Configuration
MQTT_BROKER = "localhost"  # Replace with your ESP32 IP or broker IP
MQTT_PORT = 1883
MQTT_TOPIC = "gesture/control"
PUBLISH_INTERVAL = 0.2  # seconds

# Initialize MQTT
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# Initialize MediaPipe Hand module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Open the camera (0 for default)
cap = cv2.VideoCapture(0)

# Finger tips
finger_tips_ids = [4, 8, 12, 16, 20]

# Helper to track last published time
# ~ last_publish_time = time.time()
last_sent_command = "None"


def get_finger_states(hand_landmarks, hand_label):
    fingers = []

    # Thumb logic changes based on handedness
    if hand_label == "Right":
        fingers.append(1 if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x else 0)
    else:  # Left hand
        fingers.append(1 if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x else 0)

    for tip_id in finger_tips_ids[1:]:
        fingers.append(1 if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y else 0)

    return fingers


while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    # --- NEW LOGIC START ---
    
    # By default, the command is "STOP". This will be sent if no recognized gestures are found.
    command_to_send = "STOP"
    display_gesture = ""
    action_found = False # This is a flag to prioritize the Left Hand

    if results.multi_hand_landmarks and results.multi_handedness:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            hand_label = results.multi_handedness[i].classification[0].label  # 'Left' or 'Right'
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            finger_states = get_finger_states(hand_landmarks, hand_label)

            # --- 1. CHECK FOR LEFT HAND (ACTIONS) ---
            # We check the Left hand first, as actions take priority.
            if hand_label == "Left":
                if finger_states == [1, 1, 1, 1, 1]:      # Left Hand: Full Palm
                    command_to_send = "HANDSHAKE"
                    action_found = True
                elif finger_states == [0, 1, 1, 0, 0]:    # Left Hand: Peace Sign
                    command_to_send = "JUMP"
                    action_found = True
                elif finger_states == [0, 0, 0, 0, 0]:    # Left Hand: Fist
                    command_to_send = "STAYLOW"
                    action_found = True
                elif finger_states == [0, 1, 1, 1, 1]:    # Left Hand: Four Fingers (our old Steady)
                    command_to_send = "STEADY"
                    action_found = True
                
                if action_found:
                    display_gesture = command_to_send # We want to display the action

            # --- 2. CHECK FOR RIGHT HAND (MOVEMENT) ---
            # Only check the right hand if an action gesture hasn'T already been detected
            elif hand_label == "Right" and not action_found:
                if finger_states == [0, 1, 1, 0, 0]:
                    command_to_send = "LEFT"
                elif finger_states == [0, 1, 0, 0, 0]:
                    command_to_send = "RIGHT"
                elif finger_states == [1, 1, 1, 1, 1]:
                    command_to_send = "FORWARD"
                elif finger_states == [0, 0, 0, 0, 0]:
                    command_to_send = "REVERSE"
                elif finger_states == [0, 1, 1, 1, 1]:    # Left Hand: Four Fingers (our old Steady)
                    command_to_send = "STOP"
                    action_found = True
                
                if command_to_send != "STOP":
                    display_gesture = command_to_send # Display the movement


    # --- STATE-CHANGE PUBLISH LOGIC ---
    # Only publish if the command has changed from the last loop
    if command_to_send != last_sent_command:
        client.publish(MQTT_TOPIC, command_to_send)
        print(f"STATE CHANGE! Publishing new command: {command_to_send}")
        last_sent_command = command_to_send

    # Display the active gesture on screen
    if display_gesture:
        cv2.putText(image, f"Gesture: {display_gesture}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    cv2.imshow("Gesture-Based Direction", image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- END OF LOOP ---

cap.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
