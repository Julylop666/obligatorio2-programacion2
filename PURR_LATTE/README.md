# Purr & Brew: Latte Art

Juego en **pixel art** hecho con Python, pygame, OpenCV y MediaPipe para Programación 2 (Facultad de Diseño, Universidad ORT Uruguay). Es la secuela de *Purr & Brew 2D*: mismo mundo, misma paleta y el mismo gato barista.

Don Salmón te anotó en el concurso de latte art del barrio. **Tu mano es la jarrita de leche**: la cámara sigue la punta de tu dedo índice y, cuando juntás el índice con el pulgar (pellizco), sale leche. Tenés que verter siguiendo el dibujo punteado que aparece sobre el café. Sin cámara no se puede jugar: la cámara *es* el gesto de verter.

**Repositorio en GitHub:** _(pegar acá el link del repo)_

## Cómo se juega

**Antes de empezar:** escribís tu nombre (va al top) y elegís el color de tu gatito, como en Purr & Brew. La jarra aparece agarrada por una patita de ese color.

**Objetivo:** pasar las 5 rondas del concurso y quedar lo más alto posible en el top. Los dibujos siguen el orden en que aprenden los baristas de verdad:
1. **Corazón**: la base de todo.
2. **Tulipán**: capas apiladas, cada una "empujando" a la anterior, con una línea por el medio.
3. **Rosetta**: una hoja de helecho con siete capas finitas.
4. **Cisne**: media rosetta de costado como ala, un cuello curvo y un corazoncito de cabeza.
5. **Cara de gato**: el final, guiño a Purr & Brew (los ojos son agujeros: no hay que taparlos).

**Qué hacer frente a la cámara:**
- Sentate a unos 50-80 cm de la webcam y mostrá la palma de una mano.
- La **punta del índice** mueve la jarra. En la miniatura de la cámara (arriba a la derecha) hay un recuadro punteado: es la zona útil, no hace falta llegar al borde del cuadro.
- **Pellizco** (juntar índice y pulgar) = verter leche. Abrí los dedos para dejar de verter.

**Don Salmón comenta en vivo:** es el jurado y reacciona a lo que pasa. Si derramás leche afuera se queja (cara de asco), si se está acabando la leche o se enfría el café se preocupa (gotita de sudor), si ganás una estrella salta y aplaude, y con 3 estrellas llora de emoción. Si te quedás quieto mucho rato te apura.

**Puntaje:** el porcentaje mide cuánto del dibujo cubriste con espuma, menos una penalización por la leche que cae afuera del dibujo.
- 1 estrella (40%): pasás la ronda.
- 2 estrellas (60%): bien.
- 3 estrellas (80%): Don Salmón llora de emoción. Si llegás a 3 estrellas y dejás de verter un ratito, la taza se sirve sola.

**Top:** al terminar (ganes o pierdas) tu partida se anota en el top con tu nombre y tu gatito. Los puntos son la suma de los porcentajes de todas las rondas que jugaste (máximo 500). El top se guarda en `puntajes.json`, así que queda guardado aunque cierres el juego.

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
| Teclado | Escribir tu nombre (Borrar corrige) |
| Flechas izquierda / derecha | Elegir el color del gatito |
| Esc | Pausar y seguir (en la pantalla de "sin cámara", cierra) |
| R | Volver a jugar desde la victoria, la derrota o el top (también desde la pausa) sin cerrar la ventana |
| T | Ver el top desde la portada |
| F11 | Pantalla completa (y volver a ventana) |
| M / N | Música on/off / Sonidos on/off |
| X de la ventana | Cerrar el juego (libera la cámara) |

### Estados del juego

`PORTADA → NOMBRE → ELEGIR_GATO → INSTRUCCIONES (prueba del pellizco) → JUGANDO (rondas 1 a 5) → RESULTADO_RONDA → … → VICTORIA → TOP`
Desde `JUGANDO` se puede ir a `DERROTA` (y de ahí al `TOP`). Con **R** se vuelve a la `PORTADA`. Dentro de `JUGANDO` hay una cuenta regresiva de 3 segundos, la pausa (Esc) y la pausa automática sin mano.

## Instalación y ejecución (Windows, Python 3.12)

Necesita **Python 3.12** (con 3.13 o 3.14 MediaPipe 0.10.21 no se instala). Si no la tenés: `py install 3.12` o el instalador de python.org.
Desde la carpeta del juego, en PowerShell:

```
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

La primera línea crea un entorno virtual (`.venv`) con Python 3.12, separado de otras versiones instaladas. En cada terminal nueva hay que activarlo de nuevo (segunda línea). Si PowerShell no deja activarlo ("la ejecución de scripts está deshabilitada"), correr una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

Para probar solo la cámara (sin el juego): `python prueba_camara.py`.
Los sonidos ya vienen en la carpeta `sonidos/`. Si se borran, se vuelven a crear con `python generar_sonidos.py`.

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
| `main.py` | Clase `Juego`: carga todo una sola vez, bucle principal (eventos, actualizar, dibujar, `reloj.tick`), máquina de estados, nombre, elección del gato, rondas, avisos en vivo para Don Salmón, pantalla completa, sonido del chorro y cierre con `cap.release()`. Funciones `camara_a_pantalla` y `suavizar`. |
| `ajustes.py` | Todas las constantes: colores, tamaños, velocidades, umbrales del pellizco, suavizado, tiempos, leche por ronda, umbrales de las estrellas y textos. |
| `vision.py` | Todo lo de OpenCV y MediaPipe, en la clase `Camara`: abrir la cámara, leer y espejar el cuadro (`flip`), detectar la mano (`detectar()` devuelve `(x, y)` o `None`), `hay_pellizco()`, la miniatura pixelada y `liberar()`. |
| `latte.py` | Clase `Taza`: el café, los 5 dibujos hechos con figuras en código, la máscara del dibujo, la leche vertida y el puntaje. Función `calcular_estrellas`. |
| `particulas.py` | Clase `Particula` (gota de leche que cae y se abre en espuma) y las funciones `crear_gotas` y `actualizar_particulas` (la lista que cambia). |
| `jurado.py` | Clase `Jurado` (Don Salmón): su cara según el %, los comentarios en vivo (globito) y las animaciones de cada cara (respira, salta y aplaude, suda, olorcitos, llora). |
| `puntajes.py` | El top: lee y guarda los puntajes en `puntajes.json` (con el módulo `json` de Python). |
| `dibujo.py` | Pixel art y piezas de interfaz: `pixelar`, paneles, textos, barras, estrellas, la jarra con la patita, los gatos de Purr & Brew con sus caras, los fondos y la miniatura de la cámara. |
| `escenas.py` | Qué se dibuja en cada estado: portada, nombre, elegir gato, instrucciones, HUD, cuenta regresiva, "¡Mostrá la pata!", pausa, resultado, victoria, derrota, top y aviso de cámara. |
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
  5. "Que haya un top al final y que tengas que poner tu nombre; poder elegir el color del gatito y que la jarra tenga una patita de ese color; Don Salmón más lindo, como en Purr & Brew, y que reaccione en vivo; dibujos como los que hacen los baristas de verdad; pantalla completa." (segunda versión)
- **Cita (APA):** Claude. (2026). *Prompts utilizados para la programación del juego Purr & Brew: Latte Art* [Generación de código]. Anthropic. Recuperado de https://claude.ai