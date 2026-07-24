# -*- coding: utf-8 -*-
import streamlit as st, pandas as p, yfinance as yf, datetime as dt, os, plotly.graph_objects as go
from data_collector import DataCollector
from database import TradingDatabase

st.set_page_config(page_title="AI-OS PRO Dashboard", page_icon="🏛️", layout="wide")

# =====================================================================
# MÓDULO DE SEGURIDAD INTERNA: LOGIN CONTROL LOCK (NATIVO RESPONSIVO)
# =====================================================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

def validar_credenciales():
    if st.session_state["usuario_input"].upper().strip() == "KIROSAWA" and st.session_state["clave_input"] == "Aios2026*":
        st.session_state["autenticado"] = True
        st.session_state["usuario_input"] = ""
        st.session_state["clave_input"] = ""
    else:
        st.error("🛑 Acceso Denegado: Credenciales inválidas.")

if not st.session_state["autenticado"]:
    _, col_l2, _ = st.columns([1, 2, 1])
    with col_l2:
        with st.container(border=True):
            st.title("🏛️ AI-INVESTMENT OS")
            st.write("🔒 **SECURITY ACCESS TERMINAL**")
            st.text_input("ID de Operador:", key="usuario_input", placeholder="Ej: KIROSAWA")
            st.text_input("Clave de Encriptación:", key="clave_input", type="password", placeholder="••••••••")
            st.button("Desbloquear Terminal", on_click=validar_credenciales, use_container_width=True)
        st.stop()

# =====================================================================
# SINOPSIS DEL SISTEMA (EJECUCIÓN AUTORIZADA)
# =====================================================================
st.title("🏛️ AI-INVESTMENT OPERATING SYSTEM (AI-OS) PRO")
st.caption("Filtros Cuánticos, Análisis Geométrico & Apertura Shield | Desarrollado por KIROSAWA")

db = TradingDatabase()
mod = st.sidebar.radio("Módulo:", ["📈 Operar Acciones", "🎫 Operar Opciones", "🚀 Escáner Multiticker", "📋 Bitácora"])

if st.sidebar.button("🔒 Cerrar Sesión Segura", use_container_width=True):
    st.session_state["autenticado"] = False
    st.rerun()

# --- FUNCIONES CORE MATEMÁTICAS ---
def c_emas_bb(s):
    d = p.DataFrame(index=s.index); d['Close'] = s
    for sp, c in [(9,'EMA9'),(20,'EMA20'),(40,'EMA40'),(100,'EMA100'),(200,'EMA200')]: d[c] = s.ewm(span=sp, adjust=False).mean()
    d['BB_Base'] = s.rolling(window=21).mean(); d['BB_Std'] = s.rolling(window=21).std()
    d['BB_Sup'] = d['BB_Base'] + (2.1 * d['BB_Std']); d['BB_Inf'] = d['BB_Base'] - (2.1 * d['BB_Std'])
    return d

def v_optimo(fs):
    hoy = dt.date.today()
    for f in fs:
        try:
            y, m, d = [int(x) for x in f.split('-')]
            if 7 <= (dt.date(y, m, d) - hoy).days <= 15: return f
        except: continue
    return fs if fs else "No disponible"

def verificar_filtro_apertura(index_serie):
    try:
        u = index_serie[-1]
        if hasattr(u, 'time'): return (u.time().hour == 9 and 30 <= u.time().minute <= 59)
    except: pass
    return False

def extraer_iv_segura(ticker, est, c_a):
    try:
        obj = yf.Ticker(ticker); f_e = v_optimo(obj.options)
        if f_e != "No disponible":
            dfd = obj.option_chain(f_e).calls if "CALL" in est else obj.option_chain(f_e).puts
            ive = float(dfd.loc[(dfd['strike'] - round(c_a)).abs().idxmin(), 'impliedVolatility'])
            return (ive if ive > 0 else 0.35), f_e
    except: pass
    return 0.35, "No disponible"

# =====================================================================
# MÓDULO 1: OPERAR ACCIONES
# =====================================================================
if mod == "📈 Operar Acciones":
    st.header("📈 Operación Core de Acciones al Contado")
    t = st.text_input("Ticker:", "AAPL", key="txt_acciones").upper().strip()
    cap = st.number_input("Capital (USD):", min_value=10.0, value=1000.0, key="num_acciones")
    justificacion_usuario = st.text_area("Justificación técnica:", key="area_acciones")
    if st.button("Evaluar Acción", key="btn_acciones"):
        df = yf.download(t, period="60d", interval="1h", progress=False)
        if df.empty: st.error("Sin datos.")
        else:
            sc = df['Close'][t].copy() if isinstance(df.columns, p.MultiIndex) else df['Close'].copy()
            sc = p.Series(p.to_numeric(sc.to_numpy().flatten(), errors='coerce')).dropna()
            m = c_emas_bb(sc)
            c_a, e20, e40, e200 = float(m['Close'].iloc[-1]), float(m['EMA20'].iloc[-1]), float(m['EMA40'].iloc[-1]), float(m['EMA200'].iloc[-1])
            if c_a > e200:
                st.success(f"🟢 Filtro Estructural Aprobado. Precio (${round(c_a,2)}) > EMA200 (${round(e200,2)}).")
                st.info("🔥 CRUCE + Activo" if e20 > e40 else "⏳ Espera un Pullback a soportes.")
            else: st.error(f"❌ Riesgo: Precio por debajo de la EMA200 (${round(e200,2)}).")

