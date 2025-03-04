import streamlit as st
import openai  # Para la API de GPT

# Configuración de la página
st.set_page_config(page_title="ESP32-S3 GPIO Manager", page_icon="🔌", layout="wide")

# Título de la aplicación
st.title("Sistema generativo del femtoPLC del ESP32-S3")

# Sidebar para configuración
with st.sidebar:
    st.header("Configuración de la API de GPT")
    api_key = st.text_input("Ingresa tu API Key de OpenAI", type="password")
    if api_key:
        openai.api_key = api_key
        st.success("✅ API Key configurada correctamente.")

# Inicializar el estado de la sesión para almacenar comentarios y pines
if "comentarios" not in st.session_state:
    st.session_state.comentarios = {}
if "input_pins" not in st.session_state:
    st.session_state.input_pins = []
if "output_pins" not in st.session_state:
    st.session_state.output_pins = []

# Lista de pines disponibles
pines_disponibles = [f"GPIO{i}" for i in range(40)]

# Función para actualizar la selección de pines
def actualizar_pines():
    # Si un pin se selecciona como entrada, se elimina de las salidas y viceversa
    for pin in st.session_state.input_pins:
        if pin in st.session_state.output_pins:
            st.session_state.output_pins.remove(pin)
    for pin in st.session_state.output_pins:
        if pin in st.session_state.input_pins:
            st.session_state.input_pins.remove(pin)

# Selección de pines de entrada
with st.container():
    st.subheader("Entradas")
    input_pins = st.multiselect(
        "Selecciona los pines de entrada",
        options=[pin for pin in pines_disponibles if pin not in st.session_state.output_pins],  # Excluir pines ya seleccionados como salidas
        default=st.session_state.input_pins,
        key="input_pins_selector"  # Usamos una clave única para el widget
    )

# Selección de pines de salida
with st.container():
    st.subheader("Salidas")
    output_pins = st.multiselect(
        "Selecciona los pines de salida",
        options=[pin for pin in pines_disponibles if pin not in st.session_state.input_pins],  # Excluir pines ya seleccionados como entradas
        default=st.session_state.output_pins,
        key="output_pins_selector"  # Usamos una clave única para el widget
    )

# Actualizar el estado de los pines después de la selección
if "input_pins_selector" in st.session_state:
    st.session_state.input_pins = st.session_state.input_pins_selector
if "output_pins_selector" in st.session_state:
    st.session_state.output_pins = st.session_state.output_pins_selector

# Aplicar la lógica de exclusividad
actualizar_pines()

# Mostrar la configuración seleccionada
st.write("### Configuración GPIO actual")
st.json({
    "Entradas": st.session_state.input_pins,
    "Salidas": st.session_state.output_pins
})

# Mostrar entradas y salidas en filas con comentarios
st.header("Comentarios para cada GPIO")

# Función para mostrar filas con comentarios
def mostrar_filas_con_comentarios(pines, tipo):
    for pin in pines:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.write(f"**{pin}** ({tipo})")
            with col2:
                comentario = st.text_input(
                    f"Comentario para {pin}",
                    value=st.session_state.comentarios.get(pin, ""),
                    key=f"comentario_{pin}"
                )
                st.session_state.comentarios[pin] = comentario

# Mostrar entradas con comentarios
if st.session_state.input_pins:
    st.subheader("Entradas")
    mostrar_filas_con_comentarios(st.session_state.input_pins, "Entrada")

# Mostrar salidas con comentarios
if st.session_state.output_pins:
    st.subheader("Salidas")
    mostrar_filas_con_comentarios(st.session_state.output_pins, "Salida")

# Mostrar la imagen en la segunda columna (Manejo de error si no existe)
try:
    st.image("JPG ESP.jpg", caption="Estado en vivo", use_column_width=True)
except:
    st.warning("⚠️ Imagen no encontrada: JPG ESP.jpg")

# Generación de código con GPT
st.header("Generar código asistido")
prompt = st.text_area(
    "Describe lo que quieres que haga el código en función de los Pines que deseas usar",
    height=100,
    placeholder="Ejemplo: 'Haz parpadear un LED conectado al GPIO18 cada segundo.'"
)

# Generación de código con OpenAI GPT
if st.button("Generar código con GPT"):
    if api_key:
        try:
            # Llamada a la API de GPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Escribe un código en MicroPython para el ESP32-S3 que haga lo siguiente: {prompt}. Considera los siguientes comentarios: {st.session_state.comentarios}"}],
                max_tokens=300,
                temperature=0.7
            )
            codigo_generado = response["choices"][0]["message"]["content"].strip()
            st.session_state.codigo_micropython = codigo_generado  # Guardar el código generado en el estado
            st.success("✅ Código generado con GPT:")
            st.code(codigo_generado, language="python")
        except Exception as e:
            st.error(f"❌ Error al generar el código: {e}")
    else:
        st.warning("⚠️ Ingresa una API Key válida para usar GPT.")


# Ventana para ingresar código en MicroPython
st.header("Editor de MicroPython")
codigo_micropython = st.text_area(
    "Ingresa tu código en MicroPython aquí",
    height=300,
    placeholder="from machine import Pin\nimport time\n\n# Escribe tu código aquí...",
    key="codigo_micropython"
)

# Botón para convertir de MicroPython a ST
if st.button("Convertir de MicroPython a ST"):
    if api_key:
        try:
            # Llamada a la API de GPT para convertir el código
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Convierte el siguiente código de MicroPython a ST (lenguaje estructurado): {st.session_state.codigo_micropython}. Considera los siguientes comentarios: {st.session_state.comentarios}"}],
                max_tokens=300,
                temperature=0.7
            )
            codigo_st_generado = response["choices"][0]["message"]["content"].strip()
            st.session_state.codigo_stl = codigo_st_generado  # Guardar el código generado en el estado
            st.success("✅ Código ST generado:")
            st.code(codigo_st_generado, language="plaintext")
        except Exception as e:
            st.error(f"❌ Error al convertir el código: {e}")
    else:
        st.warning("⚠️ Ingresa una API Key válida para usar GPT.")
 
# Ventana para ingresar código en STL
st.header("Editor de ST para enviar a un sistema industrial")
codigo_stl = st.text_area(
    "Ingresa tu código en STL aquí",
    height=300,
    placeholder="// Código STL aquí...",
    key="codigo_stl"
)

# Botón para convertir de ST a MicroPython
if st.button("Convertir de ST a MicroPython"):
    if api_key:
        try:
            # Llamada a la API de GPT para convertir el código
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Convierte el siguiente código de ST (lenguaje estructurado) a MicroPython: {st.session_state.codigo_stl}. Considera los siguientes comentarios: {st.session_state.comentarios}"}],
                max_tokens=300,
                temperature=0.7
            )
            codigo_micropython_generado = response["choices"][0]["message"]["content"].strip()
            st.session_state.codigo_micropython = codigo_micropython_generado  # Guardar el código generado en el estado
            st.success("✅ Código MicroPython generado:")
            st.code(codigo_micropython_generado, language="python")
        except Exception as e:
            st.error(f"❌ Error al convertir el código: {e}")
    else:
        st.warning("⚠️ Ingresa una API Key válida para usar GPT.")

# Botón para ejecutar el código (simulación)
if st.button("Ejecutar código (Simulación)"):
    st.info("⚡ Ejecutando código... (esto es una simulación)")
    st.code(codigo_micropython, language="python")




