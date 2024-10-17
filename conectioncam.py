import cv2

# URL RTSP da câmera WiFi
rtsp_url = "rtsp://usuário:senha@ip_da_camera:porta/stream"

# Abrindo o stream de vídeo
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Erro ao conectar à câmera.")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao ler o frame.")
            break

        # Exibindo o vídeo
        cv2.imshow("Câmera WiFi", frame)

        # Fechar a janela ao pressionar a tecla 'Esc'
        if cv2.waitKey(1) & 0xFF == ord('Esc'):
            break

# Fechando o stream
cap.release()
cv2.destroyAllWindows()
