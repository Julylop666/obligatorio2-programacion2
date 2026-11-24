"""ajustes.py - Constantes de Purr & Brew: Latte Art.

Acá viven TODOS los números del juego: colores, tamaños, velocidades, umbrales de la
cámara (pellizco y suavizado), tiempos, cantidad de leche y umbrales de las estrellas.
Si quiero cambiar el balance o la dificultad, toco solo este archivo.
"""
import os

# ---------------------------------------------------------------- rutas
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_SONIDOS = os.path.join(RUTA_BASE, "sonidos")
RUTA_FUENTE = os.path.join(RUTA_BASE, "fuentes", "Jersey15.ttf")

# ---------------------------------------------------------------- ventana
ANCHO = 960
ALTO = 640
# 30 y no 60: la webcam entrega unos 30 cuadros por segundo, así que más FPS no suman nada
# y MediaPipe tiene tiempo de procesar cada cuadro.
FPS = 30
TITULO = "Purr & Brew: Latte Art"
DT_MAXIMO = 0.1          # si un cuadro tarda mucho (la cámara se trabó), no dejo que el tiempo "salte"

# ---------------------------------------------------------------- paleta (la misma de Purr & Brew, sin rosado)
COLORES = {
    "texto": (94, 62, 52),
    "texto_claro": (255, 250, 243),
    "panel": (255, 247, 238),
    "zocalo": (146, 190, 180),        # bordes de los paneles: verde agua apagado
    "pared": (205, 228, 218),         # verde menta apagado
    "acento": (68, 136, 146),         # textos destacados: verde azulado
    "contorno": (62, 42, 50),
    "sombra": (210, 185, 160),
    "dorado": (246, 206, 124),
    "brillo_dorado": (236, 166, 32),
    "verde": (170, 214, 172),
    "menta": (166, 212, 192),
    "azul": (172, 202, 236),
    "azul_medio": (120, 170, 225),
    "agua": (150, 200, 240),
    "blanco": (255, 255, 255),
    "leche": (255, 252, 246),
    "espuma": (244, 228, 205),
    "cafe": (139, 94, 60),
    "crema_cafe": (176, 120, 72),     # la "crema" dorada que tiene arriba el espresso
    "cafe_oscuro": (100, 58, 40),
    "caramelo": (150, 80, 30),
    "metal": (206, 210, 220),
    "metal_oscuro": (150, 156, 170),
    "mesa": (240, 205, 165),
    "barra": (196, 150, 110),
    "tablas": (172, 126, 92),
    "madera_oscura": (150, 104, 76),
    "taza": (255, 240, 225),          # loza de la taza
    "taza_sombra": (226, 204, 186),
    "plato": (190, 217, 207),         # platito verde agua, así se ven las manchas de leche
    "plato_sombra": (146, 190, 180),
    "chaleco_verde": (112, 156, 124), # chaleco de Don Salmón
    "anteojos": (216, 207, 219),
    "delantal_celeste": (130, 187, 214),
    "nariz": (176, 98, 70),           # nariz y orejas en marrón tostado (en vez de rosado)
    "rojo_suave": (214, 110, 80),     # termómetro caliente
    "planta": (150, 205, 150),
    "planta_oscura": (112, 168, 120),
    "papel_rayas": (190, 217, 207),   # rayas del papel tapiz
    "cortina": (126, 182, 170),
    "cielo": (176, 212, 238),
    "cielo_claro": (212, 233, 242),
    "sol": (255, 240, 190),
    "nube": (255, 250, 245),
    "lampara": (255, 220, 120),
    "pizarron": (70, 86, 80),
    "tiza": (236, 240, 232),
    "mimbre": (224, 186, 142),        # individual de mimbre debajo del plato
    "mimbre_oscuro": (196, 150, 110),
    "servilleta": (190, 217, 207),
}
COLOR_DON_SALMON = (236, 150, 118)
COLOR_OJOS = (50, 35, 45)
COLOR_OJOS_BARISTA = (78, 150, 110)
COLOR_VELO = (62, 42, 50, 160)        # velo oscuro con transparencia (pausa y "Mostrá la pata")
COLOR_GUIA = (255, 244, 222, 190)     # puntitos del contorno guía (tenues, con transparencia)

