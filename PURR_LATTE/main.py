"""main.py - Purr & Brew: Latte Art. Bucle principal y máquina de estados.

Estados:
  PORTADA -> NOMBRE (escribís tu nombre) -> ELEGIR_GATO (color del gatito) -> INSTRUCCIONES
  INSTRUCCIONES -> JUGANDO (ronda 1..5) -> RESULTADO_RONDA (si llegaste a 1 estrella) -> ... -> VICTORIA
  JUGANDO -> DERROTA (se enfrió, se terminó la leche o se desbordó)
  VICTORIA / DERROTA -> (Enter) TOP -> (R) PORTADA, sin cerrar la ventana. Desde la portada, T muestra el top.
  Si la cámara no abre: SIN_CAMARA (un aviso claro en vez de un error).
Dentro de JUGANDO hay dos "pausas": la de Esc y la de cuando la cámara no ve la mano (None).

La mano se usa así: la punta del índice es la jarra y el pellizco (índice + pulgar) vierte.
El teclado solo sirve para los menús (Enter/Espacio, flechas, R, T, Esc, M, N, F11) y el nombre.
"""
import os
import pygame
from ajustes import *
from vision import Camara
from latte import Taza, calcular_estrellas
from particulas import crear_gotas, actualizar_particulas
from jurado import Jurado
from puntajes import cargar_puntajes, agregar_puntaje
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
            if clave == "chorro":
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


