"""generar_sonidos.py - Crea todos los sonidos y la música del juego desde cero, con matemática.

Igual que en Purr & Brew: nada se baja de internet. Cada .wav se arma sumando ondas seno,
ruido y "envolventes" (curvas que suben y bajan el volumen). Son 100% propios.
Se ejecuta una sola vez (los .wav ya vienen hechos en la carpeta sonidos/):
    py generar_sonidos.py

Sonidos:
  chorro_0..4.wav  chorro de leche en loop, uno por nota de la escala pentatónica (do re mi sol la)
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
from ajustes import RUTA_SONIDOS, NOTAS_CHORRO

TASA = 22050             # muestras por segundo (alcanza para estos sonidos y pesa poco)
RMS_EFECTOS = 0.09       # sonoridad pareja para todos los efectos
RMS_MUSICA = 0.05        # la música más bajita, para que no tape los efectos
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


def generar_chorro(frecuencia, semilla):
    """Chorro de leche de 1 segundo que se puede repetir sin cortes, con un tono de fondo.

    Ruido filtrado (el líquido) + un tono suave en la nota pedida (el guiño al synth)
    + burbujitas. Las frecuencias son números enteros: en 1 segundo entran ciclos completos,
    así el final empalma justo con el principio.
    """
    azar = random.Random(semilla)
    total = TASA
    ruido = pasa_bajos([azar.uniform(-1, 1) for _ in range(total)], 0.18)
    muestras = []
    for i in range(total):
        t = i / TASA
        borboteo = 0.7 + 0.2 * math.sin(2 * math.pi * 7 * t) + 0.1 * math.sin(2 * math.pi * 13 * t)
        tono = math.sin(2 * math.pi * frecuencia * t) + 0.3 * math.sin(4 * math.pi * frecuencia * t)
        muestras.append(ruido[i] * 3.0 * borboteo + tono * 0.22)
    for inicio in (0.1, 0.35, 0.6, 0.82):            # burbujitas que suben de tono
        for i in range(int(0.06 * TASA)):
            t = i / TASA
            pos = int(inicio * TASA) + i
            muestras[pos] += math.sin(2 * math.pi * frecuencia * 2 * (1 + 3 * t) * t) * math.exp(-t * 50) * 0.4
    return muestras


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
    for numero, nota in enumerate(NOTAS_CHORRO):
        guardar(f"chorro_{numero}.wav", generar_chorro(nota, 30 + numero), fundido=False)
    guardar("ding.wav", generar_ding())
    guardar("campanita.wav", generar_campanita())
    guardar("miau_triste.wav", generar_miau_triste())
    guardar("musica_lofi.wav", generar_musica(), RMS_MUSICA, fundido=False)
    print("Listo: sonidos guardados en", RUTA_SONIDOS)
