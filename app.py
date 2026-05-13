import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
import time

# CONFIGURACIÓN DE PÁGINA - OPTIMIZADA PARA MÓVIL
st.set_page_config(
    page_title="Jared-Lógica",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# CSS SIMPLIFICADO
css_mobile = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    .stApp {max-width: 100%; padding: 0;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    
    .stApp {
        background: linear-gradient(135deg, #0a0a2a 0%, #1a1a3a 100%);
    }
    
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #2E7D32, #1B5E20);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid #FFD700;
    }
    
    .main-header h1 {
        color: #FFD700;
        margin: 0;
        font-size: 1.8em;
    }
    
    .main-header p {
        color: #E8F5E9;
        margin: 5px 0 0;
        font-size: 0.8em;
    }
    
    [data-testid="stChatMessage"] {
        background-color: rgba(25, 25, 45, 0.95);
        border-radius: 20px;
        padding: 12px;
        margin: 8px 0;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    
    .stButton button {
        background: linear-gradient(135deg, #2E7D32, #1B5E20);
        color: #FFD700;
        font-weight: bold;
        border-radius: 25px;
        border: none;
        padding: 8px 12px;
        font-size: 0.85em;
    }
    
    [data-testid="stChatInput"] input {
        border-radius: 25px;
        border: 2px solid #2E7D32;
        background-color: rgba(25, 25, 45, 0.95);
        color: white;
        padding: 10px;
    }
    
    .block-container {
        padding: 0.5rem 1rem !important;
    }
    
    .stMarkdown {
        color: #f0f0f0;
    }
    
    /* Advertencia de tokens */
    .token-warning {
        font-size: 0.7em;
        text-align: center;
        color: #FFD700;
        margin-top: 10px;
    }
</style>
"""
st.markdown(css_mobile, unsafe_allow_html=True)

# ENCABEZADO
st.markdown("""
<div class="main-header">
    <h1>📐 Jared-Lógica</h1>
    <p>✨ Planeación de Lógica · Respuestas breves y concretas ✨</p>
</div>
""", unsafe_allow_html=True)

# PROMPT DEL SISTEMA CON RESTRICCIÓN DE TOKENS
SYSTEM_PROMPT = """Eres JARED-LÓGICA, experto en planeación de Lógica. REGLA IMPORTANTE: Tus respuestas NO deben superar los 3000 tokens (aproximadamente 800 palabras o 5-6 párrafos).

RESPONDE DE FORMA CONCRETA Y BREVE:

- Para planeación de unidad: Máximo 3 sesiones por respuesta. Si necesitas más, el usuario te pedirá continuar.
- Para objetivos: Máximo 5 objetivos por tipo.
- Para actividades: Describe 2-3 actividades principales, no más.
- Para rúbricas: Máximo 4 criterios de evaluación.

PROGRAMA DEL CURSO (RESUMIDO):

Unidades y horas:
- U1: El horizonte de la lógica (10h)
- U2: Las rutas del argumento (20h) 
- U3: Lógica deductiva (15h)
- U4: Armando y desarmando argumentos (15h)
- U5: Falacias y estratagemas (10h)
- U6: La lógica en acción (20h)

Objetivo General: Aplicar habilidades lógicas y pensamiento crítico en la toma de decisiones.

Contenidos clave por unidad:
U1: Funciones del lenguaje, tipos de lógica
U2: Elementos del argumento, tipos de argumentos
U3: Formalización, tablas de verdad, reglas de inferencia
U4: Reconstrucción de argumentos, escrito argumentativo
U5: Falacias informales
U6: Esquemas argumentativos (Weston, Toulmin), debate

ESTRUCTURA DE SESIÓN (Inicio-Desarrollo-Cierre):
- Inicio (15%): activación
- Desarrollo (70%): actividad centrada en estudiante
- Cierre (15%): síntesis

¡RESPUESTAS SIEMPRE BREVES Y CONCRETAS!"""

# CONTROL DE TOKENS
class TokenControl:
    def __init__(self):
        self.tokens_used = 0
        self.last_reset = time.time()
    
    def can_send(self, estimated_tokens):
        # Reiniciar cada minuto
        if time.time() - self.last_reset > 60:
            self.tokens_used = 0
            self.last_reset = time.time()
        
        if self.tokens_used + estimated_tokens > 3000:
            return False
        return True
    
    def add_tokens(self, tokens):
        self.tokens_used += tokens
    
    def estimate_tokens(self, text):
        # Aproximación: 1 token ≈ 4 caracteres en español
        return len(text) // 4

token_control = TokenControl()

# CONEXIÓN CON GROQ
try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["GROQ_API_KEY"]
    )
except KeyError:
    st.error("📐 Error: Configura GROQ_API_KEY en Secrets")
    st.stop()
except Exception as e:
    st.error(f"Error de conexión: {str(e)}")
    st.stop()

# FUNCIÓN DE VOZ
def speak_js(text):
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")[:300]
    js_code = f"""
    <script>
        var text = "{clean_text}";
        function hablar() {{
            var utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'es-MX';
            utterance.rate = 0.9;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        }}
        setTimeout(hablar, 100);
    </script>
    """
    components.html(js_code, height=0)

# HISTORIAL
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# MENSAJE DE BIENVENIDA (BREVE)
if not st.session_state.messages:
    bienvenida = """📐 **Jared-Lógica** - Respuestas breves y concretas.

**¿Qué necesitas?** 
Ej: "Unidad 2", "Objetivos U3", "Actividad falacias", "Sesión 2h U1", "Rúbrica debate"

Recuerda: Respuestas cortas. Para más detalles, pide "continuar"."""
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})
    st.session_state.last_response = bienvenida

# MOSTRAR HISTORIAL
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ADVERTENCIA DE TOKENS
st.markdown('<p class="token-warning">⚡ Respuestas limitadas a ~3000 tokens/minuto</p>', unsafe_allow_html=True)

# FUNCIÓN PARA PROCESAR RESPUESTA CON CONTROL DE TOKENS
def procesar_respuesta(user_input):
    global token_control
    
    # Estimar tokens de la consulta
    input_tokens = token_control.estimate_tokens(user_input)
    
    if not token_control.can_send(input_tokens + 500):
        st.warning("⏳ Límite de tokens por minuto. Por favor espera unos segundos antes de enviar otra solicitud.")
        return
    
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        with st.spinner("📐 Planear..."):
            try:
                # Agregar instrucción de brevedad al mensaje del usuario
                user_input_breve = f"[RESPUESTA BREVE] {user_input}"
                
                mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages[-10:]
                # Reemplazar el último mensaje del usuario con la versión breve
                mensajes_api[-1] = {"role": "user", "content": user_input_breve}
                
                stream = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=mensajes_api,
                    stream=True,
                    temperature=0.5,  # Temperatura más baja para respuestas más directas
                    max_tokens=800,   # Límite de tokens por respuesta
                )
                response = st.write_stream(stream)
                
                # Contabilizar tokens de la respuesta
                response_tokens = token_control.estimate_tokens(response)
                token_control.add_tokens(input_tokens + response_tokens)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.last_response = response
                
                # Mostrar advertencia si se acerca al límite
                if token_control.tokens_used > 2500:
                    st.info("📊 Límite de tokens: ~" + str(3000 - token_control.tokens_used) + " tokens restantes este minuto")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

# INPUT DE TEXTO
if prompt := st.chat_input("✏️ ¿Qué necesitas planear? (Sé específico para respuesta breve)"):
    procesar_respuesta(prompt)

# BOTONES SENCILLOS
col1, col2 = st.columns(2)
with col1:
    if st.button("🔊 Escuchar", use_container_width=True):
        if st.session_state.last_response:
            speak_js(st.session_state.last_response[:300])
with col2:
    if st.button("🔄 Nueva", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_response = ""
        token_control.tokens_used = 0
        st.rerun()
