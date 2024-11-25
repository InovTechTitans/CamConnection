import cv2
import pytesseract

from constants.urls import URL

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract"


def process_plate(image):
    config_tesseract = "--tessdata-dir tessdata --psm 6"

    # Converter para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplicar filtro para reduzir ruídos
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Realçar bordas
    edges = cv2.Canny(blurred, 50, 150)

    # Encontrar contornos
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filtrar contornos com base no formato da placa
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:  # A placa geralmente é retangular
            x, y, w, h = cv2.boundingRect(approx)
            plate = image[y: y + h, x: x + w]
            return plate

    return None


cap = cv2.VideoCapture(URL)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Processar o quadro para detectar a placa
    plate_image = process_plate(frame)
    if plate_image is not None:

        frame = cv2.resize(frame, (720, 480))

        # Redimensionar a placa para melhorar a leitura
        plate_image = cv2.resize(
            plate_image, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR
        )

        # Converter para escala de cinza e aplicar limiarização
        plate_gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        _, plate_thresh = cv2.threshold(plate_gray, 127, 255, cv2.THRESH_BINARY)

        # Reconhecimento OCR
        text = pytesseract.image_to_string(
            plate_thresh, config="--psm 8"
        )
        print("Texto da Placa:", text.strip())

        # Mostrar a placa detectada
        cv2.imshow("Placa Detectada", plate_image)

    # Mostrar o vídeo
    cv2.imshow("Webcam", frame)

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