# =====================================================================
# MÓDULO 2: OPERAR OPCIONES
# =====================================================================
elif mod == "🎫 Operar Opciones":
    st.header("🎫 Operación de Derivados (EMA Cruces, BB Shield & Apertura)")
    c1, col2, col3 = st.columns(3)
    with c1: t = st.text_input("Subyacente:", "SPY", key="txt_opciones").upper().strip()
    with col2: cap = st.number_input("Capital Cuenta (USD):", min_value=10.0, value=1000.0, key="num_opciones")
    with col3: risk = st.slider("% Riesgo:", 1, 100, 10, key="sld_opciones") / 100.0
    justificacion_usuario = st.text_area("¿Por qué compras contratos hoy? (Filtro Emocional):", key="area_opciones")
    if st.button("Lanzar Escáner", key="btn_opciones"):
        df = yf.download(t, period="60d", interval="1h", progress=False)
        if df.empty: st.error("Sin datos de mercado.")
        else:
            sc = df['Close'][t].copy() if isinstance(df.columns, p.MultiIndex) else df['Close'].copy()
            sc = p.Series(p.to_numeric(sc.to_numpy().flatten(), errors='coerce')).dropna()
            m = c_emas_bb(sc)
            c_a, e9, e20, e40, e200 = float(m['Close'].iloc[-1]), float(m['EMA9'].iloc[-1]), float(m['EMA20'].iloc[-1]), float(m['EMA40'].iloc[-1]), float(m['EMA200'].iloc[-1])
            bb_sup, bb_inf = float(m['BB_Sup'].iloc[-1]), float(m['BB_Inf'].iloc[-1])
            f_ap = verificar_filtro_apertura(df.index)
            est = "CALL_PM40" if c_a > e20 and e20 > e40 and c_a > e200 and c_a > bb_sup else ("PUT_PM40" if c_a < e20 and e20 < e40 and c_a < e200 and c_a < bb_inf else "SIN_ALERTA")
            
            st.markdown("### 📊 ANÁLISIS GEOMÉTRICO INSTITUCIONAL (Velas 1H)")
            dg = df.tail(45).copy(); dg['E9'] = dg['Close'].ewm(span=9, adjust=False).mean(); dg['E20'] = dg['Close'].ewm(span=20, adjust=False).mean(); dg['E40'] = dg['Close'].ewm(span=40, adjust=False).mean(); dg['E100'] = dg['Close'].ewm(span=100, adjust=False).mean(); dg['E200'] = dg['Close'].ewm(span=200, adjust=False).mean()
            dg['BB_B'] = dg['Close'].rolling(21).mean(); dg['BB_S'] = dg['Close'].rolling(21).std(); dg['B_Sup'] = dg['BB_B'] + (2.1 * dg['BB_S']); dg['B_Inf'] = dg['BB_B'] - (2.1 * dg['BB_S'])
            dg['p20'], dg['p40'] = dg['E20'].shift(1), dg['E40'].shift(1)
            c_p, c_n = (dg['E20'] > dg['E40']) & (dg['p20'] <= dg['p40']), (dg['E20'] < dg['E40']) & (dg['p20'] >= dg['p40'])
            
            cf_canvas = "#2d2613" if f_ap else "plotly_dark"
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=dg.index, open=dg['Open'][t] if isinstance(dg.columns, p.MultiIndex) else dg['Open'], high=dg['High'][t] if isinstance(dg.columns, p.MultiIndex) else dg['High'], low=dg['Low'][t] if isinstance(dg.columns, p.MultiIndex) else dg['Low'], close=dg['Close'][t] if isinstance(dg.columns, p.MultiIndex) else dg['Close'], name="Velas"))
            for c, cl, w in [('E9','#ffffff',1.5),('E20','#f1c40f',2),('E200','#9b59b6',2.5)]: fig.add_trace(go.Scatter(x=dg.index, y=dg[c], line=dict(color=cl, width=w), name=c))
            fig.add_trace(go.Scatter(x=dg.index, y=dg['B_Sup'], line=dict(color='#2ecc71', width=1.5, dash='dash'), name="Banda Sup"))
            fig.add_trace(go.Scatter(x=dg.index, y=dg['B_Inf'], line=dict(color='#e74c3c', width=1.5, dash='dash'), name="Banda Inf"))
            dp, dn = dg[c_p], dg[c_n]
            if not dp.empty: fig.add_trace(go.Scatter(x=dp.index, y=dp['Low']*0.997, mode='markers+text', marker=dict(symbol='triangle-up', size=11, color='#f1c40f'), text="CRUCE +", textposition="bottom center", name="Cruce +"))
            if not dn.empty: fig.add_trace(go.Scatter(x=dn.index, y=dn['High']*1.003, mode='markers+text', marker=dict(symbol='triangle-down', size=11, color='#e67e22'), text="CRUCE -", textposition="top center", name="Cruce -"))
            fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark" if cf_canvas=="plotly_dark" else None, paper_bgcolor=cf_canvas if cf_canvas!="plotly_dark" else None, plot_bgcolor=cf_canvas if cf_canvas!="plotly_dark" else None, margin=dict(l=10, r=10, t=10, b=10), height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            if f_ap: st.warning("⚠️ [SHIELD APERTURA ACTIVO] Bloqueo temporal en los primeros 30 minutos de Nueva York.")
            elif est == "SIN_ALERTA": st.info("🛡️ Filtro Bollinger-EMA: Activo cotiza dentro de rangos normales de compresión. Primas protegidas.")
            else:
                st.success(f"🚀 EXPANSIÓN CONFIRMADA: {est}")
                iv, f_e = extraer_iv_segura(t, est, c_a)
                st.metric("Volatilidad Implícita (IV)", f"{round(iv * 100, 2)}%")
                if any(pa in justificacion_usuario.lower() for pa in ["fomo", "rapido", "recuperar", "ganar", "urgente"]): st.error("❌ RECHAZADA: Sesgo emocional detectado.")
                else:
                    st.success("✅ CONTRATO AUTORIZADO.")
