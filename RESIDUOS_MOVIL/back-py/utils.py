import requests
import socket

def obtener_ip():
    """
    Obtiene la dirección IP pública del usuario. Si no es posible, retorna la IP local.
    """
    try:
        response = requests.get('https://api64.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            return response.json().get('ip')
    except Exception as e:
        print(f"❌ Error al obtener la IP pública: {e}")
    
    # Si falla, intenta obtener la IP local
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        print(f"❌ Error al obtener la IP local: {e}")
        return None

def obtener_ubicacion_ip(ip):
    """
    Obtiene la geolocalización basada en la dirección IP utilizando el servicio ip-api.
    """
    try:
        if not ip:
            print("❌ IP no válida para obtener la ubicación.")
            return None

        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,lat,lon", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    "ciudad": data.get("city"),
                    "region": data.get("regionName"),
                    "pais": data.get("country"),
                    "latitud": data.get("lat"),
                    "longitud": data.get("lon")
                }
            else:
                print(f"❌ Error en la respuesta de ip-api: {data}")
        else:
            print(f"❌ Error al conectar con ip-api: Código de estado {response.status_code}")
    except Exception as e:
        print(f"❌ Error al obtener la ubicación: {e}")
    
    # Retorna None si no se pudo obtener la ubicación
    return None
