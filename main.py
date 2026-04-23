import requests
import schedule
import time
from datetime import datetime
import random
import os

# ============================================================
# CONFIGURACIÓN — completá estos valores
# ============================================================
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

HORA_ENVIO = "14:45"

# ============================================================
# CONTEXTO PERSONAL — extraído de conversaciones reales
# ============================================================
CONTEXTO_PERSONAL = """
Quién es esta persona:
- Tiene 20 años casi 21, vive en Fray Bentos estudiando Ingeniería en Mecatrónica en UTEC.
  Es de Carmelo. Vive solo, alquila.
- Es introvertido, directo, no le gusta el relleno ni las frases vacías.
- Tiene metas grandes: quiere fundar empresas, ser millonario, construir proyectos serios.
  Su cabeza está siempre en plata y futuro.
- Entiende perfectamente que el físico no es vanidad — es la base. Sabe que el físico
  trae autoestima, la autoestima trae presencia, y con eso viene lo social, el amor, la plata.
  Lo tiene clarísimo en la cabeza. El problema es la acción.

Su relación con el gym:
- Pagó el gym (Fit House, Fray Bentos). Lo tiene. Va a las 3 de la tarde.
- Va muy irregular. A veces va varios días, a veces desaparece una semana.
- Sus excusas varían según el día: a veces termina de comer tarde y se le mezcla
  con lavar los platos o limpiar. A veces es pereza pura. A veces se queda con el celu
  o en la compu y se le va la hora sin darse cuenta.
- Él mismo lo sabe y lo admite: "soy pura excusa", "espero que el día se alinee ideal y nunca es así".
- Quiere que le duela faltar. Quiere que el gym sea innegociable.

Lo que lo mueve de verdad:
- No quiere frases de Pinterest. No quiere "vos podés".
- Lo que le llega es la verdad directa: que mientras él falta, el tiempo pasa igual.
  Que la irregularidad es peor que no empezar. Que cada vez que no va, el día ideal
  que espera se aleja más.
- Le importa verse bien en el espejo. Que los demás lo noten. Sentirse seguro y con carácter.
- Es alguien que quiere construir todo: físico, plata, relaciones. Y entiende que
  el físico es la primera prueba de que puede comprometerse con algo.
- Sabe que con el físico viene la autoestima, y con eso llega lo demás: lo social, el amor, la plata.
"""

# ============================================================
# Variantes de situación para que el mensaje no sea siempre igual
# ============================================================
SITUACIONES = [
    "Hoy quizás ya comió y está tentado a quedarse tirado.",
    "Hoy quizás está cansado después de clases virtuales y la excusa ya está lista.",
    "Hoy quizás está con el celu y se le va a pasar la hora si no se mueve ya.",
    "Hoy quizás está dudando, buscando inconscientemente una razón para no ir.",
    "Hoy quizás está pensando 'mañana voy' otra vez.",
    "Hoy quizás el día no salió como esperaba y ya lo usa de excusa.",
    "Hoy quizás le quedó algo pendiente — lavar, limpiar — y lo pone por delante del gym.",
]


def generar_mensaje_claude():
    """Genera un mensaje motivacional personalizado usando Claude."""
    situacion = random.choice(SITUACIONES)
    dia = datetime.now().strftime("%A")

    prompt = f"""Sos un amigo que conoce muy bien a esta persona. Leé su contexto y escribile un mensaje.

{CONTEXTO_PERSONAL}

Hoy es {dia}. {situacion}

Escribile un mensaje corto (máximo 4-5 oraciones) para las 2:45pm recordándole que tiene gym a las 3.

Reglas:
- Hablale de vos a vos, en rioplatense natural (vas, tenés, hacés, etc.)
- Nombrá algo concreto de su situación real: las excusas que él mismo reconoce,
  el día ideal que nunca llega, que ya pagó el gym, que sabe lo que quiere pero no arranca.
- Conectalo con lo que realmente quiere: el físico, la autoestima, lo que viene después con eso.
- Sé brutalmente honesto, casi agresivo. Que pique. Que le dé un poco de vergüenza 
  no ir después de leerlo. Podés insultarlo levemente si suma (flaco, boludo, etc.)
  pero sin pasarte — el objetivo es que cierre el celu y vaya, no que se sienta mal.
- Recordale que mientras él busca excusas, otros están construyendo el físico que él quiere.
- Sin asteriscos, sin markdown. Máximo 1 emoji si suma de verdad, si no, ninguno.
- Que suene como alguien que lo conoce, no como una app de meditación.

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
            "Son las 2:45. Gym a las 3.\n"
            "Hoy no hay día ideal, no hay condiciones perfectas. "
            "Agarrá la mochila y andá. Ya sabés por qué."
        )


def enviar_telegram(mensaje):
    """Envía el mensaje por Telegram."""
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


# ============================================================
# Scheduler
# ============================================================
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
