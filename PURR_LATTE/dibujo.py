"""dibujo.py - Pixel art y piezas de la interfaz (paneles, textos, barras, estrellas, jarra, gato).

Igual que en Purr & Brew, los sprites son grillas de texto: cada letra es un pixel y una
paleta dice de qué color es cada letra. pixelar() convierte la grilla en una Surface
agrandada sin suavizar, así los pixeles quedan nítidos. El juego no usa imágenes externas.
"""
import math
import random
import pygame
from ajustes import (COLORES as C, PX, PX_JARRA, PX_PATA, COLOR_OJOS_BARISTA,
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


def dibujar_boton(pantalla, rect, texto, fuente, encima, color=None):
    """Dibuja un botón pixel art (se aclara y "sube" un poquito con el mouse encima). Devuelve su Rect."""
    rect = pygame.Rect(rect)
    color = color or C["dorado"]
    if encima:
        color = aclarar(color, 0.35)
        rect = rect.move(0, -2)
    # la sombrita de abajo hace que parezca un botón que se puede apretar
    pygame.draw.rect(pantalla, C["contorno"], rect.move(0, PX).inflate(-PX * 2, 0))
    dibujar_panel(pantalla, rect, color, C["contorno"])
    if texto:
        texto_centrado(pantalla, texto, fuente, C["texto"], rect.center)
    return rect


def dibujar_boton_pantalla_completa(pantalla, rect, encima):
    """Botón cuadrado con el ícono de pantalla completa (cuatro esquinitas)."""
    rect = dibujar_boton(pantalla, rect, "", None, encima, C["panel"])
    x, y, w, h = rect.inflate(-PX * 5, -PX * 5)
    largo = PX * 2
    for cx, cy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        pygame.draw.rect(pantalla, C["texto"], (min(cx, cx + dx * largo), cy - (PX if dy < 0 else 0), largo, PX))
        pygame.draw.rect(pantalla, C["texto"], (cx - (PX if dx < 0 else 0), min(cy, cy + dy * largo), PX, largo))


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
    "OOOO..................",
    "OWWWOOOOOOOOOOOOOO....",
    ".OWWMMMMMMMMMMMMMMO...",
    "..OOMMMMMMMMMMMMMMO...",
    "...OMSSMMMMMMMMMMMOOOO",
    "...OMSSMMMMMMMMMMMO..O",
    "...OMSMMMMMMMMMMMMO..O",
    "...OMSMMMMMMMMMMMMO..O",
    "...OMSMMMMMMMMMMMMO..O",
    "...OMSMMMMMMMMMMMMO..O",
    "...OMMMMMMMMMMMMMMOOOO",
    "...OMMMMMMMMMMMMMMO...",
    "...OKKKKKKKKKKKKKKO...",
    "....OOOOOOOOOOOOOO....",
)
# La patita del gato que agarra el asa, vista de frente: cuatro deditos de pelo, cada uno con
# su almohadilla rosa, y la almohadilla grande abajo. Así se reconoce al toque que es una pata.
# (P = pelaje, B = almohadillas rosas, Q = borde oscuro)
_PATA = (
    "....QQQQ..QQQQ....",
    "...QPPPPQQPPPPQ...",
    "...QPBBPQQPBBPQ...",
    "...QPBBPQQPBBPQ...",
    ".QQQQPPQQQQPPQQQQ.",
    "QPPPPQQPPPPQQPPPPQ",
    "QPBBPQPPPPPPQPBBPQ",
    "QPBBPQPPPPPPQPBBPQ",
    ".QPPQPPPPPPPPQPPQ.",
    "..QQPPPPPPPPPPQQ..",
    "..QPPPPBBBBPPPPQ..",
    "..QPPPBBBBBBPPPQ..",
    "..QPPBBBBBBBBPPQ..",
    "..QPPBBBBBBBBPPQ..",
    "...QPPBBBBBBPPQ...",
    "....QQPPPPPPQQ....",
    "......QQQQQQ......",
)
# Dónde va la patita sobre la jarra (en pixeles de pantalla): encima del asa, a la derecha.
POS_PATA_EN_JARRA = (86, 12)


