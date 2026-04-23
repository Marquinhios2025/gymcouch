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

HORA_GYM = "14:30"
HORA_NOCHE = "22:15"

# ============================================================
# CONTEXTO PERSONAL — todo extraído de conversaciones reales
# ============================================================
CONTEXTO_PERSONAL = """
Quién es Marcos, exactamente:
- 20 años casi 21. Vive solo en Fray Bentos estudiando Mecatrónica en UTEC. Es de Carmelo.
- Le debe plata a su madre. No sobra nada.
- Autoestima de cero. Él mismo lo dijo así: "de cero".
- Se considera gordo, antipático, rarito, aburrido. Sus palabras exactas.
- No tiene novia. En Uruguay a esa edad eso pesa socialmente y él lo siente.
- Tiene UN solo amigo de confianza. El resto los corta antes de que lo lastimen.
- Es introvertido pero con una cabeza enorme: quiere fundar empresas, ser millonario,
  construir sistemas, proyectos serios. Todo en la cabeza. Casi nada en la acción.
- Tiene un sistema de gestión para un club deportivo diseñado completo — nunca lo codeó.
- Estudia Laravel, hace landings, sabe programar — pero nada vendible todavía. Todo a medias.
- Sabe perfectamente que el físico → autoestima → presencia → vida social → amor → plata.
  Lo tiene clarísimo. El problema es que no hace nada.

Su única experiencia de sentirse bien:
- Una vez en su "prime": iba al gym, corría, estaba bien consigo mismo, sin buscar nada.
  Una chica le dijo que era lindo, todo se armó alrededor suyo. Eso fue lo mejor que vivió.
  Salió de ese momento y nunca volvió. Ese es el Marcos que quiere recuperar.

Su relación con el gym ahora:
- Pagó Fit House en Fray Bentos. Con plata que no le sobra.
- Va a las 3 de la tarde. Va muy irregular. Semanas enteras sin ir.
- Excusas: comió tarde, hay que lavar, hay que limpiar, cansancio, celu, compu.
- Él mismo lo admite: "soy pura excusa". "Espero que el día se alinee y nunca es así."
- Quiere que le duela faltar. Que sea innegociable.

Lo que más le duele:
- Gastar plata en algo que no usa (le duele más que cualquier otra cosa)
- Saber que podría pero no hace nada
- No tener lo que quiere y seguir igual
- La vocecita interna que le dice que no vale la pena
"""

# ============================================================
# ÁNGULOS DE ATAQUE — cada día uno distinto, rotando
# ============================================================
ANGULOS = [
    {
        "situacion": "Está con el celu o la compu, dejando pasar la hora.",
        "angulo": "La plata. Le duele gastar y no usar. Que calcule cuánto está tirando por día sin ir. Que sea concreto y brutal."
    },
    {
        "situacion": "Está pensando en sus proyectos, en ser millonario, en el futuro.",
        "angulo": "La contradicción. Quiere construir empresas pero no puede cumplirse ni 1 hora de gym. Si no puede con eso, no puede con nada. Que lo haga sentir ridículo."
    },
    {
        "situacion": "Está tirado después de comer, con la excusa del cansancio.",
        "angulo": "El prime perdido. Él ya sabe lo que es sentirse bien. Ya lo vivió. Una chica lo eligió, la gente se acercó. Salió de eso y nunca volvió. Ese Marcos existe y está enterrado bajo las excusas."
    },
    {
        "situacion": "Está dudando, buscando una razón para no ir.",
        "angulo": "Las mujeres y lo social. Le duele no encajar, no tener novia, sentirse invisible. Sin físico sin autoestima. Sin autoestima, invisible para siempre. Que lo pique donde más duele."
    },
    {
        "situacion": "Está pensando 'mañana voy' otra vez.",
        "angulo": "La deuda con su madre. No tiene plata. Le debe. Cada día sin producir, sin construirse, es un día más en deuda. El gym es el primer paso de toda la cadena."
    },
    {
        "situacion": "Está con algo pendiente de la casa como excusa.",
        "angulo": "El patrón. Todo a medias: el gym, el sistema del club, las landings, todo. Nunca termina nada. El gym es la única cosa que puede cerrar hoy, ahora, en 1 hora y media."
    },
    {
        "situacion": "Está en la cabeza, dando vueltas, pensando demasiado.",
        "angulo": "La vocecita. Él mismo dijo que tiene una voz interna que lo jode. La única forma de callarla no es pensando — es moviéndose. Que vaya al gym a cerrarle la boca."
    },
]

