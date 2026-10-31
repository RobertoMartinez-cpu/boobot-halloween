# 🎃 Boo-Bot: chatbot de Halloween para secundaria

Chatbot web con temática de Halloween para estudiantes de secundaria (12 a 15 años). **Boo-Bot** es un fantasma simpático que responde de forma entretenida, misteriosa y educativa sobre el origen y las leyendas de Halloween, y entiende preguntas aunque tengan faltas de ortografía, no lleven tildes o usen modismos juveniles.

Está hecho en **Python** con **Streamlit** (interfaz web) y la **API de Google Gemini** (capa gratuita).

> Creado por Martínez García Roberto y Garrido Vazques Fernanda.

---

## Índice

1. [Características](#1-características)
2. [Estructura del proyecto](#2-estructura-del-proyecto)
3. [Cómo se construyó, paso a paso](#3-cómo-se-construyó-paso-a-paso)
4. [Cómo ejecutarlo en tu computadora](#4-cómo-ejecutarlo-en-tu-computadora)
5. [Cómo subirlo a GitHub](#5-cómo-subirlo-a-github)
6. [Cómo publicarlo en la nube](#6-cómo-publicarlo-en-la-nube-streamlit-community-cloud)
7. [Configuración y personalización](#7-configuración-y-personalización)
8. [Problemas que encontramos y cómo se resolvieron](#8-problemas-que-encontramos-y-cómo-se-resolvieron)
9. [Límites, privacidad y seguridad](#9-límites-privacidad-y-seguridad)

---

## 1. Características

- Interfaz de chat con tema oscuro de Halloween (morado y naranja) y emojis.
- **10 botones** en la barra lateral con las preguntas clave sobre Halloween.
- **Tolerancia a errores de ortografía:** el modelo interpreta la intención y nunca corrige al usuario.
- **Respuestas en streaming:** el texto aparece poco a poco.
- **Reintentos automáticos** cuando Gemini está saturado (error 503).
- **Límite de mensajes por sesión** para cuidar la cuota gratuita.
- **Reglas de seguridad** en el prompt para público menor de edad.
- La clave de API **nunca** está en el código: se guarda en `st.secrets`.

### Las 10 preguntas clave

| # | Pregunta |
|---|----------|
| 1 | ¿De dónde viene Halloween? |
| 2 | ¿Por qué se usa la calabaza con cara? |
| 3 | ¿Qué significa "Trick or Treat" (Dulce o truco)? |
| 4 | ¿Por qué los gatos negros tienen fama de mala suerte? |
| 5 | ¿Cuál es el origen de los disfraces de miedo? |
| 6 | ¿Qué diferencia hay entre Halloween y el Día de Muertos? |
| 7 | ¿Cuál es la leyenda de Jack O'Lantern? |
| 8 | ¿De dónde salió la historia de los vampiros y los zombis? |
| 9 | ¿Quién escribió la novela original de Frankenstein? |
| 10 | ¿Por qué se asocia el color naranja y negro a Halloween? |

---

## 2. Estructura del proyecto

```
boobot-halloween/
├── app.py                        # Aplicación completa (interfaz + lógica + prompt)
├── requirements.txt              # Dependencias de Python
├── README.md                     # Esta documentación
├── .gitignore                    # Evita subir secretos a GitHub
└── .streamlit/
    ├── config.toml               # Tema visual (colores de Halloween)
    └── secrets.toml.example      # Plantilla para la clave de API
```

El archivo real `.streamlit/secrets.toml` (con la clave) **no se sube a GitHub**.

---

## 3. Cómo se construyó, paso a paso

### Paso 1. Definir los requisitos

Antes de programar se definió qué debía hacer el chatbot:

- Público: estudiantes de secundaria (12 a 15 años).
- Temática: Halloween, con tono divertido y misterioso, pero educativo.
- Entender mensajes con faltas de ortografía, sin tildes y con modismos.
- Responder bien las 10 preguntas clave (y sus variaciones mal escritas).
- Usar una API gratuita (Google Gemini) y una interfaz sencilla.

### Paso 2. Diseñar el prompt de sistema (el "cerebro" del bot)

El prompt de sistema (`PROMPT_SISTEMA` en `app.py`) es la parte más importante. Se organizó en bloques:

1. **Personalidad y estilo:** Boo-Bot, un fantasma amistoso; respuestas de 3 a 6 oraciones, con emojis moderados y cierre con un dato curioso o una pregunta.
2. **Tolerancia a errores:** se le pide interpretar la intención, no corregir nunca la ortografía, y se le dan ejemplos reales de escritura juvenil (`"k es halowin"`, `"bampiros"`, `"frankestein"`, `"trik or tret"`).
3. **Reglas de seguridad para menores:** contenido apto para 12-15 años, rechazo con humor de retos peligrosos, respuesta cálida y sugerencia de hablar con un adulto de confianza si el usuario menciona que se siente mal.
4. **Base de conocimiento:** los datos verificados de cada una de las 10 preguntas (Samhain, nabos y calabazas, *souling* y *guising*, Mary Shelley, Día de Muertos, etc.). Se incluyen en el prompt para que el modelo no invente información.
5. **Instrucción de uso:** responder con esos datos, en su estilo, de forma resumida; para otros temas de Halloween usar conocimiento general con las mismas reglas.

> Idea clave: en lugar de programar reglas de ortografía, se aprovecha que el modelo de lenguaje ya entiende texto mal escrito y solo se le indica cómo comportarse.

### Paso 3. Obtener la clave gratuita de Gemini

1. Entrar a <https://aistudio.google.com/apikey> con una cuenta de Google.
2. Pulsar **Create API key** y copiar la clave.
3. Guardarla como secreto (nunca en el código): variable de entorno `GEMINI_API_KEY` o archivo `.streamlit/secrets.toml`.

### Paso 4. Primer prototipo con Tkinter

Se hizo una primera versión de escritorio con **Tkinter** (viene incluido con Python):

- Ventana con colores de Halloween, botones de preguntas rápidas y área de chat con scroll.
- La llamada a la API corre en un **hilo aparte** (`threading`) y se comunica con la interfaz mediante una **cola** (`queue`), para que la ventana no se congele mientras Gemini responde.
- Sirvió para validar el prompt y la conexión con Gemini.

Limitación: para compartirlo, cada persona necesitaba instalar Python, la librería y su propia clave.

### Paso 5. Migrar a Streamlit

Se pasó a **Streamlit** para que cualquiera pueda usar el chatbot desde el navegador con solo un enlace. Qué cambió:

| Tkinter | Streamlit |
|---|---|
| Ventana de escritorio | Página web (también funciona en celular) |
| Clave en cada computadora | Clave en el servidor (`st.secrets`) |
| Hilos y colas a mano | Componentes `st.chat_message` y `st.chat_input` |
| Respuesta completa al final | Respuesta en streaming (`st.write_stream`) |

Piezas principales de `app.py`:

- **Cliente de Gemini persistente:** se crea una sola vez con `@st.cache_resource`.
- **Historial:** se guarda en `st.session_state.mensajes` y se envía completo en cada petición (Gemini no recuerda conversaciones por sí solo). El rol del bot se traduce de `assistant` a `model`, que es el nombre que usa Gemini.
- **Barra lateral:** 10 botones de preguntas rápidas y un botón "Nueva conversación".
- **Entrada unificada:** el texto puede venir del cuadro de chat o de un botón (`st.session_state.pendiente`).
- **Límite por sesión:** `MAX_MENSAJES_POR_SESION`.
- **Tema:** colores en `.streamlit/config.toml` y un poco de CSS en `app.py`.

### Paso 6. Manejo de errores y reintentos

- Los errores técnicos se convierten en mensajes amigables (cuota agotada, clave inválida, modelo retirado, servicio saturado).
- Si Gemini responde **503**, la app espera 2, 4 y 6 segundos y reintenta (hasta `MAX_REINTENTOS`), siempre que aún no haya empezado a llegar la respuesta.

### Paso 7. Proteger la clave y preparar el repositorio

- `.gitignore` incluye `.streamlit/secrets.toml` para no subir la clave.
- `secrets.toml.example` sirve de plantilla sin datos reales.
- `requirements.txt` debe estar en la **raíz** del repositorio.

### Paso 8. Publicar

Se subió el proyecto a GitHub y se desplegó en Streamlit Community Cloud (ver secciones 5 y 6).

---

## 4. Cómo ejecutarlo en tu computadora

1. Instala Python (<https://www.python.org>). En Windows marca **"Add Python to PATH"**.
2. Clona o descarga el repositorio y entra a la carpeta:
   ```bash
   git clone https://github.com/TU_USUARIO/boobot-halloween.git
   cd boobot-halloween
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Copia `.streamlit/secrets.toml.example` como `.streamlit/secrets.toml` y pon tu clave:
   ```toml
   GEMINI_API_KEY = "TU_CLAVE"
   ```
   (Alternativa: define la variable de entorno `GEMINI_API_KEY`.)
5. Ejecuta **desde la carpeta del proyecto**:
   ```bash
   streamlit run app.py
   ```
   Se abre en <http://localhost:8501>. Si `streamlit` no se reconoce, usa `python -m streamlit run app.py`.

---

## 5. Cómo subirlo a GitHub

1. Crea un repositorio vacío en GitHub (sin README ni `.gitignore` automáticos).
2. En la carpeta del proyecto:
   ```bash
   git init
   git add .
   git status
   ```
3. **Revisa `git status`:** no debe aparecer `.streamlit/secrets.toml`. Para confirmarlo:
   ```bash
   git check-ignore -v .streamlit/secrets.toml
   ```
4. Haz el commit y súbelo:
   ```bash
   git commit -m "Chatbot de Halloween con Streamlit"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/boobot-halloween.git
   git push -u origin main
   ```

Si la clave llegara a subirse por error, **revócala** en <https://aistudio.google.com/apikey> y crea una nueva. Borrar el archivo después no basta: queda en el historial de Git.

Para actualizar la app después de cambios: `git add .`, `git commit -m "mensaje"` y `git push`.

---

## 6. Cómo publicarlo en la nube (Streamlit Community Cloud)

1. Entra a <https://share.streamlit.io> con tu cuenta de GitHub.
2. Pulsa **Create app** y elige el repositorio, la rama `main` y el archivo `app.py`.
3. En **Advanced settings > Secrets** pega:
   ```toml
   GEMINI_API_KEY = "TU_CLAVE"
   ```
4. Pulsa **Deploy**. Obtendrás un enlace público.

Notas:

- Cada `git push` redespliega la app automáticamente.
- La clave o los secretos se editan desde **Manage app > Settings > Secrets**.
- Los logs están en **Manage app**.
- Si nadie la usa por un tiempo, la app se "duerme" y tarda unos segundos en despertar.

---

## 7. Configuración y personalización

Todo está al inicio de `app.py`:

| Qué quieres cambiar | Dónde |
|---|---|
| Modelo de Gemini | `MODELO` |
| Mensajes por sesión | `MAX_MENSAJES_POR_SESION` |
| Reintentos ante error 503 | `MAX_REINTENTOS` |
| Botones de preguntas rápidas | `PREGUNTAS_RAPIDAS` |
| Mensaje de bienvenida | `BIENVENIDA` |
| Personalidad y datos del bot | `PROMPT_SISTEMA` |
| Colores del tema | `.streamlit/config.toml` y el bloque CSS de `app.py` |
| Créditos | `st.caption(...)` en la barra lateral |

---

## 8. Problemas que encontramos y cómo se resolvieron

| Error | Causa | Solución |
|---|---|---|
| `Cannot send a request, as the client has been closed` (Tkinter) | El cliente de Gemini era una variable local y Python lo eliminaba al terminar la función | Guardarlo en `self.cliente` (en Streamlit, `@st.cache_resource`) |
| `404 NOT_FOUND ... model is no longer available` | Google retiró el modelo anterior para cuentas nuevas | Cambiar la constante `MODELO` por el modelo vigente |
| `503 UNAVAILABLE ... high demand` | Saturación temporal de los servidores de Gemini | Reintentos automáticos con espera y mensaje amigable |
| `429 RESOURCE_EXHAUSTED` | Se agotó la cuota gratuita (por minuto o diaria) | Esperar, limitar mensajes por sesión; ver sección 9 |
| "No encontré la clave de API" en Streamlit | No se encontraba `.streamlit/secrets.toml` | Ejecutar `streamlit run app.py` desde la carpeta del proyecto, nombre exacto `secrets.toml`, y reiniciar la app |
| `secrets.toml` aparecía en `git status` | `.gitignore` y `requirements.txt` estaban dentro de `.streamlit/` | Moverlos a la raíz y ejecutar `git rm --cached .streamlit/secrets.toml` |
| Avisos `LF will be replaced by CRLF` | Diferencia de saltos de línea en Windows | Son normales; se pueden ignorar |

---

## 9. Límites, privacidad y seguridad

- **Cuota gratuita:** los límites (por minuto y por día) se aplican **por proyecto de Google Cloud**, no por clave. Todos los usuarios de la app comparten la misma cuota. Consulta tu uso real en <https://aistudio.google.com/usage>. El límite diario se reinicia a la medianoche (hora del Pacífico).
- **Privacidad:** en el nivel gratuito de la API, lo que se escribe puede ser revisado por personas y usado por Google para mejorar sus productos. Como los usuarios son menores de edad, **se recomienda indicarles que no escriban datos personales** y avisar a la persona responsable (docente, familia o institución).
- **Seguridad del contenido:** el prompt limita las respuestas a contenido apto para 12-15 años. Aun así, ningún filtro es perfecto: conviene supervisar el uso.
- **Secretos:** nunca subas tu clave a GitHub. Si se filtra, revócala de inmediato.

---

## Créditos

Creado por **Martínez García Roberto** y **Garrido Vazques Fernanda**.
