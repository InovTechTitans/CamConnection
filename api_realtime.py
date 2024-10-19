import cv2
from flask import Flask, Response

from constants import URL

app = Flask(__name__)

# URL RTSP da câmera WiFi
rtsp_url = URL.format(type="stream")


@app.route("/video_feed")
def video_feed():
    def generate():
        cap = cv2.VideoCapture(rtsp_url)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convertendo o video para JPEG
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

            # Enviando o video como uma resposta HTTP multipart
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
