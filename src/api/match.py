#!/usr/bin/python3
import json
import math

# naive implementation (no adjustment for rotation and perspective)
known_hands_NAIVE = {}

print("Loading hands for NAIVE matching algorithm")
with open("hands.json", "r") as j:
    known_hands_NAIVE = json.load(j)
print("Found", len(known_hands_NAIVE), "hand wireframes")

def naive(sign_data, req):
    matches = list()
    for sign_hand in sign_data["landmarks"]:
        #print(sign_hand)
        sign_x_arr = [x["absolute"]["x"] for x in sign_hand]
        sign_y_arr = [x["absolute"]["y"] for x in sign_hand]
        sign_hand_base_x = min(sign_x_arr)
        sign_hand_base_y = min(sign_y_arr)
        sign_hand_scale_x = max(sign_x_arr) - sign_hand_base_x
        sign_hand_scale_y = max(sign_y_arr) - sign_hand_base_y
        data_matches = list()
        for known_hand_key in known_hands_NAIVE:
            known_hand = known_hands_NAIVE[known_hand_key]
            known_x_arr = [x["absolute"]["x"] for x in known_hand]
            known_y_arr = [x["absolute"]["y"] for x in known_hand]
            known_hand_base_x = min(known_x_arr)
            known_hand_base_y = min(known_y_arr)
            known_hand_scale_x = max(known_x_arr) - known_hand_base_x
            known_hand_scale_y = max(known_y_arr) - known_hand_base_y
            i = 0
            differences = list()
            while len(known_hand) > i and len(sign_hand) > i:
                x_dif = ((sign_hand[i]["absolute"]["x"] - sign_hand_base_x) / sign_hand_scale_x)\
                    - ((known_hand[i]["absolute"]["x"] - known_hand_base_x) / known_hand_scale_x)
                y_dif = ((sign_hand[i]["absolute"]["y"] - sign_hand_base_y) / sign_hand_scale_y)\
                    - ((known_hand[i]["absolute"]["y"] - known_hand_base_y) / known_hand_scale_y)
                differences.append(math.sqrt(x_dif**2 + y_dif**2))
                i += 1
            big_dif = sum(differences) / len(differences)
            data_matches.append({"sign":known_hand_key, "score":1/big_dif})
        data_matches.sort(key= lambda x: 1/x["score"]) # sort by match confidence
        matches.append(data_matches)
    return {"signs": matches}

algorithms = {
    "naive": naive
}