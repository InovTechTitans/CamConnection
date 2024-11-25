import re
from datetime import datetime

from constants.paths import OUTPUT_REALTIME_DETECTED_PLATES
from constants.urls import URL_BACKEND
import cv2
import pytesseract
from flask import Flask, Response

from ler_placa import mandar_placa, salvar_em_csv, validar_placa

# from constants.urls import URL

app = Flask(__name__)


@app.route("/video_feed")
def video_feed():
    def generate():
        cap = cv2.VideoCapture(0)
        placas_detectadas = []
        cascade_placa = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_russian_plate_number.xml"
        )

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (720, 480))

            # Converter para escala de cinza
            cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detectar placas
            placas = cascade_placa.detectMultiScale(
                cinza, scaleFactor=1.1, minNeighbors=4, minSize=(100, 30)
            )

            for x, y, w, h in placas:
                # Desenhar um retângulo ao redor da placa
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Recortar a área da placa
                roi = frame[y : y + h, x : x + w]

                # Reconhecer texto na placa com OCR
                texto_placa = pytesseract.image_to_string(roi, config="--psm 7")
                texto_placa = texto_placa.strip().replace("\n", "").upper()

                # Validar e salvar a placa
                if validar_placa(texto_placa):
                    tipo = (
                        "Mercosul"
                        if re.match(r"[A-Z]{3}[0-9][A-Z][0-9]{2}", texto_placa)
                        else "Antigo"
                    )
                    datahora = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    placas_detectadas.append((texto_placa, tipo, datahora))
                    print(f"Placa detectada: {texto_placa} ({tipo}) {datahora}")
                    # Salvar os resultados em um CSV
                    salvar_em_csv(placas_detectadas, OUTPUT_REALTIME_DETECTED_PLATES)
                    url = URL_BACKEND  # Substitua pela URL da API
                    data = {
                        "placa": texto_placa,
                    }
                    headers = {
                        # "Authorization": "Bearer seu_token_aqui",  # Se necessário
                        "Content-Type": "application/json"  # Geralmente para APIs REST
                    }
                    mandar_placa(url, data, headers)

            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
