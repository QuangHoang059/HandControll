import cv2
from cvzone.HandTrackingModule import HandDetector
import os
import numpy as np
import win32api
import win32con


def click(x, y, options=0):
    if options == 1:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        return
    if options == 2:
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 10, 0)
        return
    if options == 3:
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -10, 0)
        return
    if options == 4:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
        return
    win32api.SetCursorPos((x, y))


indexfinger = []


def apply_low_pass_filter(coordinates, alpha=0.5):
    global indexfinger
    if len(indexfinger) == 0:
        indexfinger = coordinates
    else:
        indexfinger = alpha * coordinates + (1 - alpha) * indexfinger
        indexfinger = np.array([round(indexfinger[0]), round(indexfinger[1])])


cap = cv2.VideoCapture(0)
WIDTH = 1366
HEIGHT = 768
cap.set(3, 1300)
cap.set(4, 600)

detection = HandDetector(detectionCon=0.5, maxHands=1)
annotationstart = False
while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    hands, frame = detection.findHands(frame)
    if hands:
        hand = hands[0]
        fingers = detection.fingersUp(hand)
        cx, cy = hand["center"]
        lmlist = hand["lmList"]
        # regions
        xval = round(np.interp(lmlist[8][0], [
            WIDTH//3, WIDTH-300], [0, WIDTH+200]))
        yval = round(np.interp(lmlist[8][1], [
                     190, HEIGHT-240], [0, HEIGHT+100]))
        coordinates = np.array([xval, yval])
        apply_low_pass_filter(coordinates, 0.65)
        if fingers == [0, 1, 1, 0, 0]:
            click(indexfinger[0], indexfinger[1])
            annotationstart = False
        if annotationstart == False:
            if fingers == [0, 1, 0, 0, 0]:
                click(indexfinger[0], indexfinger[1], 1)
                annotationstart = True
            elif fingers == [1, 0, 0, 0, 0]:
                click(indexfinger[0], indexfinger[1], 2)
                # annotationstart = True
            elif fingers == [0, 0, 0, 0, 1]:
                click(indexfinger[0], indexfinger[1], 3)
                # annotationstart = True
            elif fingers == [0, 1, 1, 1, 0]:
                click(indexfinger[0], indexfinger[1], 4)
                annotationstart = True
            else:
                annotationstart = False
    else:
        annotationstart = False
    cv2.imshow('frame', frame)
    # couter delay button
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
