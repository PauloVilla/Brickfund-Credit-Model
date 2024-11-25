import streamlit as st
import pandas as pd
import numpy as np
import gspread
from config import api_key, sheet_id
import warnings


warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Pre Ofertas",
    page_icon=":clipboard:",
    layout="centered",

    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Ofertify\nAplicación para la generación de PreOfertas, basado en CIEC y Buró"
    }
)



def get_info():
    gc = gspread.api_key(api_key)
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.sheet1
    # Obtener todos los datos como una lista de listas
    data = worksheet.get_all_values()
    # Convertir a DataFrame
    data = pd.DataFrame(data[1:], columns=data[0])
    return data


df = get_info()


if "Mostrar info" not in st.session_state.keys():
    st.session_state["Mostrar info"] = 0
if "Pasa Requerimientos" not in st.session_state.keys():
    st.session_state["Pasa Requerimientos"] = 0

if "Mensaje" not in st.session_state.keys():
    st.session_state["Mensaje"] = ""


with st.sidebar:
    nombre = st.selectbox("Selecciona el cliente", df["Nombre completo"].tolist())
    if st.button("Generar Pre Oferta"):
        st.session_state["Mostrar info"] = 1


def calcular_tasa(dti, ltv, plazo_meses):
    # Peso de cada factor
    peso_dti = 0.4
    peso_ltv = 0.3
    peso_plazo = 0.3

    # Ponderaciones para cada factor
    if dti < 30:
        ajuste_dti = -0.005  # Tasa baja
    elif dti < 40:
        ajuste_dti = 0
    else:
        ajuste_dti = 0.005  # Tasa alta

    if ltv < 50:
        ajuste_ltv = -0.005
    elif ltv < 70:
        ajuste_ltv = 0
    else:
        ajuste_ltv = 0.005

    if plazo_meses <= 24:
        ajuste_plazo = -0.002
    elif plazo_meses <= 60:
        ajuste_plazo = 0
    else:
        ajuste_plazo = 0.002

    # Calcular tasa base
    tasa_base = 0.18  # Tasa inicial
    tasa_ajustada = tasa_base + (
        peso_dti * ajuste_dti +
        peso_ltv * ajuste_ltv +
        peso_plazo * ajuste_plazo 
    )

    # Limitar tasa al rango permitido
    return max(0.18, min(0.20, tasa_ajustada))

def calcular_interes_y_capital(saldo_inicial, tasa_mensual, pago_mensual):
    # Cálculo de interés del mes
    interes_mensual = saldo_inicial * tasa_mensual
    # Pago a capital
    capital_mensual = pago_mensual - interes_mensual
    return interes_mensual, capital_mensual

cliente_data = df[df["Nombre completo"] == nombre].iloc[0]
ingresos_mensuales = float(cliente_data["Ingresos mensuales promedio (MXN)"].replace(",", ""))
gastos_mensuales = float(cliente_data["Deudas actuales totales (MXN)"].replace(",", ""))
capacidad_pago = ingresos_mensuales - gastos_mensuales - float(cliente_data["Gastos fijos mensuales (MXN)"].replace(",", ""))
dti = float(cliente_data["Deudas actuales totales (MXN)"].replace(",", "")) / (ingresos_mensuales*12) * 100
ltv = float(cliente_data["Monto solicitado (MXN"].replace(",", "")) / float(cliente_data["Valor del aproximado del colateral (MXN)"].replace(",", "")) * 100
monto_solicitado = float(cliente_data["Monto solicitado (MXN"].replace(",", ""))
nombre_empresa = cliente_data["Nombre del proyecto"]
plazo_meses = int(cliente_data["Plazo estimado para el préstamo (meses)"])

tasa = calcular_tasa(dti, ltv, plazo_meses)
tasa_mensual = tasa/12

# Cálculo de pago mensual
pago_mensual = (monto_solicitado * tasa_mensual * (1 + tasa_mensual)**plazo_meses) / \
               ((1 + tasa_mensual)**plazo_meses - 1)

interes, capital = calcular_interes_y_capital(saldo_inicial=monto_solicitado, tasa_mensual=tasa_mensual, pago_mensual=pago_mensual)


if monto_solicitado < 10_000_000 or monto_solicitado>100_000_000:
    st.session_state["Pasa Requerimientos"] = 0
    st.session_state["Mensaje"] = f"Monto solicitado fuera del rango: ${monto_solicitado:,.2f}"
else:
    st.session_state["Pasa Requerimientos"] = 1

# Garanía mínima
ltv_maximo = 100 / 1.75

if ltv > ltv_maximo:
    st.session_state["Pasa Requerimientos"] = 0
    st.session_state["Mensaje"] = F"Garantía insuficiente"
else:
    st.session_state["Pasa Requerimientos"] = 1


