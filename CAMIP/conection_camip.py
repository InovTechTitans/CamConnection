import os

import cv2

os.environt["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

URL = "rstp://{}:{}@{}:{}/onvifl".format(
    os.getenv("USERNAME"),
    os.getenv("PASSWORD"),
    os.getenv("IP"),
    os.getenv("PORT"),
)
print("Conectado com: " + URL)

cap = cv2.VideoCapture(URL, cv2.CAP_FFMPEG)

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