def generar_mensaje_claude():
    angulo = random.choice(ANGULOS)
    dia = datetime.now().strftime("%A")

    prompt = f"""Sos alguien que conoce a Marcos de verdad, con toda su historia, y está harto de verlo fallar.
Leé su contexto completo y escribile un mensaje. No menciones la hora en ningún momento.

{CONTEXTO_PERSONAL}

SITUACIÓN DE HOY: {angulo['situacion']}
ÁNGULO A USAR: {angulo['angulo']}

CÓMO TIENE QUE SER EL MENSAJE:
- Tono: rabia, frustración, palo directo. Como alguien que lo quiere pero está podrido de las excusas.
- Usá datos reales de su vida: la deuda con la madre, que se siente gordo y antipático, 
  que quiere ser millonario pero no puede ir al gym, que ya tuvo su prime y lo perdió,
  que tiene todo a medias, que le duele gastar plata y está tirando la del gym.
- Que pique donde duele. Que le dé vergüenza quedarse.
- Podés putear, insultarlo (boludo, cagón, puto, lo que sume). Natural, no forzado.
- Que sea DISTINTO a estos mensajes genéricos que ya no sirven:
  "Boludo, son las 2:45, estás pagando el gym que no usás"  <- ESTO NO, muy visto
  "Mientras vos buscás excusas, otros construyen" <- ESTO NO, muy genérico
- Tiene que sonar como alguien que lo conoce de hace años y le habla con la verdad en la cara.
- Sin asteriscos. Sin markdown. Sin emojis. Rioplatense natural.
- Máximo 5 oraciones. Que cada una pegue.

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
        try:
            print(f"Respuesta completa: {response.text}")
        except:
            pass
        return (
            "Pagaste el gym y no vas. Esa plata la debés.\n"
            "Cerrá lo que tenés en la mano y andá. Ya."
        )


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            print(f"[OK] Mensaje enviado a las {datetime.now().strftime('%H:%M:%S')}")
        else:
            print(f"[ERROR] Telegram: {r.status_code} — {r.text}")
    except Exception as e:
        print(f"[ERROR] Telegram conexión: {e}")


def generar_mensaje_noche():
    """Genera un recordatorio nocturno para salir a correr o caminar."""
    prompt = f"""Sos alguien que conoce a Marcos de verdad y le mandás un recordatorio a las 10:15pm.

{CONTEXTO_PERSONAL}

El objetivo de este mensaje es recordarle que salga a correr o caminar esta noche.
No es el gym — es algo más liviano, afuera, que también cuenta.

CÓMO TIENE QUE SER:
- Más tranquilo que el mensaje del gym, pero igual de directo. No tan agresivo, más frío.
- Recordale que moverse de noche también construye. Que 30 minutos caminando o trotando
  es mejor que quedarse tirado con el celu.
- Puede conectar con su físico, su cabeza, la vocecita que se calla cuando el cuerpo se mueve.
- Sin motivación de Pinterest. Sin "vos podés". Directo y concreto.
- Rioplatense natural. Sin emojis. Sin markdown. Máximo 3 oraciones.

Solo el texto, nada más."""

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
                "max_tokens": 150,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        data = response.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"[ERROR] Claude API noche: {e}")
        return "Salí a correr o caminar. 30 minutos. La cabeza se calma sola cuando el cuerpo se mueve."


def tarea_gym():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generando mensaje gym...")
    mensaje = generar_mensaje_claude()
    print(f"Mensaje:\n{mensaje}\n")
    enviar_telegram(mensaje)


def tarea_noche():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generando mensaje noche...")
    mensaje = generar_mensaje_noche()
    print(f"Mensaje:\n{mensaje}\n")
    enviar_telegram(mensaje)


def main():
    print(f"Bot activo.")
    print(f"  Gym:   todos los días a las {HORA_GYM}")
    print(f"  Noche: todos los días a las {HORA_NOCHE}")
    print("Ctrl+C para detener.\n")
    schedule.every().day.at(HORA_GYM).do(tarea_gym)
    schedule.every().day.at(HORA_NOCHE).do(tarea_noche)
    while True:
        schedule.run_pending()
        time.sleep(30)


def test_mensaje():
    print("=== TEST GYM ===")
    mensaje = generar_mensaje_claude()
    print(f"Mensaje:\n{mensaje}\n")
    enviar_telegram(mensaje)


def test_noche():
    print("=== TEST NOCHE ===")
    mensaje = generar_mensaje_noche()
    print(f"Mensaje:\n{mensaje}\n")
    enviar_telegram(mensaje)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_mensaje()
    elif len(sys.argv) > 1 and sys.argv[1] == "testnoche":
        test_noche()
    else:
        main()
