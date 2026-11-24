"""dibujo.py - Pixel art y piezas de la interfaz (paneles, textos, barras, estrellas, jarra, gato).

Igual que en Purr & Brew, los sprites son grillas de texto: cada letra es un pixel y una
paleta dice de qué color es cada letra. pixelar() convierte la grilla en una Surface
agrandada sin suavizar, así los pixeles quedan nítidos. El juego no usa imágenes externas.
"""
import random
import pygame
from ajustes import (COLORES as C, PX, PX_JARRA, COLOR_BARISTA, COLOR_OJOS_BARISTA, ELEVACION_JARRA,
                     ANGULO_VERTER, ANCHO, ALTO, MARGEN_CAMARA_X, MARGEN_CAMARA_Y)


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


# ---------------------------------------------------------------- jarra de leche
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
_PICO_JARRA = (1.5, 1.5)      # el pixel 'W' de la punta del pico, en pixeles del arte


def dibujar_jarra(pantalla, destino, vertiendo):
    """Dibuja la jarrita de metal con el pico justo encima del punto donde cae la leche.

    Al verter se inclina. Para que el pico quede en el lugar correcto aunque la jarra gire,
    giro también el vector que va del centro del sprite al pico.
    """
    paleta = {"O": C["contorno"], "M": C["metal"], "S": C["blanco"], "K": C["metal_oscuro"],
              "W": C["leche"]}
    sprite = pixelar(_JARRA, paleta, PX_JARRA)
    angulo = ANGULO_VERTER if vertiendo else 0
    girado = pygame.transform.rotate(sprite, angulo)
    centro_sprite = pygame.Vector2(sprite.get_width() / 2, sprite.get_height() / 2)
    pico = pygame.Vector2(_PICO_JARRA[0] * PX_JARRA, _PICO_JARRA[1] * PX_JARRA)
    # pygame.transform.rotate gira en sentido antihorario y Vector2.rotate al revés (la y va
    # para abajo en pantalla), por eso uso el ángulo con signo cambiado.
    desde_centro = (pico - centro_sprite).rotate(-angulo)
    punta = pygame.Vector2(destino[0], destino[1] - ELEVACION_JARRA)
    pantalla.blit(girado, girado.get_rect(center=punta - desde_centro))


def dibujar_mira(pantalla, destino, vertiendo):
    """Dibuja la mira (4 cuadraditos) que marca dónde va a caer la leche."""
    x = int(destino[0]) // PX * PX
    y = int(destino[1]) // PX * PX
    color = C["leche"] if vertiendo else C["acento"]
    for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
        caja = (x + dx * PX, y + dy * PX, PX, PX)
        pygame.draw.rect(pantalla, C["contorno"], pygame.Rect(caja).inflate(2, 2))
        pygame.draw.rect(pantalla, color, caja)


# ---------------------------------------------------------------- gato barista (el de Purr & Brew)
_GATO = (
    "..OO........OO..",
    ".OFFO......OFFO.",
    ".OFPFOOOOOOFPFO.",
    ".OFFFFFFFFFFFFO.",
    ".OFFFFFFFFFFFFO.",
    ".OFFEEFFFFEEFFO.",
    ".OFFEEFFFFEEFFO.",
    ".OFFFFFNNFFFFFO.",
    ".OFFFLLLLLLFFFO.",
    "..OFFFFFFFFFFO..",
    "...OOOOOOOOOO...",
    "...OFFWWWWFFO...",
    "...OAAAAAAAAO...",
    "...OAAWWWWAAO...",
    "...OAAWWWWAAO...",
    "...OSSSOOSSSO...",
    "....OOO..OOO....",
)


