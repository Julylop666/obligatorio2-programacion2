"""vision.py - Todo lo de la cámara: OpenCV (abrir, leer, espejar, liberar) y MediaPipe (detectar la mano).

El resto del juego NO importa cv2 ni mediapipe: solo usa lo que devuelve la clase Camara:
  - detectar()      -> (x, y) del punto entre las puntas del índice y del pulgar, o None si no hay mano
  - hay_pellizco()  -> True si el índice y el pulgar están juntos
  - tamano_mano()   -> qué tan grande se ve la mano (cerca o lejos de la cámara), o None
  - puntas_dedos()  -> las puntas del pulgar y del índice (para dibujarlas en la miniatura), o None
  - miniatura()     -> una Surface de pygame con la imagen de la cámara (o None)
  - liberar()       -> cierra la cámara (cap.release())

Uso MediaPipe 0.10.21 con la API "solutions" (mp.solutions.hands), que trae el modelo de la
mano adentro de la biblioteca. Las versiones nuevas (0.10.30 en adelante) ya no tienen
mp.solutions, por eso la versión está fijada en requirements.txt (ver README).
"""
import math
import os
import cv2
import pygame
from ajustes import (INDICE_CAMARA, ANCHO_CAMARA, ALTO_CAMARA, MAX_MANOS, CONFIANZA_DETECCION,
                     CONFIANZA_SEGUIMIENTO, COMPLEJIDAD_MODELO, PUNTO_MUNECA, PUNTO_PULGAR,
                     PUNTO_INDICE, PUNTO_BASE_MEDIO, UMBRAL_PELLIZCO, UMBRAL_SOLTAR)

# Si mediapipe no está instalado (o es una versión sin mp.solutions) no quiero que el juego
# explote al importar: guardo el error y lo muestro en pantalla.
try:
    import mediapipe as mp
    manos_mp = mp.solutions.hands
    ERROR_MEDIAPIPE = None
except (ImportError, AttributeError) as error:
    manos_mp = None
    ERROR_MEDIAPIPE = "Falta MediaPipe 0.10.21 (py -m pip install -r requirements.txt)"
    print("Aviso:", error)


def distancia(punto_a, punto_b):
    """Devuelve la distancia entre dos puntos (x, y)."""
    return math.hypot(punto_a[0] - punto_b[0], punto_a[1] - punto_b[1])


