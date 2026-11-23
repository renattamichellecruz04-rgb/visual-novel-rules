"""Genera los MP3 de la novela visual con la API de ElevenLabs.

Uso (en la misma carpeta que guion-de-audios.csv):
    python generar_audios.py        -> solo prioridad 1 (diálogos)
    python generar_audios.py 2      -> prioridades 1 y 2
    python generar_audios.py 3      -> todo

Tu clave NO va en este archivo. Se pone como variable de entorno:
    Windows (PowerShell):  $env:ELEVENLABS_API_KEY="tu_clave"
    Mac / Linux:           export ELEVENLABS_API_KEY="tu_clave"
"""
import csv, os, sys, time
import requests

# Pega aquí los ID de voz (se copian desde tu cuenta de ElevenLabs).
VOCES = {
    "Narrador": "LBi9MYvr8AlDyPBIl3Wb",
    "Voz del abismo": "XnbuA6Hhc8gllKXizJng",
    "Protagonista": "KxO9GVAQgIgl1m323jLO",
}
MODELO = "eleven_multilingual_v2"
MAX_PRIORIDAD = int(sys.argv[1]) if len(sys.argv) > 1 else 1

clave = os.environ.get("ELEVENLABS_API_KEY")
if not clave:
    sys.exit("Falta la variable ELEVENLABS_API_KEY (mira las instrucciones arriba).")
if any("PEGA_AQUI" in v for v in VOCES.values()):
    sys.exit("Pega primero los ID de voz en el diccionario VOCES.")

os.makedirs("audio", exist_ok=True)

with open("guion-de-audios.csv", encoding="utf-8-sig", newline="") as f:
    filas = [r for r in csv.DictReader(f) if int(r["prioridad"]) <= MAX_PRIORIDAD]

for i, r in enumerate(filas, 1):
    destino = os.path.join("audio", r["archivo"])
    if os.path.exists(destino):
        print(f"[{i}/{len(filas)}] ya existe {r['archivo']}")
        continue
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOCES[r['voz']]}"
    cuerpo = {"text": r["texto"], "model_id": MODELO}
    for intento in range(2):
        resp = requests.post(
            url,
            params={"output_format": "mp3_44100_128"},
            headers={"xi-api-key": clave, "Content-Type": "application/json"},
            json=cuerpo,
            timeout=120,
        )
        if resp.status_code == 429 and intento == 0:
            time.sleep(10)
            continue
        break
    if resp.status_code != 200:
        print(f"Error {resp.status_code} en {r['archivo']}: {resp.text[:200]}")
        print("Detenido. Revisa tu clave, tu plan o tus créditos y vuelve a correr el script: continúa donde se quedó.")
        break
    with open(destino, "wb") as out:
        out.write(resp.content)
    print(f"[{i}/{len(filas)}] listo {r['archivo']}")
    time.sleep(0.5)
