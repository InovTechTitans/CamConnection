import os

import cv2

from constants import URL

os.environt["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

camera_url = URL.format(type="onvifl")

print("Conectado com: " + camera_url)

cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Sem frame")
        break
    else:
        cv2.imshow("VIDEO", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