class Camara:
    """La webcam + el detector de manos de MediaPipe. Se crea UNA sola vez, antes del bucle."""

    def __init__(self):
        """Abre la cámara y prepara el detector. Si algo falla, guarda el motivo en self.error."""
        self.cap = None
        self.detector = None
        self.cuadro = None          # último cuadro leído (ya espejado), en formato de OpenCV
        self.puntos = None          # los 21 puntos de la mano en pixeles del cuadro, o None
        self.pellizco = False
        self.ancho = ANCHO_CAMARA
        self.alto = ALTO_CAMARA
        self.error = ERROR_MEDIAPIPE
        if self.error:
            return
        # En Windows, CAP_DSHOW abre la webcam mucho más rápido que la opción por defecto.
        if os.name == "nt":
            cap = cv2.VideoCapture(INDICE_CAMARA, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(INDICE_CAMARA)
        if not cap.isOpened():
            self.error = "No se pudo abrir la cámara"
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO_CAMARA)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO_CAMARA)
        self.cap = cap
        self.detector = manos_mp.Hands(static_image_mode=False, max_num_hands=MAX_MANOS,
                                       model_complexity=COMPLEJIDAD_MODELO,
                                       min_detection_confidence=CONFIANZA_DETECCION,
                                       min_tracking_confidence=CONFIANZA_SEGUIMIENTO)

    def esta_lista(self):
        """Devuelve True si la cámara abrió y el detector está listo para usarse."""
        return self.cap is not None and self.detector is not None

    def detectar(self):
        """Lee un cuadro, lo espeja y busca la mano.

        Devuelve (x, y) del punto que queda entre las puntas del índice y del pulgar, en pixeles
        del cuadro, o None si no hay mano (o si la cámara no entregó imagen).
        Es la ÚNICA función de detección que usa el juego.
        """
        if not self.esta_lista():
            return None
        ok, cuadro = self.cap.read()
        if not ok:
            self.puntos = None
            self.pellizco = False
            return None
        # Espejo: así, si muevo la mano a la derecha, la jarra también va a la derecha (como un espejo).
        cuadro = cv2.flip(cuadro, 1)
        self.cuadro = cuadro
        self.alto, self.ancho = cuadro.shape[0], cuadro.shape[1]
        # MediaPipe trabaja con colores RGB y OpenCV lee en BGR, por eso convierto.
        rgb = cv2.cvtColor(cuadro, cv2.COLOR_BGR2RGB)
        resultado = self.detector.process(rgb)
        if not resultado.multi_hand_landmarks:
            self.puntos = None
            self.pellizco = False
            return None
        # MediaPipe da los puntos entre 0 y 1; los paso a pixeles para que las distancias
        # no se deformen (el cuadro es más ancho que alto).
        mano = resultado.multi_hand_landmarks[0].landmark
        self.puntos = []
        for punto in mano:
            self.puntos.append((punto.x * self.ancho, punto.y * self.alto))
        self.actualizar_pellizco()
        # Uso el punto del medio entre el pulgar y el índice (y no la punta del índice sola):
        # al pellizcar, el índice baja hacia el pulgar y la jarra "saltaba". Con el punto medio,
        # al juntar los dedos la jarra se queda donde estaba: es donde "agarrás" la jarrita.
        pulgar = self.puntos[PUNTO_PULGAR]
        indice = self.puntos[PUNTO_INDICE]
        return ((pulgar[0] + indice[0]) / 2, (pulgar[1] + indice[1]) / 2)

    def actualizar_pellizco(self):
        """Decide si hay pellizco comparando la distancia pulgar-índice con el tamaño de la mano."""
        tam_mano = distancia(self.puntos[PUNTO_MUNECA], self.puntos[PUNTO_BASE_MEDIO])
        if tam_mano == 0:
            return
        apertura = distancia(self.puntos[PUNTO_PULGAR], self.puntos[PUNTO_INDICE]) / tam_mano
        # Histéresis: para empezar el pellizco hay que cerrar bastante, y para soltarlo hay que
        # abrir bastante. En el medio se queda como estaba, así el chorro no se corta solo.
        if self.pellizco and apertura > UMBRAL_SOLTAR:
            self.pellizco = False
        elif not self.pellizco and apertura < UMBRAL_PELLIZCO:
            self.pellizco = True

    def hay_pellizco(self):
        """Devuelve True si en el último cuadro el índice y el pulgar estaban juntos."""
        return self.puntos is not None and self.pellizco

    def tamano_mano(self):
        """Devuelve qué tan grande se ve la mano en el cuadro (o None si no hay mano).

        Es la distancia de la muñeca a la base del dedo medio dividida por el alto del cuadro:
        si la mano está cerca de la cámara se ve más grande y el número es más alto.
        """
        if self.puntos is None:
            return None
        return distancia(self.puntos[PUNTO_MUNECA], self.puntos[PUNTO_BASE_MEDIO]) / self.alto

    def puntas_dedos(self):
        """Devuelve ((x, y) del pulgar, (x, y) del índice) en pixeles del cuadro, o None si no hay mano."""
        if self.puntos is None:
            return None
        return (self.puntos[PUNTO_PULGAR], self.puntos[PUNTO_INDICE])

    def miniatura(self, tam, pixel):
        """Devuelve el último cuadro como Surface de pygame del tamaño tam, pixelado (o None).

        Primero achico la imagen 'pixel' veces y después pygame la agranda sin suavizar:
        así la cámara también se ve pixel art.
        """
        if self.cuadro is None:
            return None
        chico = (tam[0] // pixel, tam[1] // pixel)
        reducido = cv2.resize(self.cuadro, chico, interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(reducido, cv2.COLOR_BGR2RGB)
        superficie = pygame.image.frombuffer(rgb.tobytes(), chico, "RGB")
        return pygame.transform.scale(superficie, tam)

    def liberar(self):
        """Cierra la cámara y el detector. Se llama una vez, al cerrar el juego."""
        if self.cap is not None:
            self.cap.release()
        if self.detector is not None:
            self.detector.close()