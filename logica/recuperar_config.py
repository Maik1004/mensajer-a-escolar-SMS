import json
from datetime import datetime

ARCHIVO_CONFIG = "config_mensajes.json"


def guardar_configuracion(grado, salon, fecha_programada):
    """Guarda la configuración en el archivo JSON"""
    config = {
        'grado': grado,
        'salon': salon,
        'year': fecha_programada.year,
        'mes': fecha_programada.month,
        'dia': fecha_programada.day,
        'hora': fecha_programada.hour,
        'minuto': fecha_programada.minute,
        'fecha_guardado': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    with open(ARCHIVO_CONFIG, 'w') as f:
        json.dump(config, f, indent=4)


def cargar_configuracion():
    """Carga la configuración guardada"""
    try:
        with open(ARCHIVO_CONFIG, 'r') as f:
            config = json.load(f)

            # Convertir a objeto datetime
            fecha_programada = datetime(
                year=int(config['year']),
                month=int(config['mes']),
                day=int(config['dia']),
                hour=int(config['hora']),
                minute=int(config['minuto'])
            )

            return {
                'grado': config['grado'],
                'salon': config['salon'],
                'fecha_programada': fecha_programada,
                'fecha_guardado': config['fecha_guardado']
            }
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None


# Ejemplo de uso completo
if __name__ == "__main__":
    # Ejemplo de guardado
    grado_ejemplo = "5to"
    salon_ejemplo = "A"
    fecha_ejemplo = datetime(2023, 12, 15, 14, 30)  # año, mes, día, hora, minuto

    print("Guardando configuración...")
    guardar_configuracion(grado_ejemplo, salon_ejemplo, fecha_ejemplo)

    # Ejemplo de carga
    print("\nCargando configuración...")
    config = cargar_configuracion()

    if config:
        print("\nConfiguración guardada:")
        print(f"Grado: {config['grado']}")
        print(f"Salón: {config['salon']}")
        print(f"Fecha programada: {config['fecha_programada'].strftime('%d/%m/%Y %H:%M')}")
        print(f"Guardado el: {config['fecha_guardado']}")
    else:
        print("No hay configuración guardada o el archivo está corrupto")