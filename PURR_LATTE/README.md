# Purr & Brew: Latte Art

Juego en **pixel art** hecho con Python, pygame, OpenCV y MediaPipe para Programación 2 (Facultad de Diseño, Universidad ORT Uruguay). Es la secuela de *Purr & Brew 2D*: mismo mundo, misma paleta y el mismo gato barista.

Don Salmón te anotó en el concurso de latte art del barrio. **Tu mano es la jarrita de leche**: la cámara sigue la punta de tu dedo índice y, cuando juntás el índice con el pulgar (pellizco), sale leche. Tenés que verter siguiendo el dibujo punteado que aparece sobre el café. Sin cámara no se puede jugar: la cámara *es* el gesto de verter.

**Repositorio en GitHub:** _(pegar acá el link del repo)_

## Cómo se juega

**Objetivo:** pasar las 4 rondas del concurso, de la más fácil a la más difícil:
1. Corazón  2. Tulipán  3. Rosetta  4. Cara de gato

**Qué hacer frente a la cámara:**
- Sentate a unos 50-80 cm de la webcam y mostrá la palma de una mano.
- La **punta del índice** mueve la jarra. En la miniatura de la cámara (arriba a la derecha) hay un recuadro punteado: es la zona útil, no hace falta llegar al borde del cuadro.
- **Pellizco** (juntar índice y pulgar) = verter leche. Abrí los dedos para dejar de verter.
- Cuanto más alta está la mano, más aguda suena la leche (el chorro toca una escala pentatónica).

**Puntaje:** el porcentaje mide cuánto del dibujo cubriste con espuma, menos una penalización por la leche que cae afuera del dibujo.
- 1 estrella (40%): pasás la ronda.
- 2 estrellas (60%): bien.
- 3 estrellas (80%): Don Salmón llora de emoción. Si llegás a 3 estrellas y dejás de verter un ratito, la taza se sirve sola.

**Cómo se pierde** (la dificultad es generosa: se puede ganar en el primer intento si vertés con cuidado):
- **Se enfrió el café:** el termómetro llega a cero sin que tengas 1 estrella.
- **Se terminó la leche:** la jarra se vacía sin que tengas 1 estrella. Alcanza de sobra si no vertés dos veces en el mismo lugar.
- **Se desbordó la taza:** tiraste afuera del dibujo tanta leche como el dibujo entero.

**Si la cámara no ve la mano** (la detección devuelve `None`), el juego se pausa solo: el tiempo se congela, no sale leche y aparece el cartel **"¡Mostrá la pata!"**. Al volver a mostrar la mano, seguís donde estabas.
Si la cámara no abre al iniciar, aparece una pantalla que explica qué revisar en vez de un error.

### Controles

| Control | Acción |
|---|---|
| Dedo índice frente a la cámara | Mover la jarra |
| Pellizco (índice + pulgar) | Verter leche |
| Enter / Espacio | Avanzar en los menús |
| Esc | Pausar y seguir (en la pantalla de "sin cámara", cierra) |
| R | Volver a jugar desde la victoria o la derrota (también desde la pausa) sin cerrar la ventana |
| M / N | Música on/off / Sonidos on/off |
| X de la ventana | Cerrar el juego (libera la cámara) |

### Estados del juego

`PORTADA → INSTRUCCIONES (prueba del pellizco) → JUGANDO (rondas 1 a 4) → RESULTADO_RONDA → … → VICTORIA`
Desde `JUGANDO` se puede ir a `DERROTA`. Con **R** se vuelve a la `PORTADA`. Dentro de `JUGANDO` hay una cuenta regresiva de 3 segundos, la pausa (Esc) y la pausa automática sin mano.

## Instalación y ejecución (Windows, Python 3.12)

```
py -m pip install -r requirements.txt
py main.py
```

Para probar solo la cámara (sin el juego): `py prueba_camara.py`.
Los sonidos ya vienen en la carpeta `sonidos/`. Si se borran, se vuelven a crear con `py generar_sonidos.py`.

**Bibliotecas:** `pygame-ce` (la versión mantenida por la comunidad de pygame, se usa igual: `import pygame`), `opencv-contrib-python` (OpenCV), `mediapipe` y `numpy` (la usan OpenCV y MediaPipe por dentro).

### Por qué la versión de MediaPipe está fijada (0.10.21)

Las versiones nuevas de MediaPipe (de la 0.10.30 en adelante) **ya no traen `mp.solutions`**: solo tienen la "Tasks API", que necesita bajar aparte un archivo de modelo (`hand_landmarker.task`). Comprobé las dos opciones:
- **0.10.21 + `mp.solutions.hands`:** tiene versión para Python 3.12 en Windows y el modelo de la mano viene adentro de la biblioteca. No hay que bajar nada más y el código es más corto y fácil de explicar.
- **Tasks API:** funciona con las versiones nuevas, pero hay que llevar el archivo `.task` en la carpeta y el código es más largo.

Elegí la primera opción por ser la más estable y simple, y la dejé fija en `requirements.txt`. Esa versión necesita `numpy` menor a 2 y Python 3.12 (con Python 3.13 no se instala).

Si aparece un error con `cv2`, puede ser que estén instalados `opencv-python` y `opencv-contrib-python` a la vez. Se arregla con `py -m pip uninstall opencv-python` y volviendo a correr la instalación.

## Mejores condiciones para la detección

