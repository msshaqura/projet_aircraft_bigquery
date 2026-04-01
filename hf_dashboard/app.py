"""
Application Streamlit avec connexion directe à BigQuery
Version déployée sur Hugging Face Spaces
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from google.cloud import bigquery
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Aircraft Data Analysis - BigQuery",
    page_icon="✈️",
    layout="wide"
)

# Couleurs
PRIMARY_BLUE = '#2C7DA0'

st.markdown(f"<h1 style='text-align: center; color: {PRIMARY_BLUE}'>✈️ Aircraft Data Analysis - BigQuery</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("## 🎯 Navigation")
    page = st.radio(
        "Choisissez une analyse:",
        ["✈️ Avions", "🛬 Aéroports", "📈 RPM", "📊 Croissance (ASM)"]
    )
    st.markdown("---")
    st.markdown("### 👨‍💻 Présenté par")
    st.markdown("**Mohammed SHAQURA**")
    st.markdown("Data Analyst | BigQuery Project")
    st.markdown("---")
    st.markdown("### ☁️ Base de données")
    st.info("Connexion directe à **Google BigQuery**")

# Initialiser le client BigQuery
@st.cache_resource
def init_bigquery():
    """Initialise le client BigQuery avec les credentials"""
    try:
        # Sur Hugging Face, les credentials sont dans les secrets
        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            credentials_info = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
            return bigquery.Client.from_service_account_info(credentials_info)
        else:
            # En local, utiliser le fichier JSON
            project_id = os.getenv('PROJECT_ID')
            return bigquery.Client(project=project_id)
    except Exception as e:
        st.error(f"Erreur de connexion à BigQuery: {e}")
        return None

# Récupérer les paramètres
PROJECT_ID = os.getenv('PROJECT_ID', 'dafs-16-ms')
DATASET_ID = os.getenv('DATASET_ID', 'aircraft_data')

client = init_bigquery()

if client is None:
    st.error("Impossible de se connecter à BigQuery. Vérifiez les credentials.")
    st.stop()

# ============================================
# QUESTION 1: AVIONS
# ============================================
if page == "✈️ Avions":
    st.markdown("## ✈️ Question 1: Quel avion a volé le plus ?")
    st.markdown("*Classement des avions par nombre de vols effectués*")
    
    query = f"""
    SELECT 
        a.Aircraft_Type AS avion,
        CAST(COUNT(f.Flight_Id) / 2 AS INT64) AS nombre_vols
    FROM `{PROJECT_ID}.{DATASET_ID}.individual_flights` f
    INNER JOIN `{PROJECT_ID}.{DATASET_ID}.aircraft` a 
        ON f.Aircraft_Id = a.Aircraft_Id
    GROUP BY a.Aircraft_Type
    ORDER BY nombre_vols DESC;
    """
    
    with st.spinner("Chargement des données depuis BigQuery..."):
        try:
            df = client.query(query).to_dataframe()
        except Exception as e:
            st.error(f"Erreur d'exécution: {e}")
            st.stop()
    
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(df)
        with col2:
            fig = px.bar(df, x='nombre_vols', y='avion', orientation='h', 
                         color='nombre_vols', color_continuous_scale='Blues')
            fig.update_layout(height=400)
            st.plotly_chart(fig)
        
        total = df['nombre_vols'].sum()
        st.success(f"🏆 **Gagnant:** {df.iloc[0]['avion']} avec {df.iloc[0]['nombre_vols']:,} vols ({df.iloc[0]['nombre_vols']/total*100:.1f}% du total)")
    else:
        st.error("Aucune donnée trouvée")

# ============================================
# QUESTION 2: AÉROPORTS
# ============================================
elif page == "🛬 Aéroports":
    st.markdown("## 🛬 Question 2: Quel aéroport a transporté le plus de passagers ?")
    st.markdown("*Chaque vol compte pour l'aéroport de départ ET l'aéroport d'arrivée*")
    
    query = f"""
    WITH passagers_par_vol AS (
        SELECT f.Departure_Airport_Code AS airport_code, a.Capacity AS capacite
        FROM `{PROJECT_ID}.{DATASET_ID}.individual_flights` f
        INNER JOIN `{PROJECT_ID}.{DATASET_ID}.aircraft` a ON f.Aircraft_Id = a.Aircraft_Id
        UNION ALL
        SELECT f.Destination_Airport_Code AS airport_code, a.Capacity AS capacite
        FROM `{PROJECT_ID}.{DATASET_ID}.individual_flights` f
        INNER JOIN `{PROJECT_ID}.{DATASET_ID}.aircraft` a ON f.Aircraft_Id = a.Aircraft_Id
    )
    SELECT 
        p.airport_code,
        COALESCE(ap.Airport_Name, 'Inconnu') AS aeroport,
        SUM(p.capacite) AS total_passagers
    FROM passagers_par_vol p
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.airports` ap ON p.airport_code = ap.Airport_Code
    GROUP BY p.airport_code, ap.Airport_Name
    ORDER BY total_passagers DESC;
    """
    
    with st.spinner("Chargement des données depuis BigQuery..."):
        try:
            df = client.query(query).to_dataframe()
        except Exception as e:
            st.error(f"Erreur d'exécution: {e}")
            st.stop()
    
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(df)
        with col2:
            fig = px.bar(df, x='total_passagers', y='aeroport', orientation='h',
                         color='total_passagers', color_continuous_scale='Blues')
            fig.update_layout(height=400)
            st.plotly_chart(fig)
        st.success(f"🏆 **Gagnant:** {df.iloc[0]['aeroport']} ({df.iloc[0]['airport_code']})")
    else:
        st.error("Aucune donnée trouvée")

# ============================================
# QUESTION 3: RPM
# ============================================
elif page == "📈 RPM":
    st.markdown("## 📈 Question 3: Meilleure année pour le Revenue Passenger-Miles (RPM)")
    st.markdown("*RPM = RPM_Domestic + RPM_International*")
    
    query = f"""
    WITH yearly_totals AS (
        SELECT 
            Airline_Code AS compagnie,
            Annee,
            SUM(RPM_Domestic + COALESCE(RPM_International, 0)) AS rpm_total
        FROM `{PROJECT_ID}.{DATASET_ID}.flight_summary_data`
        GROUP BY Airline_Code, Annee
    ),
    ranked AS (
        SELECT 
            compagnie,
            Annee,
            rpm_total,
            ROW_NUMBER() OVER (PARTITION BY compagnie ORDER BY rpm_total DESC) AS rang
        FROM yearly_totals
    )
    SELECT 
        compagnie,
        Annee AS meilleure_annee,
        rpm_total
    FROM ranked
    WHERE rang = 1
    ORDER BY compagnie;
    """
    
    with st.spinner("Chargement des données depuis BigQuery..."):
        try:
            df = client.query(query).to_dataframe()
        except Exception as e:
            st.error(f"Erreur d'exécution: {e}")
            st.stop()
    
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(df)
        with col2:
            fig = px.bar(df, x='compagnie', y='rpm_total', color='rpm_total',
                         color_continuous_scale='Blues', text='meilleure_annee')
            fig.update_traces(textposition='outside', texttemplate='Année: %{text}')
            fig.update_layout(height=400)
            st.plotly_chart(fig)
        for _, row in df.iterrows():
            st.success(f"🏆 **{row['compagnie']}:** {int(row['meilleure_annee'])} avec RPM = {row['rpm_total']:,.0f}")
    else:
        st.error("Aucune donnée trouvée")

# ============================================
# QUESTION 4: CROISSANCE ASM
# ============================================
elif page == "📊 Croissance (ASM)":
    st.markdown("## 📊 Question 4: Meilleure année pour la croissance (Available Seat Miles)")
    st.markdown("*Indicateur: AVG(ASM_Domestic) par compagnie et par année*")
    
    query = f"""
    WITH yearly_avg AS (
        SELECT 
            Airline_Code AS compagnie,
            Annee,
            AVG(ASM_Domestic) AS avg_asm
        FROM `{PROJECT_ID}.{DATASET_ID}.flight_summary_data`
        WHERE ASM_Domestic IS NOT NULL
        GROUP BY Airline_Code, Annee
    ),
    ranked AS (
        SELECT 
            compagnie,
            Annee,
            avg_asm,
            ROW_NUMBER() OVER (PARTITION BY compagnie ORDER BY avg_asm DESC) AS rang
        FROM yearly_avg
    )
    SELECT 
        compagnie,
        Annee AS meilleure_annee,
        ROUND(avg_asm, 2) AS avg_asm
    FROM ranked
    WHERE rang = 1
    ORDER BY compagnie;
    """
    
    with st.spinner("Chargement des données depuis BigQuery..."):
        try:
            df = client.query(query).to_dataframe()
        except Exception as e:
            st.error(f"Erreur d'exécution: {e}")
            st.stop()
    
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(df)
        with col2:
            fig = px.bar(df, x='compagnie', y='avg_asm', color='avg_asm',
                         color_continuous_scale='Blues', text='meilleure_annee')
            fig.update_traces(textposition='outside', texttemplate='Année: %{text}')
            fig.update_layout(height=400)
            st.plotly_chart(fig)
        for _, row in df.iterrows():
            st.success(f"🏆 **{row['compagnie']}:** {int(row['meilleure_annee'])} avec AVG_ASM = {row['avg_asm']:,.0f}")
    else:
        st.error("Aucune donnée trouvée")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>✈️ Aircraft Data Analysis | BigQuery | Streamlit & Plotly</p>", unsafe_allow_html=True)