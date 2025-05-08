from flask import Flask, jsonify
from flask_cors import CORS
from detector import alertas, iniciar_en_hilo
import threading

app = Flask(__name__)

# Habilitar CORS para todas las rutas
CORS(app)

@app.route('/')
def index():
    return "✅ API funcionando - Detección de residuos en tiempo real"

@app.route('/alertas', methods=['GET'])
def obtener_alertas():
    try:
        # Verifica si las alertas están disponibles
        if not alertas:
            return jsonify({
                "success": False,
                "message": "No hay alertas disponibles en este momento."
            }), 404

        # Devuelve las alertas si están disponibles
        return jsonify({
            "success": True,
            "data": alertas
        }), 200
    except Exception as e:
        # Manejo de errores inesperados
        return jsonify({
            "success": False,
            "message": "Ocurrió un error al obtener las alertas.",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando sistema de detección de residuos...")
    
    # Inicia la cámara y el detector en un hilo
    iniciar_en_hilo()

    # Inicia el servidor Flask
    app.run(host="0.0.0.0", port=9000)