# ---------------------------------------------------------------- pixel art
PX = 4                    # tamaño de un "pixel del arte" en pantalla
PX_GATO = 6               # Don Salmón en el panel del jurado (como en Purr & Brew)
PX_JARRA = 5              # la jarrita de leche

# ---------------------------------------------------------------- la taza (en pixeles del arte)
# Toda la taza se dibuja en una superficie chiquita (LIENZO) que después se agranda PX veces:
# así queda pixel art y además cada pixel del lienzo es una "celda" para el puntaje.
TAM_LIENZO = 136
CENTRO_LIENZO = TAM_LIENZO // 2
POS_LIENZO = (58, 72)     # esquina de arriba a la izquierda del lienzo en pantalla
RADIO_PLATO = 64
RADIO_TAZA = 52
RADIO_CAFE = 46
SEPARACION_GUIA = 1       # la guía es punteada: no pongo un puntito si hay otro a esta distancia o menos

# ---------------------------------------------------------------- cámara y detección
INDICE_CAMARA = 0
ANCHO_CAMARA = 640
ALTO_CAMARA = 480
MAX_MANOS = 1
CONFIANZA_DETECCION = 0.6
CONFIANZA_SEGUIMIENTO = 0.5
COMPLEJIDAD_MODELO = 0    # 0 = modelo liviano de MediaPipe (más rápido, alcanza para un dedo)
# Puntos de la mano según MediaPipe (21 en total)
PUNTO_MUNECA = 0
PUNTO_PULGAR = 4
PUNTO_INDICE = 8
PUNTO_BASE_MEDIO = 9
# Pellizco: distancia pulgar-índice dividida por el tamaño de la mano (muñeca a base del dedo medio).
# Dividir hace que funcione igual con la mano cerca o lejos de la cámara.
# Son dos umbrales distintos (histéresis) para que el pellizco no "parpadee" justo en el borde.
UMBRAL_PELLIZCO = 0.35    # por debajo de esto empieza el pellizco
UMBRAL_SOLTAR = 0.50      # por encima de esto se suelta
# Zona útil del cuadro: no hace falta llevar la mano hasta el borde de la cámara.
MARGEN_CAMARA_X = 0.18
MARGEN_CAMARA_Y = 0.15
SUAVIZADO = 0.35          # qué parte del camino hacia el dedo avanza la jarra por cuadro (1 = sin suavizar)
TOLERANCIA_SIN_MANO = 0.3 # segundos sin mano antes de mostrar el cartel (evita que parpadee)
# Hasta dónde puede ir la jarra en pantalla (un poco más que la taza)
ZONA_JARRA = (30, 50, 600, 580)

# miniatura de la cámara
TAM_MINIATURA = (224, 168)
POS_MINIATURA = (688, 24)
PIXEL_MINIATURA = 3       # la imagen de la cámara también se pixela, para que combine
TAM_CAMARA_INSTRUCCIONES = (384, 288)
POS_CAMARA_INSTRUCCIONES = (48, 150)

# ---------------------------------------------------------------- leche y partículas
CAUDAL_LECHE = 80         # gotas por segundo mientras hay pellizco
RADIO_CHORRO = 9          # en pantalla: qué tan lejos del dedo puede caer cada gota
VELOCIDAD_DESVIO = 18     # pixeles por segundo que se corre una gota mientras cae
ALTURA_GOTA = 1.0         # la gota "cae" de altura 1 a 0
VELOCIDAD_CAIDA = 4.0     # alturas por segundo (tarda 0.25 s en llegar al café)
RADIO_ESPUMA_INICIAL = 1  # en pixeles del arte
RADIO_ESPUMA_FINAL = 3
TIEMPO_ESPUMA = 0.35      # lo que tarda la espuma en terminar de abrirse
TAM_GOTA = 2              # tamaño de la gota cayendo, en pixeles del arte
ELEVACION_JARRA = 52      # cuántos pixeles por encima del punto de caída está el pico de la jarra
ANGULO_VERTER = 32        # grados que se inclina la jarra al verter

