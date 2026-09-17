"""
============================================================
 EL MUNDO ESTADÍSTICO — Simulación interactiva de distribuciones
============================================================

Versión 2: con "login" simple (solo nombre, sin verificación real),
selector de localidades de Bogotá (cada una lleva a una distribución
distinta), estilo visual neón, y sliders de MEDIA y VARIANZA directos
(en vez de los parámetros técnicos de cada distribución).

CÓMO FUNCIONA STREAMLIT (recordatorio):
Cada vez que mueves un control, Streamlit re-ejecuta TODO el script
de arriba a abajo. Usamos "st.session_state" para que la app RECUERDE
cosas entre esas re-ejecuciones (como el nombre que escribiste, o qué
localidad elegiste) -- sin session_state, la app "olvidaría" todo
cada vez que tocas cualquier control.
"""

import streamlit as st
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# PASO 1: Configuración general de la página
# ------------------------------------------------------------
st.set_page_config(
    page_title="El Mundo Estadístico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# PASO 2: Estilo visual -- plano, con un color de acento distinto
# por CATEGORÍA (una distribución = un color), sin efectos de brillo,
# y con íconos reales (librería Tabler) en vez de emojis.
# ------------------------------------------------------------

# Colores de acento por distribución (fondo oscuro + texto claro a
# juego, mismo patrón para las 4 -- así cada categoría se distingue
# de un vistazo, sin que "todo brille del mismo neón").
COLOR_POR_DISTRIBUCION = {
    "Chi-cuadrado": {"bg": "#3C3489", "text": "#CECBF6", "border": "#7F77DD"},
    "Beta":         {"bg": "#085041", "text": "#9FE1CB", "border": "#1D9E75"},
    "Gamma":        {"bg": "#712B13", "text": "#F5C4B3", "border": "#D85A30"},
    "Exponencial":  {"bg": "#72243E", "text": "#F4C0D1", "border": "#D4537E"},
}

ESTILO_BASE = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">
<style>
.stApp {
    background-color: #14141a;
    color: #e8e8ea;
}
h1, h2, h3 {
    font-weight: 500;
}
div.stButton > button {
    background-color: #1e1e26;
    color: #e8e8ea;
    border: 1px solid #3a3a45;
    border-radius: 8px;
    font-weight: 500;
}
div.stButton > button:hover {
    border-color: #7a7a88;
}
[data-testid="stMetric"] {
    background-color: #1e1e26;
    border-radius: 10px;
    padding: 10px;
}
</style>
"""
st.markdown(ESTILO_BASE, unsafe_allow_html=True)

# ------------------------------------------------------------
# PASO 3: "Login" simple -- solo pide el nombre, sin verificar nada
# ------------------------------------------------------------
if "nombre" not in st.session_state:
    st.session_state.nombre = None

if st.session_state.nombre is None:
    st.title("El Mundo Estadístico")
    st.write("Ingresa tu nombre para entrar:")

    nombre_input = st.text_input("Nombre", label_visibility="collapsed",
                                   placeholder="Escribe tu nombre aquí...")

    if st.button("Entrar ✨"):
        if nombre_input.strip() != "":
            st.session_state.nombre = nombre_input.strip()
            st.rerun()
        else:
            st.warning("Escribe algo antes de entrar 🙂")

    st.stop()

# ------------------------------------------------------------
# PASO 4: Saludo personalizado (ya con el nombre guardado)
# ------------------------------------------------------------
st.title(f"Hola, {st.session_state.nombre}")
st.caption("El Mundo Estadístico")
st.write(
    "Elige una localidad de Bogotá para explorar su distribución de "
    "probabilidad asociada, y ajusta la media y la varianza para ver "
    "cómo cambia la simulación."
)

if st.sidebar.button("Salir"):
    st.session_state.nombre = None
    st.rerun()

# ------------------------------------------------------------
# PASO 5: Selector de localidades
# ------------------------------------------------------------
LOCALIDADES = {
    "Usaquén":       {"distribucion": "Chi-cuadrado", "icono": "ti-mountain"},
    "Suba":          {"distribucion": "Chi-cuadrado", "icono": "ti-trees"},
    "Chapinero":     {"distribucion": "Beta", "icono": "ti-building-skyscraper"},
    "Teusaquillo":   {"distribucion": "Beta", "icono": "ti-school"},
    "Kennedy":       {"distribucion": "Gamma", "icono": "ti-ball-football"},
    "Fontibón":      {"distribucion": "Gamma", "icono": "ti-plane"},
    "La Candelaria": {"distribucion": "Exponencial", "icono": "ti-building-monument"},
    "Santa Fe":      {"distribucion": "Exponencial", "icono": "ti-ticket"},
}

if "localidad" not in st.session_state:
    st.session_state.localidad = "Chapinero"

st.subheader("Elige una localidad")

nombres_localidades = list(LOCALIDADES.keys())
cols = st.columns(4)
for i, loc in enumerate(nombres_localidades):
    info = LOCALIDADES[loc]
    color = COLOR_POR_DISTRIBUCION[info["distribucion"]]
    with cols[i % 4]:
        st.markdown(
            f"""
            <div style="background-color:{color['bg']}; color:{color['text']};
                        border-radius:10px; padding:10px 12px; margin-bottom:4px;">
                <i class="ti {info['icono']}" style="font-size:18px;"></i><br>
                <span style="font-size:14px; font-weight:500;">{loc}</span><br>
                <span style="font-size:12px; opacity:0.85;">{info['distribucion']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Elegir", key=f"loc_{loc}"):
            st.session_state.localidad = loc

localidad_activa = st.session_state.localidad
distribucion = LOCALIDADES[localidad_activa]["distribucion"]

color_activo = COLOR_POR_DISTRIBUCION[distribucion]
st.markdown(
    f"""
    <div style="background-color:#1e1e26; border-left:3px solid {color_activo['border']};
                border-radius:6px; padding:10px 14px; margin:12px 0;">
        Estás en <strong>{localidad_activa}</strong> — distribución {distribucion}
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# PASO 6: Controles de media y varianza (según la distribución)
# ------------------------------------------------------------
st.sidebar.header("Ajusta la simulación")

n = st.sidebar.number_input("Tamaño de muestra (n)", min_value=2,
                              max_value=1_000_000, value=200, step=10)

st.sidebar.markdown("---")
st.sidebar.subheader(f"Distribución: {distribucion}")

if distribucion == "Chi-cuadrado":
    media_deseada = st.sidebar.slider("Media deseada (μ)", min_value=1.0,
                                        max_value=50.0, value=5.0, step=0.5)
    st.sidebar.caption(
        "La Chi-cuadrada solo tiene 1 parámetro (grados de libertad), "
        "así que su varianza queda fija: σ² = 2μ (no se puede elegir aparte)."
    )
    df = media_deseada
    media_teorica = df
    varianza_teorica = 2 * df
    muestra = np.random.chisquare(df=df, size=n)
    x_curva = np.linspace(0, muestra.max(), 300)
    y_curva = stats.chi2.pdf(x_curva, df=df)
    parametros_info = f"Grados de libertad calculados: df = {df:.2f}"

elif distribucion == "Exponencial":
    media_deseada = st.sidebar.slider("Media deseada (μ)", min_value=0.5,
                                        max_value=20.0, value=2.0, step=0.5)
    st.sidebar.caption(
        "La Exponencial solo tiene 1 parámetro (λ), así que su varianza "
        "queda fija: σ² = μ² (no se puede elegir aparte)."
    )
    lam = 1 / media_deseada
    media_teorica = media_deseada
    varianza_teorica = media_deseada ** 2
    muestra = np.random.exponential(scale=media_deseada, size=n)
    x_curva = np.linspace(0, muestra.max(), 300)
    y_curva = stats.expon.pdf(x_curva, scale=media_deseada)
    parametros_info = f"λ calculada: {lam:.4f}"

elif distribucion == "Gamma":
    media_deseada = st.sidebar.slider("Media deseada (μ)", min_value=0.5,
                                        max_value=20.0, value=4.0, step=0.5)
    varianza_deseada = st.sidebar.slider("Varianza deseada (σ²)", min_value=0.1,
                                           max_value=50.0, value=4.0, step=0.1)

    escala = varianza_deseada / media_deseada
    forma = media_deseada / escala

    media_teorica = forma * escala
    varianza_teorica = forma * escala ** 2
    muestra = np.random.gamma(shape=forma, scale=escala, size=n)
    x_curva = np.linspace(0, muestra.max(), 300)
    y_curva = stats.gamma.pdf(x_curva, a=forma, scale=escala)
    parametros_info = f"Forma (k) = {forma:.3f}  |  Escala (θ) = {escala:.3f}"

elif distribucion == "Beta":
    media_deseada = st.sidebar.slider("Media deseada (μ)", min_value=0.05,
                                        max_value=0.95, value=0.5, step=0.01)

    techo_varianza = media_deseada * (1 - media_deseada)
    varianza_deseada = st.sidebar.slider(
        "Varianza deseada (σ²)", min_value=0.001,
        max_value=round(techo_varianza * 0.98, 4),
        value=round(techo_varianza * 0.3, 4), step=0.001,
    )
    st.sidebar.caption(
        f"Para μ={media_deseada:.2f}, la varianza máxima posible es "
        f"σ²<{techo_varianza:.4f} (por eso el slider no deja pasar de ahí)."
    )

    nu = media_deseada * (1 - media_deseada) / varianza_deseada - 1
    alpha = media_deseada * nu
    beta_param = (1 - media_deseada) * nu

    media_teorica = alpha / (alpha + beta_param)
    varianza_teorica = (alpha * beta_param) / (
        (alpha + beta_param) ** 2 * (alpha + beta_param + 1)
    )
    muestra = np.random.beta(a=alpha, b=beta_param, size=n)
    x_curva = np.linspace(0, 1, 300)
    y_curva = stats.beta.pdf(x_curva, a=alpha, b=beta_param)
    parametros_info = f"α = {alpha:.3f}  |  β = {beta_param:.3f}"

st.sidebar.markdown("---")
st.sidebar.caption(f"🔧 {parametros_info}")

# ------------------------------------------------------------
# PASO 7: Media y varianza MUESTRALES
# ------------------------------------------------------------
media_muestral = muestra.mean()
varianza_muestral = muestra.var(ddof=1)

st.sidebar.markdown("---")
st.sidebar.button("Generar nueva muestra")

# ------------------------------------------------------------
# PASO 8: Mostrar resultados numéricos
# ------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Valores TEÓRICOS")
    st.metric("Media teórica", f"{media_teorica:.4f}")
    st.metric("Varianza teórica", f"{varianza_teorica:.4f}")

with col2:
    st.subheader(f"Valores MUESTRALES (n = {n})")
    st.metric("Media muestral", f"{media_muestral:.4f}",
              delta=f"{media_muestral - media_teorica:+.4f} vs. teórica")
    st.metric("Varianza muestral", f"{varianza_muestral:.4f}",
              delta=f"{varianza_muestral - varianza_teorica:+.4f} vs. teórica")

# ------------------------------------------------------------
# PASO 9: Histograma
# ------------------------------------------------------------
st.subheader("Histograma de la muestra simulada")

color_hist = color_activo["border"]

plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(9, 4.5))
fig.patch.set_facecolor("#14141a")
ax.set_facecolor("#14141a")

ax.hist(muestra, bins=30, density=True, alpha=0.75,
        color=color_hist, edgecolor="#14141a", label="Muestra simulada")
ax.plot(x_curva, y_curva, color="#e8e8ea", linewidth=2,
        label="Densidad teórica")
ax.axvline(media_teorica, color="#e8e8ea", linestyle="--", linewidth=1,
           label=f"Media teórica = {media_teorica:.3f}")

ax.set_xlabel("Valor", color="#e8e8ea")
ax.set_ylabel("Densidad", color="#e8e8ea")
ax.set_title(f"{distribucion} — {localidad_activa} — n = {n}", color="#e8e8ea")
ax.legend(facecolor="#1e1e26", edgecolor="#3a3a45", labelcolor="#e8e8ea")
ax.tick_params(colors="#e8e8ea")

st.pyplot(fig)

st.markdown("---")
st.caption("Trabajo de Probabilidad y Estadística — El Mundo Estadístico")