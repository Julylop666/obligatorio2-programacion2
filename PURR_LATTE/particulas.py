"""particulas.py - Las gotas de leche: la lista de elementos que cambia durante la partida.

Cada gota vive en dos etapas:
  1. "cayendo": baja desde el pico de la jarra hasta el café y se corre un poquito.
  2. "espuma": cuando toca el café se abre como un circulito de espuma que crece.
Cuando la espuma terminó de abrirse, la gota se saca de la lista.
Mientras vertés se agregan gotas nuevas: por eso la lista crece y se achica todo el tiempo.
"""
import math
import random
import pygame
from ajustes import (COLORES as C, PX, RADIO_CHORRO, VELOCIDAD_DESVIO, ALTURA_GOTA, VELOCIDAD_CAIDA,
                     RADIO_ESPUMA_INICIAL, RADIO_ESPUMA_FINAL, TIEMPO_ESPUMA, TAM_GOTA, ELEVACION_JARRA)


class Particula:
    """Una gota de leche que cae sola y, al llegar, se abre como espuma sobre la taza."""

    def __init__(self, x, y):
        """Crea la gota apuntando a (x, y), con un poquito de azar para que el chorro no sea una línea."""
        # Elijo un punto al azar dentro de un círculo alrededor del dedo (ángulo y distancia).
        angulo = random.uniform(0, 2 * math.pi)
        distancia = random.uniform(0, RADIO_CHORRO)
        self.x = x + math.cos(angulo) * distancia
        self.y = y + math.sin(angulo) * distancia
        self.vx = random.uniform(-VELOCIDAD_DESVIO, VELOCIDAD_DESVIO)
        self.vy = random.uniform(-VELOCIDAD_DESVIO, VELOCIDAD_DESVIO)
        self.altura = ALTURA_GOTA
        self.tiempo_espuma = 0.0
        self.viva = True

    def esta_cayendo(self):
        """Devuelve True mientras la gota todavía no llegó al café."""
        return self.altura > 0

    def actualizar(self, dt, taza):
        """Mueve la gota (si cae) o abre la espuma (si ya llegó). Pinta la espuma en la taza."""
        if self.esta_cayendo():
            self.altura -= VELOCIDAD_CAIDA * dt
            self.x += self.vx * dt
            self.y += self.vy * dt
            return
        self.tiempo_espuma += dt
        avance = min(1.0, self.tiempo_espuma / TIEMPO_ESPUMA)
        # la espuma crece de a poco desde el radio inicial al final
        radio = RADIO_ESPUMA_INICIAL + (RADIO_ESPUMA_FINAL - RADIO_ESPUMA_INICIAL) * avance
        taza.agregar_espuma((self.x, self.y), round(radio))
        if avance >= 1.0:
            self.viva = False

    def dibujar(self, pantalla):
        """Dibuja la gota cayendo (con su sombrita abajo). La espuma ya está pintada en la taza."""
        if not self.esta_cayendo():
            return
        # alineo a la grilla de pixeles del arte para que se vea pixel art
        x = int(self.x) // PX * PX
        y_suelo = int(self.y) // PX * PX
        y = int(self.y - self.altura * ELEVACION_JARRA) // PX * PX
        tam = TAM_GOTA * PX
        pygame.draw.rect(pantalla, C["cafe_oscuro"], (x, y_suelo, PX, PX))
        pygame.draw.rect(pantalla, C["leche"], (x - PX // 2, y, tam // 2, tam))


def crear_gotas(destino, cantidad):
    """Devuelve una lista con 'cantidad' gotas nuevas que van a caer cerca de destino."""
    gotas = []
    for _ in range(cantidad):
        gotas.append(Particula(destino[0], destino[1]))
    return gotas


def actualizar_particulas(particulas, dt, taza):
    """Actualiza todas las gotas y devuelve una lista nueva solo con las que siguen vivas."""
    vivas = []
    for gota in particulas:
        gota.actualizar(dt, taza)
        if gota.viva:
            vivas.append(gota)
    return vivas
