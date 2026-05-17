import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Dashboard Bac 2024", layout="wide")

st.title("🎓 Dashboard BI - Baccalauréat 2024")

# Chargement des données
try:
    # On force le séparateur ; pour ton fichier
    df = pd.read_csv("datasetbac.csv", sep=";")
    
    # Nettoyage
    df.drop_duplicates(inplace=True)
    df['EFFECTIF'] = pd.to_numeric(df['EFFECTIF'], errors='coerce').fillna(0)

    # Barre latérale (Filtre)
    region = st.sidebar.selectbox("Choisir une région :", df["CRE"].unique())
    df_selection = df[df["CRE"] == region]

    # KPI
    total = int(df_selection["EFFECTIF"].sum())
    st.metric(label=f"Total Inscrits à {region}", value=f"{total:,}")

    # Graphique
    fig = px.bar(df_selection.groupby("SECTION")["EFFECTIF"].sum().reset_index(), 
                 x="SECTION", y="EFFECTIF", color="SECTION", title="Inscrits par Branche")
    st.plotly_chart(fig, use_container_width=True)

    # Tableau final
    st.write("### Détails des données", df_selection)

except Exception as e:
    st.error(f"Erreur : {e}")