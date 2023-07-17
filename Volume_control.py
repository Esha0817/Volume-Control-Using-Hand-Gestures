# Step 1: Importing all the modules
import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np


# step 2: accessing the primary camera
cap = cv2.VideoCapture(0)

# Step3: Detecting, initializing, and configuring the hands
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# step4: Accessing the speaker using pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volbar=400
volper=0

# step 5:Finding the volume range between the minimum and maximum volume
volMin, volMax = volume.GetVolumeRange()[:2]

# Step 6: Capturing an image from our camera and converting it to an RGB image
while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    lmList = []
    if results.multi_hand_landmarks:
        for handlandmark in results.multi_hand_landmarks:  # step 8: Creating a for loop to manipulate each hand
            for id, lm in enumerate(handlandmark.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)
            # step 9: Specifying the points of the thumb and middle finger we will use
    if lmList != []:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

            # step 10: Drawing a circle between the tip of the thumb and the tip of the index finger
        cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)

            # step  11: Drawing a line between points 4 and 8
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        length = hypot(x2 - x1, y2 - y1)
        vol = np.interp(length, [15, 220], [volMin, volMax])
        volbar=np.interp(length,[30,350],[400,150])
        volper = np.interp(length, [30, 350], [0, 100])
        print(vol, length)
        volume.SetMasterVolumeLevel(vol, None)

        cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255),4)
        cv2.rectangle(img, (50, int(volbar)), (85, 400), (0, 0, 255), cv2.FILLED)
        cv2.putText(img, f"{int(volper)}%", (10, 40), cv2.FONT_ITALIC, 1, (0, 255, 98), 3)
        cv2.imshow('Image', img)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

