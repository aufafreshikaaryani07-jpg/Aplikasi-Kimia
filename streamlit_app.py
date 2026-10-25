import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import math
import os

# ============================================================
# SPECTRA LAB — SHIMADZU UV-1700 PHARMASPEC
# Smart UV-Vis Analytical System
# ============================================================

st.set_page_config(
    page_title="SPECTRA LAB | UV-1700",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(0,170,255,.08), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(0,255,180,.06), transparent 30%),
        #07111f;
    color: #f4f7fb;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#07111f,#0b1728);
    border-right: 1px solid rgba(255,255,255,.08);
}

section[data-testid="stSidebar"] * {
    color: #eaf2ff !important;
}

.hero {
    padding: 30px;
    border-radius: 24px;
    background:
        linear-gradient(135deg,rgba(0,150,255,.22),rgba(0,255,190,.08)),
        linear-gradient(180deg,#0c1c30,#091421);
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 20px 60px rgba(0,0,0,.25);
    margin-bottom: 22px;
}

.hero h1 {
    font-size: 38px;
    margin: 0;
    font-weight: 800;
}

.hero p {
    color: #a9bdd3;
    margin-top: 10px;
}

.card {
    background: rgba(13,29,48,.82);
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 12px 35px rgba(0,0,0,.18);
}

.card h3 {
    margin-top: 0;
}

.metric {
    background: linear-gradient(135deg,#102943,#0c1d31);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 18px;
    padding: 18px;
    text-align: center;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
}

.metric-label {
    color: #8ea8c1;
    font-size: 13px;
}

.chip {
    display: inline-block;
    padding: 7px 12px;
    margin: 3px;
    border-radius: 999px;
    background: rgba(0,180,255,.12);
    border: 1px solid rgba(0,180,255,.25);
    color: #8edcff;
    font-size: 12px;
}

.step {
    padding: 18px;
    border-radius: 16px;
    background: linear-gradient(135deg,#0c2138,#0b1727);
    border: 1px solid rgba(255,255,255,.08);
    margin-bottom: 12px;
}

.step-number {
    font-size: 13px;
    color: #56d6ff;
    font-weight: 700;
}

.step-title {
    font-size: 18px;
    font-weight: 700;
    margin: 5px 0;
}

.step-text {
    color: #9eb4c9;
    line-height: 1.6;
}

.warning {
    padding: 15px 18px;
    border-radius: 15px;
    background: rgba(255,180,0,.09);
    border: 1px solid rgba(255,180,0,.25);
    color: #ffd98a;
}

.info {
    padding: 15px 18px;
    border-radius: 15px;
    background: rgba(0,180,255,.08);
    border: 1px solid rgba(0,180,255,.2);
    color: #a9ddff;
}

.success {
    padding: 15px 18px;
    border-radius: 15px;
    background: rgba(0,220,150,.08);
    border: 1px solid rgba(0,220,150,.22);
    color: #9ff4d7;
}

.photo-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
}

.small {
    color: #8ea8c1;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA FOTO
# ============================================================

PHOTO_DIR = "assets_uv1700"

PHOTO_MAP = {
    "Depan": "04_depan.jpg",
    "Belakang": "02_belakang_power.jpg",
    "Sisi belakang": "01_sisi_belakang.jpg",
    "Atas / Panel": "07_atas_panel.jpg",
    "Kompartemen sampel 1": "03_kompartemen_1.jpg",
    "Kompartemen sampel 2": "05_kompartemen_2.jpg",
    "Kompartemen sampel 3": "06_kompartemen_3.jpg",
    "Konteks laboratorium": "08_konteks_lab.jpg"
}

PHOTO_INFO = {
    "Depan": "Tampilan bagian depan UV-1700 dengan layar, keypad, panel kontrol, dan pintu kompartemen sampel.",
    "Belakang": "Bagian belakang instrumen yang memperlihatkan area koneksi dan catu daya.",
    "Sisi belakang": "Sudut belakang/samping instrumen untuk melihat konstruksi casing dan ventilasi.",
    "Atas / Panel": "Panel atas dan area kontrol instrumen.",
    "Kompartemen sampel 1": "Kompartemen sampel dalam kondisi terbuka.",
    "Kompartemen sampel 2": "Sudut berbeda dari area dudukan kuvet.",
    "Kompartemen sampel 3": "Detail bagian dalam kompartemen sampel.",
    "Konteks laboratorium": "Instrumen pada lingkungan laboratorium."
}


def get_photo(name):
    path = os.path.join(PHOTO_DIR, PHOTO_MAP[name])

    if os.path.exists(path):
        return Image.open(path)

    return None


# ============================================================
# SESSION STATE
# ============================================================

if "power" not in st.session_state:
    st.session_state.power = False

if "wavelength" not in st.session_state:
    st.session_state.wavelength = 500

if "mode" not in st.session_state:
    st.session_state.mode = "Photometric"

if "baseline" not in st.session_state:
    st.session_state.baseline = False

if "sample" not in st.session_state:
    st.session_state.sample = False

if "absorbance" not in st.session_state:
    st.session_state.absorbance = 0.000

if "measurements" not in st.session_state:
    st.session_state.measurements = []


# ============================================================
# FUNGSI SIMULASI
# ============================================================

def simulated_absorbance(wavelength, sample=False):

    if not sample:
        return 0.000

    peaks = [
        (275, 0.35, 18),
        (420, 0.65, 30),
        (525, 1.05, 45),
        (650, 0.45, 55)
    ]

    value = 0.02

    for center, height, width in peaks:
        value += height * np.exp(
            -((wavelength-center)**2)/(2*width**2)
        )

    noise = np.random.normal(0, 0.004)

    return max(0, float(value + noise))


def generate_spectrum():

    wavelength = np.linspace(190, 1100, 500)

    absorbance = (
        0.04
        + 0.35*np.exp(-((wavelength-275)**2)/(2*20**2))
        + 1.00*np.exp(-((wavelength-520)**2)/(2*48**2))
        + 0.45*np.exp(-((wavelength-650)**2)/(2*60**2))
    )

    absorbance += np.random.normal(0, 0.005, len(wavelength))

    return wavelength, absorbance


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("""
<div style="text-align:center;padding:10px;">
<h2>🔬 SPECTRA LAB</h2>
<p style="color:#8ea8c1;">UV-1700 Analytical System</p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "MENU",
    [
        "🏠 Dashboard",
        "📷 Foto Nyata UV-1700",
        "🧭 Eksplorasi Instrumen",
        "⚙️ Pengoperasian",
        "🎛️ Panel Virtual",
        "📈 Spectrum Scan",
        "📊 Photometric",
        "🧪 Kinetics",
        "📋 Data Pengukuran",
        "📚 Materi UV-Vis"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown("""
<div class="small">
<b>Instrumen:</b><br>
Shimadzu UV-1700 PharmaSpec<br><br>
<b>Status:</b> Simulator edukasi<br>
<b>Rentang:</b> 190–1100 nm<br>
<b>Sumber:</b> Foto instrumen pengguna
</div>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

def header():

    st.markdown("""
    <div class="hero">
        <div class="chip">UV-VIS</div>
        <div class="chip">PHOTOMETRY</div>
        <div class="chip">SPECTRUM</div>
        <h1>SPECTRA LAB</h1>
        <p>
        Smart laboratory simulator berbasis Shimadzu UV-1700 PharmaSpec.
        Eksplorasi instrumen, pengoperasian, pengukuran, dan analisis data.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# DASHBOARD
# ============================================================

def page_dashboard():

    header()

    st.markdown("## Selamat Datang 👋")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="metric">
        <div class="metric-value">190–1100</div>
        <div class="metric-label">Rentang wavelength (nm)</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="metric">
        <div class="metric-value">UV-Vis</div>
        <div class="metric-label">Jenis instrumen</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        status = "ON" if st.session_state.power else "OFF"

        st.markdown(f"""
        <div class="metric">
        <div class="metric-value">{status}</div>
        <div class="metric-label">Power instrumen</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric">
        <div class="metric-value">{st.session_state.absorbance:.3f}</div>
        <div class="metric-label">Absorbansi simulasi</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    col1, col2 = st.columns([1.2, 1])

    with col1:

        st.markdown("""
        <div class="card">
        <h3>🔬 Tentang UV-1700</h3>

        <p>
        Shimadzu UV-1700 PharmaSpec merupakan instrumen spektrofotometer
        UV-Vis yang digunakan untuk pengukuran absorbansi dan transmitansi
        sampel pada berbagai panjang gelombang.
        </p>

        <span class="chip">Deuterium Lamp</span>
        <span class="chip">Tungsten Lamp</span>
        <span class="chip">Monochromator</span>
        <span class="chip">Detector</span>
        <span class="chip">Sample Compartment</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        img = get_photo("Depan")

        if img:
            st.image(
                img,
                caption="Shimadzu UV-1700 — tampilan depan",
                use_container_width=True
            )


# ============================================================
# FOTO NYATA
# ============================================================

def page_photo():

    header()

    st.markdown("## 📷 Eksplorasi Foto Nyata UV-1700")

    st.markdown("""
    <div class="info">
    Pilih sudut instrumen untuk melihat detail berdasarkan foto yang tersedia.
    Tampilan kiri/kanan hanya ditampilkan
