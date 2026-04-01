"""
Application Streamlit pour visualiser les résultats de l'analyse
Connexion directe à BigQuery
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from google.cloud import bigquery
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Aircraft Data Analysis",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Couleurs neutres (fonctionnent en clair et sombre)
PRIMARY_BLUE = '#2C7DA0'
SECONDARY_BLUE = '#61A5C2'
ACCENT_BLUE = '#89C2D9'
DARK_GRAY = '#2C3E50'
MEDIUM_GRAY = '#5D6D7E'
LIGHT_GRAY = "#858A90"
WHITE = '#FFFFFF'

# CSS adaptable
st.markdown("""
    <style>
    .main-header {
        color: #2C7DA0;
        text-align: center;
        padding: 1rem;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .sub-header {
        color: #5D6D7E;
        text-align: center;
        padding: 0.5rem;
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# SVG de l'avion
aircraft_svg = """
<svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M21 16L14 12L21 8V16Z" fill="#2C7DA0" stroke="#2C7DA0" stroke-width="1"/>
    <path d="M14 12L3 9L2 12L3 15L14 12Z" fill="#61A5C2" stroke="#61A5C2" stroke-width="1"/>
    <path d="M14 12L17 19L14 18L12 14L14 12Z" fill="#89C2D9" stroke="#89C2D9" stroke-width="1"/>
    <circle cx="16" cy="8" r="1" fill="#FFFFFF"/>
</svg>
"""

# Titre principal
st.markdown('<div class="main-header">✈️ Aircraft Data Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analyse des vols, aéroports, RPM et croissance des compagnies aériennes</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown(aircraft_svg, unsafe_allow_html=True)
    st.markdown("### Aviation Analytics")
    st.markdown("---")
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
    
    st.markdown("### 🎯 Objectifs du projet")
    with st.expander("📋 Détail des analyses"):
        st.markdown("""
        **1. ✈️ Avions**
        - Classement des avions par nombre de vols
        
        **2. 🛬 Aéroports**
        - Classement par nombre de passagers
        - Double comptage (départ + arrivée)
        
        **3. 📈 RPM**
        - Meilleure année par compagnie
        - Évolution du RPM total
        
        **4. 📊 Croissance (ASM)**
        - Meilleure année par compagnie
        - Évolution de AVG(ASM)
        """)
    
    st.markdown("---")
    st.markdown("### 📊 Technologies")
    st.markdown("""
    | Technologie | Usage |
    |-------------|-------|
    | Python | Logique métier |
    | BigQuery | Base de données cloud |
    | Streamlit | Dashboard |
    | Plotly | Visualisation |
    | Pandas | Manipulation |
    """)

# Initialiser le client BigQuery
@st.cache_resource
def init_bigquery():
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.getenv('PROJECT_ID')
    if credentials_path and os.path.exists(credentials_path):
        return bigquery.Client.from_service_account_json(credentials_path)
    else:
        return bigquery.Client(project=project_id)

client = init_bigquery()
PROJECT_ID = os.getenv('PROJECT_ID')
DATASET_ID = os.getenv('DATASET_ID')

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
    
    with st.spinner("Chargement des données..."):
        df = client.query(query).to_dataframe()
    
    if not df.empty:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.dataframe(df, use_container_width=True)
        
        with col2:
            fig = px.bar(
                df,
                x='nombre_vols',
                y='avion',
                orientation='h',
                title='Nombre de vols par avion',
                labels={'nombre_vols': 'Nombre de vols', 'avion': 'Avion'},
                color='nombre_vols',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                height=400,
                template='plotly_white',
                font=dict(color=DARK_GRAY),
                title_font_color=PRIMARY_BLUE
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 Résumé")
        gagnant = df.iloc[0]
        total = df['nombre_vols'].sum()
        st.success(f"🏆 **Avion gagnant:** {gagnant['avion']} avec {gagnant['nombre_vols']:,} vols ({gagnant['nombre_vols']/total*100:.1f}% du total)")
    else:
        st.error("Erreur de chargement des données")

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
    
    with st.spinner("Chargement des données..."):
        df = client.query(query).to_dataframe()
    
    if not df.empty:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.dataframe(df, use_container_width=True)
        
        with col2:
            fig = px.bar(
                df,
                x='total_passagers',
                y='aeroport',
                orientation='h',
                title='Passagers transportés par aéroport',
                labels={'total_passagers': 'Nombre de passagers', 'aeroport': 'Aéroport'},
                color='total_passagers',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                height=400,
                template='plotly_white',
                font=dict(color=DARK_GRAY),
                title_font_color=PRIMARY_BLUE
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 Résumé")
        gagnant = df.iloc[0]
        st.success(f"🏆 **Aéroport gagnant:** {gagnant['aeroport']} ({gagnant['airport_code']}) avec {gagnant['total_passagers']:,} passagers")
        st.info("📌 Chaque vol compte pour l'aéroport de départ ET l'aéroport d'arrivée (double comptage)")
    else:
        st.error("Erreur de chargement des données")

# ============================================
# QUESTION 3: RPM
# ============================================
elif page == "📈 RPM":
    st.markdown("## 📈 Question 3: Meilleure année pour le Revenue Passenger-Miles (RPM)")
    st.markdown("*RPM = RPM_Domestic + RPM_International*")
    
    query_best = f"""
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
    
    query_yearly = f"""
    SELECT 
        Airline_Code AS compagnie,
        Annee,
        SUM(RPM_Domestic + COALESCE(RPM_International, 0)) AS rpm_total
    FROM `{PROJECT_ID}.{DATASET_ID}.flight_summary_data`
    GROUP BY Airline_Code, Annee
    ORDER BY compagnie, Annee;
    """
    
    with st.spinner("Chargement des données..."):
        df_best = client.query(query_best).to_dataframe()
        df_yearly = client.query(query_yearly).to_dataframe()
    
    if not df_best.empty and not df_yearly.empty:
        # Formater les nombres pour l'affichage
        df_best_display = df_best.copy()
        df_best_display['rpm_total'] = df_best_display['rpm_total'].apply(lambda x: f"{x:,.0f}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Meilleure année par compagnie")
            st.dataframe(df_best_display, use_container_width=True)
        
        with col2:
            fig = px.line(
                df_yearly,
                x='Annee',
                y='rpm_total',
                color='compagnie',
                title='Évolution du RPM Total par compagnie',
                labels={'Annee': 'Année', 'rpm_total': 'RPM Total', 'compagnie': 'Compagnie'},
                markers=True,
                color_discrete_sequence=[PRIMARY_BLUE, SECONDARY_BLUE, ACCENT_BLUE]
            )
            fig.update_layout(
                height=400,
                template='plotly_white',
                font=dict(color=DARK_GRAY),
                title_font_color=PRIMARY_BLUE
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 Résumé")
        for _, row in df_best.iterrows():
            st.success(f"🏆 **{row['compagnie']}:** Meilleure année {int(row['meilleure_annee'])} avec RPM_Total = {row['rpm_total']:,.0f}")
    else:
        st.error("Erreur de chargement des données")

# ============================================
# QUESTION 4: CROISSANCE ASM
# ============================================
elif page == "📊 Croissance (ASM)":
    st.markdown("## 📊 Question 4: Meilleure année pour la croissance (Available Seat Miles)")
    st.markdown("*Indicateur: AVG(ASM_Domestic) par compagnie et par année*")
    
    query_best = f"""
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
    
    query_yearly = f"""
    SELECT 
        Airline_Code AS compagnie,
        Annee,
        AVG(ASM_Domestic) AS avg_asm
    FROM `{PROJECT_ID}.{DATASET_ID}.flight_summary_data`
    WHERE ASM_Domestic IS NOT NULL
    GROUP BY Airline_Code, Annee
    ORDER BY compagnie, Annee;
    """
    
    with st.spinner("Chargement des données..."):
        df_best = client.query(query_best).to_dataframe()
        df_yearly = client.query(query_yearly).to_dataframe()
    
    if not df_best.empty and not df_yearly.empty:
        # Formater les nombres pour l'affichage
        df_best_display = df_best.copy()
        df_best_display['avg_asm'] = df_best_display['avg_asm'].apply(lambda x: f"{x:,.0f}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Meilleure année par compagnie")
            st.dataframe(df_best_display, use_container_width=True)
        
        with col2:
            fig = px.line(
                df_yearly,
                x='Annee',
                y='avg_asm',
                color='compagnie',
                title='Évolution de AVG(ASM) par compagnie',
                labels={'Annee': 'Année', 'avg_asm': 'AVG(ASM_Domestic)', 'compagnie': 'Compagnie'},
                markers=True,
                color_discrete_sequence=[PRIMARY_BLUE, SECONDARY_BLUE, ACCENT_BLUE]
            )
            fig.update_layout(
                height=400,
                template='plotly_white',
                font=dict(color=DARK_GRAY),
                title_font_color=PRIMARY_BLUE
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 Résumé")
        for _, row in df_best.iterrows():
            st.success(f"🏆 **{row['compagnie']}:** Meilleure année {int(row['meilleure_annee'])} avec AVG_ASM = {row['avg_asm']:,.0f}")
    else:
        st.error("Erreur de chargement des données")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>✈️ Aircraft Data Analysis Dashboard | BigQuery | Visualisation Streamlit & Plotly</p>", unsafe_allow_html=True)