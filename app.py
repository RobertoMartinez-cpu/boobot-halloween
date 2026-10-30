# -*- coding: utf-8 -*-
"""
🎃 BOO-BOT: CHATBOT DE HALLOWEEN (versión Streamlit) 🎃
-------------------------------------------------------
Chatbot web para estudiantes de secundaria (12-15 años) con Gemini.

EJECUTAR EN TU COMPUTADORA:
    pip install -r requirements.txt
    streamlit run app.py

CLAVE DE API (gratis, https://aistudio.google.com/apikey):
    - Local: crea el archivo .streamlit/secrets.toml con la línea
          GEMINI_API_KEY = "TU_CLAVE"
      (o define la variable de entorno GEMINI_API_KEY).
    - Streamlit Community Cloud: pégala en Settings > Secrets de tu app.
    NUNCA subas tu clave a GitHub.
"""

import os
import time

import streamlit as st
from google import genai
from google.genai import types

# ============================================================
# 1. CONFIGURACIÓN (cambia aquí lo que quieras)
# ============================================================

# Modelo de Gemini. Si Google lo retira o lo renombra, cambia solo esta línea.
MODELO = "gemini-3.8-flash"

# Máximo de mensajes que puede enviar una persona por sesión (protege tu cuota
# gratuita). Sube o baja este número según lo necesites.
MAX_MENSAJES_POR_SESION = 20

# Intentos máximos cuando Gemini responde "saturado" (503). 1 = sin reintentos.
MAX_REINTENTOS = 4

# Las 10 preguntas clave (botones de la barra lateral)
PREGUNTAS_RAPIDAS = [
    "¿De dónde viene Halloween?",
    "¿Por qué se usa la calabaza con cara?",
    "¿Qué significa Trick or Treat?",
    "¿Por qué los gatos negros dan mala suerte?",
    "¿De dónde vienen los disfraces de miedo?",
    "¿Halloween y Día de Muertos son lo mismo?",
    "¿Cuál es la leyenda de Jack O'Lantern?",
    "¿De dónde salieron los vampiros y los zombis?",
    "¿Quién escribió Frankenstein?",
    "¿Por qué Halloween es naranja y negro?",
]

BIENVENIDA = (
    "¡Buuu! 👻 Bienvenido a mi casa embrujada. 🏚️ Soy Boo-Bot, un fantasma que sabe "
    "TODO sobre Halloween. Toca una pregunta de la barra lateral o escribe la tuya "
    "(no importa si tienes faltas de ortografía, yo entiendo). 🦇"
)

# ============================================================
# 2. PROMPT DE SISTEMA (la personalidad y los datos del bot)
# ============================================================

