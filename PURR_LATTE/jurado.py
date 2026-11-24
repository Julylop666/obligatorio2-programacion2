"""jurado.py - Don Salmón, el jurado del concurso. Reacciona en vivo a cómo vas vertiendo.

Tiene 4 caras: neutral, aplaude, asco y llora (de emoción). Además se mueve solo:
respira (sube y baja), parpadea, aplaude con las patitas, le caen lágrimas o le salen
"olorcitos" verdes cuando algo no le gusta.
"""
import math
import pygame
from ajustes import (COLORES as C, COLOR_DON_SALMON, COLOR_OJOS, PX_GATO, NEUTRAL, APLAUDE, ASCO, LLORA,
                     FRASES_JURADO, TIEMPO_MIN_REACCION, VELOCIDAD_RESPIRO, CADA_PARPADEO,
                     DURACION_PARPADEO, VELOCIDAD_APLAUSO, UMBRALES_ESTRELLAS, UMBRAL_ASCO)
from dibujo import pixelar, con_puntos, oscurecer, aclarar

# Busto de Don Salmón: orejas, cabeza, anteojos (G = marco, H = vidrio), hocico (L),
# nariz (N), chaleco verde (V) y camisa (W). Los ojos y la boca se agregan según la cara.
_BUSTO = (
    "..OO..............OO..",
    ".ONNO............ONNO.",
    ".OFNNO..........ONNFO.",
    ".OFFNFOOOOOOOOOOFNFFO.",
    "OFFFFFFFFFFFFFFFFFFFFO",
    "OFFFFFFFFFFFFFFFFFFFFO",
    "OFFGGGGGFFFFFFGGGGGFFO",
    "OFFGHHHGGGGGGGGHHHGFFO",
    "OFFGHHHGFFFFFFGHHHGFFO",
    "OFFGHHHGFFFFFFGHHHGFFO",
    "OFFGGGGGFFFFFFGGGGGFFO",
    "OFFFFFFFFFNNFFFFFFFFFO",
    "OFFFFFLLLLOOLLLLFFFFFO",
    "OFFFFLLLLLLLLLLLLFFFFO",
    ".OFFFFLLLLLLLLLLFFFFO.",
    "..OFFFFFFFFFFFFFFFFO..",
    "...OOOOOOOOOOOOOOOO...",
    "..OVVVVWWWWWWWWVVVVO..",
    ".OVVVVVWWWWWWWWVVVVVO.",
    ".OVVVVVVWWWWWWVVVVVVO.",
    "OVVVVVVVVWWWWVVVVVVVVO",
    "OVVVVVVVVVWWVVVVVVVVVO",
)

_PATA = (
    ".OOOO.",
    "OFFFFO",
    "OFLLFO",
    "OFFFFO",
    ".OOOO.",
)

# Ojos y bocas de cada cara: listas de pixeles (x, y) que se pintan arriba del busto.
_OJOS = {
    "abiertos": [(5, 8), (5, 9), (16, 8), (16, 9)],
    "cerrados": [(4, 9), (5, 9), (6, 9), (15, 9), (16, 9), (17, 9)],          # parpadeo
    "felices": [(4, 9), (5, 8), (6, 9), (15, 9), (16, 8), (17, 9)],           # ^ ^
    "fruncidos": [(4, 9), (5, 9), (6, 8), (15, 8), (16, 9), (17, 9)],         # > <
    "llorando": [(4, 8), (5, 9), (6, 8), (15, 8), (16, 9), (17, 8)],          # u u
}
_BOCAS = {
    NEUTRAL: [(9, 13), (12, 13)],
    APLAUDE: [(8, 12), (13, 12), (8, 13), (9, 13), (10, 13), (11, 13), (12, 13), (13, 13),
              (9, 14), (10, 14), (11, 14), (12, 14)],
    ASCO: [(8, 13), (9, 14), (10, 13), (11, 14), (12, 13), (13, 14)],
    LLORA: [(9, 14), (10, 13), (11, 13), (12, 14)],
}
_LENGUA = [(9, 13), (10, 13), (11, 13), (12, 13)]   # adentro de la boca abierta (cuando aplaude)


def elegir_reaccion(porcentaje, fraccion_fuera):
    """Devuelve qué cara pone Don Salmón según el porcentaje y la leche que cayó afuera."""
    if fraccion_fuera > UMBRAL_ASCO:
        return ASCO
    if porcentaje >= UMBRALES_ESTRELLAS[2]:
        return LLORA
    if porcentaje >= UMBRALES_ESTRELLAS[0]:
        return APLAUDE
    return NEUTRAL