# ---------------------------------------------------------------- puntaje y reglas
# % = cobertura del dibujo - PENALIZACION_FUERA * (leche fuera del dibujo / tamaño del dibujo)
PENALIZACION_FUERA = 0.4
UMBRALES_ESTRELLAS = (40, 60, 80)   # % para 1, 2 y 3 estrellas (1 estrella = pasás la ronda)
LIMITE_DESBORDE = 1.0     # perdés si la leche afuera del dibujo ya ocupa lo mismo que el dibujo entero
CUENTA_REGRESIVA = 3      # segundos de "3, 2, 1" antes de cada ronda (para acomodar la mano)
TIEMPO_SERVIR = 1.5       # con 3 estrellas, si dejás de verter este tiempo, la taza se sirve sola

# Las 5 rondas del concurso, en el orden en que aprenden los baristas de verdad:
# corazón -> tulipán (círculos apilados) -> rosetta (hoja con capas) -> cisne -> cara de gato.
# tiempo = segundos hasta que el café se enfría; leche = cantidad de gotas de la jarra.
RONDAS = [
    {"dibujo": "corazon", "nombre": "Corazón", "tiempo": 60, "leche": 900},
    {"dibujo": "tulipan", "nombre": "Tulipán", "tiempo": 65, "leche": 950},
    {"dibujo": "rosetta", "nombre": "Rosetta", "tiempo": 75, "leche": 1100},
    {"dibujo": "cisne", "nombre": "Cisne", "tiempo": 75, "leche": 1050},
    {"dibujo": "gato", "nombre": "Cara de gato", "tiempo": 80, "leche": 1150},
]

# ---------------------------------------------------------------- jugador: nombre, gato y top
PELAJES = [                                # los mismos 4 gatos de Purr & Brew (nombre, color)
    ("Naranja", (240, 170, 100)),
    ("Gris", (172, 178, 190)),
    ("Crema", (246, 226, 192)),
    ("Negro", (78, 72, 84)),
]
LARGO_MAXIMO_NOMBRE = 12
RUTA_PUNTAJES = os.path.join(RUTA_BASE, "puntajes.json")
CANTIDAD_TOP = 8                          # cuántos puestos se muestran en el top

# ---------------------------------------------------------------- estados del juego
PORTADA = "PORTADA"
NOMBRE = "NOMBRE"
ELEGIR_GATO = "ELEGIR_GATO"
INSTRUCCIONES = "INSTRUCCIONES"
JUGANDO = "JUGANDO"
RESULTADO_RONDA = "RESULTADO_RONDA"
VICTORIA = "VICTORIA"
DERROTA = "DERROTA"
TOP = "TOP"
SIN_CAMARA = "SIN_CAMARA"

# motivos de derrota (y el texto que se muestra)
MOTIVOS_DERROTA = {
    "frio": "Se te enfrió el café...",
    "leche": "Se terminó la leche...",
    "desborde": "¡Se desbordó la taza!",
}