def sprite_jarra_con_pata(pelaje):
    """Arma y devuelve la jarra con la patita del color 'pelaje', en una sola Surface.

    La jarra y la patita se pixelan cada una con su tamaño (PX_JARRA y PX_PATA) y después
    pego la patita encima del asa. Así puedo achicar la patita sin achicar la jarra.
    """
    paleta = {"O": C["contorno"], "M": C["metal"], "S": C["blanco"], "K": C["metal_oscuro"],
              "W": C["leche"], "P": pelaje, "B": C["almohadilla"], "Q": oscurecer(pelaje, 0.4)}
    jarra = pixelar(_JARRA, paleta, PX_JARRA)
    pata = pixelar(_PATA, paleta, PX_PATA)
    ancho = max(jarra.get_width(), POS_PATA_EN_JARRA[0] + pata.get_width())
    alto = max(jarra.get_height(), POS_PATA_EN_JARRA[1] + pata.get_height())
    junta = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    junta.blit(jarra, (0, 0))
    junta.blit(pata, POS_PATA_EN_JARRA)
    return junta
_PICO_JARRA = (1.5, 1.5)      # el pixel 'W' de la punta del pico, en pixeles del arte


def dibujar_jarra(pantalla, destino, vertiendo, pelaje, elevacion):
    """Dibuja la jarrita (agarrada por la pata del color elegido) con el pico sobre 'destino'.

    elevacion: cuántos pixeles por encima del café está el pico (jarra alta o baja).
    Al verter se inclina. Para que el pico quede en el lugar correcto aunque la jarra gire,
    giro también el vector que va del centro del sprite al pico.
    """
    # la armo una sola vez por color y la guardo (como hace pixelar con los sprites)
    clave = ("jarra", tuple(pelaje))
    if clave not in _sprites_armados:
        _sprites_armados[clave] = sprite_jarra_con_pata(pelaje)
    sprite = _sprites_armados[clave]
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


# ---------------------------------------------------------------- adornos de la portada
def pintar_cielo(superficie, rect):
    """Pinta un cielo pixel art: 4 franjas de color (de celeste a durazno) y, entre franja y
    franja, dos filas de "tramado" (pixeles alternados como un tablero de ajedrez) que hacen
    que el cambio se vea suave sin dejar de ser pixel art.
    """
    x, y, ancho, alto = rect
    colores = [C["cielo_arriba"], C["cielo"], C["cielo_claro"], C["cielo_horizonte"]]
    alto_franja = alto / len(colores)
    for fila in range(alto):
        franja = min(len(colores) - 1, int(fila / alto_franja))
        # ¿estoy en las 2 últimas filas de la franja? Ahí va el tramado con el color de abajo
        en_borde = franja < len(colores) - 1 and fila >= (franja + 1) * alto_franja - 2
        for columna in range(ancho):
            color = colores[franja]
            if en_borde and (columna + fila) % 2 == 0:
                color = colores[franja + 1]
            superficie.set_at((x + columna, y + fila), color)


def crear_cafetera():
    """Arma y devuelve la cafetera espresso de la barra (pixel art), agrandada PX veces."""
    chica = pygame.Surface((30, 28), pygame.SRCALPHA)
    borde = C["contorno"]
    # dos tacitas arriba (las cafeteras de verdad las tienen ahí para que estén calentitas)
    for x in (6, 16):
        pygame.draw.rect(chica, borde, (x, 0, 8, 5))
        pygame.draw.rect(chica, C["taza"], (x + 1, 1, 6, 3))
    # cuerpo de metal con su brillo
    pygame.draw.rect(chica, borde, (1, 5, 28, 17))
    pygame.draw.rect(chica, C["metal"], (2, 6, 26, 15))
    pygame.draw.rect(chica, C["blanco"], (3, 7, 2, 12))
    # dos relojitos de presión y la plaquita dorada
    for x in (9, 18):
        pygame.draw.circle(chica, borde, (x + 2, 10), 3)
        pygame.draw.circle(chica, C["blanco"], (x + 2, 10), 2)
        chica.set_at((x + 2, 9), borde)
    pygame.draw.rect(chica, C["brillo_dorado"], (12, 15, 6, 2))
    # grupo y portafiltro (el "mango" negro), con un hilito de café cayendo en la tacita
    pygame.draw.rect(chica, borde, (11, 18, 8, 3))
    pygame.draw.rect(chica, borde, (19, 19, 8, 2))
    pygame.draw.line(chica, C["cafe_oscuro"], (15, 21), (15, 23))
    # bandeja de abajo con la tacita
    pygame.draw.rect(chica, borde, (1, 25, 28, 3))
    pygame.draw.rect(chica, C["metal_oscuro"], (2, 25, 26, 2))
    pygame.draw.rect(chica, borde, (12, 22, 7, 4))
    pygame.draw.rect(chica, C["taza"], (13, 23, 5, 2))
    return pygame.transform.scale(chica, (30 * PX, 28 * PX))


