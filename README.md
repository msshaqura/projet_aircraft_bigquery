# ✈️ Aircraft Data Analysis Project

## 📝 Description

Ce projet analyse des données d'aviation pour répondre à quatre questions clés :
1. Quel avion a effectué le plus de vols ?
2. Quel aéroport a transporté le plus de passagers ?
3. Quelle est la meilleure année pour le Revenue Passenger-Miles (RPM) par compagnie ?
4. Quelle est la meilleure année pour la croissance (ASM) par compagnie ?

## 📊 Structure du Projet
aircraft-analysis/
│
├── data/
│ └── aircraft_db.sql # Script SQL original
│
├── notebooks/
│ └── 01_aircraft_analysis.ipynb # Notebook d'analyse
│
├── src/
│ ├── init.py
│ └── database.py # Module de connexion PostgreSQL
│
├── results/
│ ├── aircraft_clean.csv
│ ├── airlines_clean.csv
│ ├── airports_clean.csv
│ ├── individual_flights_clean.csv
│ ├── flight_summary_clean.csv
│ ├── question1_avions.csv
│ ├── question2_aeroports.csv
│ ├── question3_rpm_best_year.csv
│ ├── question3_rpm_yearly.csv
│ ├── question4_croissance_best_year.csv
│ └── question4_croissance_yearly.csv
│
├── app/
│ └── streamlit_app.py # Dashboard interactif (à créer)
│
├── .env # Variables d'environnement
├── .gitignore
├── requirements.txt
└── README.md


## 🚀 Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/msshaqura/aircraft-analysis.git
cd aircraft-analysis

2. Créer et activer l'environnement virtuel
python -m venv venv_aircraft
source venv_aircraft/bin/activate  # Sur Mac/Linux
venv_aircraft\Scripts\activate     # Sur Windows

3. Installer les dépendances
pip install -r requirements.txt

4. Configurer la base de données
Créer une base de données PostgreSQL nommée aircraft_db

Exécuter le script data/aircraft_db.sql

Créer un fichier .env avec :
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aircraft_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe

5. Exécuter l'analyse
jupyter notebook notebooks/01_aircraft_analysis.ipynb

📈 Résultats des Analyses
Question 1: Avion ayant effectué le plus de vols
Avion	Code	Nombre de vols	Pourcentage
Goose	g72	1,008	44.4%
Thundercat	t10	553	24.4%
Miniflock	12a	277	12.2%
Question 2: Aéroport ayant transporté le plus de passagers
Aéroport	Code	Passagers	Pourcentage
Amazon Mothership	AMP	2,423,400	39.6%
Nestland Airport	NSA	1,999,700	32.7%
Flocktopia	FKT	1,685,200	27.6%
Question 3: Meilleure année pour le RPM par compagnie
Compagnie	Année	RPM Domestic	RPM International	RPM Total
AA	2015	9,175,044	2,737,550	11,912,594
FA	2016	13,405,774	3,912,894	17,318,668
GA	2016	34,637,841	14,622,381	49,260,222
Question 4: Meilleure année pour la croissance (AVG ASM)
Compagnie	Année	AVG ASM Domestic
AA	2002	315,931
FA	2016	427,255
GA	2016	1,100,640
📁 Fichiers CSV Exportés
Tous les résultats sont disponibles dans le dossier results/ au format CSV, prêts à être utilisés dans d'autres outils d'analyse.

🛠️ Technologies Utilisées
Python 3.9+

PostgreSQL - Base de données

Pandas - Manipulation des données

Jupyter Notebook - Analyse exploratoire

Streamlit - Dashboard interactif (à venir)

📝 Auteur
[Mohammed SHAQURA]

📄 Licence
MIT