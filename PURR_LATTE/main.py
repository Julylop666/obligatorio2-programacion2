"""main.py - Purr & Brew: Latte Art. Bucle principal y máquina de estados.

Estados:
  PORTADA -> INSTRUCCIONES (prueba de pellizco) -> JUGANDO (ronda 1..4)
  JUGANDO -> RESULTADO_RONDA (si llegaste a 1 estrella) -> JUGANDO (ronda siguiente) ... -> VICTORIA
  JUGANDO -> DERROTA (se enfrió, se terminó la leche o se desbordó)
  VICTORIA / DERROTA -> (R) -> PORTADA, sin cerrar la ventana.
  Si la cámara no abre: SIN_CAMARA (un aviso claro en vez de un error).
Dentro de JUGANDO hay dos "pausas": la de Esc y la de cuando la cámara no ve la mano (None).

La mano se usa así: la punta del índice es la jarra y el pellizco (índice + pulgar) vierte.
El teclado solo sirve para los menús (Enter/Espacio, R, Esc, M, N).
"""
import os
import pygame
from ajustes import *
from vision import Camara
from latte import Taza, calcular_estrellas
from particulas import crear_gotas, actualizar_particulas
from jurado import Jurado
from dibujo import crear_fondo_mesa, crear_fondo_cafeteria, dibujar_jarra, dibujar_mira
import escenas


# ---------------------------------------------------------------- carga de recursos (una sola vez)
def cargar_sonidos():
    """Carga todos los efectos UNA sola vez y devuelve un diccionario {nombre: Sound}.

    Si no hay audio o falta un archivo, avisa por consola y el juego sigue sin ese sonido.
    """
    sonidos = {}
    try:
        pygame.mixer.init()
    except pygame.error as error:
        print("Aviso: no se pudo iniciar el audio:", error)
        return sonidos
    for clave, archivo in ARCHIVOS_SONIDO.items():
        ruta = os.path.join(RUTA_SONIDOS, archivo)
        try:
            sonido = pygame.mixer.Sound(ruta)
            if clave.startswith("chorro"):
                sonido.set_volume(VOLUMEN_CHORRO)
            else:
                sonido.set_volume(VOLUMEN_EFECTOS)
            sonidos[clave] = sonido
        except (pygame.error, FileNotFoundError) as error:
            print(f"Aviso: no se pudo cargar {ruta} ({error}). ¿Corriste generar_sonidos.py?")
    return sonidos


def iniciar_musica():
    """Carga la música lo-fi y la deja sonando en loop. Devuelve True si pudo."""
    ruta = os.path.join(RUTA_SONIDOS, ARCHIVO_MUSICA)
    try:
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(VOLUMEN_MUSICA)
        pygame.mixer.music.play(-1)          # -1 = repetir para siempre
        return True
    except pygame.error as error:
        print(f"Aviso: no se pudo cargar la música {ruta} ({error})")
        return False


def cargar_fuentes():
    """Carga la fuente pixel (Jersey 15) en varios tamaños y devuelve un diccionario."""
    tamanos = {"titulo": 72, "grande": 48, "normal": 30, "chica": 24}
    fuentes = {}
    for nombre, tamano in tamanos.items():
        try:
            fuentes[nombre] = pygame.font.Font(RUTA_FUENTE, tamano)
        except (pygame.error, FileNotFoundError):
            fuentes[nombre] = pygame.font.Font(None, tamano)    # fuente de pygame, por las dudas
    return fuentes


# ---------------------------------------------------------------- cuentas con la posición de la mano
def camara_a_pantalla(punto, ancho_cuadro, alto_cuadro):
    """Convierte (x, y) en pixeles de la cámara a (x, y) en la pantalla, dentro de ZONA_JARRA.

    Solo uso la parte del medio del cuadro (sin los márgenes): así no hace falta estirar
    el brazo hasta el borde para llegar a la orilla de la taza.
    """
    u = (punto[0] / ancho_cuadro - MARGEN_CAMARA_X) / (1 - 2 * MARGEN_CAMARA_X)
    v = (punto[1] / alto_cuadro - MARGEN_CAMARA_Y) / (1 - 2 * MARGEN_CAMARA_Y)
    u = max(0.0, min(1.0, u))
    v = max(0.0, min(1.0, v))
    zona = pygame.Rect(ZONA_JARRA)
    return (zona.left + u * zona.width, zona.top + v * zona.height)


