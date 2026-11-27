"""tutorial.py - El tutorial de Don Salmón: 6 páginas cortitas, con dibujos y la cámara en vivo.

Igual que en Purr & Brew: cada página tiene un título, lo que "dice" Don Salmón en su globito
y una función que dibuja la ilustración de arriba. Las ilustraciones usan las MISMAS piezas
del juego (la jarra con la patita, la taza, las barras, las estrellas), así lo que se ve acá
es exactamente lo que después aparece al jugar. En las primeras páginas la cámara está en vivo,
así podés probar cada gesto antes de jugar.

Para agregar o cambiar una página alcanza con editar la lista PAGINAS (abajo de todo).
"""
import math
import pygame
from ajustes import (COLORES as C, ANCHO, PX, RONDAS, UMBRALES_ESTRELLAS, RECT_TUTORIAL_ILUSTRACION,
                     RECT_TUTORIAL_GLOBO, POS_DON_SALMON_TUTORIAL, RECT_BOTON_ANTERIOR, RECT_BOTON_SIGUIENTE,
                     TAM_CAMARA_TUTORIAL, PELAJES, TAM_LIENZO)
from dibujo import (dibujar_panel, texto_centrado, texto_envuelto, dibujar_barra, dibujar_fila_estrellas,
                    dibujar_camara, dibujar_jarra, dibujar_boton)
from latte import Taza
from escenas import dibujar_fondo_cafeteria


# ---------------------------------------------------------------- piezas chiquitas para los dibujos
def numerito(pantalla, fuentes, centro, numero):
    """Dibuja un cuadradito con el número de paso (como en el tutorial de Purr & Brew)."""
    rect = pygame.Rect(0, 0, 34, 34)
    rect.center = centro
    dibujar_panel(pantalla, rect, C["acento"], C["contorno"])
    texto_centrado(pantalla, str(numero), fuentes["normal"], C["texto_claro"], rect.center)


def paso(pantalla, fuentes, x, y, numero, texto, ancho=400):
    """Escribe un paso numerado: el cuadradito con el número y el texto al lado. Devuelve dónde terminó."""
    numerito(pantalla, fuentes, (x + 17, y + 14), numero)
    return texto_envuelto(pantalla, texto, fuentes["chica"], C["texto"], (x + 46, y, ancho, 90)) + 10


def tecla(pantalla, fuentes, centro, texto, ancho=56):
    """Dibuja una tecla del teclado con una letra o palabra adentro."""
    rect = pygame.Rect(0, 0, ancho, 48)
    rect.center = centro
    dibujar_panel(pantalla, rect, C["blanco"], C["contorno"])
    pygame.draw.rect(pantalla, C["sombra"], (rect.x + 8, rect.bottom - 10, rect.width - 16, 4))
    texto_centrado(pantalla, texto, fuentes["normal"], C["texto"], (rect.centerx, rect.centery - 3))


def cartelito(pantalla, fuentes, centro, texto, color):
    """Dibuja un cartelito de color con un texto adentro (para marcar 'sí' o 'no')."""
    superficie = fuentes["chica"].render(texto, False, C["texto"])
    rect = superficie.get_rect().inflate(28, 14)
    rect.center = centro
    dibujar_panel(pantalla, rect, color, C["contorno"])
    pantalla.blit(superficie, superficie.get_rect(center=rect.center))


