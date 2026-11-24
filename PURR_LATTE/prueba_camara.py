"""prueba_camara.py - Prueba la cámara sola, sin el juego (Etapa 1).

Muestra la imagen de la cámara pixelada, el punto del dedo índice y si hay pellizco.
Sirve para ver si la detección anda bien con la luz y el fondo que tengo.
Se ejecuta con: python prueba_camara.py   (se cierra con la X o con Esc)
"""
import pygame
from ajustes import COLORES as C, FPS
from vision import Camara


def principal():
    """Abre una ventanita con la cámara y dibuja el punto del dedo encima."""
    pygame.init()
    pantalla = pygame.display.set_mode((640, 520))
    pygame.display.set_caption("Prueba de cámara - Purr & Brew: Latte Art")
    fuente = pygame.font.Font(None, 30)
    reloj = pygame.time.Clock()
    camara = Camara()                      # la cámara se abre UNA vez, antes del bucle
    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                corriendo = False
        punto = camara.detectar()
        pantalla.fill(C["pared"])
        imagen = camara.miniatura((640, 480), 4)
        if imagen is not None:
            pantalla.blit(imagen, (0, 0))
        if punto is None:
            texto = camara.error or "No veo la mano (None)"
        else:
            # paso del tamaño del cuadro de la cámara al tamaño de la ventana
            x = int(punto[0] / camara.ancho * 640)
            y = int(punto[1] / camara.alto * 480)
            color = C["blanco"] if camara.hay_pellizco() else C["acento"]
            pygame.draw.circle(pantalla, C["contorno"], (x, y), 14)
            pygame.draw.circle(pantalla, color, (x, y), 10)
            texto = f"Dedo en ({x}, {y})  -  pellizco: {'SÍ' if camara.hay_pellizco() else 'no'}"
        pantalla.blit(fuente.render(texto, True, C["texto"]), (12, 490))
        pygame.display.flip()
        reloj.tick(FPS)
    camara.liberar()                       # siempre libero la cámara al salir
    pygame.quit()


if __name__ == "__main__":
    principal()