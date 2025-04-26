import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="REPFAE", layout="wide")

# Mostrar el logo (cambia esta URL a tu URL de GitHub si tienes otra imagen)
st.image("https://raw.githubusercontent.com/tuusuario/repfae/main/fondoazul%20aceite.png", width=250)

# Variables de sesión
if "turnos" not in st.session_state:
    st.session_state["turnos"] = []
if "lat" not in st.session_state:
    st.session_state["lat"] = None
if "lon" not in st.session_state:
    st.session_state["lon"] = None
if "modo" not in st.session_state:
    st.session_state["modo"] = None

# Capturar ubicación automática mediante navegador
components.html(
    """
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            window.parent.postMessage({ lat: latitude, lon: longitude }, "*");
        },
        (error) => {
            alert('⚠️ No se pudo obtener tu ubicación. Acepta permisos de geolocalización.');
        }
    );
    </script>
    """,
    height=0,
)

# Capturar la posición enviada
message = st.experimental_get_query_params()
if "lat" in message and "lon" in message:
    st.session_state["lat"] = float(message["lat"][0])
    st.session_state["lon"] = float(message["lon"][0])

# Login lateral para seleccionar el rol
st.sidebar.title("Acceso REPFAE")
rol = st.sidebar.selectbox("Selecciona tu rol:", ["Estudiante", "Profesor"])

if rol == "Profesor":
    usuario = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    if usuario == "profesor" and password == "repfae2024":
        st.session_state["modo"] = "profesor"
    elif usuario and password:
        st.error("⚠️ Usuario o contraseña incorrectos.")
elif rol == "Estudiante":
    st.session_state["modo"] = "estudiante"

# Lógica según el rol
if st.session_state["modo"] == "estudiante":
    st.title("📝 Registro de Turno - Estudiante")

    nombre = st.text_input("Nombre completo del estudiante")
    correo = st.text_input("Correo UVa")
    fecha = st.date_input("Fecha del turno", value=datetime.now())
    turno = st.selectbox("Tipo de turno", ["Mañana", "Tarde", "Noche", "Guardia"])
    profesor = st.text_input("Nombre completo del profesor responsable")

    registrar = st.button("Registrar Turno")

    if registrar:
        if not (nombre and correo and profesor):
            st.warning("⚠️ Completa todos los campos obligatorios.")
        elif st.session_state["lat"] is None or st.session_state["lon"] is None:
            st.warning("⚠️ No se ha detectado ubicación todavía. Espera o recarga la página.")
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
                "Latitud": st.session_state["lat"],
                "Longitud": st.session_state["lon"]
            })
            st.success("✅ Turno registrado correctamente.")

elif st.session_state["modo"] == "profesor":
    st.title("👨‍🏫 Panel de Control - Profesor")

    if st.session_state["turnos"]:
        df = pd.DataFrame(st.session_state["turnos"])
        st.dataframe(df)

        # Mapa en tiempo real
        st.subheader("🗺️ Mapa de Localizaciones")
        m = folium.Map(location=[40.4168, -3.7038], zoom_start=6)

        color_dict = {"Mañana": "green", "Tarde": "orange", "Noche": "blue", "Guardia": "red"}

        for _, row in df.iterrows():
            folium.Marker(
                location=[row["Latitud"], row["Longitud"]],
                popup=f"{row['Estudiante']} - {row['Turno']} - {row['Marcaje']}",
                icon=folium.Icon(color=color_dict.get(row["Turno"], "gray"))
            ).add_to(m)

        st_folium(m, width=700, height=500)

        # Exportar Excel
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
        st.info("ℹ️ Aún no hay turnos registrados.")