PROMPT_SISTEMA = """
Eres "Boo-Bot", un fantasma simpático y misterioso que vive en una casa embrujada
y es experto en Halloween. Hablas con estudiantes de secundaria (12 a 15 años).

PERSONALIDAD Y ESTILO
- Responde SIEMPRE en español, con tono divertido, misterioso y amistoso, como un
  narrador de historias de misterio, pero sin exagerar.
- Usa emojis de Halloween con moderación (🎃👻🦇🕸️🧛🧟🐈‍⬛💀).
- Respuestas cortas y fáciles de leer: de 3 a 6 oraciones. Puedes terminar con un
  "dato escalofriante" o una pregunta curiosa para seguir platicando.
- Si el tema lo permite, cierra con una frase tipo "¿Quieres saber más? 👻".
- Explica como si hablaras con un adolescente: claro, sin sonar infantil ni aburrido.

TOLERANCIA A ERRORES (MUY IMPORTANTE)
- Los usuarios son adolescentes y pueden escribir con faltas de ortografía, sin tildes,
  sin signos de interrogación, con abreviaturas, en minúsculas, con letras repetidas
  o con modismos (ej.: "k es halowin", "xq la calabasa tiene cara", "de donde bienen los
  bampiros", "quien escribio frankestein", "q onda con el dia de muertos", "trik or tret").
- NUNCA corrijas ni regañes por la ortografía. Interpreta la intención y responde
  directamente. Si de verdad no entiendes, pregunta con amabilidad qué quiso decir.
- Reconoce variantes como: Halloween/Jalogüin/Halowin, Frankenstein/Frankestein,
  Jack O'Lantern/Jack o linterna, vampiro/bampiro, zombi/zombie/sombi.

REGLAS DE SEGURIDAD (público menor de edad)
- Mantén todo apto para 12-15 años: nada de gore, violencia explícita, contenido
  sexual, drogas, alcohol ni instrucciones peligrosas.
- Si piden algo peligroso o inapropiado (por ejemplo, retos riesgosos o asustar a
  alguien de forma dañina), responde con humor que ese hechizo está prohibido y ofrece
  una alternativa segura (por ejemplo, decorar, hacer un disfraz, contar una leyenda).
- Si el usuario menciona sentirse mal, en peligro o muy triste, responde con calidez,
  sin bromas de terror, y sugiere hablar con un adulto de confianza (familia, maestro
  o prefecto).
- Si preguntan algo que NO tiene que ver con Halloween, puedes responder brevemente si
  es seguro y educativo, y luego regresar con gracia al tema de Halloween.
- No inventes datos. Si no estás seguro, dilo con honestidad ("dicen las leyendas
  que…", "algunos historiadores creen que…").

BASE DE CONOCIMIENTO: LAS 10 PREGUNTAS CLAVE (datos que debes respetar)

1) ¿De dónde viene Halloween?
   De la fiesta celta de Samhain, en Irlanda, Escocia y zonas cercanas, hace unos
   2,000 años. Marcaba el fin de la cosecha y el inicio del invierno (31 de octubre al
   1 de noviembre); creían que la frontera entre vivos y espíritus se hacía delgada.
   Luego la Iglesia cristiana puso el Día de Todos los Santos el 1 de noviembre; la
   noche anterior se llamó "All Hallows' Eve", que con el tiempo se volvió "Halloween".
   Los inmigrantes irlandeses la llevaron a Estados Unidos, donde se volvió popular.

2) ¿Por qué se usa la calabaza con cara?
   Viene de la tradición irlandesa de tallar nabos y remolachas para hacer faroles
   que ahuyentaran espíritus. En Estados Unidos los inmigrantes encontraron calabazas,
   que son más grandes y fáciles de tallar. Se relaciona con la leyenda de Jack O'Lantern.

3) ¿Qué significa "Trick or Treat" (Dulce o truco)?
   Significa "truco o trato": los niños piden dulces y, en broma, amenazan con una
   travesura si no reciben nada. Se inspira en tradiciones europeas medievales como
   el "souling" (pedir pastelitos de alma a cambio de oraciones por los muertos) y el
   "guising" (disfrazarse e ir de casa en casa en Escocia e Irlanda). La costumbre se
   popularizó en Estados Unidos y Canadá alrededor de 1920-1950. En México tiene su
   versión de pedir "calaverita" en Día de Muertos.

4) ¿Por qué los gatos negros tienen fama de mala suerte?
   En la Europa medieval se les asoció con brujas y con lo misterioso, porque se
   pensaba que las brujas tenían gatos como compañeros o que se transformaban en ellos.
   Eso es superstición: los gatos negros no traen mala suerte. En otros lugares son
   símbolo de buena suerte (por ejemplo, en Japón y en partes del Reino Unido), y en
   el antiguo Egipto los gatos eran muy respetados. Puedes recordar que adoptar
   gatitos negros es una gran idea y que a veces tardan más en ser adoptados por el mito.

5) ¿Cuál es el origen de los disfraces de miedo?
   En Samhain, los celtas usaban pieles de animales y máscaras para confundir o
   ahuyentar a los espíritus que andaban sueltos esa noche. Después se mezcló con el
   "guising" y con las fiestas modernas, donde los disfraces pasaron a ser de monstruos,
   brujas, fantasmas, personajes de películas, etc.

6) ¿Qué diferencia hay entre Halloween y el Día de Muertos?
   Son distintos. Halloween viene de tradiciones celtas y europeas y hoy es una fiesta
   divertida y de terror, con disfraces y dulces. El Día de Muertos (1 y 2 de
   noviembre) es una tradición mexicana con raíces prehispánicas y mezcla católica;
   es para recordar y honrar con cariño a los seres queridos que murieron, con altares
   u ofrendas, cempasúchil, pan de muerto, calaveritas y fotos. No es "el Halloween de
   México": su tono es de memoria, amor y celebración de la vida. Fue reconocido por la
   UNESCO como Patrimonio Cultural Inmaterial de la Humanidad. Trátalo siempre con respeto.

7) ¿Cuál es la leyenda de Jack O'Lantern?
   Es un cuento irlandés sobre "Jack el Tacaño", un tipo bebedor y tramposo que engañó
   al Diablo varias veces. Cuando murió, no lo dejaron entrar al cielo, y el Diablo no
   quiso que entrara al infierno por las trampas que le hizo; le lanzó un carbón
   encendido. Jack lo puso dentro de un nabo hueco y vaga por el mundo con ese farol
   (de ahí "Jack of the Lantern", Jack el de la linterna).

8) ¿De dónde salió la historia de los vampiros y los zombis?
   Vampiros: viene del folclore de Europa del Este y los Balcanes, donde se temía a
   muertos que regresaban a molestar a los vivos (siglos XVII y XVIII). El médico John
   Polidori escribió "El vampiro" (1819), y Bram Stoker publicó "Drácula" (1897), que
   fijó la imagen moderna (inspirada vagamente en historias sobre Vlad el Empalador,
   pero Drácula es ficción).
   Zombis: vienen del folclore de Haití y las creencias vudú de origen africano, donde
   se hablaba de personas sin voluntad controladas por un hechicero. El cine moderno,
   sobre todo "La noche de los muertos vivientes" (1968) de George Romero, creó al
   zombi que come cerebros y que hoy conocemos.

9) ¿Quién escribió la novela original de Frankenstein?
   La escribió Mary Shelley, a los 18-19 años. Nació de un reto de historias de miedo
   en el verano de 1816 (el "año sin verano") en Suiza, con su pareja Percy Shelley, Lord
   Byron y John Polidori. Se publicó en 1818 con el título "Frankenstein; o, el moderno
   Prometeo". Dato clave: Frankenstein es el nombre del científico, Victor Frankenstein,
   no del monstruo (que en la novela no tiene nombre).

10) ¿Por qué se asocia el color naranja y negro a Halloween?
   Naranja: representa la cosecha, el otoño, las calabazas y el fuego de las hogueras de
   Samhain. Negro: representa la noche, la oscuridad, la muerte y el invierno que se
   acerca. Juntos simbolizan el cambio entre la cosecha y la oscuridad. A veces se suma
   el morado, asociado con lo místico y la magia.

CÓMO USAR ESTA BASE
- Cuando pregunten por uno de estos temas (aunque esté muy mal escrito), responde con
  estos datos, en tu estilo, resumido y entretenido. Para otras preguntas sobre
  Halloween, monstruos o leyendas, usa tu conocimiento general con las mismas reglas.
"""

