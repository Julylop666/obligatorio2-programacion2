"""dibujo.py - Pixel art y piezas de la interfaz (paneles, textos, barras, estrellas, jarra, gato).

Igual que en Purr & Brew, los sprites son grillas de texto: cada letra es un pixel y una
paleta dice de qué color es cada letra. pixelar() convierte la grilla en una Surface
agrandada sin suavizar, así los pixeles quedan nítidos. El juego no usa imágenes externas.
"""
import random
import pygame
from ajustes import (COLORES as C, PX, PX_JARRA, COLOR_OJOS_BARISTA,
                     ANGULO_VERTER, ANCHO, ALTO, MARGEN_CAMARA_X, MARGEN_CAMARA_Y, POS_LIENZO,
                     TAM_LIENZO, RADIO_PLATO)


# ---------------------------------------------------------------- colores y pixelado
def oscurecer(color, factor=0.8):
    """Devuelve el mismo color pero más oscuro (factor menor a 1)."""
    return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))


def aclarar(color, factor=0.5):
    """Devuelve el mismo color pero más claro (factor entre 0 y 1)."""
    return (int(color[0] + (255 - color[0]) * factor), int(color[1] + (255 - color[1]) * factor),
            int(color[2] + (255 - color[2]) * factor))


# Guardo cada sprite ya armado para no reconstruirlo en cada cuadro (sería lento).
_sprites_armados = {}


def pixelar(grilla, paleta, px):
    """Convierte una grilla de texto en una Surface pixel art agrandada px veces y la devuelve.

    grilla: tupla de strings (una letra = un pixel, '.' = transparente).
    paleta: diccionario {letra: (r, g, b)}.
    """
    clave = (tuple(grilla), tuple(sorted(paleta.items())), px)
    if clave in _sprites_armados:
        return _sprites_armados[clave]
    ancho = max(len(fila) for fila in grilla)
    chica = pygame.Surface((ancho, len(grilla)), pygame.SRCALPHA)
    for y, fila in enumerate(grilla):
        for x, letra in enumerate(fila):
            if letra in paleta:
                chica.set_at((x, y), paleta[letra])
    grande = pygame.transform.scale(chica, (ancho * px, len(grilla) * px))
    _sprites_armados[clave] = grande
    return grande


def superponer(grilla, encima, columna, fila):
    """Devuelve una copia de la grilla con otra grilla 'encima' pegada desde (columna, fila).

    Los '.' de la grilla de encima son transparentes: no tapan nada. Si hace falta, la grilla
    se agranda para que entre lo de encima.
    """
    filas = [list(f) for f in grilla]
    for y, fila_encima in enumerate(encima):
        for x, letra in enumerate(fila_encima):
            if letra == ".":
                continue
            while len(filas) <= fila + y:
                filas.append([])
            destino = filas[fila + y]
            while len(destino) <= columna + x:
                destino.append(".")
            destino[columna + x] = letra
    return tuple("".join(f) for f in filas)


def con_puntos(grilla, puntos, letra):
    """Devuelve una copia de la grilla con la letra puesta en cada (x, y) de la lista puntos."""
    filas = [list(fila) for fila in grilla]
    for x, y in puntos:
        filas[y][x] = letra
    return tuple("".join(fila) for fila in filas)


# ---------------------------------------------------------------- paneles y texto
def dibujar_panel(pantalla, rect, color=None, borde=None):
    """Dibuja un panel pixel art con esquinas escalonadas (como en Purr & Brew) y devuelve su Rect."""
    color = color or C["panel"]
    borde = borde or C["zocalo"]
    rect = pygame.Rect(rect)
    b = PX
    x, y, w, h = rect
    # dos rectángulos cruzados forman el borde con las esquinas "comidas"
    pygame.draw.rect(pantalla, borde, (x + b, y, w - 2 * b, h))
    pygame.draw.rect(pantalla, borde, (x, y + b, w, h - 2 * b))
    pygame.draw.rect(pantalla, color, (x + 2 * b, y + b, w - 4 * b, h - 2 * b))
    pygame.draw.rect(pantalla, color, (x + b, y + 2 * b, w - 2 * b, h - 4 * b))
    return rect