def dibujar_gato_barista(pantalla, pie, px, mirando=1):
    """Dibuja al gato barista naranja con su delantal celeste, parado con los pies en 'pie'."""
    paleta = {"O": oscurecer(COLOR_BARISTA, 0.38), "F": COLOR_BARISTA, "L": aclarar(COLOR_BARISTA, 0.55),
              "E": COLOR_OJOS_BARISTA, "P": C["nariz"], "N": C["nariz"], "W": C["blanco"],
              "A": C["delantal_celeste"], "S": COLOR_BARISTA}
    sprite = pixelar(_GATO, paleta, px)
    if mirando < 0:
        sprite = pygame.transform.flip(sprite, True, False)
    rect = sprite.get_rect(midbottom=pie)
    sombra = pygame.Rect(0, 0, 14 * px, 3 * px)
    sombra.center = (rect.centerx, rect.bottom)
    pygame.draw.ellipse(pantalla, oscurecer(C["mesa"], 0.85), sombra)
    pantalla.blit(sprite, rect)


# ---------------------------------------------------------------- fondo (se arma UNA vez)
def crear_fondo_mesa():
    """Arma y devuelve el fondo del juego: una mesa de madera vista desde arriba, con detalles.

    Se dibuja en chiquito (un pixel = un pixel del arte) y después se agranda PX veces.
    """
    azar = random.Random(4)                 # semilla fija: el fondo sale igual siempre
    ancho, alto = ANCHO // PX, ALTO // PX
    chica = pygame.Surface((ancho, alto))
    alto_tabla = 10
    for fila in range(0, alto, alto_tabla):
        color = C["mesa"] if (fila // alto_tabla) % 2 == 0 else oscurecer(C["mesa"], 0.95)
        pygame.draw.rect(chica, color, (0, fila, ancho, alto_tabla))
        pygame.draw.line(chica, C["barra"], (0, fila), (ancho, fila))           # junta entre tablas
        corte = azar.randint(20, ancho - 20)
        pygame.draw.line(chica, C["barra"], (corte, fila), (corte, fila + alto_tabla - 1))
        for _ in range(3):                                                       # vetas de la madera
            x = azar.randint(0, ancho - 12)
            y = fila + azar.randint(3, alto_tabla - 3)
            pygame.draw.line(chica, oscurecer(color, 0.92), (x, y), (x + azar.randint(4, 12), y))
    # granos de café sueltos en la mesa
    for x, y in ((150, 140), (156, 144), (152, 150), (8, 150), (14, 146), (152, 30), (6, 40)):
        pygame.draw.rect(chica, C["cafe_oscuro"], (x, y, 3, 2))
        chica.set_at((x + 1, y), C["caramelo"])
    return pygame.transform.scale(chica, (ancho * PX, alto * PX))


def crear_fondo_cafeteria():
    """Arma y devuelve el fondo de las pantallas de menú: la pared menta de la cafetería y la barra."""
    ancho, alto = ANCHO // PX, ALTO // PX
    chica = pygame.Surface((ancho, alto))
    chica.fill(C["pared"])
    for x in range(0, ancho, 12):                                 # papel tapiz a rayas
        pygame.draw.line(chica, C["menta"], (x, 0), (x, alto))
    pygame.draw.rect(chica, C["zocalo"], (0, 112, ancho, 4))       # zócalo
    pygame.draw.rect(chica, C["barra"], (0, 116, ancho, alto - 116))
    pygame.draw.rect(chica, C["mesa"], (0, 116, ancho, 6))         # tapa de la barra
    for x in range(0, ancho, 20):                                 # tablas del mostrador
        pygame.draw.line(chica, C["tablas"], (x, 122), (x, alto))
    # estante con tacitas
    pygame.draw.rect(chica, C["madera_oscura"], (14, 66, 56, 3))
    for i, color in enumerate((C["taza"], C["menta"], C["azul"])):
        pygame.draw.rect(chica, C["contorno"], (18 + i * 17, 58, 10, 8))
        pygame.draw.rect(chica, color, (19 + i * 17, 59, 8, 6))
    # plantita en maceta
    pygame.draw.rect(chica, C["contorno"], (218, 96, 14, 16))
    pygame.draw.rect(chica, C["caramelo"], (219, 97, 12, 14))
    for dx, dy in ((-4, -6), (0, -10), (4, -7), (8, -4), (-6, -2)):
        pygame.draw.rect(chica, C["planta"], (223 + dx, 92 + dy, 5, 5))
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