# ============================================================
# 3. CONFIGURACIÓN DE LA PÁGINA Y ESTILO
# ============================================================

st.set_page_config(page_title="Boo-Bot 🎃", page_icon="🎃", layout="centered")

# CSS extra para darle ambiente de Halloween (los colores base están en
# .streamlit/config.toml)
st.markdown(
    """
    <style>
    h1 { color: #ff7518 !important; text-align: center; }
    .subtitulo { text-align: center; color: #f5e6ff; font-style: italic;
                 margin-top: -10px; margin-bottom: 10px; }
    section[data-testid="stSidebar"] button {
        border: 1px solid #ff7518; text-align: left;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #ff7518; color: black; border-color: #ff7518;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎃 Boo-Bot 👻")
st.markdown(
    '<p class="subtitulo">🦇 Pregúntame lo que quieras sobre Halloween 🕸️</p>',
    unsafe_allow_html=True,
)

# ============================================================
# 4. CONEXIÓN CON GEMINI
# ============================================================


def obtener_api_key():
    """Busca la clave en st.secrets y, si no está, en la variable de entorno."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:  # noqa: BLE001  (no hay archivo de secrets)
        pass
    return os.environ.get("GEMINI_API_KEY", "")


@st.cache_resource
def crear_cliente(api_key):
    """Crea el cliente una sola vez y lo reutiliza (cache_resource lo mantiene vivo)."""
    return genai.Client(api_key=api_key)


API_KEY = obtener_api_key()
if not API_KEY:
    st.error(
        "No encontré la clave de API. 🕸️ Agrega GEMINI_API_KEY en "
        ".streamlit/secrets.toml (local) o en Settings > Secrets (Streamlit Cloud)."
    )
    st.stop()

cliente = crear_cliente(API_KEY)


def generar_respuesta(historial):
    """Llama a Gemini en modo streaming y va entregando el texto poco a poco.

    historial: lista de mensajes {"role": "user"|"assistant", "content": "..."}
    """
    # Gemini usa el rol "model" en lugar de "assistant"
    contenidos = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part.from_text(text=m["content"])],
        )
        for m in historial
    ]
    config = types.GenerateContentConfig(
        system_instruction=PROMPT_SISTEMA,
        temperature=0.8,          # más alto = más creativo
        max_output_tokens=2048,   # límite de largo de respuesta
    )
    # Reintentos automáticos: si Gemini está saturado (error 503) esperamos unos
    # segundos y volvemos a intentar, siempre que todavía no haya empezado a responder.
    for intento in range(1, MAX_REINTENTOS + 1):
        ya_respondio = False
        try:
            for fragmento in cliente.models.generate_content_stream(
                model=MODELO, contents=contenidos, config=config
            ):
                if fragmento.text:
                    ya_respondio = True
                    yield fragmento.text
            return  # terminó bien
        except Exception as e:  # noqa: BLE001
            saturado = "503" in str(e) or "UNAVAILABLE" in str(e)
            if saturado and not ya_respondio and intento < MAX_REINTENTOS:
                time.sleep(2 * intento)  # espera 2 s, luego 4 s, etc.
                continue
            raise


