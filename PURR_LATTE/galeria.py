"""galeria.py - La galería de los mejores artes: la mejor taza de cada dibujo, con quién la hizo.

Se guarda en la carpeta galeria/:
  - una foto por dibujo (corazon.png, tulipan.png, ...): la taza tal cual quedó;
  - galeria.json con los datos: {"corazon": {"nombre": "Lola", "porcentaje": 93}, ...}
Las fotos se cargan UNA vez al abrir el juego. Cuando alguien supera un récord, la foto nueva
se guarda en el archivo y también queda en memoria (no hace falta volver a leerla).
"""
import json
import os
import pygame
from ajustes import RUTA_GALERIA, RUTA_GALERIA_JSON


def ruta_foto(dibujo):
    """Devuelve la ruta del archivo de la foto de un dibujo (por ejemplo galeria/corazon.png)."""
    return os.path.join(RUTA_GALERIA, dibujo + ".png")


def cargar_galeria():
    """Lee galeria.json y las fotos. Devuelve (datos, fotos).

    datos: {dibujo: {"nombre": ..., "porcentaje": ...}}   fotos: {dibujo: Surface}
    Si no hay galería todavía (o algo está roto), devuelve diccionarios vacíos.
    """
    try:
        with open(RUTA_GALERIA_JSON, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (OSError, ValueError):
        return {}, {}
    if not isinstance(datos, dict):
        return {}, {}
    fotos = {}
    for dibujo in list(datos.keys()):
        try:
            fotos[dibujo] = pygame.image.load(ruta_foto(dibujo))
        except (pygame.error, FileNotFoundError):
            del datos[dibujo]          # si falta la foto, ese récord no se muestra
    return datos, fotos


def es_record(datos, dibujo, porcentaje):
    """Devuelve True si el porcentaje supera al mejor guardado para ese dibujo (o si no había)."""
    if dibujo not in datos:
        return True
    return porcentaje > datos[dibujo]["porcentaje"]


def guardar_arte(datos, fotos, dibujo, nombre, porcentaje, foto):
    """Si es récord, guarda la foto y los datos (en memoria y en la carpeta). Devuelve True si guardó."""
    if not es_record(datos, dibujo, porcentaje):
        return False
    datos[dibujo] = {"nombre": nombre, "porcentaje": porcentaje}
    fotos[dibujo] = foto
    try:
        os.makedirs(RUTA_GALERIA, exist_ok=True)
        pygame.image.save(foto, ruta_foto(dibujo))
        with open(RUTA_GALERIA_JSON, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
    except (OSError, pygame.error) as error:
        print("Aviso: no se pudo guardar la galería:", error)
    return True