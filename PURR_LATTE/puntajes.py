"""puntajes.py - El top del concurso: guarda y lee los puntajes en un archivo puntajes.json.

Cada puntaje es un diccionario: {"nombre": "Lola", "puntos": 342, "estrellas": 9, "pelaje": 0}.
  - puntos = la suma de los porcentajes de todas las rondas que jugaste (máximo 500).
  - pelaje = el número del gato que elegiste (para dibujar su carita en el top).
El archivo se lee una sola vez al abrir el juego y se escribe al terminar cada partida.
"""
import json
from ajustes import RUTA_PUNTAJES


def cargar_puntajes():
    """Lee puntajes.json y devuelve la lista de puntajes (vacía si el archivo no existe o está roto)."""
    try:
        with open(RUTA_PUNTAJES, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (OSError, ValueError):
        # OSError: el archivo todavía no existe. ValueError: el archivo está roto.
        return []
    if not isinstance(datos, list):
        return []
    return datos


def guardar_puntajes(puntajes):
    """Escribe la lista de puntajes en puntajes.json. Devuelve True si pudo guardar."""
    try:
        with open(RUTA_PUNTAJES, "w", encoding="utf-8") as archivo:
            json.dump(puntajes, archivo, ensure_ascii=False, indent=2)
        return True
    except OSError as error:
        print("Aviso: no se pudo guardar el top:", error)
        return False


def puntos_de(puntaje):
    """Devuelve los puntos de un puntaje. Sirve para ordenar la lista con sort(key=...)."""
    return puntaje["puntos"]


def agregar_puntaje(puntajes, nombre, puntos, estrellas, pelaje):
    """Agrega un puntaje nuevo, ordena la lista de mayor a menor y la guarda en el archivo.

    Devuelve el puesto (0 = primero) en el que quedó el puntaje nuevo, para resaltarlo en el top.
    """
    nuevo = {"nombre": nombre, "puntos": puntos, "estrellas": estrellas, "pelaje": pelaje}
    puntajes.append(nuevo)
    # reverse=True: de mayor a menor. Si hay empate, sort deja primero al que ya estaba.
    puntajes.sort(key=puntos_de, reverse=True)
    guardar_puntajes(puntajes)
    return puntajes.index(nuevo)