- **Luz:** de frente o de costado, pareja. Evitá tener una ventana o una lámpara fuerte atrás (la mano queda a contraluz).
- **Fondo:** liso y que no sea del color de la piel. Mejor sin otras personas ni manos en el cuadro (el juego sigue una sola mano).
- **Distancia:** entre 50 y 80 cm de la cámara, con la mano entera adentro del cuadro y la palma mirando a la cámara.
- **Gesto:** para el pellizco, juntá bien las puntas del índice y el pulgar. Para soltar, abrí los dedos con ganas: hay dos umbrales distintos (histéresis) para que el chorro no se corte solo.
- Si la jarra tiembla, se puede subir el suavizado bajando `SUAVIZADO` en `ajustes.py`.

## Qué hay en cada archivo

| Archivo | Qué tiene |
|---|---|
| `main.py` | Clase `Juego`: carga todo una sola vez, bucle principal (eventos, actualizar, dibujar, `reloj.tick`), máquina de estados, rondas, sonido del chorro y cierre con `cap.release()`. Funciones `camara_a_pantalla`, `suavizar` y `nota_segun_altura`. |
| `ajustes.py` | Todas las constantes: colores, tamaños, velocidades, umbrales del pellizco, suavizado, tiempos, leche por ronda, umbrales de las estrellas y textos. |
| `vision.py` | Todo lo de OpenCV y MediaPipe, en la clase `Camara`: abrir la cámara, leer y espejar el cuadro (`flip`), detectar la mano (`detectar()` devuelve `(x, y)` o `None`), `hay_pellizco()`, la miniatura pixelada y `liberar()`. |
| `latte.py` | Clase `Taza`: el café, los 4 dibujos hechos con figuras en código, la máscara del dibujo, la leche vertida y el puntaje. Función `calcular_estrellas`. |
| `particulas.py` | Clase `Particula` (gota de leche que cae y se abre en espuma) y las funciones `crear_gotas` y `actualizar_particulas` (la lista que cambia). |
| `jurado.py` | Clase `Jurado` (Don Salmón): elige y anima sus 4 caras (neutral, aplaude, asco, llora). |
| `dibujo.py` | Pixel art y piezas de interfaz: `pixelar`, paneles, textos, barras, estrellas, jarra, gato barista, fondos y la miniatura de la cámara. |
| `escenas.py` | Qué se dibuja en cada estado: portada, instrucciones, HUD, cuenta regresiva, "¡Mostrá la pata!", pausa, resultado, victoria, derrota y aviso de cámara. |
| `generar_sonidos.py` | Crea todos los `.wav` con matemática (ondas seno, ruido y envolventes). |
| `prueba_camara.py` | Prueba suelta de la cámara: muestra el punto del dedo y si hay pellizco. |

**Cómo se calcula el puntaje** (en `latte.py`): toda la taza se dibuja en un lienzo chiquito de 136 × 136 pixeles que después se agranda 4 veces (por eso se ve pixel art). Cada pixel del lienzo es una celda. El dibujo guía se pinta en una superficie y se convierte en una **máscara** (qué celdas son del dibujo). La leche se pinta en otra superficie con su propia máscara. `cubiertas` son las celdas que están en las dos; `fuera` son las celdas con leche que no son del dibujo.
`% = cubiertas / total del dibujo − 0.4 × fuera / total del dibujo`

## Recursos y licencias

- **Gráficos:** todos hechos en código (grillas de texto convertidas en pixel art y figuras de pygame). No hay imágenes externas. Son propios.
- **Sonidos y música:** generados por código con `generar_sonidos.py` (ondas seno, ruido filtrado y envolventes). Son propios.
- **Fuente:** *Jersey 15*, de The Soft Type Project Authors, con licencia **SIL Open Font License 1.1** (archivo `fuentes/OFL.txt`). Fuente: https://github.com/scfried/soft-type-jersey
- **Modelo de la mano:** viene incluido en MediaPipe (Google), con licencia Apache 2.0.

## Uso de IA

- **Herramienta:** Claude (Anthropic), modelo Claude Opus 5.5, en claude.ai.
- **Para qué la usé:** para programar el juego por etapas a partir de mi documento de contexto (idea, reglas, estética y estados que definí yo); para comparar qué versión de MediaPipe funciona con Python 3.12 en Windows; para generar los sonidos por código; para revisar docstrings y comentarios, y para el borrador de este README. El diseño del juego, la estética (heredada de mi juego anterior) y las decisiones de reglas son mías. Revisé el código y puedo explicarlo.
- **Prompts más relevantes:**
  1. "Leé el contexto del proyecto (contexto.md), la consigna del Obligatorio 2 (PDF) y mi juego anterior Purr & Brew (zip) para copiar su estética, paleta y forma de organizar el código. Después programá el juego completo 'Purr & Brew: Latte Art' según TODO lo definido en el contexto."
  2. "Puntaje: dibujá el contorno guía en una máscara (Surface o grilla) y pintá la leche vertida en otra. % = celdas del dibujo cubiertas / total del dibujo − penalización por celdas fuera. Mantenelo simple y explicable."
  3. "MediaPipe: verificá qué API funciona con Python 3.12 en Windows. Las versiones nuevas pueden no tener mp.solutions. Elegí una opción estable y explicame la elección en el README."
  4. "Trabajá por etapas y al final de cada una decime qué commit hago y con qué mensaje."
- **Cita (APA):** Claude. (2026). *Prompts utilizados para la programación del juego Purr & Brew: Latte Art* [Generación de código]. Anthropic. Recuperado de https://claude.ai
