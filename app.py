import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(page_title="REPFAE", layout="wide")

# LOGO de la Facultad
st.image("https://TU_URL_DEL_LOGO", width=250)  # Cambiar por tu URL real

# Variables de sesión
if "turnos" not in st.session_state:
    st.session_state["turnos"] = []
if "modo" not in st.session_state:
    st.session_state["modo"] = None

# Geolocalización Automática usando JavaScript
components.html(
    """
    <script>
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const streamlitLat = window.parent.document.querySelectorAll('input[data-testid="stTextInput"]')[0];
            const streamlitLon = window.parent.document.querySelectorAll('input[data-testid="stTextInput"]')[1];
            streamlitLat.value = lat;
            streamlitLon.value = lon;
            streamlitLat.dispatchEvent(new Event('input', { bubbles: true }));
            streamlitLon.dispatchEvent(new Event('input', { bubbles: true }));
        },
        function(error) {
            alert('⚠️ No se pudo obtener tu ubicación. Acepta el permiso de localización.');
        }
    );
    </script>
    """,
    height=0,
)

# Login Inicial: Elegir rol
st.sidebar.title("Acceso REPFAE")
rol = st.sidebar.selectbox("Selecciona tu rol:", ["Estudiante", "Profesor"])

if rol == "Profesor":
    password = st.sidebar.text_input("Contraseña:", type="password")
    if password == "repfae2024":
        st.session_state["modo"] = "profesor"
    else:
        st.error("⚠️ Contraseña incorrecta para el rol de Profesor.")
elif rol == "Estudiante":
    st.session_state["modo"] = "estudiante"

# Lógica de la app
if st.session_state["modo"] == "estudiante":
    st.title("📝 Registro de Turno - Estudiante")

    latitud = st.text_input("Latitud (capturada automáticamente)", disabled=True)
    longitud = st.text_input("Longitud (capturada automáticamente)", disabled=True)

    nombre = st.text_input("Nombre completo del estudiante")
    correo = st.text_input("Correo UVa")
    fecha = st.date_input("Fecha del turno", value=datetime.now())
    turno = st.selectbox("Tipo de turno", ["Mañana", "Tarde", "Noche", "Guardia"])
    profesor = st.text_input("Nombre completo del profesor responsable")

    registrar = st.button("Registrar Turno")

    if registrar:
        if not (nombre and correo and profesor and latitud and longitud):
            st.warning("⚠️ Todos los campos deben estar completos y ubicación activa.")
        else:
            horas_dict = {"Mañana": 7.5, "Tarde": 7.5, "Noche": 10.5, "Guardia": 12}
            horas = horas_dict[turno]
            marcaje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["turnos"].append({
                "Estudiante": nombre,
                "Correo UVa": correo,
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Turno": turno,
                "Horas": horas,
                "Profesor": profesor,
                "Marcaje": marcaje,
                "Latitud": latitud,
                "Longitud": longitud
            })
            st.success("✅ Turno registrado correctamente.")

elif st.session_state["modo"] == "profesor":
    st.title("👨‍🏫 Panel de Control - Profesor")

    if st.session_state["turnos"]:
        df = pd.DataFrame(st.session_state["turnos"])
        st.dataframe(df)

        # Exportación a Excel
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Turnos")
                df.groupby("Estudiante")["Horas"].sum().reset_index().to_excel(writer, index=False, sheet_name="Resumen_Estudiantes")
                df.groupby("Profesor")["Horas"].sum().reset_index().to_excel(writer, index=False, sheet_name="Resumen_Profesores")
            return output.getvalue()

        excel_data = to_excel(df)
        st.download_button("📥 Descargar Excel", data=excel_data, file_name="Turnos_REPFAE.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Aún no hay turnos registrados.")