class Jurado:
    """Don Salmón: guarda su cara actual y la anima con el paso del tiempo."""

    def __init__(self):
        """Empieza con cara neutral y los relojes de la animación en cero."""
        self.cara = NEUTRAL
        self.tiempo = 0.0
        self.desde_cambio = 0.0

    def poner_cara(self, cara):
        """Cambia la cara en el momento (para las pantallas de resultado, victoria y derrota)."""
        self.cara = cara
        self.desde_cambio = 0.0

    def reaccionar(self, porcentaje, fraccion_fuera):
        """Mira cómo va la taza y cambia de cara, pero no más seguido que TIEMPO_MIN_REACCION."""
        nueva = elegir_reaccion(porcentaje, fraccion_fuera)
        # si cambiara en cada cuadro, cuando el % está justo en un umbral la cara temblaría
        if nueva != self.cara and self.desde_cambio >= TIEMPO_MIN_REACCION:
            self.poner_cara(nueva)

    def frase(self):
        """Devuelve lo que dice Don Salmón con la cara que tiene ahora."""
        return FRASES_JURADO[self.cara]

    def actualizar(self, dt):
        """Avanza los relojes de la animación (respiro, parpadeo, aplausos y lágrimas)."""
        self.tiempo += dt
        self.desde_cambio += dt

    def armar_cara(self):
        """Devuelve la grilla del busto con los ojos y la boca de la cara actual."""
        parpadea = (self.tiempo % CADA_PARPADEO) < DURACION_PARPADEO
        if self.cara == APLAUDE:
            ojos = "felices"
        elif self.cara == ASCO:
            ojos = "fruncidos"
        elif self.cara == LLORA:
            ojos = "llorando"
        elif parpadea:
            ojos = "cerrados"
        else:
            ojos = "abiertos"
        grilla = con_puntos(_BUSTO, _OJOS[ojos], "E")
        grilla = con_puntos(grilla, _BOCAS[self.cara], "O")
        if self.cara == APLAUDE:
            grilla = con_puntos(grilla, _LENGUA, "T")
        return grilla

    def dibujar(self, pantalla, pie):
        """Dibuja a Don Salmón con los pies del busto en 'pie' (centro de abajo)."""
        px = PX_GATO
        pelo = COLOR_DON_SALMON
        paleta = {"O": oscurecer(pelo, 0.38), "F": pelo, "L": aclarar(pelo, 0.55), "N": C["nariz"],
                  "G": C["anteojos"], "H": aclarar(pelo, 0.75), "E": COLOR_OJOS, "V": C["chaleco_verde"],
                  "W": C["blanco"], "T": C["rojo_suave"]}
        sprite = pixelar(self.armar_cara(), paleta, px)
        # respiro: sube un pixel la mitad del tiempo; cuando llora tiembla para los costados
        sube = math.sin(self.tiempo * VELOCIDAD_RESPIRO * math.pi) > 0
        dx = 0
        if self.cara == LLORA:
            dx = px if int(self.tiempo * 10) % 2 == 0 else -px
        rect = sprite.get_rect(midbottom=(pie[0] + dx, pie[1] - (px if sube else 0)))
        pantalla.blit(sprite, rect)
        self.dibujar_patas(pantalla, rect, paleta)
        if self.cara == LLORA:
            self.dibujar_lagrimas(pantalla, rect)
        elif self.cara == ASCO:
            self.dibujar_olor(pantalla, rect)

    def dibujar_patas(self, pantalla, rect, paleta):
        """Dibuja las dos patitas: quietas abajo, o juntándose y separándose si aplaude."""
        px = PX_GATO
        pata = pixelar(_PATA, paleta, px)
        if self.cara == APLAUDE and int(self.tiempo * VELOCIDAD_APLAUSO * 2) % 2 == 0:
            columnas, fila = (6, 10), 14          # juntas (¡plap!)
        elif self.cara == APLAUDE:
            columnas, fila = (3, 13), 14          # separadas
        else:
            columnas, fila = (1, 15), 17          # apoyadas
        for columna in columnas:
            pantalla.blit(pata, (rect.x + columna * px, rect.y + fila * px))

    def dibujar_lagrimas(self, pantalla, rect):
        """Dibuja gotitas celestes que caen debajo de los anteojos (lágrimas de emoción)."""
        px = PX_GATO
        for columna in (5, 16):
            for i in range(2):
                # cada lágrima baja 6 pixeles del arte y vuelve a empezar (el % hace el loop)
                bajada = (self.tiempo * 7 + i * 3) % 6
                x = rect.x + columna * px
                y = rect.y + int(11 + bajada) * px
                pygame.draw.rect(pantalla, C["agua"], (x, y, px, px * 2))

    def dibujar_olor(self, pantalla, rect):
        """Dibuja tres líneas onduladas verdes al costado de la cabeza (algo huele mal)."""
        px = PX_GATO
        for i in range(3):
            x0 = rect.right + px
            y0 = rect.y + (2 + i * 4) * px
            for paso in range(4):
                ondita = px if (paso + int(self.tiempo * 6)) % 2 == 0 else 0
                pygame.draw.rect(pantalla, C["verde"], (x0 + paso * px, y0 + ondita, px, px))
