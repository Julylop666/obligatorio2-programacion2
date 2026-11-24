"""escenas.py - Lo que se dibuja en cada estado: portada, instrucciones, HUD de la ronda,
resultado, victoria, derrota, pausa, "¡Mostrá la pata!" y el aviso de cámara que no abre.

Estas funciones solo DIBUJAN: no cambian nada del juego. Reciben lo que necesitan mostrar.
"""
import math
import pygame
from ajustes import (COLORES as C, ANCHO, PX, RONDAS, COLOR_VELO, RECT_PANEL_CAMARA,
                     RECT_PANEL_JURADO, RECT_PANEL_PUNTAJE, RECT_TITULO_RONDA, RECT_BARRA_LECHE,
                     RECT_BARRA_TEMPERATURA, TAM_MINIATURA, POS_MINIATURA, POS_JURADO,
                     TAM_CAMARA_INSTRUCCIONES, POS_CAMARA_INSTRUCCIONES, MOTIVOS_DERROTA,
                     POS_LIENZO, TAM_LIENZO, UMBRALES_ESTRELLAS)
from dibujo import (dibujar_panel, texto_centrado, texto_envuelto, dibujar_barra, dibujar_fila_estrellas,
                    dibujar_velo, dibujar_camara, dibujar_gato_barista, dibujar_jarra, pixelar)
from latte import calcular_estrellas

