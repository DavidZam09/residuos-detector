import cv2
from ultralytics import YOLO
from utils import obtener_ip, obtener_ubicacion_ip
import threading
import requests

# Cargar modelo entrenado para detectar plástico y papel
modelo = YOLO('yolov8l.pt')  # Cambia por tu modelo personalizado si lo tienes

alertas = []
detector_activo = True  # Variable global para controlar el bucle del detector

def detectar_residuos(frame):
    try:
        resultados = modelo(frame)
        nombres = resultados[0].names
        clases_detectadas = [nombres[c.item()] for c in resultados[0].boxes.cls]

        for clase in clases_detectadas:
            if clase in ['bottle', 'paper']:  # Asegúrate que así estén nombrados en tu modelo
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
                if len(alertas) >= 10:  # Limitar el número de alertas almacenadas
                    alertas.pop(0)
                alertas.append(alerta)
                break

        return resultados[0].plot()  # Devuelve imagen con anotaciones para mostrar
    except Exception as e:
        print(f"❌ Error al procesar el frame: {e}")
        return frame  # Devuelve el frame original en caso de error

def iniciar_detector(camara=0):
    global detector_activo
    cap = cv2.VideoCapture(camara)

    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        return

    print("✅ Cámara abierta correctamente. Iniciando detección...")
    while detector_activo:
        ret, frame = cap.read()
        if not ret:
            print("❌ No se pudo leer el frame de la cámara.")
            break

        # Detecta y obtén frame anotado
        frame_anotado = detectar_residuos(frame)

        # Opcional: Mostrar el frame en una ventana (para pruebas locales)
        cv2.imshow("Detección de Residuos", frame_anotado)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Presiona 'q' para salir
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🛑 Detección detenida. Cámara liberada.")

def iniciar_en_hilo(camara=0):
    hilo = threading.Thread(target=iniciar_detector, args=(camara,))
    hilo.daemon = True
    hilo.start()
    print("🔍 Detector iniciado en un hilo separado.")

def detener_detector():
    global detector_activo
    detector_activo = False
    print("🛑 Solicitando detener el detector...")
