from flask import Flask, request, jsonify

import numpy as np
import cv2
#from cv2 import cv
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


# Init hands functionality

server = Flask("hand_tracking")

@server.route("/", methods=['POST'])
def calculate_wireframe():
    hands = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=request.args.get("hands", default=2, type=int),
        min_detection_confidence=0.5)

    #print(hands._output_stream_type_info is not None)
    # Read an image, flip it around y-axis for correct handedness output (see
    # above).
    #print(request.data)
    #with open("/tmp/image.png", "wb") as f:
    #    f.write(request.data)
    
    nparr = np.fromstring(request.data, dtype=np.uint8)
    image = cv2.flip(cv2.imdecode(nparr, cv2.IMREAD_COLOR), 1)
    #image = cv2.flip(cv2.imread("/tmp/image.png"), 1)
    image_proc = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #print(image is not None)
    #print(image_proc is not None)
    # Convert the BGR image to RGB before processing.
    results = hands.process(image_proc)

    # process hand landmarks into something that Flask can use
    #print('handedness:', results.multi_handedness)
    handedness = []
    if results.multi_handedness is not None:
        for hand in results.multi_handedness:
            #print(hand.classification)
            #print(hand.classification[0])
            handedness.append({"score":hand.classification[0].score, "label":hand.classification[0].label})
    # process hand landmarks into something that Flask can use
    landmarks = []
    image_rows, image_cols, _ = image.shape
    if results.multi_hand_landmarks is not None:
        for hand_landmarks in results.multi_hand_landmarks:
            #print(hand_landmarks)
            #print('hand_landmarks:', hand_landmarks)
            jsonable_landmarks = {}
            for idx, landmark in enumerate(hand_landmarks.landmark):
                if landmark.visibility < 0 or landmark.presence < 0:
                    continue
                landmark_px = mp_drawing._normalized_to_pixel_coordinates(landmark.x, landmark.y, image_cols, image_rows)
                if landmark_px:
                    jsonable_landmarks[idx] = {
                        "absolute": {"x":landmark.x, "y": landmark.y},
                        "image": {"x":landmark_px[0], "y": landmark_px[1]}
                    }
            if jsonable_landmarks:
                # make json list instead of janky dict[int -> dict]
                jsonable_landmarks2 = [{}] * len(jsonable_landmarks)
                for x in jsonable_landmarks:
                    jsonable_landmarks2[int(x)] = jsonable_landmarks[x]
                landmarks.append(jsonable_landmarks2)
            #mp_drawing.draw_landmarks(annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    #cv2.imwrite('/tmp/annotated_image' + str(idx) + '.png', cv2.flip(image, 1))
    hands.close()
    return jsonify({"landmarks": landmarks, "handedness": handedness})
