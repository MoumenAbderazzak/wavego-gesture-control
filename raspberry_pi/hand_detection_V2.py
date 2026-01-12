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

    direction = ""

    if results.multi_hand_landmarks and results.multi_handedness:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            hand_label = results.multi_handedness[i].classification[0].label  # 'Left' or 'Right'
            
            # Only process when hand is "Right"
            
            if hand_label == "Right": 
                
                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                finger_states = get_finger_states(hand_landmarks, hand_label)

                # Map finger states to gestures
                if finger_states == [0, 1, 1, 0, 0]:
                    direction = "LEFT"
                elif finger_states == [0, 1, 0, 0, 0]:
                    direction = "RIGHT"
                elif finger_states == [1, 1, 1, 1, 1]:
                    direction = "FORWARD"
                elif finger_states == [0, 0, 0, 0, 0]:
                    direction = "REVERSE"
                elif finger_states == [0, 1, 1, 1, 1]:
                    direction = "STOP"

    # Decide what to display and publish
    # ~ mqtt_direction = direction if direction else "STEADY"
    display_direction = direction  # Only show real gestures

    # ~ # Periodic MQTT publish
    # ~ current_time = time.time()
    # ~ if current_time - last_publish_time >= PUBLISH_INTERVAL:
        # ~ mqtt_direction = direction if direction else "STOP"
        # ~ display_direction = direction  # Only display real gestures

        # ~ # Always publish current direction
        # ~ # client.publish(MQTT_TOPIC, mqtt_direction)
        # ~ # print(f"Published: {mqtt_direction}")
        # ~ # last_direction = mqtt_direction
        # ~ # last_publish_time = current_time
        
        # Check if direction changed
        
    current_command = direction if direction else "STEADY"
        
    if current_command != last_sent_command:
        client.publish(MQTT_TOPIC, current_command)
        print(f"Published: {current_command}")
        last_sent_command = current_command
        

    # Display only real gestures
    if display_direction:
        cv2.putText(image, f"Gesture: {display_direction}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    cv2.imshow("Gesture-Based Direction", image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
