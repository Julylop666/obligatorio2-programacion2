"""generar_sonidos.py - Crea todos los sonidos y la música del juego desde cero, con matemática.

Igual que en Purr & Brew: nada se baja de internet. Cada .wav se arma sumando ondas seno,
ruido y "envolventes" (curvas que suben y bajan el volumen). Son 100% propios.
Se ejecuta una sola vez (los .wav ya vienen hechos en la carpeta sonidos/):
    python generar_sonidos.py   (con el .venv activado)

Sonidos:
  chorro.wav       chorro de leche en loop
  ding.wav         pasaste la ronda
  campanita.wav    aparece una estrella
  miau_triste.wav  perdiste
  musica_lofi.wav  música de fondo
"""
import math
import os
import random
import struct
import wave
from ajustes import RUTA_SONIDOS

TASA = 22050             # muestras por segundo (alcanza para estos sonidos y pesa poco)
RMS_EFECTOS = 0.09       # sonoridad pareja para todos los efectos
RMS_MUSICA = 0.05        # la música más bajita, para que no tape los efectos
RMS_CHORRO = 0.035       # el chorro suena todo el tiempo mientras vertés: tiene que ser suave
TECHO_PICO = 0.85        # ningún sonido pasa de este pico (si no, distorsiona)


def guardar(nombre, muestras, rms_objetivo=RMS_EFECTOS, fundido=True):
    """Normaliza las muestras (entre -1 y 1) y las guarda como WAV mono de 16 bits.

    La ganancia se calcula por sonoridad (RMS) para que todos los efectos suenen parejo.
    fundido=False es para los loops: un fundido al principio y al final haría un "hueco"
    cada vez que el loop vuelve a empezar.
    """
    muestras = list(muestras)
    if fundido:
        largo = int(0.006 * TASA)
        for i in range(min(largo, len(muestras))):
            muestras[i] *= i / largo
            muestras[-1 - i] *= i / largo
    pico = max(1e-9, max(abs(m) for m in muestras))
    rms = math.sqrt(sum(m * m for m in muestras) / len(muestras))
    ganancia = min(rms_objetivo / rms, TECHO_PICO / pico)
    datos = bytearray()
    for m in muestras:
        valor = max(-1.0, min(1.0, m * ganancia))
        datos += struct.pack("<h", int(valor * 32767))
    os.makedirs(RUTA_SONIDOS, exist_ok=True)
    with wave.open(os.path.join(RUTA_SONIDOS, nombre), "wb") as archivo:
        archivo.setnchannels(1)
        archivo.setsampwidth(2)
        archivo.setframerate(TASA)
        archivo.writeframes(bytes(datos))


def pasa_bajos(muestras, factor):
    """Filtro pasa-bajos simple: cada muestra se acerca de a poco a la anterior (más grave y suave)."""
    salida = []
    y = 0.0
    for m in muestras:
        y += (m - y) * factor
        salida.append(y)
    return salida


def campana(frecuencia, t, decaimiento):
    """Devuelve una nota tipo campanita en el instante t (con dos armónicos que le dan brillo)."""
    if t < 0:
        return 0.0
    onda = (math.sin(2 * math.pi * frecuencia * t) + 0.3 * math.sin(4 * math.pi * frecuencia * t)
            + 0.1 * math.sin(6 * math.pi * frecuencia * t))
    return onda * math.exp(-t * decaimiento)


def pasa_altos(muestras, factor):
    """Filtro pasa-altos simple: a la señal le resto su versión suavizada (se quedan los agudos)."""
    graves = pasa_bajos(muestras, factor)
    salida = []
    for i in range(len(muestras)):
        salida.append(muestras[i] - graves[i])
    return salida


def burbuja(frecuencia, t):
    """Devuelve el sonido de un 'glup' en el instante t: un tono grave que sube apenas y se apaga suave."""
    if t < 0:
        return 0.0
    tono = frecuencia * (1 + 0.8 * t)            # sube un poquito de tono mientras suena
    return math.sin(2 * math.pi * tono * t) * math.exp(-t * 18)


def generar_chorro():
    """Chorro de leche suave, de 2 segundos, que se repite sin cortes.

    La idea es que sea agradable, no fiel: leche cayendo despacito.
      - Un "shhh" grave: ruido filtrado DOS veces con un pasa-bajos, así no le quedan agudos
        (los agudos son los que hacen ese "fuzz" molesto). Le saco también lo más grave de
        todo para que no retumbe.
      - Unos pocos "glups" graves y bajitos, que le dan el toque de líquido.
    Para que el loop no tenga costura, genero un poco más largo y el final se funde con el
    principio (mientras uno baja, el otro sube).
    """
    azar = random.Random(30)
    total = 2 * TASA
    extra = int(0.4 * TASA)                       # lo que se funde al final
    largo = total + extra
    shhh = pasa_bajos(pasa_bajos([azar.uniform(-1, 1) for _ in range(largo)], 0.07), 0.07)
    shhh = pasa_altos(shhh, 0.02)                 # saco el retumbe
    # vaivén lento al azar, para que el chorro "respire" y no sea un ruido parejo
    vaiven = pasa_bajos([azar.uniform(0.6, 1.0) for _ in range(largo)], 0.0005)
    muestras = []
    for i in range(largo):
        muestras.append(shhh[i] * vaiven[i])
    # pocos glups (unos 5 por segundo), graves y suaves
    largo_glup = int(0.25 * TASA)
    for _ in range(11):
        inicio = azar.randint(0, total - 1)
        frecuencia = azar.uniform(170, 320)
        fuerza = azar.uniform(0.02, 0.05)
        for i in range(largo_glup):
            if inicio + i < largo:
                muestras[inicio + i] += burbuja(frecuencia, i / TASA) * fuerza
    # el final se funde con el principio: así cuando el loop vuelve a empezar no hay salto
    for i in range(extra):
        mezcla = i / extra
        muestras[i] = muestras[i] * mezcla + muestras[total + i] * (1 - mezcla)
    return muestras[:total]