def dibujar_banderines(pantalla, y, t):
    """Dibuja una guirnalda de banderines de concurso de lado a lado (se mueven apenas, con el aire)."""
    colores = (C["menta"], C["dorado"], C["azul"], C["taza"], C["verde"])
    pygame.draw.line(pantalla, C["contorno"], (0, y), (ANCHO, y), 2)
    for i, x in enumerate(range(8, ANCHO, 48)):
        vaiven = round(math.sin(t * 2 + i) * 2)
        punta = (x + 16 + vaiven, y + 34)
        pygame.draw.polygon(pantalla, C["contorno"], [(x - 2, y), (x + 34, y), (punta[0], punta[1] + 3)])
        pygame.draw.polygon(pantalla, colores[i % len(colores)], [(x + 2, y + 2), (x + 30, y + 2), punta])


def dibujar_ventana_abierta(pantalla, t):
    """Dibuja (encima del fondo) la ventana de la cafetería abierta, con las nubes pasando
    despacito y las cortinas que se mueven apenas con el viento. Va en todas las pantallas
    con el fondo de la cafetería.

    Se dibuja en chiquito (pixeles del arte) en cada cuadro y después se agranda: así las
    cortinas se mueven "de a pixel", como pixel art.
    """
    ancho, alto = 60, 52
    origen = (4, 34)                              # dónde va, en pixeles del arte de la pantalla
    chica = pygame.Surface((ancho, alto))
    # 1) pared con las rayas del papel tapiz (el pedacito de pared que queda alrededor)
    chica.fill(C["pared"])
    for x in range(0, 64, 8):
        pygame.draw.rect(chica, C["papel_rayas"], (x - origen[0], 0, 2, alto))
    # 2) el hueco de la ventana: cielo, sol y dos nubes que cruzan muy despacio
    pygame.draw.rect(chica, C["contorno"], (6, 6, 44, 40))
    pintar_cielo(chica, (8, 8, 40, 36))
    pygame.draw.circle(chica, C["sol"], (29, 19), 6)
    for i, y in enumerate((14, 32)):
        x = 8 + int(t * 2 + i * 22) % 48 - 6        # avanza y, cuando sale por un lado, entra por el otro
        recorte = chica.get_clip()
        chica.set_clip((8, 8, 40, 36))            # que las nubes no se salgan del vidrio
        pygame.draw.rect(chica, C["nube"], (x, y, 10, 3))
        pygame.draw.rect(chica, C["nube"], (x + 2, y - 2, 5, 2))
        chica.set_clip(recorte)
    # 3) las dos hojas de vidrio abiertas hacia adentro, contra los costados del marco.
    #    Se ven enteras (de arriba a abajo) y angostitas, porque están de costado: así se
    #    entiende que la ventana está abierta y en el medio no hay vidrio, solo cielo.
    for x, adentro in ((8, 1), (40, -1)):
        pygame.draw.rect(chica, C["blanco"], (x, 8, 8, 36))                  # marco de la hoja
        pygame.draw.rect(chica, C["cielo_claro"], (x + 1, 9, 6, 34))          # vidrio
        pygame.draw.line(chica, C["blanco"], (x + 1, 26), (x + 6, 26))        # travesaño
        # brillo del vidrio (una rayita en diagonal) y una sombrita del lado de adentro
        pygame.draw.line(chica, C["blanco"], (x + 2, 14), (x + 4, 11))
        pygame.draw.line(chica, C["blanco"], (x + 2, 34), (x + 4, 31))
        borde_sombra = x + 7 if adentro == 1 else x
        pygame.draw.line(chica, C["papel_rayas"], (borde_sombra, 8), (borde_sombra, 43))
    # 4) cortinas afuera del marco: arriba quedan fijas en el barral y abajo se mecen poquito.
    #    Las dos se corren JUNTAS para el mismo lado, como cuando entra una brisa.
    vaiven = round(math.sin(t * 1.6) * 1.6)        # entre -2 y 2 pixeles: poquito
    for borde in (0, 50):
        forma = [(borde, 4), (borde + 6, 4), (borde + 6 + vaiven, 48), (borde + vaiven, 48)]
        pygame.draw.polygon(chica, C["cortina"], forma)
        pygame.draw.line(chica, oscurecer(C["cortina"], 0.85), (borde + 3, 5), (borde + 3 + vaiven, 47))
    # 5) el barral de madera arriba
    pygame.draw.rect(chica, C["madera_oscura"], (0, 2, 58, 3))
    pantalla.blit(pygame.transform.scale(chica, (ancho * PX, alto * PX)), (origen[0] * PX, origen[1] * PX))