# ---------------------------------------------------------------- jurado (Don Salmón)
# Caras (cada una tiene su animación)
NEUTRAL = "neutral"
CONTENTO = "contento"       # salta y aplaude
PREOCUPADO = "preocupado"   # gotita de sudor y signo de exclamación
ASCO = "asco"               # olorcitos verdes y se sacude
LLORA = "llora"             # lágrimas de emoción
# Lo que dice según cómo va el % (cuando no está comentando algo puntual)
FRASES_CARA = {
    NEUTRAL: "A ver, a ver...",
    CONTENTO: "¡Eso, eso!",
    PREOCUPADO: "Mmm...",
    ASCO: "Uf...",
    LLORA: "¡Es arte! *snif*",
}
# Comentarios en vivo: evento -> (cara que pone, frases posibles). Se elige una frase al azar.
COMENTARIOS = {
    "empieza": (CONTENTO, ["¡Suerte, gatito!", "¡Mostrame esa pata!", "¡Despacito y con amor!"]),
    "estrella": (CONTENTO, ["¡Una estrella más!", "¡Así se hace!", "¡Bravo, bravo!"]),
    "derrame": (ASCO, ["¡Ey, eso va afuera!", "¡Cuidado con el plato!", "¡Uy, se te chorrea!"]),
    "casi_desborde": (ASCO, ["¡Se te desborda!", "¡Pará, pará!"]),
    "poca_leche": (PREOCUPADO, ["¡Queda poca leche!", "Ojo con la jarra..."]),
    "frio": (PREOCUPADO, ["¡Se enfría el café!", "¡Apurate un poquito!"]),
    "quieto": (PREOCUPADO, ["¿Y? ¡Dale que se enfría!", "¿Te quedaste dormido?"]),
    "vuelve_mano": (CONTENTO, ["¡Ahí está esa pata!", "¡Volviste!"]),
}
DURACION_COMENTARIO = 2.5   # segundos que se ve el globito con el comentario
ESPERA_MISMO_COMENTARIO = 7 # no repite el mismo tipo de comentario antes de esto
TIEMPO_MIN_REACCION = 0.7   # la cara de base no cambia más rápido que esto (si no, tiembla)
UMBRAL_ASCO = 0.30          # cara de asco si lo de afuera pasa el 30% del dibujo
# "derrame": junto la leche que cae afuera en un balde que se va vaciando solo; si se llena, comenta
UMBRAL_DERRAME = 45         # celdas
VACIADO_DERRAME = 30        # celdas por segundo
FRACCION_CASI_DESBORDE = 0.7
FRACCION_POCA_LECHE = 0.25
FRACCION_FRIO = 0.25
TIEMPO_QUIETO = 6           # segundos sin verter (con poco %) para que te apure
VELOCIDAD_RESPIRO = 2.0     # vueltas por segundo del "respiro" (sube y baja)
CADA_PARPADEO = 3.2         # segundos entre parpadeos
DURACION_PARPADEO = 0.15
VELOCIDAD_APLAUSO = 6       # aplausos por segundo
ALTURA_SALTO = 2            # pixeles del arte que salta cuando está contento

# ---------------------------------------------------------------- HUD
RECT_PANEL_CAMARA = (668, 12, 264, 196)
RECT_PANEL_JURADO = (668, 216, 264, 236)
RECT_GLOBO = (684, 226, 232, 64)
POS_JURADO = (800, 440)     # dónde apoya los pies Don Salmón
RECT_PANEL_PUNTAJE = (668, 460, 264, 168)
RECT_TITULO_RONDA = (16, 10, 320, 46)
RECT_BARRA_LECHE = (690, 548, 220, 18)
RECT_BARRA_TEMPERATURA = (690, 600, 220, 18)
DURACION_ESTRELLA = 0.5     # en el resultado, cada estrella aparece medio segundo después de la otra

# ---------------------------------------------------------------- sonido
ARCHIVOS_SONIDO = {
    "chorro": "chorro.wav",          # leche saliendo de la jarra (en loop)
    "ding": "ding.wav",              # pasaste la ronda
    "campanita": "campanita.wav",    # aparece una estrella
    "miau_triste": "miau_triste.wav",# perdiste
}
ARCHIVO_MUSICA = "musica_lofi.wav"
VOLUMEN_EFECTOS = 0.8
VOLUMEN_CHORRO = 0.5
VOLUMEN_MUSICA = 0.45
FUNDIDO_CHORRO = 80       # milisegundos de fundido al prender o apagar el chorro