def texto_centrado(pantalla, texto, fuente, color, centro, sombra=None):
    """Escribe una línea centrada en el punto dado (con sombrita opcional). Devuelve su Rect."""
    superficie = fuente.render(texto, False, color)
    rect = superficie.get_rect(center=centro)
    if sombra:
        pantalla.blit(fuente.render(texto, False, sombra), rect.move(PX // 2 + 1, PX // 2 + 1))
    pantalla.blit(superficie, rect)
    return rect


def texto_envuelto(pantalla, texto, fuente, color, rect, interlineado=2):
    """Escribe un texto partiéndolo en líneas para que entre en el ancho del rect.

    Devuelve la coordenada y donde terminó, para poder seguir escribiendo abajo.
    """
    rect = pygame.Rect(rect)
    y = rect.top
    linea = ""
    for palabra in texto.split():
        prueba = (linea + " " + palabra).strip()
        if fuente.size(prueba)[0] <= rect.width:
            linea = prueba
        else:
            pantalla.blit(fuente.render(linea, False, color), (rect.left, y))
            y += fuente.get_height() + interlineado
            linea = palabra
    if linea:
        pantalla.blit(fuente.render(linea, False, color), (rect.left, y))
        y += fuente.get_height() + interlineado
    return y


def dibujar_velo(pantalla, color):
    """Oscurece toda la pantalla con un color semitransparente (para pausas y avisos)."""
    velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    velo.fill(color)
    pantalla.blit(velo, (0, 0))


# ---------------------------------------------------------------- barras y estrellas
def dibujar_barra(pantalla, rect, fraccion, color_lleno, color_fondo=None):
    """Dibuja una barra pixel art que se llena según fraccion (de 0 a 1)."""
    rect = pygame.Rect(rect)
    fraccion = max(0.0, min(1.0, fraccion))
    pygame.draw.rect(pantalla, C["contorno"], rect.inflate(PX * 2, PX * 2))
    pygame.draw.rect(pantalla, color_fondo or C["sombra"], rect)
    # redondeo el ancho a múltiplos de PX para que la barra avance "a saltitos" de pixel
    ancho = int(rect.width * fraccion) // PX * PX
    if ancho > 0:
        pygame.draw.rect(pantalla, color_lleno, (rect.x, rect.y, ancho, rect.height))
        pygame.draw.rect(pantalla, aclarar(color_lleno, 0.5), (rect.x, rect.y, ancho, PX))


_ESTRELLA = (
    "....O....",
    "...OYO...",
    "OOOOYOOOO",
    "OYYYYYYYO",
    ".OYYYYYO.",
    "..OYYYO..",
    ".OYYOYYO.",
    ".OYO.OYO.",
    ".OO...OO.",
)


def dibujar_estrella(pantalla, centro, llena, px=PX):
    """Dibuja una estrella pixel art: dorada si está llena, apagada si no."""
    relleno = C["dorado"] if llena else C["sombra"]
    sprite = pixelar(_ESTRELLA, {"O": C["contorno"], "Y": relleno}, px)
    pantalla.blit(sprite, sprite.get_rect(center=centro))


def dibujar_fila_estrellas(pantalla, centro, cantidad, total=3, px=PX, separacion=48):
    """Dibuja 'total' estrellas en fila, centradas, con las primeras 'cantidad' encendidas."""
    inicio = centro[0] - separacion * (total - 1) / 2
    for i in range(total):
        dibujar_estrella(pantalla, (round(inicio + i * separacion), centro[1]), i < cantidad, px)


# ---------------------------------------------------------------- jarra de leche con la patita
_JARRA = (
    "OOO.............",
    "OWWOOOOOOOOOO...",
    ".OOMMMMMMMMMMO..",
    "..OMSMMMMMMMMOOO",
    "..OMSMMMMMMMMO.O",
    "..OMSMMMMMMMMO.O",
    "..OMSMMMMMMMMO.O",
    "..OMSMMMMMMMMOOO",
    "..OMMMMMMMMMMO..",
    "..OKKKKKKKKKKO..",
    "...OOOOOOOOOO...",
)
# La patita del gato que agarra el asa: redondita, con los deditos marcados
# (P = pelaje, R = almohadillas más claras, Q = borde oscuro).
_PATA = (
    "..QQQQ..",
    ".QPPPPQ.",
    "QPQPPQPQ",
    "QPPPPPPQ",
    "QPRPPRPQ",
    "QPPRRPPQ",
    ".QPPPPQ.",
    "..QQQQ..",
)
_JARRA_CON_PATA = superponer(_JARRA, _PATA, 11, 1)
_PICO_JARRA = (1.5, 1.5)      # el pixel 'W' de la punta del pico, en pixeles del arte


def dibujar_jarra(pantalla, destino, vertiendo, pelaje, elevacion):
    """Dibuja la jarrita (agarrada por la pata del color elegido) con el pico sobre 'destino'.

    elevacion: cuántos pixeles por encima del café está el pico (jarra alta o baja).
    Al verter se inclina. Para que el pico quede en el lugar correcto aunque la jarra gire,
    giro también el vector que va del centro del sprite al pico.
    """
    paleta = {"O": C["contorno"], "M": C["metal"], "S": C["blanco"], "K": C["metal_oscuro"],
              "W": C["leche"], "P": pelaje, "R": aclarar(pelaje, 0.5), "Q": oscurecer(pelaje, 0.4)}
    sprite = pixelar(_JARRA_CON_PATA, paleta, PX_JARRA)
    angulo = ANGULO_VERTER if vertiendo else 0
    girado = pygame.transform.rotate(sprite, angulo)
    centro_sprite = pygame.Vector2(sprite.get_width() / 2, sprite.get_height() / 2)
    pico = pygame.Vector2(_PICO_JARRA[0] * PX_JARRA, _PICO_JARRA[1] * PX_JARRA)
    # pygame.transform.rotate gira en sentido antihorario y Vector2.rotate al revés (la y va
    # para abajo en pantalla), por eso uso el ángulo con signo cambiado.
    desde_centro = (pico - centro_sprite).rotate(-angulo)
    punta = pygame.Vector2(destino[0], destino[1] - elevacion)
    pantalla.blit(girado, girado.get_rect(center=punta - desde_centro))


def dibujar_mira(pantalla, destino, vertiendo, radio):
    """Dibuja la mira (4 cuadraditos) que marca dónde va a caer la leche.

    Los cuadraditos se separan según 'radio' (en pantalla): así se ve qué tan ancho va a
    caer el chorro antes de verter.
    """
    x = int(destino[0]) // PX * PX
    y = int(destino[1]) // PX * PX
    color = C["leche"] if vertiendo else C["acento"]
    paso = max(2, round(radio / PX))
    for dx, dy in ((-paso, 0), (paso, 0), (0, -paso), (0, paso)):
        caja = (x + dx * PX, y + dy * PX, PX, PX)
        pygame.draw.rect(pantalla, C["contorno"], pygame.Rect(caja).inflate(2, 2))
        pygame.draw.rect(pantalla, color, caja)


# ---------------------------------------------------------------- gatos (los de Purr & Brew)
# El mismo gato del juego anterior. Los ojos y la boca no están en la grilla: se agregan
# según la cara (así un mismo gato puede estar contento, preocupado, llorando...).
_GATO = (
    "..OO........OO..",
    ".OFFO......OFFO.",
    ".OFNFOOOOOOFNFO.",
    ".OFFFFFFFFFFFFO.",
    ".OFFFFFFFFFFFFO.",
    ".OFFFFFFFFFFFFO.",
    ".OFFFFFFFFFFFFO.",
    ".OFFFFFNNFFFFFO.",
    ".OFFFLLLLLLFFFO.",
    "..OFFFFFFFFFFO..",
    "...OOOOOOOOOO...",
    "...OFFFFFFFFO...",
    "...OFLLLLLLFO...",
    "...OFLLLLLLFO...",
    "...OFFFFFFFFO...",
    "...OFFFOOFFFO...",
    "....OOO..OOO....",
)
_COLA_PELO = [(13, 14), (14, 14), (14, 13), (14, 12), (14, 11)]
_COLA_BORDE = [(13, 13), (15, 11), (15, 12), (15, 13), (15, 14), (13, 15), (14, 15), (14, 10)]
_DELANTAL = ("......WWWW......",
             "....AAAAAAAA....",
             "....AAAAAAAA....",
             "....AAWWWWAA....",
             "....AAWWWWAA....")
_CHALECO = ("................",
            "....VVV..VVV....",
            "....VVV..VVV....",
            "....VVV..VVV....",
            "....VVV..VVV....")
_ANTEOJOS = ([(x, 4) for x in (3, 4, 5, 6, 9, 10, 11, 12)] + [(x, 7) for x in (3, 4, 5, 6, 9, 10, 11, 12)]
             + [(x, y) for x in (3, 6, 9, 12) for y in (5, 6)] + [(7, 5), (8, 5)])

# Cada cara: (pixeles de los ojos, pixeles de la boca). Los ojos van en las columnas 4-5 y 10-11.
_OJOS_ABIERTOS = [(4, 5), (5, 5), (4, 6), (5, 6), (10, 5), (11, 5), (10, 6), (11, 6)]
_OJOS_CERRADOS = [(4, 6), (5, 6), (10, 6), (11, 6)]
_SONRISA = [(6, 8), (7, 9), (8, 9), (9, 8)]            # forma de U
CARAS = {
    "neutral": (_OJOS_ABIERTOS, []),
    "parpadeo": (_OJOS_CERRADOS, []),
    "contento": (_OJOS_ABIERTOS, _SONRISA),
    "preocupado": (_OJOS_ABIERTOS, [(7, 8), (8, 8)]),
    "asco": (_OJOS_CERRADOS, [(6, 8), (7, 9), (8, 8), (9, 9)]),
    "llora": (_OJOS_CERRADOS, _SONRISA),                  # llora de emoción: ojos cerrados y sonrisa
}


def grilla_gato(cara="neutral", lentes=False, chaleco=False, delantal=False):
    """Arma y devuelve la grilla de un gato con la cara y la ropa pedidas."""
    grilla = con_puntos(_GATO, _COLA_PELO, "F")
    grilla = con_puntos(grilla, _COLA_BORDE, "O")
    if chaleco:
        grilla = superponer(grilla, _CHALECO, 0, 10)
    if delantal:
        grilla = superponer(grilla, _DELANTAL, 0, 10)
    ojos, boca = CARAS[cara]
    grilla = con_puntos(grilla, ojos, "E")
    grilla = con_puntos(grilla, boca, "B")
    if lentes:
        grilla = con_puntos(grilla, _ANTEOJOS, "G")
    return grilla


def paleta_gato(pelaje, ojos):
    """Devuelve la paleta de colores de un gato según su pelaje y el color de sus ojos."""
    return {"O": oscurecer(pelaje, 0.38), "F": pelaje, "L": aclarar(pelaje, 0.55), "E": ojos,
            "N": C["nariz"], "B": oscurecer(pelaje, 0.3), "G": C["anteojos"], "W": C["blanco"],
            "A": C["delantal_celeste"], "V": C["chaleco_verde"]}


def dibujar_gato(pantalla, pie, pelaje, px, cara="neutral", ojos=COLOR_OJOS_BARISTA, lentes=False,
                 chaleco=False, delantal=False, sombra=True, mirando=1):
    """Dibuja un gato pixel art parado con los pies en 'pie' (centro de abajo). Devuelve su Rect."""
    sprite = pixelar(grilla_gato(cara, lentes, chaleco, delantal), paleta_gato(pelaje, ojos), px)
    if mirando < 0:
        sprite = pygame.transform.flip(sprite, True, False)
    rect = sprite.get_rect(midbottom=pie)
    if sombra:
        caja = pygame.Rect(0, 0, 14 * px, 3 * px)
        caja.center = (rect.centerx, rect.bottom - px // 2)
        superficie = pygame.Surface(caja.size, pygame.SRCALPHA)
        pygame.draw.ellipse(superficie, (62, 42, 50, 60), superficie.get_rect())
        pantalla.blit(superficie, caja)
    pantalla.blit(sprite, rect)
    return rect


# ---------------------------------------------------------------- fondos (se arman UNA vez)
def crear_fondo_mesa():
    """Arma y devuelve el fondo de la ronda: la barra de madera vista desde arriba, con un
    individual de mimbre debajo del plato y unos granos de café sueltos.

    Se dibuja en chiquito (un pixel = un pixel del arte) y después se agranda PX veces.
    """
    azar = random.Random(4)                 # semilla fija: el fondo sale igual siempre
    ancho, alto = ANCHO // PX, ALTO // PX
    chica = pygame.Surface((ancho, alto))
    # tablas de madera: cada una con un borde claro arriba, una junta oscura y vetas suaves
    alto_tabla = 14
    for numero, fila in enumerate(range(0, alto, alto_tabla)):
        color = C["barra"] if numero % 2 == 0 else oscurecer(C["barra"], 0.94)
        pygame.draw.rect(chica, color, (0, fila, ancho, alto_tabla))
        pygame.draw.line(chica, aclarar(color, 0.18), (0, fila + 1), (ancho, fila + 1))
        pygame.draw.line(chica, C["madera_oscura"], (0, fila), (ancho, fila))
        for _ in range(6):
            x = azar.randint(0, ancho - 20)
            y = fila + azar.randint(4, alto_tabla - 3)
            pygame.draw.line(chica, oscurecer(color, 0.93), (x, y), (x + azar.randint(8, 22), y))
    # individual de mimbre: anillos alternados alrededor de donde va el plato
    centro = (POS_LIENZO[0] // PX + TAM_LIENZO // 2, POS_LIENZO[1] // PX + TAM_LIENZO // 2)
    radio = RADIO_PLATO + 8
    pygame.draw.circle(chica, C["madera_oscura"], centro, radio + 1)
    for r in range(radio, 0, -2):
        pygame.draw.circle(chica, C["mimbre"] if (r // 2) % 2 == 0 else C["mimbre_oscuro"], centro, r)
    # sombra del plato (un poquito corrida hacia abajo a la derecha)
    pygame.draw.circle(chica, oscurecer(C["mimbre_oscuro"], 0.8), (centro[0] + 2, centro[1] + 3), RADIO_PLATO)
    # granos de café sueltos
    for x, y in ((150, 140), (156, 146), (160, 136), (8, 30), (14, 36), (151, 60), (10, 140), (16, 146)):
        pygame.draw.rect(chica, C["cafe_oscuro"], (x, y, 3, 2))
        chica.set_at((x + 1, y), C["caramelo"])
    return pygame.transform.scale(chica, (ancho * PX, alto * PX))


def crear_fondo_cafeteria():
    """Arma y devuelve el fondo de los menús: el interior de la cafetería de Don Salmón
    (papel tapiz, ventana con sol, estantes con tacitas, lámparas, pizarrón y la barra).
    """
    ancho, alto = ANCHO // PX, ALTO // PX
    chica = pygame.Surface((ancho, alto))
    chica.fill(C["pared"])
    for x in range(0, ancho, 8):                                           # papel tapiz a rayas
        pygame.draw.rect(chica, C["papel_rayas"], (x, 0, 2, 104))
    pygame.draw.rect(chica, C["madera_oscura"], (0, 96, ancho, 24))        # guardapared de madera
    pygame.draw.rect(chica, C["zocalo"], (0, 94, ancho, 3))
    for x in range(6, ancho, 16):
        pygame.draw.rect(chica, oscurecer(C["madera_oscura"], 0.85), (x, 100, 10, 16), 1)
    # ventana con sol, nubes y cortinas (a la izquierda)
    pygame.draw.rect(chica, C["contorno"], (10, 40, 44, 40))
    pygame.draw.rect(chica, C["cielo"], (12, 42, 40, 36))
    pygame.draw.rect(chica, C["cielo_claro"], (12, 62, 40, 16))
    pygame.draw.circle(chica, C["sol"], (40, 54), 6)
    for x, y in ((14, 48), (28, 66)):
        pygame.draw.rect(chica, C["nube"], (x, y, 10, 3))
        pygame.draw.rect(chica, C["nube"], (x + 2, y - 2, 5, 2))
    pygame.draw.line(chica, C["blanco"], (32, 42), (32, 77))
    pygame.draw.line(chica, C["blanco"], (12, 60), (51, 60))
    pygame.draw.rect(chica, C["cortina"], (8, 38, 6, 44))
    pygame.draw.rect(chica, C["cortina"], (50, 38, 6, 44))
    pygame.draw.rect(chica, C["madera_oscura"], (6, 36, 52, 3))
    # estantes con tacitas (a la derecha)
    colores = (C["taza"], C["menta"], C["azul"], C["dorado"])
    for repisa in (48, 70):
        pygame.draw.rect(chica, C["contorno"], (176, repisa + 6, 56, 3))
        pygame.draw.rect(chica, C["barra"], (176, repisa + 6, 56, 2))
        for i in range(4):
            x = 180 + i * 13
            pygame.draw.rect(chica, C["contorno"], (x - 1, repisa - 1, 9, 7))
            pygame.draw.rect(chica, colores[i], (x, repisa, 7, 5))
    # pizarrón con el menú (garabatos de tiza)
    pygame.draw.rect(chica, C["madera_oscura"], (182, 14, 46, 28))
    pygame.draw.rect(chica, C["pizarron"], (184, 16, 42, 24))
    for i, largo in enumerate((30, 22, 26)):
        pygame.draw.line(chica, C["tiza"], (188, 21 + i * 7), (188 + largo, 21 + i * 7))
    # lámparas colgantes
    for x in (76, 164):
        pygame.draw.line(chica, C["contorno"], (x, 0), (x, 10))
        pygame.draw.rect(chica, C["contorno"], (x - 7, 10, 15, 6))
        pygame.draw.rect(chica, C["dorado"], (x - 6, 11, 13, 4))
        pygame.draw.rect(chica, C["lampara"], (x - 4, 16, 9, 2))
    # plantita en maceta sobre la barra
    pygame.draw.rect(chica, C["contorno"], (218, 106, 14, 14))
    pygame.draw.rect(chica, C["caramelo"], (219, 107, 12, 12))
    for dx, dy in ((-4, -6), (0, -10), (4, -7), (8, -4), (-6, -2)):
        pygame.draw.rect(chica, C["planta"], (223 + dx, 102 + dy, 5, 5))
        pygame.draw.rect(chica, C["planta_oscura"], (223 + dx, 106 + dy, 5, 1))
    # la barra (mostrador) de madera
    pygame.draw.rect(chica, C["contorno"], (0, 118, ancho, alto - 118))
    pygame.draw.rect(chica, C["mesa"], (0, 119, ancho, 5))
    pygame.draw.rect(chica, C["barra"], (0, 124, ancho, alto - 124))
    for x in range(8, ancho, 16):
        pygame.draw.line(chica, C["tablas"], (x, 125), (x, alto))
    return pygame.transform.scale(chica, (ancho * PX, alto * PX))


# ---------------------------------------------------------------- cámara en pantalla
def dibujar_camara(pantalla, imagen, rect, punto, pellizco, fuente):
    """Dibuja la imagen de la cámara en 'rect', con la zona útil punteada y el punto del dedo.

    punto: (u, v) entre 0 y 1 dentro del cuadro, o None si no hay mano.
    """
    rect = pygame.Rect(rect)
    pygame.draw.rect(pantalla, C["contorno"], rect.inflate(PX * 2, PX * 2))
    if imagen is None:
        pygame.draw.rect(pantalla, C["cafe_oscuro"], rect)
        texto_centrado(pantalla, "Sin imagen", fuente, C["texto_claro"], rect.center)
        return
    pantalla.blit(imagen, rect)
    # zona útil: la parte del cuadro que se usa para mover la jarra (los bordes no hacen falta)
    zona = pygame.Rect(rect.x + rect.width * MARGEN_CAMARA_X, rect.y + rect.height * MARGEN_CAMARA_Y,
                       rect.width * (1 - 2 * MARGEN_CAMARA_X), rect.height * (1 - 2 * MARGEN_CAMARA_Y))
    for x in range(zona.left, zona.right, PX * 3):
        pygame.draw.rect(pantalla, C["dorado"], (x, zona.top, PX, 2))
        pygame.draw.rect(pantalla, C["dorado"], (x, zona.bottom, PX, 2))
    for y in range(zona.top, zona.bottom, PX * 3):
        pygame.draw.rect(pantalla, C["dorado"], (zona.left, y, 2, PX))
        pygame.draw.rect(pantalla, C["dorado"], (zona.right, y, 2, PX))
    if punto is not None:
        x = rect.x + int(punto[0] * rect.width)
        y = rect.y + int(punto[1] * rect.height)
        color = C["blanco"] if pellizco else C["acento"]
        pygame.draw.rect(pantalla, C["contorno"], (x - 7, y - 7, 14, 14))
        pygame.draw.rect(pantalla, color, (x - 5, y - 5, 10, 10))