import cv2
from ultralytics import YOLO
from utils import obtener_ip, obtener_ubicacion_ip
import threading
import requests

# Cargar modelo entrenado para detectar plástico y papel
modelo = YOLO('yolov8l.pt')  # Cambia por tu modelo personalizado si lo tienes

alertas = []

def detectar_residuos(frame):
    resultados = modelo(frame)
    nombres = resultados[0].names
    clases_detectadas = [nombres[c.item()] for c in resultados[0].boxes.cls]

    for clase in clases_detectadas:
        if clase in ['bottle', 'papel']:  # asegúrate que así estén nombrados en tu modelo
            ip = obtener_ip()
            if not ip:
                print("❌ No se pudo obtener la IP.")
                continue

            ubicacion = obtener_ubicacion_ip(ip)
            if not ubicacion:
                print("❌ No se pudo obtener la ubicación para la IP:", ip)
                continue

            mensaje = f"Se ha detectado un residuo ({clase})"
            alerta = {
                "mensaje": mensaje,
                "ip": ip,
                "ubicacion": ubicacion
            }
            print(alerta)
            alertas.append(alerta)
            break

    return resultados[0].plot()  # Devuelve imagen con anotaciones para mostrar
def iniciar_detector(camara=0):
    cap = cv2.VideoCapture(camara)

    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detecta y obtén frame anotado
        frame_anotado = detectar_residuos(frame)

    cap.release()
    cv2.destroyAllWindows()

def iniciar_en_hilo():
    hilo = threading.Thread(target=iniciar_detector)
    hilo.daemon = True
    hilo.start()
