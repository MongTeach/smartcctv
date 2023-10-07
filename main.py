import cv2
from cvzone.PoseModule import PoseDetector
import pyglet.media
import threading
import os
import requests
import uuid
import time

cap = cv2.VideoCapture(0) #webcam
ws, hs = 640, 640
cap.set(3, ws)
cap.set(4, hs)

if not cap.isOpened():
    print("Camera can't open!!!")
    exit()

detector = PoseDetector()
sound = pyglet.media.load("alarm.wav", streaming=False)
people = {}  # Dictionary to store UUIDs and their last detected time
img_count, breakcount = 0, 0

from datetime import datetime

def sendTelegram(uuid):
    path = 'img/'  # Replace your path directory
    url = 'https://api.telegram.org/bot'
    token = "6225436246:AAH6QBagO-tl6vopT6zhVl_FMnYUKwHRIwg"  # Replace Your Token Bot
    chat_id = "1382980362"  # Replace Your Chat ID
    caption = f"People Detected (UUID: {uuid}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}!!! "
    img_name = f'image_{img_count}.png'
    
    cv2.imwrite(os.path.join(path, img_name), img)
    files = {'photo': open(path + img_name, 'rb')}
    resp = requests.post(url + token + '/sendPhoto?chat_id=' + chat_id + '&caption=' + caption, files=files)
    print(f'Response Code: {resp.status_code}')

while True:
    success, img = cap.read()
    img = detector.findPose(img, draw=False)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    img_name = f'image_{img_count}.png'

    soundThread = threading.Thread(target=sound.play, args=())
    
    if bboxInfo:
        cv2.rectangle(img, (120, 20), (470, 80), (0, 0, 255), cv2.FILLED)
        cv2.putText(img, "PEOPLE DETECTED!!!", (130, 60),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        breakcount += 1

        if breakcount >= 30:
            if not people:
                img_count += 1
                uuid_str = str(uuid.uuid4())
                people[uuid_str] = time.time()
                teleThread = threading.Thread(target=sendTelegram, args=(uuid_str,))
                soundThread.start()
                teleThread.start()
    else:
        breakcount = 0

    # Check if any UUIDs should be removed (if 5 minutes have passed)
    current_time = time.time()
    expired_uuids = [uuid_key for uuid_key, timestamp in people.items() if current_time - timestamp >= 300]
    for uuid_key in expired_uuids:
        del people[uuid_key]

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cv2.destroyAllWindows()

