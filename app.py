import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from streamlit_folium import st_folium
import folium
import streamlit.components.v1 as components

st.set_page_config(page_title="REPFAE", layout="wide")

# Mostrar el logo de la Facultad
st.image("https://github.com/Chema1987/repfae/blob/main/fondoazul%20aceite.png?raw=true", width=250)

# Variables de sesión
if "turnos" not in st.session_state:
    st.session_state["turnos"] = []
if "modo" not in st.session_state:
    st.session_state["modo"] = None
if "latitud" not in st.session_state:
    st.session_state["latitud"] = None
if "longitud" not in st.session_state:
    st.session_state["longitud"] = None

# Inyectar JavaScript para capturar geolocalización automática
components.html(
    """
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const data = {latitud: latitude, longitud: longitude};
            window.parent.postMessage(data, "*");
        },
        (error) => {
            alert('⚠️ No se pudo obtener tu ubicación. Por favor, permite acceso a la localización.');
        }
    );
    </script>
    """,
    height=0,
)

# Captura de datos enviados por el navegador
st.session_state["latitud"] = st.query_params.get("latitud", [None])[0]
st.session_state["longitud"] = st.query_params.get("longitud", [None])[0]

# Panel lateral para elegir el rol
st.sidebar.title("Acceso REPFAE")
rol = st.sidebar.selectbox("Selecciona tu rol:", ["Estudiante", "Profesor"])

if rol == "Profesor":
    usuario = st.sidebar.text_input("Usuario")
    contraseña = st.sidebar.text_input("Contraseña", type="password")
    if usuario == "profesor" and contraseña == "repfae2024":
        st.session_state["modo"] = "profesor"
    elif usuario and contraseña:
        st.error("⚠️ Usuario o contraseña incorrectos.")
elif rol == "Estudiante":
    st.session_state["modo"] = "estudiante"

# Funcionalidad según el modo
if st.session_state["modo"] == "estudiante":
    st.title("📝 Registro de Turno - Estudiante")

    nombre = st.text_input("Nombre completo del estudiante")
    correo = st.text_input("Correo UVa")
    fecha = st.date_input("Fecha del turno", value=datetime.now())
    turno = st.selectbox("Tipo de turno", ["Mañana", "Tarde", "Noche", "Guardia"])
    profesor = st.text_input("Nombre completo del profesor responsable")

    if st.button("Registrar Turno"):
        if not (nombre and correo and profesor):
            st.warning("⚠️ Completa todos los campos.")
        elif st.session_state["latitud"] is None or st.session_state["longitud"] is None:
            st.warning("⚠️ No se detectó la ubicación aún. Espera o recarga la página.")
        else:
            horas_turno = {"Mañana": 7.5, "Tarde": 7.5, "Noche": 10.5, "Guardia": 12}
            horas = horas_turno[turno]
            marcaje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            st.session_state["turnos"].append({
                "Estudiante": nombre,
                "Correo UVa": correo,
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Turno": turno,
                "Horas": horas,
                "Profesor": profesor,
                "Marcaje": marcaje,
                "Latitud": st.session_state["latitud"],
                "Longitud": st.session_state["longitud"]
            })
            st.success("✅ Turno registrado correctamente.")

elif st.session_state["modo"] == "profesor":
    st.title("👨‍🏫 Panel de Control - Profesor")

    if st.session_state["turnos"]:
        df = pd.DataFrame(st.session_state["turnos"])
        st.subheader("📄 Turnos Registrados")
        st.dataframe(df)

        # Mapa con localizaciones de turnos
        st.subheader("🗺️ Mapa de Localizaciones de Estudiantes")
        m = folium.Map(location=[40.4168, -3.7038], zoom_start=6)
        color_turnos = {"Mañana": "green", "Tarde": "orange", "Noche": "blue", "Guardia": "red"}

        for _, row in df.iterrows():
            folium.Marker(
                location=[float(row["Latitud"]), float(row["Longitud"])],
                popup=f"{row['Estudiante']} - {row['Turno']} ({row['Marcaje']})",
                icon=folium.Icon(color=color_turnos.get(row["Turno"], "gray"))
            ).add_to(m)

        st_folium(m, width=700, height=500)

        # Descargar Excel
        def to_excel(dataframe):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                dataframe.to_excel(writer, index=False, sheet_name="Turnos")
                dataframe.groupby("Estudiante")["Horas"].sum().reset_index().to_excel(writer, index=False, sheet_name="Resumen_Estudiantes")
                dataframe.groupby("Profesor")["Horas"].sum().reset_index().to_excel(writer, index=False, sheet_name="Resumen_Profesores")
            return output.getvalue()

        excel_bytes = to_excel(df)
        st.download_button(
            label="📥 Descargar Excel de Turnos",
            data=excel_bytes,
            file_name="Turnos_REPFAE.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info("ℹ️ No hay turnos registrados aún.")
