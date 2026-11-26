"""escenas.py - Lo que se dibuja en cada estado: portada, nombre, elegir gato, HUD de la ronda,
resultado, victoria, derrota, top, galería, pausa, "¡Mostrá la pata!" y el aviso de cámara.
(El tutorial tiene su propio archivo: tutorial.py.)

Estas funciones solo DIBUJAN: no cambian nada del juego. Reciben lo que necesitan mostrar.
"""
import math
import pygame
from ajustes import (COLORES as C, ANCHO, PX, RONDAS, COLOR_VELO, RECT_PANEL_CAMARA, RECT_PANEL_JURADO,
                     RECT_GLOBO, RECT_PANEL_PUNTAJE, RECT_TITULO_RONDA, RECT_BARRA_LECHE,
                     RECT_BARRA_TEMPERATURA, TAM_MINIATURA, POS_MINIATURA, POS_JURADO, PELAJES,
                     MOTIVOS_DERROTA, POS_LIENZO, TAM_LIENZO, UMBRALES_ESTRELLAS, CANTIDAD_TOP,
                     LARGO_MAXIMO_NOMBRE, RECT_BOTON_EMPEZAR, RECT_BOTON_TOP, RECT_BOTON_GALERIA,
                     SALUDO_DON_SALMON, CENTRO_TAZA_PORTADA, RADIO_TAZA_PORTADA)
from dibujo import (dibujar_panel, texto_centrado, texto_envuelto, dibujar_barra, dibujar_fila_estrellas,
                    dibujar_estrella, dibujar_velo, dibujar_camara, dibujar_gato, pixelar, dibujar_boton,
                    dibujar_banderines, dibujar_vapor)
from latte import calcular_estrellas

