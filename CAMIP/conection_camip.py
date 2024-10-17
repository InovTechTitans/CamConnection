import cv2
import os

USERNAME = '1'
PASSWORD = '1'
IP = '1'
PORT = '1'

os.environt["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

URL = 'rstp://{}:{}@{}:{}/onvifl'.format{USERNAME, PASSWORD, IP, PORT}
print('Conectado com: ' + URL)

cap = cv2.VideoCapture(URL, cv2.CAP_FFMPEG)

while True:
    ret, frame = cap.read()
    if ret == False:
        print('Sem frame')
        break
    else:


        cv2.imshow('VIDEO', frame)

    if cv2.waitKey(1) & 0xFF == ord ('q'):
        break

cap.release()
cv2.destroyAllWindows()

