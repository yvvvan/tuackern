import cv2
import time
cap = cv2.VideoCapture(0)
# time.sleep(10)
# Capture frame
ret, frame = cap.read()
if ret:
    cv2.imwrite('image.jpg', frame)
    print("saved")
else:
    print("error")

cap.release()