CENTRO_TAZA = (POS_LIENZO[0] + TAM_LIENZO * PX // 2, POS_LIENZO[1] + TAM_LIENZO * PX // 2)


def titulo_con_sombra(pantalla, texto, fuente, centro):
    """Escribe un título grande en color oscuro con una sombra clara, estilo cartel."""
    texto_centrado(pantalla, texto, fuente, C["texto"], centro, sombra=C["dorado"])


def parpadea(t, veces_por_segundo=1.5):
    """Devuelve True la mitad del tiempo: sirve para hacer titilar un texto."""
    return math.sin(t * veces_por_segundo * 2 * math.pi) > -0.3


# ---------------------------------------------------------------- portada e instrucciones
def dibujar_portada(pantalla, fondo, fuentes, taza_muestra, jurado, t):
    """Portada: título, el gato barista, Don Salmón y una taza con un corazón de muestra."""
    pantalla.blit(fondo, (0, 0))
    panel = dibujar_panel(pantalla, (150, 24, 660, 150))
    titulo_con_sombra(pantalla, "Purr & Brew", fuentes["titulo"], (ANCHO // 2, panel.y + 54))
    texto_centrado(pantalla, "LATTE ART", fuentes["grande"], C["acento"], (ANCHO // 2, panel.y + 112))
    # taza de muestra, más chica, apoyada sobre la barra
    taza_muestra.dibujar(pantalla, con_guia=False, pos=(ANCHO // 2 - 136, 214), px=2)
    dibujar_gato_barista(pantalla, (190, 512), 8)
    dibujar_jarra(pantalla, (262, 470), False)
    jurado.dibujar(pantalla, (770, 512))
    caja = dibujar_panel(pantalla, (150, 528, 660, 100))
    texto_centrado(pantalla, "Don Salmón te anotó en el concurso de latte art del barrio.",
                   fuentes["chica"], C["texto"], (ANCHO // 2, caja.y + 26))
    if parpadea(t):
        texto_centrado(pantalla, "Enter o Espacio para empezar", fuentes["normal"], C["acento"],
                       (ANCHO // 2, caja.y + 58))
    texto_centrado(pantalla, "M música  ·  N sonidos  ·  Esc pausa", fuentes["chica"], C["texto"],
                   (ANCHO // 2, caja.y + 84))


def dibujar_instrucciones(pantalla, fondo, fuentes, imagen, punto, pellizco, t):
    """Instrucciones: cómo poner la mano y una prueba en vivo del pellizco."""
    pantalla.blit(fondo, (0, 0))
    dibujar_panel(pantalla, (24, 20, 912, 600))
    titulo_con_sombra(pantalla, "¿Cómo se juega?", fuentes["grande"], (ANCHO // 2, 62))
    rect_camara = pygame.Rect(POS_CAMARA_INSTRUCCIONES, TAM_CAMARA_INSTRUCCIONES)
    dibujar_camara(pantalla, imagen, rect_camara, punto, pellizco, fuentes["chica"])
    # indicador de la prueba de pellizco
    estado = pygame.Rect(rect_camara.x, rect_camara.bottom + 16, rect_camara.width, 56)
    if punto is None:
        color, texto = C["sombra"], "No veo tu mano todavía"
    elif pellizco:
        color, texto = C["verde"], "¡Pellizco! Sale leche"
    else:
        color, texto = C["azul"], "Mano detectada: ahora pellizcá"
    dibujar_panel(pantalla, estado, color, C["contorno"])
    texto_centrado(pantalla, texto, fuentes["normal"], C["texto"], estado.center)

    pasos = [
        "1. Sentate a unos 50-80 cm de la cámara, con buena luz de frente.",
        "2. Mostrá la palma: la punta del dedo índice mueve la jarra.",
        "3. Juntá índice y pulgar (pellizco) para verter la leche.",
        "4. Seguí el dibujo punteado. Lo que cae afuera resta.",
        "5. Ojo con la leche de la jarra y con el café, que se enfría.",
        "1 estrella pasa la ronda. Con 3, Don Salmón llora de emoción.",
        "Truco: cuanto más alta la mano, más aguda suena la leche.",
    ]
    y = 140
    for paso in pasos:
        y = texto_envuelto(pantalla, paso, fuentes["chica"], C["texto"], (468, y, 440, 200)) + 10
    if parpadea(t):
        texto_centrado(pantalla, "Enter o Espacio: ¡a competir!", fuentes["normal"], C["acento"], (688, 580))


# ---------------------------------------------------------------- HUD de la ronda
def dibujar_hud(pantalla, fuentes, numero_ronda, imagen, punto, pellizco, jurado, porcentaje,
                fraccion_leche, fraccion_temperatura):
    """Dibuja todo lo que rodea a la taza mientras jugás: título, cámara, jurado, % y barras."""
    ronda = RONDAS[numero_ronda]
    caja = dibujar_panel(pantalla, RECT_TITULO_RONDA)
    texto_centrado(pantalla, f"Ronda {numero_ronda + 1}/{len(RONDAS)}: {ronda['nombre']}",
                   fuentes["normal"], C["texto"], caja.center)
    # cámara
    dibujar_panel(pantalla, RECT_PANEL_CAMARA)
    dibujar_camara(pantalla, imagen, (POS_MINIATURA, TAM_MINIATURA), punto, pellizco, fuentes["chica"])
    # jurado y su frase
    panel = dibujar_panel(pantalla, RECT_PANEL_JURADO)
    jurado.dibujar(pantalla, POS_JURADO)
    texto_centrado(pantalla, jurado.frase(), fuentes["chica"], C["acento"], (panel.centerx, panel.bottom - 22))
    # puntaje
    panel = dibujar_panel(pantalla, RECT_PANEL_PUNTAJE)
    texto_centrado(pantalla, f"{porcentaje}%", fuentes["grande"], C["texto"], (panel.centerx, panel.y + 32))
    dibujar_fila_estrellas(pantalla, (panel.centerx, panel.y + 70), calcular_estrellas(porcentaje))
    pantalla.blit(fuentes["chica"].render("Leche", False, C["texto"]), (RECT_BARRA_LECHE[0], RECT_BARRA_LECHE[1] - 24))
    dibujar_barra(pantalla, RECT_BARRA_LECHE, fraccion_leche, C["leche"])
    pantalla.blit(fuentes["chica"].render("Temperatura", False, C["texto"]),
                  (RECT_BARRA_TEMPERATURA[0], RECT_BARRA_TEMPERATURA[1] - 24))
    # el termómetro pasa de rojo (caliente) a celeste (frío)
    color = C["rojo_suave"] if fraccion_temperatura > 0.5 else (C["dorado"] if fraccion_temperatura > 0.25 else C["azul"])
    dibujar_barra(pantalla, RECT_BARRA_TEMPERATURA, fraccion_temperatura, color)


def dibujar_cuenta(pantalla, fuentes, segundos):
    """Dibuja el '3, 2, 1' grande sobre la taza antes de empezar a verter."""
    numero = math.ceil(segundos)
    caja = dibujar_panel(pantalla, pygame.Rect(0, 0, 220, 130).move(CENTRO_TAZA[0] - 110, CENTRO_TAZA[1] - 65))
    texto_centrado(pantalla, str(numero), fuentes["titulo"], C["texto"], (caja.centerx, caja.y + 50))
    texto_centrado(pantalla, "Acomodá la mano", fuentes["chica"], C["acento"], (caja.centerx, caja.bottom - 22))


def dibujar_sin_mano(pantalla, fuentes, t):
    """Cartel de cuando la cámara no ve la mano: el juego está en pausa y el tiempo congelado."""
    dibujar_velo(pantalla, COLOR_VELO)
    caja = dibujar_panel(pantalla, pygame.Rect(0, 0, 440, 170).move(CENTRO_TAZA[0] - 220, CENTRO_TAZA[1] - 85))
    titulo_con_sombra(pantalla, "¡Mostrá la pata!", fuentes["grande"], (caja.centerx, caja.y + 46))
    texto_centrado(pantalla, "Poné la mano frente a la cámara.", fuentes["chica"], C["texto"],
                   (caja.centerx, caja.y + 96))
    texto_centrado(pantalla, "El tiempo está congelado.", fuentes["chica"], C["acento"],
                   (caja.centerx, caja.y + 126))


def dibujar_pausa(pantalla, fuentes):
    """Menú de pausa (Esc)."""
    dibujar_velo(pantalla, COLOR_VELO)
    caja = dibujar_panel(pantalla, (280, 200, 400, 220))
    titulo_con_sombra(pantalla, "Pausa", fuentes["grande"], (caja.centerx, caja.y + 50))
    lineas = ["Esc: seguir jugando", "R: volver a la portada", "M: música  ·  N: sonidos"]
    for i, linea in enumerate(lineas):
        texto_centrado(pantalla, linea, fuentes["normal"], C["texto"], (caja.centerx, caja.y + 108 + i * 34))


# ---------------------------------------------------------------- resultado y fin de partida
def dibujar_resultado(pantalla, fondo, fuentes, numero_ronda, taza, jurado, estrellas_visibles, listo, t):
    """Resultado de una ronda: la taza terminada, el %, las estrellas que van apareciendo y el jurado."""
    pantalla.blit(fondo, (0, 0))
    taza.dibujar(pantalla, con_guia=False)
    ronda = RONDAS[numero_ronda]
    panel = dibujar_panel(pantalla, (668, 12, 264, 616))
    texto_centrado(pantalla, f"{ronda['nombre']}", fuentes["grande"], C["texto"], (panel.centerx, 52))
    texto_centrado(pantalla, f"{taza.porcentaje}%", fuentes["titulo"], C["acento"], (panel.centerx, 120))
    dibujar_fila_estrellas(pantalla, (panel.centerx, 184), estrellas_visibles, px=6, separacion=70)
    jurado.dibujar(pantalla, (panel.centerx, 380))
    texto_centrado(pantalla, jurado.frase(), fuentes["chica"], C["acento"], (panel.centerx, 404))
    texto_centrado(pantalla, f"1 estrella: {UMBRALES_ESTRELLAS[0]}%", fuentes["chica"], C["texto"], (panel.centerx, 456))
    texto_centrado(pantalla, f"2 estrellas: {UMBRALES_ESTRELLAS[1]}%", fuentes["chica"], C["texto"], (panel.centerx, 480))
    texto_centrado(pantalla, f"3 estrellas: {UMBRALES_ESTRELLAS[2]}%", fuentes["chica"], C["texto"], (panel.centerx, 504))
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


def dibujar_victoria(pantalla, fondo, fuentes, estrellas_por_ronda, jurado, t):
    """Pantalla de victoria: trofeo, estrellas de cada ronda y Don Salmón llorando de emoción."""
    pantalla.blit(fondo, (0, 0))
    caja = dibujar_panel(pantalla, (120, 20, 720, 600))
    titulo_con_sombra(pantalla, "¡Ganaste el concurso!", fuentes["titulo"], (ANCHO // 2, 78))
    total = sum(estrellas_por_ronda)
    texto_centrado(pantalla, f"{total} de {len(RONDAS) * 3} estrellas", fuentes["normal"], C["acento"],
                   (ANCHO // 2, 132))
    for i, estrellas in enumerate(estrellas_por_ronda):
        y = 176 + i * 44
        pantalla.blit(fuentes["chica"].render(RONDAS[i]["nombre"], False, C["texto"]), (190, y - 12))
        dibujar_fila_estrellas(pantalla, (440, y), estrellas, px=3, separacion=36)
    trofeo = pixelar(_TROFEO, {"O": C["contorno"], "Y": C["dorado"], "W": C["blanco"], "K": C["madera_oscura"]}, 8)
    # el trofeo flota un poquito (sube y baja con un seno)
    pantalla.blit(trofeo, trofeo.get_rect(center=(680, 260 + round(math.sin(t * 3) * 6))))
    dibujar_gato_barista(pantalla, (330, 556), 8)
    jurado.dibujar(pantalla, (640, 548))
    if parpadea(t):
        texto_centrado(pantalla, "R: volver a jugar", fuentes["normal"], C["acento"], (ANCHO // 2, caja.bottom - 34))


def dibujar_derrota(pantalla, fondo, fuentes, motivo, numero_ronda, taza, jurado, t):
    """Pantalla de derrota: el motivo, cómo quedó la taza y la opción de volver a jugar."""
    pantalla.blit(fondo, (0, 0))
    taza.dibujar(pantalla, con_guia=True)
    panel = dibujar_panel(pantalla, (668, 12, 264, 616))
    texto_centrado(pantalla, "Perdiste", fuentes["grande"], C["texto"], (panel.centerx, 52))
    texto_envuelto(pantalla, MOTIVOS_DERROTA[motivo], fuentes["normal"], C["acento"],
                   (panel.x + 22, 88, panel.width - 44, 80))
    texto_centrado(pantalla, f"{RONDAS[numero_ronda]['nombre']}: {taza.porcentaje}%", fuentes["normal"],
                   C["texto"], (panel.centerx, 180))
    texto_centrado(pantalla, f"Para pasar: {UMBRALES_ESTRELLAS[0]}%", fuentes["chica"], C["texto"],
                   (panel.centerx, 210))
    jurado.dibujar(pantalla, (panel.centerx, 400))
    consejos = {"frio": "Tip: vertí más seguido, sin pausas largas.",
                "leche": "Tip: no vertás dos veces en el mismo lugar.",
                "desborde": "Tip: soltá el pellizco cuando salís del dibujo."}
    texto_envuelto(pantalla, consejos[motivo], fuentes["chica"], C["texto"], (panel.x + 22, 432, panel.width - 44, 80))
    if parpadea(t):
        texto_centrado(pantalla, "R: volver a jugar", fuentes["normal"], C["acento"], (panel.centerx, 586))


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
        "4. Cerrá esta ventana y volvé a abrir el juego (py main.py).",
    ]
    y = caja.y + 160
    for linea in lineas:
        y = texto_envuelto(pantalla, linea, fuentes["chica"], C["texto"], (caja.x + 60, y, caja.width - 120, 60)) + 12
    texto_centrado(pantalla, "Cerrá con la X o con Esc", fuentes["chica"], C["acento"], (ANCHO // 2, caja.bottom - 30))
