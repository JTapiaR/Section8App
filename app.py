import streamlit as st
import pandas as pd
import pydeck as pdk
from dotenv import load_dotenv

# Configuración de la página debe ser la primera llamada de Streamlit
st.set_page_config(
    page_title="Section-8 Properties Map",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Agregar un logo en el encabezado del dashboard
logo_url = "Analíticalogo.png"  # Reemplaza con la ruta de tu logo
st.image(logo_url, width=400)

# Título visible en la aplicación
st.title("Section 8 Properties Analysis")

# Título general del dashboard
st.header("Description of the project:Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. ")

# Función para cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv('Datos/Data_Final2.csv')
    return df

@st.cache_data
def get_filtered_data(state, counties, home_types):
    df = load_data()
    if state:
        df = df[df['state'] == state]
    if counties:
        df = df[df['County'].isin(counties)]
    return df

# Cargar los datos completos
df = load_data()

# Verificar las columnas en el DataFrame
#st.write("Columnas disponibles en el DataFrame:", df.columns)

# Filtrar por estado
states = df['state'].unique()
selected_state = st.selectbox('Select a State', states)

# Filtrar por condados
filtered_df_state = get_filtered_data(selected_state, None, None)
counties = filtered_df_state['County'].unique()
selected_counties = st.multiselect('Select one or more counties click in the desired name', counties)

# Filtrar por tipo de vivienda (homeType)
home_types = df['homeType'].unique()
selected_home_types = st.multiselect('Select Home Types', home_types, default=home_types)

# Mostrar un mensaje de carga
st.text('Loading data...done!')

# Crear tarjetas y mapas para cada condado seleccionado
if selected_counties:
    for county in selected_counties:
        county_df = get_filtered_data(selected_state, [county], selected_home_types)

        # Añadir columna de colores basada en la columna Section_8
        county_df['color'] = county_df['Section_8'].apply(lambda x: [0, 255, 0, 160] if x == 1 else [255, 0, 0, 160])

        # Obtener valores únicos de 'bedrooms'
        bedrooms = county_df['bedrooms'].unique()
        bedrooms = sorted(bedrooms)
        bedrooms.insert(0, 'All')  # Agregar la opción 'All' al principio

        st.write(f"## {county} County")

        # Mostrar métricas
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total Section 8 Properties", value=county_df[county_df['Section_8'] == 1].shape[0])
        with col2:
            st.metric(label="Total Non-Section 8 Properties", value=county_df[county_df['Section_8'] == 0].shape[0])

        # Control de selección de número de cuartos
        selected_bedrooms = st.radio(f'Select Bedrooms for {county}', bedrooms, index=0, key=f'bedrooms_{county}', horizontal=True)
        
        # Aplicar filtro de dormitorios si no es 'All'
        if selected_bedrooms != 'All':
            county_df = county_df[county_df['bedrooms'] == selected_bedrooms]

        # Control de selección de tipo de vivienda
        selected_home_types = st.radio(f'Select Home Types for {county}', home_types, index=0, key=f'hometypes_{county}', horizontal=True)
        
        # Aplicar filtro de tipo de vivienda
        if selected_home_types != 'All':
            county_df = county_df[county_df['homeType'] == selected_home_types]

        # Verificar que hay datos en el DataFrame filtrado
        if county_df.empty:
            st.warning(f"No data available for {county} County with the selected filters.")
            continue

        # Crear el mapa interactivo con Pydeck centrado en el condado
        midpoint = (county_df['latitude'].mean(), county_df['longitude'].mean())

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=county_df,
            get_position='[longitude, latitude]',
            get_color='color',
            get_radius=200,
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=midpoint[0],
            longitude=midpoint[1],
            zoom=10,
            pitch=50,
        )

        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "text": "Price per Sq Foot: {price_sq_foot}\nBedrooms: {bedrooms}\nSection 8: {Section_8}"
            }
        )

        # Mostrar el mapa en Streamlit
        st.pydeck_chart(r)

        # Filtrar propiedades Section 8
        section_8_properties = county_df[county_df['Section_8'] == 1]
        
        # Mostrar tabla con propiedades Section 8
        st.write("### Section 8 Properties")
        st.dataframe(section_8_properties[[
            "zpid",
            "detailUrl_InfoTOD",
            "price_sq_foot",
            "bedrooms",
            "FRM",
            "yearBuilt",
            "SCHOOLSMeandistance",
            "price_to_rent_ratio_InfoTOD",
            "livingArea",
            "lastSoldPrice",
            "description"
        ]])
else:
    st.write("Please select at least one county to view the data.")






