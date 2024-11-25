import re
from datetime import datetime

import cv2
import pandas as pd
import pytesseract

from constants.urls import URL
from utils import create_if_not_exist

# Configurar o Tesseract OCR (Linux)
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
# Configurar o Tesseract OCR (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract"


def validar_placa(regex, texto_placa: str) -> bool:
    return bool(re.match(regex, texto_placa))


def verificar_texto(texto_placa):
    regex_placas_mercosul = r'^[A-Z]{3}[0-9]{1}[A-Z]{1}[0-9]{2}$'
    regex_placas_antigas = r'^[A-Z]{3}[\s|-]?[0-9]{4}$'

    if len(texto_placa) == 7:
        if validar_placa(regex_placas_mercosul, texto_placa):
            data = {"placa": [texto_placa], "datahora": [datetime.now().strftime("%d/%m/%Y, %H:%M:%S")]}
            df = pd.DataFrame(data)
            df.to_csv("placas.csv", mode="a", index=False, header=False)
            return
    if len(texto_placa) == 6:
        if validar_placa(regex_placas_antigas, texto_placa):
            data = {"placa": [texto_placa], "datahora": [datetime.now().strftime("%d/%m/%Y, %H:%M:%S")]}
            df = pd.DataFrame(data)
            df.to_csv("placas.csv", mode="a", index=False, header=False)
            return


def process_frame(frame):
    # Convert frame to grayscale for better processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Use Haar cascade for license plate detection
    plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_russian_plate_number.xml")

    # Detect plates
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))

    for (x, y, w, h) in plates:
        # Draw rectangle around the plate
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Crop the detected plate
        plate_region = gray[y:y + h, x:x + w]

        # Apply OCR to the cropped plate region
        text = pytesseract.image_to_string(plate_region, config="--psm 8 --oem 3")

        # Clean up the text
        text = ''.join(filter(str.isalnum, text))

        # Display the detected text on the frame
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        print(f"Texto da Placa: {text.strip()}", )

        verificar_texto(text.upper())

    return frame


if __name__ == "__main__":

    # Abrindo o stream de vídeo
    cap = cv2.VideoCapture(URL)

    if not cap.isOpened():
        print("Erro ao conectar à câmera.")
    else:

        df = pd.DataFrame(columns=['placas', 'datahora'])
        arquivo_placas = "output/placas.csv"
        create_if_not_exist(arquivo_placas)
        df.to_csv(arquivo_placas, index=False)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erro ao ler o frame.")
                break

            frame = cv2.resize(frame, (720, 480))

            processed_frame = process_frame(frame)

            cv2.imshow("License Plate Detection", processed_frame)

            # Fechar a janela ao pressionar a tecla 'Esc'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