if st.session_state["Mostrar info"] == 1 and st.session_state["Pasa Requerimientos"] == 1:
    # Estilos CSS
    st.markdown("""
    <style>
        .title {
            font-size: 2.3em;
            font-weight: bold;
            text-align: left;
            color: #1e2019;
        }
        .subtitle {
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 1em;
            color: #070358;
        }
        .info-box {
            background-color: #f9f9f9;
            padding: 1em;
            margin-bottom: 1em;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .highlight {
            font-weight: bold;
            color: #E74C3C;
        }
        .footer {
            text-align: center;
            margin-top: 2em;
            font-size: 0.7em;
            color: #777;
        }
    </style>
    """, unsafe_allow_html=True)

    # Cargar la imagen
    image = "logo.jpg"


    # Contenedor principal
    
    
    with st.container():
        izq,  der = st.columns(2)

        izq.markdown(f"""
        <div class="title">
            Preoferta de Crédito
        </div>
        <div class="subtitle">
            {nombre_empresa}
        </div>
       
        """, unsafe_allow_html=True)
        izq_logo, logo = der.columns(2)
        logo.image(image=image, use_column_width=True, caption="Brickfund")


    with st.container(border=False):
        st.markdown(
            f"""
            <div style="background-color:#587b7f; padding:1px; border-radius:5px;">
                
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f'<p style="color:#272346; font-weight:bold; text-align:left; font-size:28px;">{nombre.title()}</p>', unsafe_allow_html=True)
        colt1, colt2 = st.columns(2)
        with colt1:
            st.markdown(f"""
            <div>
                <p style="color:#272346; font-size:14px;"><strong>Número de proyectos:</strong> {cliente_data["Número de proyectos completados con éxito"]}<br>
                  <strong>RFC:</strong> {cliente_data["RFC"].upper()}</p>
            </div>
            """, unsafe_allow_html=True)
        with colt2:
            st.markdown(f"""
            <div>
                <p style="color:#272346; font-size:14px;"><strong>Número telefónico:</strong> {cliente_data["Número telefónico"]}<br>
                  <strong>Correo electrónico:</strong> {cliente_data["Correo electrónico"].lower()}</p>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("""<div style="background-color:#587b7f; padding:1px; border-radius:5px;"></div>""", unsafe_allow_html=True)
    st.container(height=10, border=False)
    with st.container(border=False):
        monto, info_monto = st.columns(2)
        monto.markdown(
            f"""
            <div style="text-align: left; font-size:13px;">
                <span style="font-weight: bold; font-size:13px;">Monto:</span> <br>
                <span style="font-size:28px; font-weight: bold;, sans-serif; color: #04045C;">
                    ${monto_solicitado:,.2f} MXN
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        info_monto.markdown(f"""
            <div>
                <p style="color:#272346; font-size:14px; text-align:right;"><strong>Pago Mensual:</strong> ${np.round(pago_mensual, 2):,.2f} MXN<br>
                  <strong>Capital:</strong> ${np.round(capital, 2):,.2f} MXN<br>
                  <strong>Interés:</strong> ${np.round(interes, 2):,.2f} MXN</p>
            </div>
            """, unsafe_allow_html=True)
    # Sección de detalles del crédito
    st.container(height=10, border=False)

    with st.container(border=False):
        col1, col2, col3 = st.columns(3)
         # Estilos comunes para los títulos y valores
        title_style = "font-weight: bold; text-align: center; font-size: 18px;"
        value_style = "text-align: center; font-size: 16px;"

        # Columna 1: Tasa
        with col1:
            st.markdown(
                f"""
                <div style="{title_style}">Tasa</div>
                <hr style="margin: 5px; border: 1px solid #587b7f;">
                <div style="{value_style}">{tasa:.2%} Anual</div>
                """,
                unsafe_allow_html=True,
            )

        # Columna 2: Plazo
        with col2:
            st.markdown(
                f"""
                <div style="{title_style}">Plazo</div>
                <hr style="margin: 5px; border: 1px solid #587b7f;">
                <div style="{value_style}">{plazo_meses} Meses</div>
                """,
                unsafe_allow_html=True,
            )

        # Columna 3: Comisión
        with col3:
            st.markdown(
                f"""
                <div style="{title_style}">Comisión</div>
                <hr style="margin: 5px; border: 1px solid #587b7f;">
                <div style="{value_style}">Por Definir</div>
                """,
                unsafe_allow_html=True,
            )
    

    st.container(height=20, border=False)

    # Observaciones importantes
    with st.container(border=False):
        st.markdown("""
        <div class="info-box">
            <ul>
                <strong>Esta preoferta puede variar debido a cargos adicionales. Está sujeta a:</strong>
                <li> Revisión de burós de crédito.</li>
                <li> Validación de estados financieros.</li>
                <li> Evaluación de la garantía por un valuador independiente.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # st.markdown("\n\n\n")
    # Pie de página
    with st.container():
        
        st.markdown("""
        <div class="footer">
            <p>
            Para más información, comuníquese con nuestro equipo de análisis al teléfono <strong>(33) 3377 9676</strong>.<br>
            Este documento es para efectos informativos y no constituye obligación para las partes en relación con el otorgamiento.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.session_state["Mostrar info"] = 0
elif st.session_state["Mostrar info"] == 1 and st.session_state["Pasa Requerimientos"] == 0:
    st.error(f"El cliente no cumple con los criterios de crédito.\n {st.session_state['Mensaje']}")
    st.session_state["Mostrar info"] = 0

else:
    st.markdown("# Herramienta Preofertas Brickfund!")
    st.info("Ingrese un cliente!")
    st.session_state["Mostrar info"] = 0