def generar_ding():
    """Pasaste la ronda: dos notas brillantes que suben (sol y do agudo)."""
    total = int(1.0 * TASA)
    muestras = []
    for i in range(total):
        t = i / TASA
        muestras.append(campana(784.0, t, 5) * 0.8 + campana(1046.5, t - 0.14, 4.5))
    return muestras


def generar_campanita():
    """Aparece una estrella: una campanita aguda y cortita con un brillito arriba."""
    total = int(0.7 * TASA)
    muestras = []
    for i in range(total):
        t = i / TASA
        muestras.append(campana(1568.0, t, 7) + campana(2349.3, t - 0.05, 9) * 0.4)
    return muestras


def generar_miau_triste():
    """Perdiste: un 'miau' que baja de tono, con un temblor (vibrato) al final."""
    duracion = 0.9
    muestras = []
    fase = 0.0
    for i in range(int(duracion * TASA)):
        avance = i / (duracion * TASA)
        vibrato = 12 * math.sin(2 * math.pi * 6 * i / TASA) * avance
        # sube un poquito al principio ("mi...") y después cae ("...au")
        frecuencia = 620 + 160 * math.sin(math.pi * min(1.0, avance * 3)) - 300 * avance + vibrato
        fase += 2 * math.pi * frecuencia / TASA
        envolvente = math.sin(math.pi * avance) ** 0.7
        muestras.append(envolvente * (math.sin(fase) + 0.45 * math.sin(2 * fase) + 0.2 * math.sin(3 * fase)))
    return pasa_bajos(muestras, 0.4)


def generar_musica():
    """Loop lo-fi de 24 segundos a 80 pulsos por minuto: acordes, bajo, bombo, hi-hat y notitas.

    Acordes: Fmaj7 - Em7 - Dm7 - Cmaj7 (cada uno dura 4 pulsos) y se repiten dos veces
    con distintas notitas arriba.
    """
    azar = random.Random(23)                     # semilla fija: sale la misma música siempre
    pulso = 60 / 80
    acordes = [
        (87.31, [174.61, 220.0, 261.63, 329.63]),    # Fmaj7
        (82.41, [164.81, 196.0, 246.94, 293.66]),    # Em7
        (73.42, [146.83, 174.61, 220.0, 261.63]),    # Dm7
        (65.41, [130.81, 164.81, 196.0, 246.94]),    # Cmaj7
    ]
    pentatonica = [523.25, 587.33, 659.25, 783.99, 880.0]
    largo_acorde = 4 * pulso
    total = int(largo_acorde * len(acordes) * 2 * TASA)
    buf = [0.0] * total
    for vuelta in range(2):
        for n, (bajo, notas) in enumerate(acordes):
            inicio = int((vuelta * len(acordes) + n) * largo_acorde * TASA)
            for i in range(int(largo_acorde * TASA)):
                t = i / TASA
                env = min(1.0, t / 0.3) * min(1.0, (largo_acorde - t) / 0.4)   # entra y sale suave
                pad = 0.0
                for f in notas:
                    pad += math.sin(2 * math.pi * f * t)
                buf[inicio + i] += pad * 0.05 * env + math.sin(2 * math.pi * bajo * t) * 0.2 * env
            # notitas de la melodía en corcheas (medio pulso), algunas sí y otras no
            for paso in range(8):
                if azar.random() < 0.45:
                    f = azar.choice(pentatonica)
                    ini = inicio + int(paso * pulso / 2 * TASA)
                    for i in range(int(0.5 * TASA)):
                        if ini + i < total:
                            buf[ini + i] += campana(f, i / TASA, 6) * 0.06
    # batería suave: bombo en los pulsos 1 y 3, hi-hat en los contratiempos
    pulsos = int(total / TASA / pulso)
    for p in range(pulsos):
        ini = int(p * pulso * TASA)
        if p % 2 == 0:
            for i in range(int(0.25 * TASA)):
                t = i / TASA
                if ini + i < total:
                    buf[ini + i] += math.sin(2 * math.pi * (55 + 60 * math.exp(-t * 30)) * t) * math.exp(-t * 14) * 0.35
        ini_hat = ini + int(pulso / 2 * TASA)
        for i in range(int(0.04 * TASA)):
            if ini_hat + i < total:
                buf[ini_hat + i] += azar.uniform(-1, 1) * math.exp(-i / TASA * 90) * 0.05
    for i in range(total):                        # crujidito de vinilo, como en Purr & Brew
        if azar.random() < 0.0005:
            buf[i] += azar.uniform(-0.06, 0.06)
    return pasa_bajos(buf, 0.5)


if __name__ == "__main__":
    guardar("chorro.wav", generar_chorro(), RMS_CHORRO, fundido=False)
    guardar("ding.wav", generar_ding())
    guardar("campanita.wav", generar_campanita())
    guardar("miau_triste.wav", generar_miau_triste())
    guardar("musica_lofi.wav", generar_musica(), RMS_MUSICA, fundido=False)
    print("Listo: sonidos guardados en", RUTA_SONIDOS)