import cv2
from flask import Flask, Response

from ler_placa2 import process_frame
from constants.urls import URL

app = Flask(__name__)


@app.route("/video_feed")
def video_feed():
    def generate():
        cap = cv2.VideoCapture(URL)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (720, 480))

            processed_frame = process_frame(frame)

            ret, buffer = cv2.imencode(".jpg", processed_frame)
            frame = buffer.tobytes()

            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
