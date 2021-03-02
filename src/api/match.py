#!/usr/bin/python3
import json
import math

# naive implementation (no adjustment for rotation and perspective)
known_hands_NAIVE = {}

print("Loading hands for NAIVE matching algorithm")
with open("hands.json", "r") as j:
    known_hands_NAIVE = json.load(j)
print("Found", len(known_hands_NAIVE), "hand wireframes (NAIVE)")

def naive(sign_data, req=None):
    matches = list()
    for sign_hand in sign_data["landmarks"]:
        #print(sign_hand)
        data_matches = list()
        for known_hand_key in known_hands_NAIVE:
            known_hand = known_hands_NAIVE[known_hand_key]
            big_dif = absolute_difference(known_hand, sign_hand)
            data_matches.append({"sign":known_hand_key, "score":1/big_dif})
        data_matches.sort(key= lambda x: 1/x["score"]) # sort by match confidence
        matches.append(data_matches)
    return {"signs": matches}

# slightly better implementation with support L/R discrimination (still no rotation)
known_hands_NEW = {}

print("Loading hands for NAIVE matching algorithm")
with open("hands2.json", "r") as j:
    known_hands_NEW = json.load(j)
print("Found", len(known_hands_NEW), "hand wireframes (NEW)")

def new_format(sign_data, req):
    matches = list()
    index = 0
    for sign_hand in sign_data["landmarks"]:
        is_right = sign_data["handedness"][index]["label"].lower() == "right"
        #print(sign_hand)
        data_matches = list()
        for sign_key in known_hands_NEW:
            #print(sign_key)
            known_sign = known_hands_NEW[sign_key] # contains matching data like strategy
            big_dif = match_using_strategy(known_sign, sign_hand, is_right)
            if big_dif is not None:
                data_matches.append({"sign":sign_key, "score":1/big_dif})
        data_matches.sort(key= lambda x: 1/x["score"]) # sort by match confidence
        matches.append(data_matches)
        index += 1
    return {"signs": matches}

# common utility functions

def absolute_difference(a, b):
    # adjustment factors for hand sign a
    a_x_arr = [x["absolute"]["x"] for x in a]
    a_y_arr = [x["absolute"]["y"] for x in a]
    a_base_x = min(a_x_arr)
    a_base_y = min(a_y_arr)
    a_scale_x = max(a_x_arr) - a_base_x
    a_scale_y = max(a_y_arr) - a_base_y
    # hand sign b
    b_x_arr = [x["absolute"]["x"] for x in b]
    b_y_arr = [x["absolute"]["y"] for x in b]
    b_base_x = min(b_x_arr)
    b_base_y = min(b_y_arr)
    b_scale_x = max(b_x_arr) - b_base_x
    b_scale_y = max(b_y_arr) - b_base_y
    # calculate difference
    i = 0
    misses = 0
    differences = list()
    while len(a) > i and len(b) > i:
        if 0 > a[i]["absolute"]["y"] or 0 > a[i]["absolute"]["x"]:
            misses += 1
            i += 1
            continue
        x_dif = ((b[i]["absolute"]["x"] - b_base_x) / b_scale_x)\
            - ((a[i]["absolute"]["x"] - a_base_x) / a_scale_x)
        y_dif = ((b[i]["absolute"]["y"] - b_base_y) / b_scale_y)\
            - ((a[i]["absolute"]["y"] - a_base_y) / a_scale_y)
        differences.append(math.sqrt(x_dif**2 + y_dif**2))
        i += 1
    return sum(differences) / (i + 1 - misses)

def match_using_strategy(known_sign, hand, is_right):
    hands_to_check = known_sign["landmarks_L"] # left hand best hand (and default hand)
    if is_right:
        hands_to_check = known_sign["landmarks_R"]
    if known_sign["match"] == "ANY":
        differences = list()
        for known_hand in hands_to_check:
            if len(known_hand) != 0:
                differences.append(absolute_difference(known_hand, hand))
        if len(differences) == 0:
            return None
        return min(differences)


algorithms = {
    "naive": naive,
    "boogaloo": new_format
}