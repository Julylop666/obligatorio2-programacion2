"""jurado.py - Don Salmón, el jurado del concurso. Reacciona EN VIVO a lo que va pasando.

Es el mismo gato de Purr & Brew (pelaje salmón, anteojos y chaleco verde). Tiene dos capas:
  - una cara "de base" según cómo va el porcentaje (neutral, contento o llorando de emoción);
  - comentarios puntuales cuando pasa algo (derramaste, queda poca leche, ganaste una estrella...):
    durante unos segundos pone otra cara, cambia de animación y lo dice en un globito.
Animaciones: respira, parpadea, salta y aplaude, se le cae una gotita de sudor, le salen
olorcitos verdes, llora de emoción.
"""
import math
import random
import pygame
from ajustes import (COLORES as C, COLOR_DON_SALMON, COLOR_OJOS, PX_GATO, NEUTRAL, CONTENTO, PREOCUPADO,
                     ASCO, LLORA, FRASES_CARA, COMENTARIOS, DURACION_COMENTARIO, ESPERA_MISMO_COMENTARIO,
                     TIEMPO_MIN_REACCION, VELOCIDAD_RESPIRO, CADA_PARPADEO, DURACION_PARPADEO,
                     VELOCIDAD_APLAUSO, ALTURA_SALTO, UMBRALES_ESTRELLAS, UMBRAL_ASCO)
from dibujo import pixelar, dibujar_gato, oscurecer, aclarar

_PATITA = (
    ".OOO.",
    "OFFFO",
    "OLLFO",
    ".OOO.",
)
_TABLA = (                # la tablita de jurado que tiene en la mano
    "..OO..",
    "OOKKOO",
    "OWWWWO",
    "OWAAWO",
    "OWWWWO",
    "OWAAWO",
    "OWWWWO",
    "OOOOOO",
)
_EXCLAMACION = ("OO", "OO", "OO", "..", "OO")


def elegir_cara(porcentaje, fraccion_fuera):
    """Devuelve la cara de base según el porcentaje y la leche que cayó afuera del dibujo."""
    if fraccion_fuera > UMBRAL_ASCO:
        return ASCO
    if porcentaje >= UMBRALES_ESTRELLAS[2]:
        return LLORA
    if porcentaje >= UMBRALES_ESTRELLAS[0]:
        return CONTENTO
    return NEUTRAL