def dibujar_vapor(pantalla, centro_x, base_y, t):
    """Dibuja tres hilitos de vapor que suben ondulando desde el café (se ve que está calentito)."""
    capa = pygame.Surface((120, 90), pygame.SRCALPHA)
    for i, dx in enumerate((24, 60, 96)):
        for paso in range(8):
            # cada cuadradito sube con el tiempo y se va borrando a medida que sube
            altura = (paso * 11 + t * 30 + i * 17) % 88
            x = dx + round(math.sin(altura / 12 + i) * 6)
            transparencia = int(235 * (1 - altura / 88))
            # un borde gris clarito alrededor para que el vapor se vea también contra la pared clara
            y = int(88 - altura) // PX * PX
            capa.fill((150, 170, 165, transparencia // 2), (x // PX * PX - 1, y - 1, PX + 2, PX * 2 + 2))
            capa.fill((255, 255, 255, transparencia), (x // PX * PX, y, PX, PX * 2))
    pantalla.blit(capa, (centro_x - 60, base_y - 88))


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
    (papel tapiz, estantes con tacitas, lámparas, pizarrón y la barra). La ventana se dibuja
    aparte, encima, porque tiene las cortinas moviéndose.
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
    # (la ventana no va acá: se dibuja aparte, animada, con dibujar_ventana_abierta)
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
def dibujar_camara(pantalla, imagen, rect, dedos, pellizco, fuente):
    """Dibuja la imagen de la cámara en 'rect', con la zona útil punteada, las puntas del pulgar
    y del índice unidas por una línea, y el punto del medio (donde está la jarra).

    dedos: ((u, v) del pulgar, (u, v) del índice), entre 0 y 1 dentro del cuadro, o None.
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
    if dedos is None:
        return
    pulgar = (rect.x + int(dedos[0][0] * rect.width), rect.y + int(dedos[0][1] * rect.height))
    indice = (rect.x + int(dedos[1][0] * rect.width), rect.y + int(dedos[1][1] * rect.height))
    medio = ((pulgar[0] + indice[0]) // 2, (pulgar[1] + indice[1]) // 2)
    # si hay pellizco todo se pone blanco (como la leche): se ve clarito que está vertiendo
    color = C["blanco"] if pellizco else C["dorado"]
    pygame.draw.line(pantalla, C["contorno"], pulgar, indice, 5)
    pygame.draw.line(pantalla, color, pulgar, indice, 2)
    for x, y in (pulgar, indice):
        pygame.draw.rect(pantalla, C["contorno"], (x - 5, y - 5, 10, 10))
        pygame.draw.rect(pantalla, color, (x - 3, y - 3, 6, 6))
    pygame.draw.rect(pantalla, C["contorno"], (medio[0] - 7, medio[1] - 7, 14, 14))
    pygame.draw.rect(pantalla, C["blanco"] if pellizco else C["acento"], (medio[0] - 5, medio[1] - 5, 10, 10))