CENTRO_TAZA = (POS_LIENZO[0] + TAM_LIENZO * PX // 2, POS_LIENZO[1] + TAM_LIENZO * PX // 2)
_FLECHA = ("OOOOOOO", ".OYYYO.", "..OYO..", "...O...")


def titulo_con_sombra(pantalla, texto, fuente, centro):
    """Escribe un título grande en color oscuro con una sombra dorada, estilo cartel."""
    texto_centrado(pantalla, texto, fuente, C["texto"], centro, sombra=C["dorado"])


def parpadea(t, veces_por_segundo=1.5):
    """Devuelve True la mayor parte del tiempo y False un ratito: sirve para hacer titilar un texto."""
    return math.sin(t * veces_por_segundo * 2 * math.pi) > -0.3


def dibujar_globo(pantalla, rect, texto, fuente, punta_x):
    """Dibuja un globito de diálogo con el texto adentro y una puntita que baja hacia punta_x."""
    rect = pygame.Rect(rect)
    dibujar_panel(pantalla, rect, C["blanco"], C["contorno"])
    puntita = [(punta_x - 8, rect.bottom - PX), (punta_x + 8, rect.bottom - PX), (punta_x, rect.bottom + 12)]
    pygame.draw.polygon(pantalla, C["contorno"], puntita)
    pygame.draw.polygon(pantalla, C["blanco"], [(punta_x - 4, rect.bottom - PX - 1), (punta_x + 4, rect.bottom - PX - 1),
                                                (punta_x, rect.bottom + 5)])
    alto_texto = fuente.get_height() * 2
    # si la frase es corta va en una línea centrada; si no, se parte en dos
    if fuente.size(texto)[0] <= rect.width - 24:
        texto_centrado(pantalla, texto, fuente, C["texto"], rect.center)
    else:
        texto_envuelto(pantalla, texto, fuente, C["texto"],
                       (rect.x + 14, rect.centery - alto_texto // 2, rect.width - 28, alto_texto), 0)


# ---------------------------------------------------------------- portada, nombre y elegir gato
def dibujar_portada(pantalla, fondo, fuentes, taza_muestra, cafetera, jurado, pelaje, mouse, t):
    """Portada: banderines del concurso, el título, la taza humeante (que también es un botón),
    la cafetera, tu gato, Don Salmón saludando y los botones. mouse: posición del mouse.
    """
    pantalla.blit(fondo, (0, 0))
    dibujar_banderines(pantalla, 0, t)
    panel = dibujar_panel(pantalla, (240, 20, 480, 140))
    titulo_con_sombra(pantalla, "Purr & Brew", fuentes["titulo"], (ANCHO // 2, panel.y + 52))
    texto_centrado(pantalla, "LATTE ART", fuentes["grande"], C["acento"], (ANCHO // 2, panel.y + 106))
    # la cafetera apoyada SOBRE la mesada (la franja clara de la barra), no delante del zócalo
    pantalla.blit(cafetera, cafetera.get_rect(midbottom=(276, 492)))
    # La taza es un botón: con el mouse encima "sube" un poquito y se le marca el borde.
    encima = mouse_sobre_taza(mouse)
    alto = 8 if encima else 0
    centro_x, centro_y = CENTRO_TAZA_PORTADA
    if encima:
        pygame.draw.circle(pantalla, C["dorado"], (centro_x, centro_y - alto), RADIO_TAZA_PORTADA + 6, 4)
    taza_muestra.dibujar(pantalla, con_guia=False, pos=(centro_x - 136, centro_y - 136 - alto), px=2)
    dibujar_vapor(pantalla, centro_x, centro_y - 92 - alto, t)
    if encima:
        dibujar_globo(pantalla, (centro_x - 110, 170, 220, 46), "¡Tocá para empezar!", fuentes["chica"], centro_x)
    dibujar_gato(pantalla, (130, 560), pelaje, 7, "contento", delantal=True)
    jurado.dibujar(pantalla, (810, 560), 7)
    # Don Salmón saluda con su globito (la puntita apunta a él)
    dibujar_globo(pantalla, (640, 340, 300, 70), SALUDO_DON_SALMON, fuentes["chica"], 810)
    botones = ((RECT_BOTON_EMPEZAR, "¡Empezar!", fuentes["grande"]), (RECT_BOTON_TOP, "Top (T)", fuentes["normal"]),
               (RECT_BOTON_GALERIA, "Galería (G)", fuentes["normal"]))
    for rect, texto, fuente in botones:
        rect = pygame.Rect(rect)
        dibujar_boton(pantalla, rect, texto, fuente, rect.collidepoint(mouse))


def mouse_sobre_taza(mouse):
    """Devuelve True si el mouse está sobre la taza grande de la portada (un círculo)."""
    distancia = math.hypot(mouse[0] - CENTRO_TAZA_PORTADA[0], mouse[1] - CENTRO_TAZA_PORTADA[1])
    return distancia <= RADIO_TAZA_PORTADA


def dibujar_nombre(pantalla, fondo, fuentes, nombre, jurado, t):
    """Pantalla para escribir el nombre con el teclado (va a aparecer en el top)."""
    pantalla.blit(fondo, (0, 0))
    caja = dibujar_panel(pantalla, (180, 60, 600, 300))
    titulo_con_sombra(pantalla, "¿Cómo te llamás?", fuentes["grande"], (ANCHO // 2, caja.y + 52))
    texto_centrado(pantalla, "Don Salmón te anota en la planilla del concurso.", fuentes["chica"], C["texto"],
                   (ANCHO // 2, caja.y + 98))
    campo = dibujar_panel(pantalla, (ANCHO // 2 - 200, caja.y + 128, 400, 64), C["blanco"], C["contorno"])
    escrito = texto_centrado(pantalla, nombre, fuentes["grande"], C["texto"], campo.center)
    # El cursor es una barrita que titila justo después de la última letra. Va aparte del texto
    # (y no como un "_" pegado) para que el nombre no se corra cuando aparece y desaparece.
    if int(t * 2) % 2 == 0 and len(nombre) < LARGO_MAXIMO_NOMBRE:
        x = escrito.right + 4 if nombre else campo.centerx
        pygame.draw.rect(pantalla, C["acento"], (x, campo.centery - 18, PX, 36))
    texto_centrado(pantalla, "Escribí con el teclado  ·  Borrar: corregir", fuentes["chica"], C["texto"],
                   (ANCHO // 2, caja.y + 220))
    if nombre.strip():
        texto_centrado(pantalla, "Enter: listo", fuentes["normal"], C["acento"], (ANCHO // 2, caja.y + 260))
    jurado.dibujar(pantalla, (ANCHO // 2, 560), 7)


def dibujar_elegir_gato(pantalla, fondo, fuentes, elegido, t):
    """Pantalla para elegir el color del gatito (como en Purr & Brew). Se elige con las flechas."""
    pantalla.blit(fondo, (0, 0))
    caja = dibujar_panel(pantalla, (60, 24, 840, 96))
    titulo_con_sombra(pantalla, "Elegí tu gatito", fuentes["grande"], (ANCHO // 2, caja.y + 38))
    texto_centrado(pantalla, "Flechas izquierda y derecha para elegir  ·  Enter para confirmar", fuentes["chica"],
                   C["texto"], (ANCHO // 2, caja.y + 74))
    for i, (nombre, color) in enumerate(PELAJES):
        x = 150 + i * 220
        cara = "contento" if i == elegido else "neutral"
        dibujar_gato(pantalla, (x, 470), color, 7, cara, delantal=True)
        dibujar_panel(pantalla, (x - 70, 490, 140, 44), C["dorado"] if i == elegido else C["panel"])
        texto_centrado(pantalla, nombre, fuentes["normal"], C["texto"], (x, 512))
        if i == elegido:
            # una flechita que rebota arriba del gato elegido
            flecha = pixelar(_FLECHA, {"O": C["contorno"], "Y": C["dorado"]}, 8)
            salto = round(abs(math.sin(t * 4)) * 10)
            pantalla.blit(flecha, flecha.get_rect(midbottom=(x, 340 - salto)))


# ---------------------------------------------------------------- HUD de la ronda
def dibujar_hud(pantalla, fuentes, numero_ronda, imagen, dedos, pellizco, jurado, porcentaje,
                fraccion_leche, fraccion_temperatura, servir):
    """Dibuja todo lo que rodea a la taza mientras jugás: título, cámara, jurado, % y barras.

    servir: None si todavía no se puede servir; si no, cuánto falta para servir (de 0 a 1).
    """
    ronda = RONDAS[numero_ronda]
    caja = dibujar_panel(pantalla, RECT_TITULO_RONDA)
    texto_centrado(pantalla, f"Ronda {numero_ronda + 1}/{len(RONDAS)}: {ronda['nombre']}",
                   fuentes["normal"], C["texto"], caja.center)
    # cámara
    dibujar_panel(pantalla, RECT_PANEL_CAMARA)
    dibujar_camara(pantalla, imagen, (POS_MINIATURA, TAM_MINIATURA), dedos, pellizco, fuentes["chica"])
    # jurado con su globito (el globo se resalta en dorado cuando hace un comentario puntual)
    dibujar_panel(pantalla, RECT_PANEL_JURADO)
    jurado.dibujar(pantalla, POS_JURADO)
    dibujar_globo(pantalla, RECT_GLOBO, jurado.frase(), fuentes["chica"], POS_JURADO[0])
    if jurado.esta_comentando():
        pygame.draw.rect(pantalla, C["dorado"], pygame.Rect(RECT_GLOBO).inflate(4, 4), 2)
    # puntaje: el % a la izquierda y las estrellas a la derecha, y abajo las dos barras
    panel = dibujar_panel(pantalla, RECT_PANEL_PUNTAJE)
    texto_centrado(pantalla, f"{porcentaje}%", fuentes["grande"], C["texto"], (panel.x + 62, panel.y + 34))
    dibujar_fila_estrellas(pantalla, (panel.x + 178, panel.y + 34), calcular_estrellas(porcentaje), separacion=42)
    pantalla.blit(fuentes["chica"].render("Leche", False, C["texto"]), (RECT_BARRA_LECHE[0], RECT_BARRA_LECHE[1] - 24))
    dibujar_barra(pantalla, RECT_BARRA_LECHE, fraccion_leche, C["leche"])
    pantalla.blit(fuentes["chica"].render("Temperatura", False, C["texto"]),
                  (RECT_BARRA_TEMPERATURA[0], RECT_BARRA_TEMPERATURA[1] - 24))
    # el termómetro pasa de rojo (caliente) a dorado y después a celeste (frío)
    if fraccion_temperatura > 0.5:
        color = C["rojo_suave"]
    elif fraccion_temperatura > 0.25:
        color = C["dorado"]
    else:
        color = C["azul"]
    dibujar_barra(pantalla, RECT_BARRA_TEMPERATURA, fraccion_temperatura, color)
    # aviso para servir (abajo a la izquierda, sobre la mesa) con una barrita que se llena
    if servir is not None:
        aviso = dibujar_panel(pantalla, (16, 584, 330, 46))
        if servir > 0:
            dibujar_barra(pantalla, (aviso.x + 16, aviso.centery - 8, aviso.width - 32, 16), servir, C["verde"])
        else:
            texto_centrado(pantalla, "Para servir: sacá la jarra de la taza", fuentes["chica"], C["texto"], aviso.center)


def dibujar_cuenta(pantalla, fuentes, segundos):
    """Dibuja el '3, 2, 1' grande sobre la taza antes de empezar a verter."""
    numero = math.ceil(segundos)
    caja = dibujar_panel(pantalla, pygame.Rect(0, 0, 220, 130).move(CENTRO_TAZA[0] - 110, CENTRO_TAZA[1] - 65))
    texto_centrado(pantalla, str(numero), fuentes["titulo"], C["texto"], (caja.centerx, caja.y + 50))
    texto_centrado(pantalla, "Acomodá la mano", fuentes["chica"], C["acento"], (caja.centerx, caja.bottom - 22))


def dibujar_sin_mano(pantalla, fuentes):
    """Cartel de cuando la cámara no ve la mano: el juego está en pausa y el tiempo congelado."""
    dibujar_velo(pantalla, COLOR_VELO)
    caja = dibujar_panel(pantalla, pygame.Rect(0, 0, 440, 170).move(CENTRO_TAZA[0] - 220, CENTRO_TAZA[1] - 85))
    titulo_con_sombra(pantalla, "¡Mostrá la pata!", fuentes["grande"], (caja.centerx, caja.y + 46))
    texto_centrado(pantalla, "Poné la mano frente a la cámara.", fuentes["chica"], C["texto"],
                   (caja.centerx, caja.y + 96))
    texto_centrado(pantalla, "El tiempo está congelado.", fuentes["chica"], C["acento"],
                   (caja.centerx, caja.y + 126))


# Los renglones del menú de pausa, en orden (main.py usa esta misma lista para saber qué hacer).
OPCIONES_PAUSA = ["seguir", "musica", "efectos", "pantalla", "portada"]
TEXTOS_PAUSA = {"seguir": "Seguir jugando", "musica": "Música", "efectos": "Sonidos",
                "pantalla": "Pantalla completa", "portada": "Volver a la portada"}


def rects_pausa():
    """Devuelve un diccionario con el rectángulo de cada cosa que se puede tocar en la pausa.

    La uso para dibujar el menú Y para saber dónde hiciste clic: así las dos cosas siempre
    coinciden (si muevo un botón, se mueve en los dos lados).
    """
    rects = {}
    for i, opcion in enumerate(OPCIONES_PAUSA):
        fila = pygame.Rect(300, 186 + i * 64, 360, 48)
        rects[opcion] = fila
        if opcion in ("musica", "efectos"):
            rects[opcion + "_menos"] = pygame.Rect(fila.x + 124, fila.y + 4, 40, 40)
            rects[opcion + "_mas"] = pygame.Rect(fila.right - 44, fila.y + 4, 40, 40)
    return rects


def dibujar_pausa(pantalla, fuentes, opcion, volumen_musica, volumen_efectos, mouse):
    """Menú de pausa (P o Esc): seguir, volumen de la música, volumen de los sonidos, pantalla
    completa y volver a la portada. 'opcion' es el renglón elegido con las flechas.
    """
    dibujar_velo(pantalla, COLOR_VELO)
    caja = dibujar_panel(pantalla, (260, 100, 440, 470))
    titulo_con_sombra(pantalla, "Pausa", fuentes["grande"], (caja.centerx, caja.y + 46))
    rects = rects_pausa()
    volumenes = {"musica": volumen_musica, "efectos": volumen_efectos}
    for i, nombre in enumerate(OPCIONES_PAUSA):
        fila = rects[nombre]
        elegido = i == opcion or fila.collidepoint(mouse)
        if nombre in volumenes:
            # renglón de volumen: nombre, botón -, barrita y botón +
            if elegido:
                dibujar_panel(pantalla, fila, C["dorado"], C["brillo_dorado"])
            pantalla.blit(fuentes["normal"].render(TEXTOS_PAUSA[nombre], False, C["texto"]), (fila.x + 14, fila.y + 9))
            menos = rects[nombre + "_menos"]
            mas = rects[nombre + "_mas"]
            dibujar_boton(pantalla, menos, "-", fuentes["normal"], menos.collidepoint(mouse), C["panel"])
            dibujar_boton(pantalla, mas, "+", fuentes["normal"], mas.collidepoint(mouse), C["panel"])
            barra = (menos.right + 12, fila.centery - 8, mas.x - menos.right - 24, 16)
            dibujar_barra(pantalla, barra, volumenes[nombre], C["acento"])
        else:
            dibujar_boton(pantalla, fila, TEXTOS_PAUSA[nombre], fuentes["normal"], elegido,
                          C["dorado"] if elegido else C["panel"])
    texto_centrado(pantalla, "Flechas: elegir y cambiar  ·  P o Esc: seguir", fuentes["chica"],
                   C["texto"], (caja.centerx, caja.bottom - 24))


# ---------------------------------------------------------------- resultado y fin de partida
def dibujar_resultado(pantalla, fondo, fuentes, numero_ronda, taza, jurado, estrellas_visibles, listo, record, t):
    """Resultado de una ronda: la taza terminada, el %, las estrellas que van apareciendo y el jurado.

    record: True si esta taza es la mejor de su dibujo (entra a la galería).
    """
    pantalla.blit(fondo, (0, 0))
    taza.dibujar(pantalla, con_guia=False)
    if record:
        cartel = dibujar_panel(pantalla, (150, 594, 360, 40), C["dorado"], C["brillo_dorado"])
        texto_centrado(pantalla, "¡Récord! Tu taza entra a la galería", fuentes["chica"], C["texto"], cartel.center)
    panel = dibujar_panel(pantalla, (668, 12, 264, 616))
    texto_centrado(pantalla, RONDAS[numero_ronda]["nombre"], fuentes["grande"], C["texto"], (panel.centerx, 52))
    texto_centrado(pantalla, f"{taza.porcentaje}%", fuentes["titulo"], C["acento"], (panel.centerx, 120))
    dibujar_fila_estrellas(pantalla, (panel.centerx, 184), estrellas_visibles, px=6, separacion=70)
    dibujar_globo(pantalla, (panel.x + 16, 230, panel.width - 32, 60), jurado.frase(), fuentes["chica"], panel.centerx)
    jurado.dibujar(pantalla, (panel.centerx, 440))
    for i, umbral in enumerate(UMBRALES_ESTRELLAS):
        texto = f"{i + 1} estrella{'s' if i > 0 else ''}: {umbral}%"
        texto_centrado(pantalla, texto, fuentes["chica"], C["texto"], (panel.centerx, 470 + i * 24))
    if listo and parpadea(t):
        siguiente = "siguiente ronda" if numero_ronda + 1 < len(RONDAS) else "ver el final"
        texto_centrado(pantalla, "Enter o Espacio:", fuentes["chica"], C["texto"], (panel.centerx, 560))
        texto_centrado(pantalla, siguiente, fuentes["normal"], C["acento"], (panel.centerx, 588))


_TROFEO = (
    ".OOOOOOOOOO.",
    "OOYYYYYYYYOO",
    "OYOYYYYYYOYO",
    "OYOYYWYYYOYO",
    ".OOYYWYYYOO.",
    "...OYYYYO...",
    "....OYYO....",
    ".....OO.....",
    "....OYYO....",
    "...OOOOOO...",
    "...OKKKKO...",
    "...OOOOOO...",
)


def dibujar_victoria(pantalla, fondo, fuentes, estrellas_por_ronda, puntos, jurado, pelaje, t):
    """Pantalla de victoria: trofeo, estrellas de cada ronda, los puntos y los dos gatos festejando."""
    pantalla.blit(fondo, (0, 0))
    caja = dibujar_panel(pantalla, (120, 20, 720, 600))
    titulo_con_sombra(pantalla, "¡Ganaste el concurso!", fuentes["titulo"], (ANCHO // 2, 74))
    texto_centrado(pantalla, f"{puntos} puntos  ·  {sum(estrellas_por_ronda)} de {len(RONDAS) * 3} estrellas",
                   fuentes["normal"], C["acento"], (ANCHO // 2, 126))
    for i, estrellas in enumerate(estrellas_por_ronda):
        y = 168 + i * 38
        pantalla.blit(fuentes["chica"].render(RONDAS[i]["nombre"], False, C["texto"]), (190, y - 12))
        dibujar_fila_estrellas(pantalla, (440, y), estrellas, px=3, separacion=36)
    trofeo = pixelar(_TROFEO, {"O": C["contorno"], "Y": C["dorado"], "W": C["blanco"], "K": C["madera_oscura"]}, 8)
    # el trofeo flota un poquito (sube y baja con un seno)
    pantalla.blit(trofeo, trofeo.get_rect(center=(690, 250 + round(math.sin(t * 3) * 6))))
    dibujar_gato(pantalla, (320, 530), pelaje, 7, "contento", delantal=True)
    jurado.dibujar(pantalla, (640, 530), 7)
    if parpadea(t):
        texto_centrado(pantalla, "Enter: ver la galería", fuentes["normal"], C["acento"], (ANCHO // 2, caja.bottom - 34))


def dibujar_derrota(pantalla, fondo, fuentes, motivo, numero_ronda, taza, puntos, jurado, t):
    """Pantalla de derrota: el motivo, cómo quedó la taza, los puntos y la opción de volver a jugar."""
    pantalla.blit(fondo, (0, 0))
    taza.dibujar(pantalla, con_guia=True)
    panel = dibujar_panel(pantalla, (668, 12, 264, 616))
    texto_centrado(pantalla, "Perdiste", fuentes["grande"], C["texto"], (panel.centerx, 50))
    texto_envuelto(pantalla, MOTIVOS_DERROTA[motivo], fuentes["normal"], C["acento"], (panel.x + 22, 82, panel.width - 44, 80))
    texto_centrado(pantalla, f"{RONDAS[numero_ronda]['nombre']}: {taza.porcentaje}%", fuentes["normal"],
                   C["texto"], (panel.centerx, 166))
    texto_centrado(pantalla, f"Para pasar: {UMBRALES_ESTRELLAS[0]}%", fuentes["chica"], C["texto"], (panel.centerx, 194))
    texto_centrado(pantalla, f"Puntos: {puntos}", fuentes["normal"], C["texto"], (panel.centerx, 228))
    jurado.dibujar(pantalla, (panel.centerx, 400))
    consejos = {"frio": "Tip: vertí más seguido, sin pausas largas.",
                "leche": "Tip: no vertás dos veces en el mismo lugar.",
                "desborde": "Tip: soltá el pellizco cuando salís del dibujo."}
    texto_envuelto(pantalla, consejos[motivo], fuentes["chica"], C["texto"], (panel.x + 22, 428, panel.width - 44, 80))
    if parpadea(t):
        texto_centrado(pantalla, "Enter: ver la galería", fuentes["normal"], C["acento"], (panel.centerx, 580))


def dibujar_top(pantalla, fondo, fuentes, puntajes, resaltado, t):
    """El top del concurso: los mejores puntajes con nombre, gatito, estrellas y puntos.

    resaltado: el puesto (0 = primero) de la partida que acaba de terminar, o None.
    """
    pantalla.blit(fondo, (0, 0))
    caja = dibujar_panel(pantalla, (150, 16, 660, 608))
    titulo_con_sombra(pantalla, "Top del concurso", fuentes["grande"], (ANCHO // 2, 58))
    if not puntajes:
        texto_centrado(pantalla, "Todavía no hay puntajes. ¡Sé el primero!", fuentes["normal"], C["texto"],
                       (ANCHO // 2, 300))
    for puesto, puntaje in enumerate(puntajes[:CANTIDAD_TOP]):
        y = 110 + puesto * 56
        fila = pygame.Rect(caja.x + 24, y, caja.width - 48, 48)
        if puesto == resaltado:
            dibujar_panel(pantalla, fila, C["dorado"], C["brillo_dorado"])
        texto_centrado(pantalla, f"{puesto + 1}.", fuentes["normal"], C["texto"], (fila.x + 30, fila.centery))
        # la carita del gato que eligió (si el número no es válido, uso el primero)
        pelaje = PELAJES[puntaje["pelaje"]][1] if 0 <= puntaje["pelaje"] < len(PELAJES) else PELAJES[0][1]
        dibujar_gato(pantalla, (fila.x + 82, fila.bottom + 2), pelaje, 3, sombra=False)
        pantalla.blit(fuentes["normal"].render(puntaje["nombre"], False, C["texto"]), (fila.x + 120, fila.y + 8))
        dibujar_estrella(pantalla, (fila.x + 380, fila.centery), True, 3)
        texto_centrado(pantalla, str(puntaje["estrellas"]), fuentes["normal"], C["texto"], (fila.x + 412, fila.centery))
        texto_centrado(pantalla, f"{puntaje['puntos']} pts", fuentes["normal"], C["acento"], (fila.right - 64, fila.centery))
    if resaltado is not None and resaltado >= CANTIDAD_TOP:
        texto_centrado(pantalla, f"Quedaste en el puesto {resaltado + 1}. ¡La próxima entrás!", fuentes["chica"],
                       C["texto"], (ANCHO // 2, caja.bottom - 62))
    if parpadea(t):
        texto_centrado(pantalla, "Enter, R o Esc: volver a la portada", fuentes["normal"], C["acento"],
                       (ANCHO // 2, caja.bottom - 30))


def dibujar_galeria(pantalla, fondo, fuentes, datos, fotos, vacias, nuevos, desde_final, t):
    """Galería de los mejores artes: la mejor taza de cada dibujo, con quién la hizo y su %.

    datos: {dibujo: {"nombre", "porcentaje"}}  fotos: {dibujo: Surface}
    vacias: {dibujo: Surface} con la taza sin leche, para los dibujos que todavía no tienen récord.
    nuevos: los dibujos en los que batiste el récord en esta partida (se marcan en dorado).
    desde_final: True si llegaste acá al terminar una partida (después sigue el top).
    """
    pantalla.blit(fondo, (0, 0))
    titulo = dibujar_panel(pantalla, (230, 10, 500, 56))
    titulo_con_sombra(pantalla, "Galería de los mejores artes", fuentes["normal"], titulo.center)
    for i, ronda in enumerate(RONDAS):
        # 3 marcos arriba y 2 abajo, centrados
        fila, columna = (0, i) if i < 3 else (1, i - 3)
        x = 90 + columna * 280 if fila == 0 else 230 + columna * 280
        y = 80 + fila * 270
        dibujo = ronda["dibujo"]
        if dibujo in nuevos:
            marco = dibujar_panel(pantalla, (x, y, 220, 256), C["dorado"], C["brillo_dorado"])
            cinta = dibujar_panel(pantalla, (x + 130, y - 10, 100, 32), C["acento"], C["contorno"])
            texto_centrado(pantalla, "¡Nuevo!", fuentes["chica"], C["texto_claro"], cinta.center)
        else:
            marco = dibujar_panel(pantalla, (x, y, 220, 256))
        foto = fotos.get(dibujo, vacias[dibujo])
        pantalla.blit(pygame.transform.scale(foto, (TAM_LIENZO, TAM_LIENZO)), (marco.centerx - TAM_LIENZO // 2, y + 12))
        texto_centrado(pantalla, ronda["nombre"], fuentes["normal"], C["texto"], (marco.centerx, y + 170))
        if dibujo in datos:
            texto_centrado(pantalla, f"{datos[dibujo]['porcentaje']}%", fuentes["normal"], C["acento"],
                           (marco.centerx, y + 200))
            texto_centrado(pantalla, f"por {datos[dibujo]['nombre']}", fuentes["chica"], C["texto"], (marco.centerx, y + 230))
        else:
            texto_centrado(pantalla, "Todavía nadie", fuentes["chica"], C["texto"], (marco.centerx, y + 214))
    if parpadea(t):
        texto = "Enter: ver el top" if desde_final else "R o Esc: volver a la portada"
        texto_centrado(pantalla, texto, fuentes["normal"], C["acento"], (ANCHO // 2, 620))


def dibujar_sin_camara(pantalla, fondo, fuentes, error):
    """Aviso claro cuando la cámara (o MediaPipe) no anda: el juego no se rompe, explica qué hacer."""
    pantalla.blit(fondo, (0, 0))
    caja = dibujar_panel(pantalla, (120, 80, 720, 440))
    titulo_con_sombra(pantalla, "No encuentro la cámara", fuentes["grande"], (ANCHO // 2, caja.y + 56))
    texto_centrado(pantalla, error, fuentes["normal"], C["acento"], (ANCHO // 2, caja.y + 112))
    lineas = [
        "Este juego se juega con la mano frente a la webcam.",
        "1. Conectá la cámara (o revisá que no esté tapada).",
        "2. Cerrá otras apps que la estén usando (Zoom, Meet, Teams).",
        "3. En Windows: Configuración > Privacidad > Cámara, permitir apps.",
        "4. Cerrá esta ventana y volvé a abrir el juego.",
    ]
    y = caja.y + 160
    for linea in lineas:
        y = texto_envuelto(pantalla, linea, fuentes["chica"], C["texto"], (caja.x + 60, y, caja.width - 120, 60)) + 12
    texto_centrado(pantalla, "Cerrá con la X o con Esc", fuentes["chica"], C["acento"], (ANCHO // 2, caja.bottom - 30))