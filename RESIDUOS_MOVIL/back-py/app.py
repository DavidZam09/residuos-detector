from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from detector import alertas, iniciar_en_hilo, detener_detector, detectar_residuos
import cv2

app = Flask(__name__)

# Habilitar CORS para todas las rutas
CORS(app)

# Variable global para el acceso a la cámara
camera = None

@app.route('/')
def index():
    return "✅ API funcionando - Detección de residuos en tiempo real"

@app.route('/alertas', methods=['GET'])
def obtener_alertas():
    try:
        if not alertas:
            return jsonify({
                "success": False,
                "message": "No hay alertas disponibles en este momento."
            }), 404

        return jsonify({
            "success": True,
            "data": alertas
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Ocurrió un error al obtener las alertas.",
            "error": str(e)
        }), 500

@app.route('/start-camera', methods=['POST'])
def start_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return jsonify({"success": False, "message": "No se pudo abrir la cámara"}), 500
        print("✅ Cámara iniciada correctamente.")
        return jsonify({"success": True, "message": "Cámara iniciada correctamente"}), 200
    else:
        return jsonify({"success": True, "message": "La cámara ya está activa"}), 200

@app.route('/stop-camera', methods=['POST'])
def stop_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None
        print("🛑 Cámara detenida correctamente.")
        return jsonify({"success": True, "message": "Cámara detenida correctamente"}), 200
    else:
        return jsonify({"success": False, "message": "La cámara no está activa"}), 400

@app.route('/stream', methods=['GET'])
def stream_video():
    def generate_frames():
        global camera
        if camera is None:
            return
        while True:
            success, frame = camera.read()
            if not success:
                break

            # Procesar el frame para detección de residuos
            frame_procesado = detectar_residuos(frame)

            # Codificar el frame procesado como JPEG
            _, buffer = cv2.imencode('.jpg', frame_procesado)
            frame_bytes = buffer.tobytes()

            # Enviar el frame al cliente
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("🚀 Iniciando sistema de detección de residuos...")
    try:
        # Inicia el servidor Flask
        app.run(host="0.0.0.0", port=9000)
    except KeyboardInterrupt:
        print("🛑 Deteniendo el servidor...")
        detener_detector()
        if camera is not None:
            camera.release()
        print("✅ Cámara liberada y servidor detenido.")
