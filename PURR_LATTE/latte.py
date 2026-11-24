"""latte.py - La taza: el café, el dibujo guía, la leche vertida y el puntaje.

Idea del puntaje (simple a propósito):
  - Todo se dibuja en un "lienzo" chiquito (TAM_LIENZO x TAM_LIENZO pixeles del arte).
    Cada pixel del lienzo es una celda.
  - El dibujo (corazón, tulipán...) se pinta en una Surface y de ahí saco una MÁSCARA:
    qué celdas son parte del dibujo.
  - La leche que va cayendo se pinta en otra Surface, y de ahí otra máscara.
  - cubiertas = celdas que están en las dos máscaras a la vez (overlap_area).
  - % = cubiertas / total del dibujo - penalización por las celdas con leche fuera del dibujo.
"""
import random
import pygame
from ajustes import (COLORES as C, PX, TAM_LIENZO, CENTRO_LIENZO, POS_LIENZO, RADIO_PLATO,
                     RADIO_TAZA, RADIO_CAFE, SEPARACION_GUIA, COLOR_GUIA, PENALIZACION_FUERA,
                     UMBRALES_ESTRELLAS, LIMITE_DESBORDE)


# ---------------------------------------------------------------- funciones sueltas
def calcular_estrellas(porcentaje):
    """Devuelve cuántas estrellas (0 a 3) vale un porcentaje, según UMBRALES_ESTRELLAS."""
    estrellas = 0
    for umbral in UMBRALES_ESTRELLAS:
        if porcentaje >= umbral:
            estrellas += 1
    return estrellas


def punto(u, v):
    """Pasa un punto del dibujo (u, v entre -1 y 1, relativos al radio del café) al lienzo.

    Devuelve (x, y) en pixeles del lienzo. Así los dibujos no dependen del tamaño de la taza.
    """
    return (CENTRO_LIENZO + u * RADIO_CAFE, CENTRO_LIENZO + v * RADIO_CAFE)


def elipse(superficie, color, u, v, ancho, alto):
    """Dibuja una elipse centrada en (u, v) con ancho y alto relativos al radio del café."""
    x, y = punto(u - ancho / 2, v - alto / 2)
    pygame.draw.ellipse(superficie, color, (round(x), round(y), round(ancho * RADIO_CAFE),
                                            round(alto * RADIO_CAFE)))


def poligono(superficie, color, puntos_uv):
    """Dibuja un polígono a partir de una lista de puntos (u, v)."""
    pygame.draw.polygon(superficie, color, [punto(u, v) for u, v in puntos_uv])


def tallo(superficie, color, v_arriba, v_abajo, ancho):
    """Dibuja el palito vertical del medio (el 'tallo' del tulipán y de la rosetta)."""
    elipse(superficie, color, 0, (v_arriba + v_abajo) / 2, ancho, v_abajo - v_arriba)


def media_luna(superficie, color, u, v, ancho, alto, corrimiento):
    """Dibuja una 'media luna': una elipse a la que le saco otra elipse igual de alta pero más
    angosta y corrida hacia arriba. Así se forman las capas del tulipán y de la rosetta.
    """
    elipse(superficie, color, u, v, ancho, alto)
    elipse(superficie, (0, 0, 0, 0), u, v - corrimiento, ancho * 0.8, alto)


# ---------------------------------------------------------------- los 5 dibujos
# Cada función pinta su dibujo con figuras simples (círculos, elipses y polígonos) en blanco.
# Lo que se pinta con TRANSPARENTE queda como "agujero" (por ejemplo, los ojos del gato).
# Están en el orden en que los aprenden los baristas, del más fácil al más difícil.
def dibujar_corazon(sup, color):
    """Corazón: dos círculos arriba y un triángulo que baja hasta la punta."""
    elipse(sup, color, -0.30, -0.20, 0.72, 0.72)
    elipse(sup, color, 0.30, -0.20, 0.72, 0.72)
    poligono(sup, color, [(-0.64, -0.10), (0.64, -0.10), (0.0, 0.68)])