def suavizar(actual, objetivo):
    """Devuelve un punto que avanza solo una parte (SUAVIZADO) desde 'actual' hacia 'objetivo'.

    Así la jarra no tiembla aunque MediaPipe mueva el punto un par de pixeles en cada cuadro.
    """
    if actual is None:
        return objetivo
    return (actual[0] + (objetivo[0] - actual[0]) * SUAVIZADO,
            actual[1] + (objetivo[1] - actual[1]) * SUAVIZADO)


def nota_segun_altura(y_pantalla):
    """Devuelve qué nota del chorro (0 = la más grave) toca según la altura de la jarra."""
    zona = pygame.Rect(ZONA_JARRA)
    arriba = 1 - (y_pantalla - zona.top) / zona.height      # 1 = mano arriba, 0 = mano abajo
    nota = int(arriba * len(NOTAS_CHORRO))
    return max(0, min(len(NOTAS_CHORRO) - 1, nota))


# ---------------------------------------------------------------- el juego
class Juego:
    """Guarda el estado de toda la partida y tiene el bucle principal."""

    def __init__(self):
        """Abre la ventana y carga TODO una sola vez: cámara, sonidos, fuentes y fondos."""
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO)
        self.reloj = pygame.time.Clock()
        self.fuentes = cargar_fuentes()
        self.fondo_mesa = crear_fondo_mesa()
        self.fondo_cafeteria = crear_fondo_cafeteria()
        self.camara = Camara()
        self.sonidos = cargar_sonidos()
        self.musica_on = iniciar_musica()
        self.sonidos_on = True
        self.canal_chorro = pygame.mixer.Channel(0) if pygame.mixer.get_init() else None
        if self.canal_chorro is not None:
            pygame.mixer.set_reserved(1)         # el canal 0 queda solo para el chorro
        self.nota_sonando = None
        self.taza_muestra = Taza("corazon")      # la taza decorada de la portada
        self.taza_muestra.rellenar_perfecto()
        self.jurado = Jurado()
        self.t = 0.0                             # reloj general para las animaciones
        # datos de la mano (se actualizan en cada cuadro)
        self.punto_camara = None
        self.pellizco = False
        self.pos_jarra = None
        self.tiempo_sin_mano = 0.0
        self.corriendo = True
        self.volver_a_portada()
        if not self.camara.esta_lista():
            self.estado = SIN_CAMARA

    # ------------------------------------------------------------ cambios de estado
    def volver_a_portada(self):
        """Deja todo listo para una partida nueva y muestra la portada."""
        self.estado = PORTADA
        self.ronda = 0
        self.estrellas_por_ronda = []
        self.motivo_derrota = None
        self.pausado = False
        self.taza = Taza(RONDAS[0]["dibujo"])
        self.particulas = []
        self.jurado.poner_cara(APLAUDE)
        self.parar_chorro()

    def empezar_ronda(self, numero):
        """Prepara la ronda 'numero': taza nueva, leche llena, café caliente y cuenta regresiva."""
        self.estado = JUGANDO
        self.ronda = numero
        datos = RONDAS[numero]
        self.taza = Taza(datos["dibujo"])
        self.particulas = []
        self.leche = datos["leche"]
        self.tiempo = datos["tiempo"]
        self.cuenta = CUENTA_REGRESIVA
        self.gotas_pendientes = 0.0
        self.tiempo_quieto = 0.0
        self.porcentaje = 0
        self.pausado = False
        self.jurado.poner_cara(NEUTRAL)

    def terminar_ronda(self, motivo):
        """Termina la ronda: si llegaste a 1 estrella pasás al resultado; si no, perdés por 'motivo'."""
        self.parar_chorro()
        estrellas = calcular_estrellas(self.taza.calcular_puntaje())
        if estrellas >= 1:
            self.estrellas_por_ronda.append(estrellas)
            self.estrellas_ronda = estrellas
            self.estrellas_visibles = 0
            self.tiempo_resultado = 0.0
            self.estado = RESULTADO_RONDA
            self.jurado.poner_cara(LLORA if estrellas == 3 else APLAUDE)
            self.reproducir("ding")
        else:
            self.perder(motivo)

    def perder(self, motivo):
        """Pasa a la pantalla de derrota guardando por qué se perdió."""
        self.parar_chorro()
        self.motivo_derrota = motivo
        self.estado = DERROTA
        self.jurado.poner_cara(ASCO)
        self.reproducir("miau_triste")

    def siguiente_ronda(self):
        """Desde el resultado: va a la próxima ronda o, si era la última, a la victoria."""
        if self.ronda + 1 < len(RONDAS):
            self.empezar_ronda(self.ronda + 1)
        else:
            self.estado = VICTORIA
            self.jurado.poner_cara(LLORA)
            self.reproducir("ding")

    # ------------------------------------------------------------ sonido
    def reproducir(self, clave):
        """Hace sonar un efecto si existe y si los sonidos están prendidos."""
        if self.sonidos_on and clave in self.sonidos:
            self.sonidos[clave].play()

    def actualizar_chorro(self, vertiendo):
        """Prende, apaga o cambia de nota el sonido del chorro según la altura de la jarra."""
        if self.canal_chorro is None:
            return
        if not vertiendo or not self.sonidos_on:
            self.parar_chorro()
            return
        nota = nota_segun_altura(self.pos_jarra[1])
        if nota != self.nota_sonando:
            clave = f"chorro_{nota}"
            if clave in self.sonidos:
                # loops=-1: el chorro se repite mientras sigas vertiendo
                self.canal_chorro.play(self.sonidos[clave], loops=-1, fade_ms=FUNDIDO_CHORRO)
            self.nota_sonando = nota

    def parar_chorro(self):
        """Apaga el chorro con un fundido corto (para que no haga 'clic')."""
        if self.canal_chorro is not None and self.nota_sonando is not None:
            self.canal_chorro.fadeout(FUNDIDO_CHORRO)
        self.nota_sonando = None

    def alternar_musica(self):
        """M: prende o apaga la música de fondo."""
        if not pygame.mixer.get_init():
            return
        self.musica_on = not self.musica_on
        if self.musica_on:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    def alternar_sonidos(self):
        """N: prende o apaga los efectos (y corta el chorro si estaba sonando)."""
        self.sonidos_on = not self.sonidos_on
        if not self.sonidos_on:
            self.parar_chorro()

    # ------------------------------------------------------------ eventos
    def manejar_evento(self, evento):
        """Atiende la X de la ventana y las teclas de los menús según el estado."""
        if evento.type == pygame.QUIT:
            self.corriendo = False
            return
        if evento.type != pygame.KEYDOWN:
            return
        tecla = evento.key
        if tecla == pygame.K_m:
            self.alternar_musica()
        elif tecla == pygame.K_n:
            self.alternar_sonidos()
        avanzar = tecla in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER)
        if self.estado == SIN_CAMARA and tecla == pygame.K_ESCAPE:
            self.corriendo = False
        elif self.estado == PORTADA and avanzar:
            self.estado = INSTRUCCIONES
        elif self.estado == INSTRUCCIONES and avanzar:
            self.estrellas_por_ronda = []
            self.empezar_ronda(0)
        elif self.estado == JUGANDO and tecla == pygame.K_ESCAPE:
            self.pausado = not self.pausado
            self.parar_chorro()
        elif self.estado == JUGANDO and self.pausado and tecla == pygame.K_r:
            self.volver_a_portada()
        elif self.estado == RESULTADO_RONDA and avanzar and self.estrellas_visibles == self.estrellas_ronda:
            self.siguiente_ronda()
        elif self.estado in (VICTORIA, DERROTA) and tecla == pygame.K_r:
            self.volver_a_portada()

    # ------------------------------------------------------------ actualizar
    def leer_mano(self, dt):
        """Le pide a vision.py dónde está el dedo y si hay pellizco, y mueve la jarra suavizada."""
        self.punto_camara = self.camara.detectar()
        if self.punto_camara is None:
            # None: no hay mano. La jarra se queda donde estaba y no hay pellizco.
            self.pellizco = False
            self.tiempo_sin_mano += dt
            return
        self.tiempo_sin_mano = 0.0
        self.pellizco = self.camara.hay_pellizco()
        objetivo = camara_a_pantalla(self.punto_camara, self.camara.ancho, self.camara.alto)
        self.pos_jarra = suavizar(self.pos_jarra, objetivo)

    def actualizar(self, dt):
        """Actualiza la cámara, las animaciones y, si estás jugando, la ronda."""
        self.t += dt
        self.jurado.actualizar(dt)
        if self.estado == SIN_CAMARA:
            return
        self.leer_mano(dt)
        if self.estado == JUGANDO:
            self.actualizar_ronda(dt)
        elif self.estado == RESULTADO_RONDA:
            self.actualizar_resultado(dt)

    def actualizar_ronda(self, dt):
        """Un cuadro de la ronda: verter, mover gotas, enfriar el café y revisar si se terminó."""
        # Pausa (Esc) o sin mano (None): no sale leche, no se mueve nada y el tiempo se congela.
        if self.pausado or self.punto_camara is None:
            self.parar_chorro()
            return
        if self.cuenta > 0:
            self.cuenta -= dt
            return
        vertiendo = self.pellizco and self.leche > 0
        if vertiendo:
            # el caudal es de CAUDAL_LECHE gotas por segundo: junto "pedacitos" de gota en cada
            # cuadro y cuando suman una o más, las creo (así no depende de los FPS)
            self.gotas_pendientes += CAUDAL_LECHE * dt
            cantidad = min(int(self.gotas_pendientes), self.leche)
            self.gotas_pendientes -= int(self.gotas_pendientes)
            self.particulas += crear_gotas(self.pos_jarra, cantidad)
            self.leche -= cantidad
        self.actualizar_chorro(vertiendo)
        self.particulas = actualizar_particulas(self.particulas, dt, self.taza)
        self.tiempo -= dt
        self.porcentaje = self.taza.calcular_puntaje()
        self.jurado.reaccionar(self.porcentaje, self.taza.fraccion_fuera())

        # ¿se terminó la ronda?
        if self.taza.hay_desborde():
            self.perder("desborde")
            return
        if calcular_estrellas(self.porcentaje) == 3 and not vertiendo:
            # con 3 estrellas, si dejás de verter un ratito, se sirve sola (ya está perfecta)
            self.tiempo_quieto += dt
            if self.tiempo_quieto >= TIEMPO_SERVIR:
                self.terminar_ronda("frio")
                return
        else:
            self.tiempo_quieto = 0.0
        if self.tiempo <= 0:
            self.terminar_ronda("frio")
        elif self.leche <= 0 and not self.particulas:
            # espero a que caigan las últimas gotas antes de evaluar
            self.terminar_ronda("leche")

    def actualizar_resultado(self, dt):
        """Hace aparecer las estrellas del resultado de a una, con una campanita cada una."""
        self.tiempo_resultado += dt
        deberian = min(self.estrellas_ronda, int(self.tiempo_resultado / DURACION_ESTRELLA))
        if deberian > self.estrellas_visibles:
            self.estrellas_visibles = deberian
            self.reproducir("campanita")

    # ------------------------------------------------------------ dibujar
    def punto_en_cuadro(self):
        """Devuelve el dedo como (u, v) entre 0 y 1 del cuadro, para dibujarlo en la miniatura."""
        if self.punto_camara is None:
            return None
        return (self.punto_camara[0] / self.camara.ancho, self.punto_camara[1] / self.camara.alto)

    def dibujar_ronda(self):
        """Dibuja la mesa, la taza, las gotas, la jarra, el HUD y los carteles de la ronda."""
        self.pantalla.blit(self.fondo_mesa, (0, 0))
        self.taza.dibujar(self.pantalla)
        for gota in self.particulas:
            gota.dibujar(self.pantalla)
        if self.pos_jarra is not None:
            vertiendo = self.pellizco and self.leche > 0 and self.cuenta <= 0 and not self.pausado
            dibujar_mira(self.pantalla, self.pos_jarra, vertiendo)
            dibujar_jarra(self.pantalla, self.pos_jarra, vertiendo)
        datos = RONDAS[self.ronda]
        imagen = self.camara.miniatura(TAM_MINIATURA, PIXEL_MINIATURA)
        escenas.dibujar_hud(self.pantalla, self.fuentes, self.ronda, imagen, self.punto_en_cuadro(),
                            self.pellizco, self.jurado, self.porcentaje, self.leche / datos["leche"],
                            self.tiempo / datos["tiempo"])
        if self.pausado:
            escenas.dibujar_pausa(self.pantalla, self.fuentes)
        elif self.tiempo_sin_mano > TOLERANCIA_SIN_MANO:
            escenas.dibujar_sin_mano(self.pantalla, self.fuentes, self.t)
        elif self.cuenta > 0:
            escenas.dibujar_cuenta(self.pantalla, self.fuentes, self.cuenta)

    def dibujar(self):
        """Dibuja la pantalla que corresponde al estado actual."""
        if self.estado == PORTADA:
            escenas.dibujar_portada(self.pantalla, self.fondo_cafeteria, self.fuentes, self.taza_muestra,
                                    self.jurado, self.t)
        elif self.estado == INSTRUCCIONES:
            imagen = self.camara.miniatura(TAM_CAMARA_INSTRUCCIONES, PIXEL_MINIATURA)
            escenas.dibujar_instrucciones(self.pantalla, self.fondo_cafeteria, self.fuentes, imagen,
                                          self.punto_en_cuadro(), self.pellizco, self.t)
        elif self.estado == JUGANDO:
            self.dibujar_ronda()
        elif self.estado == RESULTADO_RONDA:
            escenas.dibujar_resultado(self.pantalla, self.fondo_mesa, self.fuentes, self.ronda, self.taza,
                                      self.jurado, self.estrellas_visibles,
                                      self.estrellas_visibles == self.estrellas_ronda, self.t)
        elif self.estado == VICTORIA:
            escenas.dibujar_victoria(self.pantalla, self.fondo_cafeteria, self.fuentes, self.estrellas_por_ronda,
                                     self.jurado, self.t)
        elif self.estado == DERROTA:
            escenas.dibujar_derrota(self.pantalla, self.fondo_mesa, self.fuentes, self.motivo_derrota,
                                    self.ronda, self.taza, self.jurado, self.t)
        elif self.estado == SIN_CAMARA:
            escenas.dibujar_sin_camara(self.pantalla, self.fondo_cafeteria, self.fuentes, self.camara.error)
        pygame.display.flip()

    # ------------------------------------------------------------ bucle principal
    def ejecutar(self):
        """Bucle principal: eventos -> actualizar -> dibujar -> reloj.tick. Al salir libera la cámara."""
        dt = 0.0
        while self.corriendo:
            for evento in pygame.event.get():
                self.manejar_evento(evento)
            self.actualizar(dt)
            self.dibujar()
            # tick espera lo necesario para no pasar de FPS y devuelve los milisegundos que
            # pasaron desde el cuadro anterior: lo paso a segundos para el próximo actualizar
            dt = min(self.reloj.tick(FPS) / 1000, DT_MAXIMO)
        self.camara.liberar()        # adentro llama a cap.release()
        pygame.quit()


if __name__ == "__main__":
    Juego().ejecutar()
