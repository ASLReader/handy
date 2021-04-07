import os
import firebase_admin
from firebase_admin import db
import json

print("Loading hands from FIREBASE")
cred = firebase_admin.credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
default_app = firebase_admin.initialize_app(None, {'databaseURL': 'https://handy-94ecc-default-rtdb.firebaseio.com/'})
print("Firebase App Name:", default_app.name)
hands = db.reference('/').order_by_key().get()
known_hands_FIREBASE = {}
for key, val in hands.items():
    known_hands_FIREBASE[key] = val
print("Found", len(known_hands_FIREBASE), "hand wireframes (FIRE)")
'''
with open("hands_firebase.json", "w") as f:
    json.dump(known_hands_FIREBASE, f, indent=2)
'''