# ---------------------------------------------------------------- el juego
class Juego:
    """Guarda el estado de toda la partida y tiene el bucle principal."""

    def __init__(self):
        """Abre la ventana y carga TODO una sola vez: cámara, sonidos, fuentes, fondos y el top."""
        pygame.init()
        # SCALED: el juego se dibuja siempre en 960x640 y pygame lo agranda solo en pantalla
        # completa (F11), sin deformarlo. Así no tengo que cambiar ninguna coordenada.
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED)
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
        self.chorro_sonando = False
        self.puntajes = cargar_puntajes()
        self.taza_muestra = Taza("corazon")      # la taza decorada de la portada
        self.taza_muestra.rellenar_perfecto()
        self.jurado = Jurado()
        self.t = 0.0                             # reloj general para las animaciones
        # el jugador: su nombre y el gato que eligió (se mantienen entre partidas)
        self.nombre = ""
        self.pelaje = 0
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
        self.porcentajes = []                    # el % de cada ronda jugada (suman los puntos)
        self.motivo_derrota = None
        self.puesto = None
        self.pausado = False
        self.taza = Taza(RONDAS[0]["dibujo"])
        self.particulas = []
        self.jurado.reiniciar(CONTENTO)
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
        # cosas que usa Don Salmón para comentar en vivo
        self.estrellas_ahora = 0
        self.fuera_anterior = 0
        self.balde_derrame = 0.0
        self.sin_verter = 0.0
        self.avisos_dados = []                   # avisos que se dicen una sola vez por ronda
        self.jurado.reiniciar(NEUTRAL)

    def terminar_ronda(self, motivo):
        """Termina la ronda: si llegaste a 1 estrella pasás al resultado; si no, perdés por 'motivo'."""
        self.parar_chorro()
        porcentaje = self.taza.calcular_puntaje()
        self.porcentajes.append(porcentaje)
        estrellas = calcular_estrellas(porcentaje)
        if estrellas >= 1:
            self.estrellas_por_ronda.append(estrellas)
            self.estrellas_ronda = estrellas
            self.estrellas_visibles = 0
            self.tiempo_resultado = 0.0
            self.estado = RESULTADO_RONDA
            self.jurado.reiniciar(LLORA if estrellas == 3 else CONTENTO)
            self.reproducir("ding")
        else:
            self.perder(motivo)

    def perder(self, motivo):
        """Pasa a la pantalla de derrota, guarda por qué se perdió y anota el puntaje en el top."""
        self.parar_chorro()
        if len(self.porcentajes) == self.ronda:          # (si perdió por desborde, falta esta ronda)
            self.porcentajes.append(self.taza.calcular_puntaje())
        self.motivo_derrota = motivo
        self.estado = DERROTA
        self.jurado.reiniciar(ASCO if motivo == "desborde" else PREOCUPADO)
        self.reproducir("miau_triste")
        self.anotar_en_el_top()

    def siguiente_ronda(self):
        """Desde el resultado: va a la próxima ronda o, si era la última, a la victoria."""
        if self.ronda + 1 < len(RONDAS):
            self.empezar_ronda(self.ronda + 1)
        else:
            self.estado = VICTORIA
            self.jurado.reiniciar(LLORA)
            self.reproducir("ding")
            self.anotar_en_el_top()

    def puntos(self):
        """Devuelve los puntos de la partida: la suma de los porcentajes de todas las rondas jugadas."""
        return sum(self.porcentajes)

    def anotar_en_el_top(self):
        """Guarda el puntaje de esta partida en el top (archivo puntajes.json) y recuerda el puesto."""
        self.puesto = agregar_puntaje(self.puntajes, self.nombre.strip(), self.puntos(),
                                      sum(self.estrellas_por_ronda), self.pelaje)

    # ------------------------------------------------------------ sonido
    def reproducir(self, clave):
        """Hace sonar un efecto si existe y si los sonidos están prendidos."""
        if self.sonidos_on and clave in self.sonidos:
            self.sonidos[clave].play()

    def actualizar_chorro(self, vertiendo):
        """Prende o apaga el sonido del chorro según si estás vertiendo."""
        if self.canal_chorro is None or "chorro" not in self.sonidos:
            return
        if vertiendo and self.sonidos_on and not self.chorro_sonando:
            # loops=-1: el chorro se repite mientras sigas vertiendo
            self.canal_chorro.play(self.sonidos["chorro"], loops=-1, fade_ms=FUNDIDO_CHORRO)
            self.chorro_sonando = True
        elif not vertiendo or not self.sonidos_on:
            self.parar_chorro()

    def parar_chorro(self):
        """Apaga el chorro con un fundido corto (para que no haga 'clic')."""
        if self.canal_chorro is not None and self.chorro_sonando:
            self.canal_chorro.fadeout(FUNDIDO_CHORRO)
        self.chorro_sonando = False

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
    def escribir_nombre(self, evento):
        """En la pantalla del nombre: agrega letras, borra con Backspace y sigue con Enter."""
        if evento.type == pygame.TEXTINPUT:
            # TEXTINPUT trae la letra ya escrita (con tildes y ñ). Ignoro espacios al principio.
            if len(self.nombre) < LARGO_MAXIMO_NOMBRE and (self.nombre or evento.text != " "):
                self.nombre = (self.nombre + evento.text)[:LARGO_MAXIMO_NOMBRE]
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_BACKSPACE:
                self.nombre = self.nombre[:-1]
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.nombre.strip():
                self.estado = ELEGIR_GATO
            elif evento.key == pygame.K_ESCAPE:
                self.estado = PORTADA

    def manejar_evento(self, evento):
        """Atiende la X de la ventana y las teclas de los menús según el estado."""
        if evento.type == pygame.QUIT:
            self.corriendo = False
            return
        if self.estado == NOMBRE:
            # mientras escribís el nombre, las letras son letras (la M no apaga la música)
            self.escribir_nombre(evento)
            return
        if evento.type != pygame.KEYDOWN:
            return
        tecla = evento.key
        if tecla == pygame.K_F11:
            pygame.display.toggle_fullscreen()
        elif tecla == pygame.K_m:
            self.alternar_musica()
        elif tecla == pygame.K_n:
            self.alternar_sonidos()
        avanzar = tecla in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER)
        if self.estado == SIN_CAMARA and tecla == pygame.K_ESCAPE:
            self.corriendo = False
        elif self.estado == PORTADA and avanzar:
            self.estado = NOMBRE
        elif self.estado == PORTADA and tecla == pygame.K_t:
            self.puesto = None
            self.estado = TOP
        elif self.estado == ELEGIR_GATO:
            self.elegir_gato(tecla, avanzar)
        elif self.estado == INSTRUCCIONES and avanzar:
            self.empezar_ronda(0)
        elif self.estado == JUGANDO and tecla == pygame.K_ESCAPE:
            self.pausado = not self.pausado
            self.parar_chorro()
        elif self.estado == JUGANDO and self.pausado and tecla == pygame.K_r:
            self.volver_a_portada()
        elif self.estado == RESULTADO_RONDA and avanzar and self.estrellas_visibles == self.estrellas_ronda:
            self.siguiente_ronda()
        elif self.estado in (VICTORIA, DERROTA) and avanzar:
            self.estado = TOP
        elif self.estado in (VICTORIA, DERROTA, TOP) and tecla == pygame.K_r:
            self.volver_a_portada()
        elif self.estado == TOP and tecla == pygame.K_ESCAPE:
            self.volver_a_portada()

    def elegir_gato(self, tecla, avanzar):
        """En la pantalla de los gatos: las flechas cambian de gato y Enter confirma."""
        if tecla == pygame.K_LEFT:
            self.pelaje = (self.pelaje - 1) % len(PELAJES)      # el % hace que dé la vuelta
        elif tecla == pygame.K_RIGHT:
            self.pelaje = (self.pelaje + 1) % len(PELAJES)
        elif avanzar:
            self.estado = INSTRUCCIONES
        elif tecla == pygame.K_ESCAPE:
            self.estado = NOMBRE

    # ------------------------------------------------------------ actualizar
    def leer_mano(self, dt):
        """Le pide a vision.py dónde está el dedo y si hay pellizco, y mueve la jarra suavizada."""
        self.punto_camara = self.camara.detectar()
        if self.punto_camara is None:
            # None: no hay mano. La jarra se queda donde estaba y no hay pellizco.
            self.pellizco = False
            self.tiempo_sin_mano += dt
            return
        if self.tiempo_sin_mano > TOLERANCIA_SIN_MANO and self.estado == JUGANDO:
            self.jurado.comentar("vuelve_mano")
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
            if self.cuenta <= 0:
                self.jurado.comentar("empieza")
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
        self.avisar_al_jurado(dt, vertiendo)

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

    def avisar_una_vez(self, evento):
        """Le pide a Don Salmón que comente algo que solo tiene sentido decir una vez por ronda."""
        if evento not in self.avisos_dados and self.jurado.comentar(evento):
            self.avisos_dados.append(evento)

    def avisar_al_jurado(self, dt, vertiendo):
        """Mira qué pasó en este cuadro y, si vale la pena, Don Salmón lo comenta en vivo."""
        datos = RONDAS[self.ronda]
        # Ganaste una estrella nueva: campanita y festejo.
        estrellas = calcular_estrellas(self.porcentaje)
        if estrellas > self.estrellas_ahora:
            self.reproducir("campanita")
            self.jurado.comentar("estrella")
        self.estrellas_ahora = estrellas
        # Derrame: la leche que cae afuera va a un "balde" que se vacía solo de a poco.
        # Si cae mucha de golpe, el balde se llena y Don Salmón se queja. Unas gotitas sueltas no.
        nueva_afuera = max(0, self.taza.fuera - self.fuera_anterior)
        self.fuera_anterior = self.taza.fuera
        self.balde_derrame = max(0.0, self.balde_derrame - VACIADO_DERRAME * dt) + nueva_afuera
        if self.balde_derrame > UMBRAL_DERRAME:
            self.jurado.comentar("derrame")
            self.balde_derrame = 0.0
        if self.taza.fraccion_fuera() > FRACCION_CASI_DESBORDE:
            self.avisar_una_vez("casi_desborde")
        if self.leche / datos["leche"] < FRACCION_POCA_LECHE:
            self.avisar_una_vez("poca_leche")
        if self.tiempo / datos["tiempo"] < FRACCION_FRIO:
            self.avisar_una_vez("frio")
        # Si pasa mucho rato sin verter (y todavía no está perfecta), te apura.
        if vertiendo or estrellas == 3:
            self.sin_verter = 0.0
        else:
            self.sin_verter += dt
            if self.sin_verter > TIEMPO_QUIETO:
                self.jurado.comentar("quieto")
                self.sin_verter = 0.0

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
            dibujar_jarra(self.pantalla, self.pos_jarra, vertiendo, PELAJES[self.pelaje][1])
        datos = RONDAS[self.ronda]
        imagen = self.camara.miniatura(TAM_MINIATURA, PIXEL_MINIATURA)
        escenas.dibujar_hud(self.pantalla, self.fuentes, self.ronda, imagen, self.punto_en_cuadro(),
                            self.pellizco, self.jurado, self.porcentaje, self.leche / datos["leche"],
                            self.tiempo / datos["tiempo"])
        if self.pausado:
            escenas.dibujar_pausa(self.pantalla, self.fuentes)
        elif self.tiempo_sin_mano > TOLERANCIA_SIN_MANO:
            escenas.dibujar_sin_mano(self.pantalla, self.fuentes)
        elif self.cuenta > 0:
            escenas.dibujar_cuenta(self.pantalla, self.fuentes, self.cuenta)

    def dibujar(self):
        """Dibuja la pantalla que corresponde al estado actual."""
        pelaje = PELAJES[self.pelaje][1]
        if self.estado == PORTADA:
            escenas.dibujar_portada(self.pantalla, self.fondo_cafeteria, self.fuentes, self.taza_muestra,
                                    self.jurado, pelaje, self.t)
        elif self.estado == NOMBRE:
            escenas.dibujar_nombre(self.pantalla, self.fondo_cafeteria, self.fuentes, self.nombre, self.jurado, self.t)
        elif self.estado == ELEGIR_GATO:
            escenas.dibujar_elegir_gato(self.pantalla, self.fondo_cafeteria, self.fuentes, self.pelaje, self.t)
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
                                     self.puntos(), self.jurado, pelaje, self.t)
        elif self.estado == DERROTA:
            escenas.dibujar_derrota(self.pantalla, self.fondo_mesa, self.fuentes, self.motivo_derrota,
                                    self.ronda, self.taza, self.puntos(), self.jurado, self.t)
        elif self.estado == TOP:
            escenas.dibujar_top(self.pantalla, self.fondo_cafeteria, self.fuentes, self.puntajes, self.puesto, self.t)
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