def dibujar_tulipan(sup, color):
    """Tulipán: tres capas apiladas (cada una 'empuja' a la anterior) y una línea por el medio.

    Se dibuja de abajo hacia arriba: cada capa nueva se apoya adentro del hueco de la anterior,
    igual que cuando el barista vierte un círculo, después otro encima, y otro.
    """
    media_luna(sup, color, 0.0, 0.40, 1.30, 0.62, 0.20)
    media_luna(sup, color, 0.0, 0.12, 1.00, 0.52, 0.17)
    # arriba de todo, un corazoncito
    elipse(sup, color, -0.14, -0.30, 0.34, 0.32)
    elipse(sup, color, 0.14, -0.30, 0.34, 0.32)
    poligono(sup, color, [(-0.30, -0.26), (0.30, -0.26), (0.0, 0.0)])
    tallo(sup, color, -0.36, 0.72, 0.08)


def dibujar_rosetta(sup, color):
    """Rosetta: una hoja de helecho hecha con siete capas finitas, anchas abajo y angostas arriba,
    un tallo que la corta por el medio y un corazoncito en la punta.
    """
    # (altura, ancho) de cada capa: la hoja es más ancha cerca de la base y se afina arriba
    capas = [(0.62, 1.00), (0.44, 1.22), (0.26, 1.28), (0.08, 1.20), (-0.10, 1.04), (-0.28, 0.82),
             (-0.44, 0.58)]
    for v, ancho in capas:
        media_luna(sup, color, 0.0, v, ancho, 0.32, 0.15)
    elipse(sup, color, 0.0, -0.62, 0.26, 0.20)
    tallo(sup, color, -0.62, 0.84, 0.08)


def dibujar_cisne(sup, color):
    """Cisne: media rosetta de costado (el ala), un cuello curvo y un corazoncito de cabeza."""
    alas = [(-0.10, 0.52, 1.00), (-0.20, 0.32, 0.84), (-0.28, 0.14, 0.68), (-0.34, -0.02, 0.52)]
    for u, v, ancho in alas:
        media_luna(sup, color, u, v, ancho, 0.30, 0.13)
    # El cuello es una línea gruesa que pasa por estos puntos (una curva como una S suave).
    cuello = [(0.38, 0.54), (0.48, 0.38), (0.52, 0.22), (0.50, 0.06), (0.44, -0.08),
              (0.36, -0.20), (0.30, -0.32), (0.28, -0.46)]
    pygame.draw.lines(sup, color, False, [punto(u, v) for u, v in cuello], round(0.15 * RADIO_CAFE))
    for u, v in cuello:
        elipse(sup, color, u, v, 0.15, 0.15)     # circulitos en las uniones para que no queden puntas
    # cabeza: un corazoncito chico mirando a la izquierda, con el pico
    elipse(sup, color, 0.20, -0.56, 0.26, 0.24)
    poligono(sup, color, [(0.10, -0.62), (-0.06, -0.56), (0.10, -0.50)])


def dibujar_gato(sup, color):
    """Cara de gato: cabeza redonda, dos orejas triangulares y los ojos como agujeros."""
    elipse(sup, color, 0.0, 0.12, 1.24, 1.00)
    poligono(sup, color, [(-0.60, -0.08), (-0.50, -0.74), (-0.10, -0.34)])
    poligono(sup, color, [(0.60, -0.08), (0.50, -0.74), (0.10, -0.34)])
    agujero = (0, 0, 0, 0)
    elipse(sup, agujero, -0.25, 0.06, 0.24, 0.24)
    elipse(sup, agujero, 0.25, 0.06, 0.24, 0.24)


DIBUJOS = {
    "corazon": dibujar_corazon,
    "tulipan": dibujar_tulipan,
    "rosetta": dibujar_rosetta,
    "cisne": dibujar_cisne,
    "gato": dibujar_gato,
}


def crear_forma(nombre):
    """Devuelve una Surface del tamaño del lienzo con el dibujo pedido pintado en blanco."""
    forma = pygame.Surface((TAM_LIENZO, TAM_LIENZO), pygame.SRCALPHA)
    DIBUJOS[nombre](forma, C["blanco"])
    return forma


