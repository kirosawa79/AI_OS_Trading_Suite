from __future__ import annotations
import shutil
from pathlib import Path
import pandas as pd
import streamlit as st
from config.settings import SETTINGS
from market.data import download_ohlcv
from market.session import opening_shield_active
from indicators.engine import calculate_indicators
from signals.engine import evaluate_signal
from psychology.engine import analyze_justification
from options_engine.selector import select_contract, OptionSelectionError
from risk.engine import build_position_plan
from database.repository import TradingRepository
from charts.plotly_engine import market_chart
from scanner.service import scan_tickers

st.set_page_config(page_title=SETTINGS.app_name,page_icon='🏛️',layout='wide')

def authenticated():
    if st.session_state.get('authenticated'): return True
    st.title('🏛️ AI-OS PRO v3 Institutional')
    user=st.text_input('ID de operador').upper().strip()
    password=st.text_input('Clave',type='password')
    if st.button('Desbloquear terminal',use_container_width=True):
        try:
            ok=user==st.secrets['auth']['usuario'].upper().strip() and password==st.secrets['auth']['clave']
        except Exception:
            st.error('Configura .streamlit/secrets.toml.'); return False
        if ok: st.session_state['authenticated']=True; st.rerun()
        else: st.error('Credenciales inválidas.')
    return False

if not authenticated(): st.stop()

@st.cache_resource
def repo(): return TradingRepository()

@st.cache_data(ttl=300,show_spinner=False)
def load_market(ticker): return calculate_indicators(download_ohlcv(ticker))

st.title(SETTINGS.app_name)
module=st.sidebar.radio('Módulo',['📈 Acciones','🎫 Opciones','🚀 Escáner','📋 Bitácora'])
if st.sidebar.button('Cerrar sesión'):
    st.session_state.clear(); st.rerun()

if module=='📈 Acciones':
    ticker=st.text_input('Ticker','AAPL').upper().strip()
    justification=st.text_area('Plan técnico','Entrada sobre soporte; stop bajo EMA40; riesgo definido.')
    if st.button('Evaluar acción'):
        try:
            data=load_market(ticker); shield=opening_shield_active(data.index[-1]); signal=evaluate_signal(ticker,data,shield); psych=analyze_justification(justification)
            st.plotly_chart(market_chart(data,ticker),use_container_width=True)
            c1,c2,c3=st.columns(3); c1.metric('Precio',f"${data['Close'].iloc[-1]:.2f}"); c2.metric('AI score',f'{signal.score}/100'); c3.metric('Señal',signal.strategy)
            for x in signal.reasons: st.success(x)
            for x in signal.warnings: st.warning(x)
            if psych.blocked: st.error(f'{psych.bias}: {psych.message}')
            elif signal.authorized: st.success('Evaluación técnica autorizada. No equivale a una orden ejecutada.')
            else: st.info('No se autoriza una entrada con las reglas actuales.')
            repo().save_evaluation(ticker=ticker,estrategia=signal.strategy,justificacion=justification,bloqueado=int(psych.blocked or not signal.authorized),sesgo_detectado=psych.bias,precio=float(data['Close'].iloc[-1]),score=signal.score,estado='EVALUADA')
        except Exception as exc: st.exception(exc)

elif module=='🎫 Opciones':
    a,b,c=st.columns(3)
    ticker=a.text_input('Subyacente','SPY').upper().strip(); capital=b.number_input('Capital USD',min_value=10.0,value=1000.0); risk_pct=c.slider('Riesgo máximo',1,10,3)/100
    justification=st.text_area('Plan técnico','Entrada por ruptura; stop estructural; riesgo máximo definido.')
    if st.button('Evaluar contrato real'):
        try:
            data=load_market(ticker); signal=evaluate_signal(ticker,data,opening_shield_active(data.index[-1])); psych=analyze_justification(justification)
            st.plotly_chart(market_chart(data,ticker),use_container_width=True)
            if psych.blocked: st.error(f'{psych.bias}: {psych.message}')
            elif not signal.authorized: st.warning(f'Señal no autorizada: {signal.strategy}, score {signal.score}/100.')
            else:
                contract=select_contract(ticker,signal.strategy,float(data['Close'].iloc[-1])); plan=build_position_plan(capital,risk_pct,contract.ask)
                cols=st.columns(5)
                cols[0].metric('Tipo',contract.option_type); cols[1].metric('Strike',f'${contract.strike:.2f}'); cols[2].metric('Ask',f'${contract.ask:.2f}'); cols[3].metric('IV',f'{contract.implied_volatility*100:.1f}%'); cols[4].metric('Spread',f'{contract.spread_pct*100:.1f}%')
                st.write(f'**Vencimiento:** {contract.expiration} · **OI:** {contract.open_interest} · **Volumen:** {contract.volume} · **Contrato:** {contract.contract_symbol}')
                if plan.valid:
                    st.success(f'{plan.quantity} contrato(s), costo estimado ${plan.total_cost:,.2f}, dentro de un presupuesto de ${plan.risk_budget:,.2f}.')
                    if st.button('Registrar evaluación autorizada'):
                        repo().save_evaluation(ticker=ticker,estrategia=signal.strategy,justificacion=justification,bloqueado=0,sesgo_detectado=psych.bias,precio=float(data['Close'].iloc[-1]),score=signal.score,contrato=contract.contract_symbol,vencimiento=contract.expiration,strike=contract.strike,bid=contract.bid,ask=contract.ask,iv=contract.implied_volatility,open_interest=contract.open_interest,volumen=contract.volume,riesgo_pct=risk_pct,cantidad=plan.quantity,costo_total=plan.total_cost,estado='AUTORIZADA')
                        st.success('Evaluación guardada.')
                else: st.error(plan.reason)
        except OptionSelectionError as exc: st.error(str(exc))
        except Exception as exc: st.exception(exc)

elif module=='🚀 Escáner':
    text=st.text_input('Tickers separados por comas','AAPL,NVDA,SPY,TSLA')
    if st.button('Escanear'):
        tickers=list(dict.fromkeys(x.strip().upper() for x in text.split(',') if x.strip()))[:20]
        st.dataframe(pd.DataFrame(scan_tickers(tickers)),use_container_width=True,hide_index=True)

else:
    st.dataframe(repo().recent(100),use_container_width=True,hide_index=True)
