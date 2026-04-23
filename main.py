import requests
import schedule
import time
from datetime import datetime
import random
import os

# ============================================================
# CONFIGURACIÓN
# ============================================================
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

HORA_ENVIO = "14:45"

# ============================================================
# CONTEXTO PERSONAL
# ============================================================
CONTEXTO_PERSONAL = """
Quién es esta persona:
- Tiene 20 años casi 21, vive en Fray Bentos estudiando Ingeniería en Mecatrónica en UTEC.
  Es de Carmelo. Vive solo, alquila. No sobra la plata.
- Es introvertido, directo, no le gusta el relleno ni las frases vacías.
- Tiene metas grandes: quiere fundar empresas, ser millonario, construir proyectos serios.
  Su cabeza está siempre en plata y futuro.
- Entiende perfectamente que el físico no es vanidad — es la base. Sabe que el físico
  trae autoestima, la autoestima trae presencia, y con eso viene lo social, el amor, la plata.
  Lo tiene clarísimo en la cabeza. El problema es la acción.
- Lo que más le duele: gastar plata en algo que no usa. No tener lo que quiere. Saber que
  podría pero no hace nada.

Su relación con el gym:
- Pagó el gym (Fit House, Fray Bentos). Plata que salió de su bolsillo. Va a las 3 de la tarde.
- Va muy irregular. A veces va varios días, a veces desaparece una semana entera.
- Sus excusas varían: a veces comió tarde y se mezcla con lavar o limpiar. A veces pereza pura.
  A veces se queda con el celu o la compu y se le va la hora sin darse cuenta.
- Él mismo lo admite: "soy pura excusa", "espero que el día se alinee ideal y nunca es así".
- Quiere que le duela faltar. Quiere que el gym sea innegociable.
"""

# ============================================================
# Variantes de situación
# ============================================================
SITUACIONES = [
    "Hoy quizás ya comió y está tentado a quedarse tirado con el celu.",
    "Hoy quizás está cansado después de clases virtuales y la excusa ya está lista en la cabeza.",
    "Hoy quizás está con el celu y se le va a pasar la hora si no se mueve ya.",
    "Hoy quizás está dudando, buscando inconscientemente una razón para no ir.",
    "Hoy quizás está pensando 'mañana voy' otra vez.",
    "Hoy quizás el día no salió como esperaba y ya lo usa de excusa.",
    "Hoy quizás le quedó algo pendiente — lavar, limpiar — y lo pone por delante del gym.",
]


def generar_mensaje_claude():
    situacion = random.choice(SITUACIONES)
    dia = datetime.now().strftime("%A")

    prompt = f"""Sos un amigo que conoce muy bien a esta persona y está harto de verlo fallar. 
Leé su contexto y escribile un mensaje para las 2:45pm.

{CONTEXTO_PERSONAL}

Hoy es {dia}. {situacion}

Escribile un mensaje corto (máximo 4-5 oraciones).

Reglas — seguílas al pie de la letra:
- Tono: rabia contenida, palo directo. Como alguien que lo quiere pero está harto de las excusas.
- Usá su dolor real: está pagando un gym que no usa. Quiere plata, físico, mina, vida — 
  y no puede ni cumplirse ir a entrenar. Eso tiene que picar.
- Podés insultarlo si suma: boludo, cagón, flaco. Natural, no forzado.
- Recordale que el tiempo corre igual mientras él busca excusas. Que otros están construyendo
  lo que él quiere mientras él está tirado.
- Que la rabia y la vergüenza lo muevan. El objetivo es que cierre lo que tiene en la mano y vaya.
- NADA de "vos podés", NADA de aliento suave, NADA de frases de Pinterest.
- Sin asteriscos, sin markdown. Sin emojis.
- Rioplatense natural (vas, tenés, hacés).

Solo el texto del mensaje, nada más."""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-5",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        data = response.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"[ERROR] Claude API: {e}")
        print(f"Respuesta completa: {response.text}")
        return (
            "Son las 2:45. Estás pagando un gym que no usás.\n"
            "Cerrá lo que tenés en la mano y andá. Ya."
        )


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            print(f"[OK] Mensaje enviado a las {datetime.now().strftime('%H:%M:%S')}")
        else:
            print(f"[ERROR] Telegram: {r.status_code} — {r.text}")
    except Exception as e:
        print(f"[ERROR] Telegram conexión: {e}")


def tarea_diaria():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generando mensaje...")
    mensaje = generar_mensaje_claude()
    print(f"Mensaje generado:\n{mensaje}\n")
    enviar_telegram(mensaje)


def main():
    print(f"Bot activo. Enviará mensaje todos los días a las {HORA_ENVIO}")
    print("Ctrl+C para detener.\n")
    schedule.every().day.at(HORA_ENVIO).do(tarea_diaria)
    while True:
        schedule.run_pending()
        time.sleep(30)


def test_mensaje():
    print("Enviando mensaje de prueba...")
    mensaje = generar_mensaje_claude()
    print(f"Mensaje:\n{mensaje}\n")
    enviar_telegram(mensaje)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_mensaje()
    else:
        main()