def celdas_del_borde(mascara):
    """Devuelve la lista de celdas del dibujo que tocan una celda vacía (el contorno).

    Recorro todo el lienzo: si una celda es del dibujo y alguna vecina no, es borde.
    Lo hago a mano (y no con mask.outline) para que también salga el borde de los agujeros.
    """
    borde = []
    ancho, alto = mascara.get_size()
    for y in range(1, alto - 1):
        for x in range(1, ancho - 1):
            if mascara.get_at((x, y)):
                vecinas = (mascara.get_at((x + 1, y)), mascara.get_at((x - 1, y)),
                           mascara.get_at((x, y + 1)), mascara.get_at((x, y - 1)))
                if not all(vecinas):
                    borde.append((x, y))
    return borde


# ---------------------------------------------------------------- la clase Taza
class Taza:
    """Una taza de café con su dibujo guía, la leche que le vas echando y su puntaje."""

    def __init__(self, nombre_dibujo):
        """Prepara todas las superficies de la ronda: base, guía, leche y la máscara del dibujo."""
        self.nombre_dibujo = nombre_dibujo
        self.base = self.crear_base()
        # máscara del dibujo: lo que quede fuera del café no cuenta (por si un dibujo se pasa)
        circulo = pygame.Surface((TAM_LIENZO, TAM_LIENZO), pygame.SRCALPHA)
        pygame.draw.circle(circulo, C["blanco"], (CENTRO_LIENZO, CENTRO_LIENZO), RADIO_CAFE)
        mascara_forma = pygame.mask.from_surface(crear_forma(nombre_dibujo))
        self.mascara_dibujo = mascara_forma.overlap_mask(pygame.mask.from_surface(circulo), (0, 0))
        self.total_dibujo = self.mascara_dibujo.count()
        self.guia = self.crear_guia()
        # acá se va pintando la leche (empieza transparente)
        self.leche = pygame.Surface((TAM_LIENZO, TAM_LIENZO), pygame.SRCALPHA)
        self.lienzo = pygame.Surface((TAM_LIENZO, TAM_LIENZO), pygame.SRCALPHA)
        self.azar = random.Random()
        self.porcentaje = 0
        self.fuera = 0              # celdas con leche que NO son del dibujo

    def crear_base(self):
        """Dibuja y devuelve el plato, la taza y el café (lo que no cambia durante la ronda)."""
        base = pygame.Surface((TAM_LIENZO, TAM_LIENZO), pygame.SRCALPHA)
        centro = (CENTRO_LIENZO, CENTRO_LIENZO)
        # plato
        pygame.draw.circle(base, C["contorno"], centro, RADIO_PLATO)
        pygame.draw.circle(base, C["plato_sombra"], centro, RADIO_PLATO - 1)
        pygame.draw.circle(base, C["plato"], (CENTRO_LIENZO - 1, CENTRO_LIENZO - 2), RADIO_PLATO - 3)
        # asa de la taza (a la derecha)
        asa = pygame.Rect(0, 0, 16, 14)
        asa.midleft = (CENTRO_LIENZO + RADIO_TAZA - 4, CENTRO_LIENZO)
        pygame.draw.rect(base, C["contorno"], asa, border_radius=5)
        pygame.draw.rect(base, C["taza"], asa.inflate(-2, -2), border_radius=4)
        pygame.draw.rect(base, C["plato"], asa.inflate(-8, -8), border_radius=2)
        # taza: borde, loza y una sombra adentro
        pygame.draw.circle(base, C["contorno"], centro, RADIO_TAZA + 1)
        pygame.draw.circle(base, C["taza"], centro, RADIO_TAZA)
        pygame.draw.circle(base, C["taza_sombra"], centro, RADIO_CAFE + 2)
        # café con su crema: anillo oscuro en el borde y pintitas más claras (semilla fija)
        pygame.draw.circle(base, C["cafe_oscuro"], centro, RADIO_CAFE)
        pygame.draw.circle(base, C["cafe"], centro, RADIO_CAFE - 2)
        azar = random.Random(9)
        for _ in range(140):
            x = azar.randint(-RADIO_CAFE, RADIO_CAFE)
            y = azar.randint(-RADIO_CAFE, RADIO_CAFE)
            if x * x + y * y < (RADIO_CAFE - 4) ** 2:
                base.set_at((CENTRO_LIENZO + x, CENTRO_LIENZO + y), C["caramelo"])
        return base

    def crear_guia(self):
        """Devuelve una Surface con el contorno del dibujo punteado y tenue."""
        guia = pygame.Surface((TAM_LIENZO, TAM_LIENZO), pygame.SRCALPHA)
        puestos = set()
        s = SEPARACION_GUIA
        for x, y in celdas_del_borde(self.mascara_dibujo):
            # Para que quede punteado en cualquier dirección (también en diagonal), pongo un
            # puntito solo si no hay otro puntito ya puesto en el cuadradito de alrededor.
            cerca = False
            for dx in range(-s, s + 1):
                for dy in range(-s, s + 1):
                    if (x + dx, y + dy) in puestos:
                        cerca = True
            if not cerca:
                puestos.add((x, y))
                guia.set_at((x, y), COLOR_GUIA)
        return guia

    # ------------------------------------------------------------ leche
    def a_lienzo(self, pos_pantalla):
        """Convierte una posición de la pantalla a coordenadas del lienzo. Devuelve (x, y) enteros."""
        return (int((pos_pantalla[0] - POS_LIENZO[0]) // PX), int((pos_pantalla[1] - POS_LIENZO[1]) // PX))

    def agregar_espuma(self, pos_pantalla, radio):
        """Pinta un círculo de espuma en el lugar donde cayó (o se está abriendo) una gota."""
        x, y = self.a_lienzo(pos_pantalla)
        # si cae fuera del lienzo (en la mesa), esa leche se pierde y no se dibuja
        if 0 <= x < TAM_LIENZO and 0 <= y < TAM_LIENZO:
            # casi toda la espuma blanca y un poco más cremosa, para que tenga textura
            color = C["leche"] if self.azar.random() < 0.85 else C["espuma"]
            pygame.draw.circle(self.leche, color, (x, y), radio)

    def calcular_puntaje(self):
        """Calcula y devuelve el porcentaje (0 a 100) comparando la máscara de leche con la del dibujo."""
        mascara_leche = pygame.mask.from_surface(self.leche)
        cubiertas = self.mascara_dibujo.overlap_area(mascara_leche, (0, 0))
        self.fuera = mascara_leche.count() - cubiertas
        cobertura = cubiertas / self.total_dibujo
        penalizacion = PENALIZACION_FUERA * self.fuera / self.total_dibujo
        porcentaje = round((cobertura - penalizacion) * 100)
        self.porcentaje = max(0, min(100, porcentaje))
        return self.porcentaje

    def fraccion_fuera(self):
        """Devuelve la leche fuera del dibujo como fracción del tamaño del dibujo (1 = un dibujo entero)."""
        return self.fuera / self.total_dibujo

    def hay_desborde(self):
        """Devuelve True si se tiró muchísima leche afuera del dibujo (pierde la ronda)."""
        return self.fraccion_fuera() > LIMITE_DESBORDE

    # ------------------------------------------------------------ dibujo
    def dibujar(self, pantalla, con_guia=True, pos=POS_LIENZO, px=PX):
        """Arma el lienzo (base + leche + guía) y lo dibuja agrandado en la pantalla."""
        self.lienzo.fill((0, 0, 0, 0))
        self.lienzo.blit(self.base, (0, 0))
        self.lienzo.blit(self.leche, (0, 0))
        if con_guia:
            # la guía va arriba de la leche para que se siga viendo el borde mientras vertés
            self.lienzo.blit(self.guia, (0, 0))
        grande = pygame.transform.scale(self.lienzo, (TAM_LIENZO * px, TAM_LIENZO * px))
        pantalla.blit(grande, pos)

    def rellenar_perfecto(self):
        """Pinta la leche exactamente sobre el dibujo (para la taza de muestra de la portada)."""
        self.leche = self.mascara_dibujo.to_surface(setcolor=C["leche"], unsetcolor=(0, 0, 0, 0))