def dedos_dibujados(pantalla, centro, separacion, juntos):
    """Dibuja los dos puntitos de los dedos (pulgar e índice) como se ven en la cámara del juego."""
    color = C["blanco"] if juntos else C["dorado"]
    a = (centro[0] - separacion, centro[1] + separacion // 2)
    b = (centro[0] + separacion, centro[1] - separacion // 2)
    pygame.draw.line(pantalla, C["contorno"], a, b, 7)
    pygame.draw.line(pantalla, color, a, b, 3)
    for x, y in (a, b):
        pygame.draw.rect(pantalla, C["contorno"], (x - 9, y - 9, 18, 18))
        pygame.draw.rect(pantalla, color, (x - 6, y - 6, 12, 12))


def cafecito(pantalla, centro, ancho):
    """Dibuja un charquito de café (visto un poco de costado) para que la leche blanca se vea encima."""
    rect = pygame.Rect(0, 0, ancho, ancho // 3)
    rect.center = centro
    pygame.draw.ellipse(pantalla, C["contorno"], rect.inflate(6, 6))
    pygame.draw.ellipse(pantalla, C["cafe"], rect)


def gotitas(pantalla, x, y_arriba, y_abajo, ancho, t):
    """Dibuja gotitas de leche que caen entre dos alturas (animadas con el tiempo t)."""
    for i in range(6):
        avance = (t * 1.6 + i / 6) % 1               # cada gota va de 0 (arriba) a 1 (abajo)
        gx = x + math.sin(i * 2.3) * ancho
        gy = y_arriba + (y_abajo - y_arriba) * avance
        pygame.draw.rect(pantalla, C["leche"], (int(gx) // PX * PX, int(gy) // PX * PX, PX, PX * 2))


def camara_en_vivo(pantalla, fuentes, vivo, rect):
    """Dibuja la cámara en vivo con los dedos marcados, igual que en el juego, del tamaño de 'rect'."""
    rect = pygame.Rect(rect)
    imagen = vivo["imagen"]
    if imagen is not None and imagen.get_size() != rect.size:
        imagen = pygame.transform.scale(imagen, rect.size)
    dibujar_camara(pantalla, imagen, rect, vivo["dedos"], vivo["pellizco"], fuentes["chica"])


# ---------------------------------------------------------------- ilustraciones (una por página)
# Todas reciben la pantalla, las fuentes, lo que está pasando en vivo (cámara, pellizco,
# grosor) y el tiempo t para las animaciones. Dibujan adentro de RECT_TUTORIAL_ILUSTRACION.
def ilus_mano(pantalla, fuentes, vivo, t):
    """Página 1: cómo ponerse frente a la cámara."""
    x0, y0 = RECT_TUTORIAL_ILUSTRACION[0], RECT_TUTORIAL_ILUSTRACION[1]
    camara_en_vivo(pantalla, fuentes, vivo, (x0 + 30, y0 + 20, TAM_CAMARA_TUTORIAL[0], TAM_CAMARA_TUTORIAL[1]))
    y = y0 + 24
    y = paso(pantalla, fuentes, x0 + 400, y, 1, "Sentate frente a la compu, a un brazo de distancia (50 a 80 cm).")
    y = paso(pantalla, fuentes, x0 + 400, y, 2, "Prendé una luz de frente. Si la luz está atrás tuyo, no te veo.")
    y = paso(pantalla, fuentes, x0 + 400, y, 3, "Levantá una mano y mostrale la palma a la cámara.")
    if vivo["dedos"] is None:
        cartelito(pantalla, fuentes, (x0 + 640, y0 + 262), "Todavía no veo tu mano", C["sombra"])
    else:
        cartelito(pantalla, fuentes, (x0 + 640, y0 + 262), "¡Te veo! Mové la mano", C["verde"])


def ilus_pellizco(pantalla, fuentes, vivo, t):
    """Página 2: dedos abiertos = no sale; pellizco = sale leche. Con la prueba en vivo."""
    x0, y0 = RECT_TUTORIAL_ILUSTRACION[0], RECT_TUTORIAL_ILUSTRACION[1]
    pelaje = PELAJES[vivo["pelaje"]][1]
    # dedos abiertos
    texto_centrado(pantalla, "Dedos abiertos", fuentes["normal"], C["texto"], (x0 + 130, y0 + 24))
    dedos_dibujados(pantalla, (x0 + 130, y0 + 100), 34, False)
    cafecito(pantalla, (x0 + 122, y0 + 240), 120)
    dibujar_jarra(pantalla, (x0 + 120, y0 + 236), False, pelaje, 50)
    cartelito(pantalla, fuentes, (x0 + 130, y0 + 278), "No sale leche", C["sombra"])
    # pellizco
    texto_centrado(pantalla, "Pellizco", fuentes["normal"], C["texto"], (x0 + 390, y0 + 24))
    dedos_dibujados(pantalla, (x0 + 390, y0 + 100), 4, True)
    cafecito(pantalla, (x0 + 382, y0 + 240), 120)
    pygame.draw.ellipse(pantalla, C["leche"], (x0 + 362, y0 + 232, 40, 14))
    dibujar_jarra(pantalla, (x0 + 380, y0 + 236), True, pelaje, 50)
    gotitas(pantalla, x0 + 382, y0 + 186, y0 + 236, 4, t)
    cartelito(pantalla, fuentes, (x0 + 390, y0 + 278), "¡Sale leche!", C["verde"])
    # prueba en vivo
    rect = pygame.Rect(x0 + 560, y0 + 16, 280, 210)
    camara_en_vivo(pantalla, fuentes, vivo, rect)
    if vivo["dedos"] is None:
        cartelito(pantalla, fuentes, (rect.centerx, y0 + 262), "Mostrá la mano", C["sombra"])
    elif vivo["pellizco"]:
        cartelito(pantalla, fuentes, (rect.centerx, y0 + 262), "¡Pellizco! Sale leche", C["verde"])
    else:
        cartelito(pantalla, fuentes, (rect.centerx, y0 + 262), "Probá: juntá los dedos", C["azul"])


def ilus_grosor(pantalla, fuentes, vivo, t):
    """Página 3: mano lejos = jarra alta = chorro finito; mano cerca = jarra baja = chorro gordo."""
    x0, y0 = RECT_TUTORIAL_ILUSTRACION[0], RECT_TUTORIAL_ILUSTRACION[1]
    pelaje = PELAJES[vivo["pelaje"]][1]
    texto_centrado(pantalla, "Mano lejos", fuentes["normal"], C["texto"], (x0 + 130, y0 + 24))
    cafecito(pantalla, (x0 + 122, y0 + 224), 130)
    dibujar_jarra(pantalla, (x0 + 120, y0 + 220), True, pelaje, 100)
    gotitas(pantalla, x0 + 122, y0 + 122, y0 + 220, 2, t)
    pygame.draw.ellipse(pantalla, C["leche"], (x0 + 112, y0 + 218, 20, 8))
    cartelito(pantalla, fuentes, (x0 + 130, y0 + 268), "Chorro finito: detalles", C["azul"])
    texto_centrado(pantalla, "Mano cerca", fuentes["normal"], C["texto"], (x0 + 390, y0 + 24))
    cafecito(pantalla, (x0 + 382, y0 + 224), 130)
    pygame.draw.ellipse(pantalla, C["leche"], (x0 + 346, y0 + 214, 76, 20))
    dibujar_jarra(pantalla, (x0 + 380, y0 + 220), True, pelaje, 40)
    gotitas(pantalla, x0 + 382, y0 + 180, y0 + 220, 14, t)
    cartelito(pantalla, fuentes, (x0 + 390, y0 + 268), "Chorro gordo: rellenar", C["verde"])
    # prueba en vivo: la barra se mueve cuando acercás o alejás la mano
    rect = pygame.Rect(x0 + 560, y0 + 16, 280, 210)
    camara_en_vivo(pantalla, fuentes, vivo, rect)
    pantalla.blit(fuentes["chica"].render("fino", False, C["texto"]), (rect.x, y0 + 250))
    pantalla.blit(fuentes["chica"].render("gordo", False, C["texto"]), (rect.right - 52, y0 + 250))
    dibujar_barra(pantalla, (rect.x + 52, y0 + 254, rect.width - 112, 18), vivo["grosor"], C["leche"])


def ilus_dibujo(pantalla, fuentes, vivo, t):
    """Página 4: seguir el dibujo punteado y cuántas estrellas da cada porcentaje."""
    x0, y0 = RECT_TUTORIAL_ILUSTRACION[0], RECT_TUTORIAL_ILUSTRACION[1]
    vivo["taza_ejemplo"].dibujar(pantalla, con_guia=True, pos=(x0 + 30, y0 + 14), px=2)
    x = x0 + 380
    filas = [(1, f"{UMBRALES_ESTRELLAS[0]}%", "Pasás de ronda"),
             (2, f"{UMBRALES_ESTRELLAS[1]}%", "¡Muy bien!"),
             (3, f"{UMBRALES_ESTRELLAS[2]}%", "Don Salmón llora de emoción")]
    for i, (estrellas, porcentaje, texto) in enumerate(filas):
        y = y0 + 40 + i * 70
        dibujar_fila_estrellas(pantalla, (x + 60, y), estrellas, px=3, separacion=36)
        texto_centrado(pantalla, porcentaje, fuentes["normal"], C["acento"], (x + 160, y))
        pantalla.blit(fuentes["chica"].render(texto, False, C["texto"]), (x + 200, y - 12))
    texto_centrado(pantalla, "Los puntitos marcan el dibujo que tenés que pintar.", fuentes["chica"], C["texto"],
                   (x + 230, y0 + 236))
    texto_centrado(pantalla, f"Son {len(RONDAS)} dibujos, del más fácil al más difícil.", fuentes["chica"], C["texto"],
                   (x + 230, y0 + 266))


def ilus_cuidado(pantalla, fuentes, vivo, t):
    """Página 5: la leche se acaba, el café se enfría, no hay que desbordar y cómo servir."""
    x0, y0 = RECT_TUTORIAL_ILUSTRACION[0], RECT_TUTORIAL_ILUSTRACION[1]
    # las dos barras, que bajan solas para que se entienda que se gastan
    baja = 1 - (t * 0.15) % 1
    pantalla.blit(fuentes["normal"].render("Leche", False, C["texto"]), (x0 + 30, y0 + 20))
    dibujar_barra(pantalla, (x0 + 30, y0 + 58, 300, 22), baja, C["leche"])
    pantalla.blit(fuentes["normal"].render("Temperatura del café", False, C["texto"]), (x0 + 30, y0 + 100))
    dibujar_barra(pantalla, (x0 + 30, y0 + 138, 300, 22), baja, C["rojo_suave"] if baja > 0.5 else C["azul"])
    texto_envuelto(pantalla, "Si se te acaba la leche o se te enfría el café sin 1 estrella, perdés.",
                   fuentes["chica"], C["texto"], (x0 + 30, y0 + 186, 320, 90))
    # servir: la jarra se va de la taza
    pygame.draw.line(pantalla, C["zocalo"], (x0 + 400, y0 + 10), (x0 + 400, y0 + 290), 3)
    texto_centrado(pantalla, "¿Terminaste? ¡Serví!", fuentes["normal"], C["acento"], (x0 + 640, y0 + 24))
    taza = vivo["taza_ejemplo"]
    taza.dibujar(pantalla, con_guia=False, pos=(x0 + 430, y0 + 60), px=1)
    afuera = (math.sin(t * 2) + 1) / 2              # la jarra va y viene: adentro -> afuera de la taza
    jarra_x = x0 + 498 + afuera * 220
    dibujar_jarra(pantalla, (jarra_x, y0 + 150), False, PELAJES[vivo["pelaje"]][1], 40)
    texto_envuelto(pantalla, "Con al menos 1 estrella, sacá la jarra de la taza y quedate quieto un ratito.",
                   fuentes["chica"], C["texto"], (x0 + 430, y0 + 216, 420, 90))


def ilus_teclas(pantalla, fuentes, vivo, t):
    """Página 6: si no te ve, pausa sola; y las teclas por si las necesitás."""
    x0, y0 = RECT_TUTORIAL_ILUSTRACION[0], RECT_TUTORIAL_ILUSTRACION[1]
    cartel = dibujar_panel(pantalla, (x0 + 30, y0 + 30, 340, 120), C["panel"], C["contorno"])
    texto_centrado(pantalla, "¡Mostrá la pata!", fuentes["grande"], C["texto"], (cartel.centerx, cartel.y + 44))
    texto_centrado(pantalla, "El tiempo está congelado.", fuentes["chica"], C["acento"], (cartel.centerx, cartel.y + 90))
    texto_envuelto(pantalla, "Si sacás la mano de la cámara, el juego se pausa solo y te espera.",
                   fuentes["chica"], C["texto"], (x0 + 30, y0 + 176, 340, 90))
    teclas = [("P", "Pausa y volumen"), ("F11", "Pantalla completa"), ("M", "Música sí / no"), ("N", "Sonidos sí / no")]
    for i, (nombre, que_hace) in enumerate(teclas):
        y = y0 + 40 + i * 64
        tecla(pantalla, fuentes, (x0 + 480, y), nombre, 72)
        pantalla.blit(fuentes["normal"].render(que_hace, False, C["texto"]), (x0 + 536, y - 16))


# (título, lo que dice Don Salmón, función que dibuja la ilustración)
PAGINAS = [
    ("Tu mano es la jarra",
     "¡Bienvenido al concurso! Acá no se usa el mouse ni el teclado: se juega con tu mano frente a la cámara. "
     "Mirá la imagen: cuando te vea, vas a ver dos puntitos en tus dedos.",
     ilus_mano),
    ("Pellizcá para verter",
     "Juntá la punta del dedo índice con la del pulgar, como si agarraras la jarrita. Mientras los tengas "
     "juntos sale leche. Abrí los dedos y se corta. ¡Probalo ahora con la cámara!",
     ilus_pellizco),
    ("Cerca o lejos",
     "Truco de barista: si acercás la mano a la cámara, la jarra baja y sale un chorro gordo para rellenar. "
     "Si la alejás, sale finito, para las partes chiquitas. Mirá cómo se mueve la barra.",
     ilus_grosor),
    ("Seguí el dibujo",
     "En el café aparece un dibujo punteado. Pintalo con espuma sin salirte: lo que cae afuera resta. "
     "Con 1 estrella pasás a la siguiente ronda. ¡Y se puede llegar al 100%!",
     ilus_dibujo),
    ("Ojo con esto",
     "La leche no es infinita y el café se enfría. Si tirás muchísima leche afuera, se desborda y perdés. "
     "Cuando te guste cómo quedó, sacá la jarra de la taza y se sirve.",
     ilus_cuidado),
    ("Si no te veo, te espero",
     "Si sacás la mano de la cámara, pauso todo hasta que vuelvas. Con la P (o Esc) pausás vos y podés "
     "cambiar el volumen. ¡A demostrar lo que sabés! Yo voy a estar mirando, eh.",
     ilus_teclas),
]


class Tutorial:
    """Las páginas del tutorial: en qué página estás y cómo se dibuja cada una."""

    def __init__(self):
        """Empieza en la primera página y prepara la taza de ejemplo (un corazón a medio pintar)."""
        self.pagina = 0
        self.taza_ejemplo = Taza("corazon")
        self.taza_ejemplo.rellenar_perfecto()
        # borro la mitad de abajo de la leche para que se vea "a medio hacer"
        mitad = self.taza_ejemplo.leche.get_height() // 2 + 6
        self.taza_ejemplo.leche.fill((0, 0, 0, 0), (0, mitad, TAM_LIENZO, TAM_LIENZO))

    def reiniciar(self):
        """Vuelve a la primera página."""
        self.pagina = 0

    def es_la_ultima(self):
        """Devuelve True si estás en la última página."""
        return self.pagina == len(PAGINAS) - 1

    def siguiente(self):
        """Pasa a la página siguiente. Devuelve True si ya estaba en la última (hay que empezar a jugar)."""
        if self.es_la_ultima():
            return True
        self.pagina += 1
        return False

    def anterior(self):
        """Vuelve una página (si no estás en la primera)."""
        if self.pagina > 0:
            self.pagina -= 1

    def boton_en(self, pos):
        """Devuelve 'anterior', 'siguiente' o None según qué botón haya en la posición del mouse."""
        if self.pagina > 0 and pygame.Rect(RECT_BOTON_ANTERIOR).collidepoint(pos):
            return "anterior"
        if pygame.Rect(RECT_BOTON_SIGUIENTE).collidepoint(pos):
            return "siguiente"
        return None

    def dibujar(self, pantalla, fondo, fuentes, jurado, vivo, mouse, t):
        """Dibuja la página actual: título, ilustración, Don Salmón con su globito y los botones.

        vivo: diccionario con lo que pasa en la cámara (imagen, dedos, pellizco, grosor, pelaje).
        """
        titulo, texto, ilustracion = PAGINAS[self.pagina]
        vivo["taza_ejemplo"] = self.taza_ejemplo
        dibujar_fondo_cafeteria(pantalla, fondo, t)
        caja = dibujar_panel(pantalla, (300, 8, 360, 50))
        texto_centrado(pantalla, titulo, fuentes["normal"], C["texto"], caja.center)
        dibujar_panel(pantalla, (24, 64, 912, 568))
        dibujar_panel(pantalla, RECT_TUTORIAL_ILUSTRACION, C["blanco"], C["zocalo"])
        ilustracion(pantalla, fuentes, vivo, t)
        # Don Salmón explicando, con su globito
        globo = dibujar_panel(pantalla, RECT_TUTORIAL_GLOBO, C["blanco"], C["contorno"])
        pygame.draw.polygon(pantalla, C["contorno"], [(globo.x, globo.y + 50), (globo.x - 18, globo.y + 72),
                                                      (globo.x, globo.y + 80)])
        texto_envuelto(pantalla, texto, fuentes["chica"], C["texto"], globo.inflate(-36, -24))
        jurado.dibujar(pantalla, POS_DON_SALMON_TUTORIAL)
        # botones y puntitos de página
        if self.pagina > 0:
            rect = pygame.Rect(RECT_BOTON_ANTERIOR)
            dibujar_boton(pantalla, rect, "< Anterior", fuentes["normal"], rect.collidepoint(mouse), C["panel"])
        rect = pygame.Rect(RECT_BOTON_SIGUIENTE)
        texto_boton = "¡A jugar!" if self.es_la_ultima() else "Siguiente >"
        dibujar_boton(pantalla, rect, texto_boton, fuentes["normal"], rect.collidepoint(mouse))
        for i in range(len(PAGINAS)):
            x = ANCHO // 2 - (len(PAGINAS) - 1) * 14 + i * 28
            color = C["acento"] if i == self.pagina else C["sombra"]
            pygame.draw.rect(pantalla, C["contorno"], (x - 7, 579, 14, 14))
            pygame.draw.rect(pantalla, color, (x - 5, 581, 10, 10))
        texto_centrado(pantalla, "Enter o flechas para pasar de página", fuentes["chica"], C["texto"], (ANCHO // 2, 610))