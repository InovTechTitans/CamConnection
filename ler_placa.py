import csv
import re
from datetime import datetime
from typing import Dict

import cv2
import pytesseract
import requests

from constants.paths import OUTPUT_REALTIME_DETECTED_PLATES
from constants.urls import URL_BACKEND

# Configurar o pytesseract (ajuste o caminho para sua instalação do Tesseract, se necessário)
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
)


# Função para validar placas de carro com regex
def validar_placa(texto):
    padrao_antigo = r"[A-Z]{3}[\s|-]?[0-9]{4}"  # Padrão antigo (ABC1234)
    padrao_mercosul = r"[A-Z]{3}[0-9][A-Z][0-9]{2}"  # Padrão Mercosul (ABC1D23)

    if re.match(padrao_antigo, texto) or re.match(padrao_mercosul, texto):
        return True


# Função para salvar resultados em CSV
def salvar_em_csv(placas, nome_arquivo):
    with open(nome_arquivo, mode="a", newline="", encoding="utf-8") as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv)
        escritor_csv.writerow(["Placa", "Tipo", "DataHora"])

        for placa, tipo, datahora in placas:
            placa = placa.replace("|", "").replace(" ", "").strip()
            escritor_csv.writerow([placa, tipo, datahora])


def mandar_placa(url: str, data: Dict, headers: Dict) -> requests.Response:
    """
    Envia um POST para uma API.

    :param url: URL da API.
    :param dados: Dados a serem enviados (dict).
    :param cabecalhos: Headers opcionais (dict).
    :return: Resposta da API.
    """
    try:
        # Envia o POST
        resposta = requests.post(url, json=data, headers=headers)

        # Verifica o código de status
        if resposta.status_code == 200:
            print("Sucesso:", resposta.json())
        else:
            print(f"Erro {resposta.status_code}: {resposta.text}")

        return resposta
    except requests.RequestException as e:
        print(f"Erro ao enviar a requisição: {e}")


# Configuração da câmera
def detectar_placas_da_camera():
    # Carregar modelo Haar Cascade (substitua por YOLO, se necessário)
    cascade_placa = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_russian_plate_number.xml"
    )

    # Iniciar captura de vídeo
    camera = cv2.VideoCapture(0)
    placas_detectadas = []

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Erro ao acessar a câmera.")
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

        # Parar com a tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        # Mostrar o vídeo em tempo real
        cv2.imshow("Deteccao de Placas", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


# Iniciar o programa
if __name__ == "__main__":
    detectar_placas_da_camera()