class Jurado:
    """Don Salmón: guarda su cara, lo que está diciendo y los relojes de sus animaciones."""

    def __init__(self):
        """Empieza tranquilo, sin decir nada especial."""
        self.cara_base = NEUTRAL
        self.tiempo = 0.0
        self.desde_cambio = 0.0
        self.comentario = None          # (cara, frase) mientras dura un comentario
        self.tiempo_comentario = 0.0
        self.ultima_vez = {}            # evento -> momento en que lo dijo por última vez

    def reiniciar(self, cara=NEUTRAL):
        """Pone una cara fija y borra los comentarios (al empezar una ronda o en los resultados)."""
        self.cara_base = cara
        self.desde_cambio = 0.0
        self.comentario = None
        self.ultima_vez = {}

    def reaccionar(self, porcentaje, fraccion_fuera):
        """Mira cómo va la taza y cambia la cara de base, pero no más seguido que TIEMPO_MIN_REACCION."""
        nueva = elegir_cara(porcentaje, fraccion_fuera)
        # si cambiara en cada cuadro, cuando el % está justo en un umbral la cara temblaría
        if nueva != self.cara_base and self.desde_cambio >= TIEMPO_MIN_REACCION:
            self.cara_base = nueva
            self.desde_cambio = 0.0

    def comentar(self, evento):
        """Dice algo sobre un evento ('derrame', 'poca_leche', 'estrella'...) y cambia de cara.

        No repite el mismo tipo de comentario muy seguido, para no ser pesado.
        Devuelve True si de verdad lo dijo.
        """
        ultima = self.ultima_vez.get(evento, -ESPERA_MISMO_COMENTARIO)
        if self.tiempo - ultima < ESPERA_MISMO_COMENTARIO:
            return False
        cara, frases = COMENTARIOS[evento]
        self.comentario = (cara, random.choice(frases))
        self.tiempo_comentario = DURACION_COMENTARIO
        self.ultima_vez[evento] = self.tiempo
        return True

    def cara(self):
        """Devuelve la cara que se ve ahora: la del comentario si está hablando, si no la de base."""
        if self.comentario is not None:
            return self.comentario[0]
        return self.cara_base

    def frase(self):
        """Devuelve lo que dice ahora (el comentario, o la frase de su cara de base)."""
        if self.comentario is not None:
            return self.comentario[1]
        return FRASES_CARA[self.cara_base]

    def esta_comentando(self):
        """Devuelve True mientras se ve un comentario puntual."""
        return self.comentario is not None

    def actualizar(self, dt):
        """Avanza los relojes de la animación y hace que el comentario se termine solo."""
        self.tiempo += dt
        self.desde_cambio += dt
        if self.comentario is not None:
            self.tiempo_comentario -= dt
            if self.tiempo_comentario <= 0:
                self.comentario = None

    # ------------------------------------------------------------ dibujo
    def dibujar(self, pantalla, pie, px=PX_GATO):
        """Dibuja a Don Salmón con los pies en 'pie', con la animación de la cara que tiene."""
        cara = self.cara()
        x, y = pie
        if cara == CONTENTO:
            # salta: sube y baja con el valor absoluto de un seno (rebota contra el piso)
            y -= round(abs(math.sin(self.tiempo * 6)) * ALTURA_SALTO) * px
        elif cara == ASCO:
            x += px if int(self.tiempo * 8) % 2 == 0 else -px       # se sacude
        elif cara == LLORA:
            x += px // 2 if int(self.tiempo * 12) % 2 == 0 else -px // 2   # tiembla de emoción
        elif math.sin(self.tiempo * VELOCIDAD_RESPIRO * math.pi) > 0:
            y -= px // 2                                              # respira
        dibujo_cara = cara
        if cara in (NEUTRAL, PREOCUPADO) and (self.tiempo % CADA_PARPADEO) < DURACION_PARPADEO:
            dibujo_cara = "parpadeo"
        rect = dibujar_gato(pantalla, (x, y), COLOR_DON_SALMON, px, dibujo_cara, COLOR_OJOS,
                            lentes=True, chaleco=True)
        paleta = {"O": oscurecer(COLOR_DON_SALMON, 0.38), "F": COLOR_DON_SALMON,
                  "L": aclarar(COLOR_DON_SALMON, 0.55), "K": C["metal_oscuro"], "W": C["blanco"],
                  "A": C["acento"]}
        if cara == CONTENTO:
            self.dibujar_aplauso(pantalla, rect, paleta, px)
        else:
            tabla = pixelar(_TABLA, paleta, px)
            pantalla.blit(tabla, (rect.x - 2 * px, rect.y + 10 * px))
        if cara == PREOCUPADO:
            self.dibujar_sudor(pantalla, rect, px)
        elif cara == ASCO:
            self.dibujar_olor(pantalla, rect, px)
        elif cara == LLORA:
            self.dibujar_lagrimas(pantalla, rect, px)

    def dibujar_aplauso(self, pantalla, rect, paleta, px):
        """Dos patitas delante del pecho que se juntan y se separan (¡plap, plap!)."""
        patita = pixelar(_PATITA, paleta, px)
        juntas = int(self.tiempo * VELOCIDAD_APLAUSO * 2) % 2 == 0
        columnas = (4, 7) if juntas else (2, 9)
        for columna in columnas:
            pantalla.blit(patita, (rect.x + columna * px, rect.y + 10 * px))

    def dibujar_sudor(self, pantalla, rect, px):
        """Una gotita celeste que cae al costado de la cabeza y un signo de exclamación arriba."""
        bajada = (self.tiempo * 6) % 4
        pygame.draw.rect(pantalla, C["agua"], (rect.right - 2 * px, rect.y + int(3 + bajada) * px, px, 2 * px))
        signo = pixelar(_EXCLAMACION, {"O": C["brillo_dorado"]}, px)
        pantalla.blit(signo, (rect.centerx - px, rect.y - 7 * px))

    def dibujar_olor(self, pantalla, rect, px):
        """Tres líneas onduladas verdes al costado de la cabeza (algo no le gustó nada)."""
        for i in range(3):
            x0 = rect.right
            y0 = rect.y + (1 + i * 3) * px
            for paso in range(4):
                ondita = px if (paso + int(self.tiempo * 6)) % 2 == 0 else 0
                pygame.draw.rect(pantalla, C["verde"], (x0 + paso * px, y0 + ondita, px, px))

    def dibujar_lagrimas(self, pantalla, rect, px):
        """Gotitas celestes que caen debajo de los anteojos (lágrimas de emoción)."""
        for columna in (4, 11):
            for i in range(2):
                # cada lágrima baja 5 pixeles del arte y vuelve a empezar (el % hace el loop)
                bajada = (self.tiempo * 7 + i * 2.5) % 5
                pygame.draw.rect(pantalla, C["agua"],
                                 (rect.x + columna * px, rect.y + int(8 + bajada) * px, px, px * 2))