def mensaje_de_error(e):
    """Convierte errores técnicos en mensajes amigables."""
    msg = str(e)
    if "429" in msg or "quota" in msg.lower() or "RESOURCE_EXHAUSTED" in msg:
        return ("Los fantasmas están muy ocupados (límite gratuito alcanzado). "
                "Espera un minuto y vuelve a intentar. ⏳")
    if "503" in msg or "UNAVAILABLE" in msg:
        return ("Hay muchos fantasmas haciendo fila en Gemini en este momento. 👻 "
                "Intenta de nuevo en unos segundos.")
    if "API key" in msg or "401" in msg or "403" in msg:
        return "La clave de API no parece válida. Avísale a quien administra la app. 🔑"
    if "404" in msg or "NOT_FOUND" in msg:
        return "El modelo de Gemini ya no existe. Hay que actualizar la variable MODELO. 🧙"
    return f"Un hechizo falló: {msg}"


# ============================================================
# 5. ESTADO DE LA SESIÓN Y BARRA LATERAL
# ============================================================

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []  # historial de la conversación

with st.sidebar:
    st.header("🎃 Preguntas clave")
    for i, pregunta in enumerate(PREGUNTAS_RAPIDAS):
        if st.button(pregunta, key=f"preg_{i}", use_container_width=True):
            st.session_state.pendiente = pregunta  # se procesa más abajo
    st.divider()
    if st.button("🧹 Nueva conversación", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

# ============================================================
# 6. MOSTRAR EL CHAT
# ============================================================

with st.chat_message("assistant", avatar="👻"):
    st.markdown(BIENVENIDA)

for m in st.session_state.mensajes:
    avatar = "🧑‍🎤" if m["role"] == "user" else "👻"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])

# ============================================================
# 7. ENTRADA DEL USUARIO (escrita o desde un botón)
# ============================================================

texto_escrito = st.chat_input("Escribe tu pregunta... 🎃")
texto = texto_escrito or st.session_state.pop("pendiente", None)

if texto:
    enviados = sum(1 for m in st.session_state.mensajes if m["role"] == "user")
    if enviados >= MAX_MENSAJES_POR_SESION:
        st.warning(
            "¡Llegaste al límite de preguntas de esta sesión! 🕯️ "
            "Pulsa «Nueva conversación» para seguir platicando."
        )
    else:
        # Guardar y mostrar el mensaje del usuario
        st.session_state.mensajes.append({"role": "user", "content": texto})
        with st.chat_message("user", avatar="🧑‍🎤"):
            st.markdown(texto)

        # Pedir y mostrar la respuesta (en streaming)
        with st.chat_message("assistant", avatar="👻"):
            try:
                with st.spinner("Boo-Bot está invocando una respuesta... 🕯️"):
                    flujo = generar_respuesta(st.session_state.mensajes)
                    respuesta = st.write_stream(flujo)
                st.session_state.mensajes.append(
                    {"role": "assistant", "content": respuesta}
                )
            except Exception as e:  # noqa: BLE001
                st.session_state.mensajes.pop()  # quitar la pregunta que falló
                st.error(mensaje_de_error(e))
