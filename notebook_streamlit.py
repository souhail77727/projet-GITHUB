import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# CONFIGURATION DE LA PAGE
# =====================================================
st.set_page_config(
    page_title="Dashboard Bac 2024",
    layout="wide"
)

st.title("🎓 Dashboard BI - Baccalauréat 2024")
st.markdown("---")

# =====================================================
# CHARGEMENT DES DONNÉES
# =====================================================

try:
    # Lecture du fichier CSV
    df = pd.read_csv("datasetbac.csv", sep=";")

    # =================================================
    # NETTOYAGE DES DONNÉES
    # =================================================

    # Suppression des doublons
    df.drop_duplicates(inplace=True)

    # Conversion EFFECTIF en numérique
    df['EFFECTIF'] = pd.to_numeric(
        df['EFFECTIF'],
        errors='coerce'
    ).fillna(0)

    # Nettoyage des colonnes texte
    for col in ["CRE", "SECTION", "GENRE"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    # =================================================
    # SIDEBAR - FILTRES
    # =================================================

    st.sidebar.header("🔍 Filtres")

    regions = ["TOUTES"] + sorted(df["CRE"].unique().tolist())

    region = st.sidebar.selectbox(
        "Choisir une région :",
        regions
    )

    # =================================================
    # APPLICATION DU FILTRE
    # =================================================

    if region == "TOUTES":
        df_selection = df
    else:
        df_selection = df[df["CRE"] == region]

    # =================================================
    # KPI PRINCIPAUX
    # =================================================

    total_inscrits = int(df_selection["EFFECTIF"].sum())

    total_sections = df_selection["SECTION"].nunique()

    total_regions = df_selection["CRE"].nunique()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "👨‍🎓 Total Inscrits",
        f"{total_inscrits:,}"
    )

    col2.metric(
        "📚 Nombre de Sections",
        total_sections
    )

    col3.metric(
        "📍 Nombre de Régions",
        total_regions
    )

    st.markdown("---")

    # =================================================
    # GRAPHIQUES
    # =================================================

    col4, col5 = st.columns(2)

    # -------------------------------------------------
    # Graphique 1 : Inscrits par section
    # -------------------------------------------------

    with col4:

        st.subheader("📊 Inscrits par Branche")

        df_section = (
            df_selection
            .groupby("SECTION")["EFFECTIF"]
            .sum()
            .reset_index()
            .sort_values("EFFECTIF", ascending=False)
        )

        fig = px.bar(
            df_section,
            x="SECTION",
            y="EFFECTIF",
            color="SECTION",
            text_auto=".2s"
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Graphique 2 : Répartition par genre
    # -------------------------------------------------

    with col5:

        st.subheader("👥 Répartition par Genre")

        df_genre = (
            df_selection
            .groupby("GENRE")["EFFECTIF"]
            .sum()
            .reset_index()
        )

        fig2 = px.pie(
            df_genre,
            names="GENRE",
            values="EFFECTIF",
            hole=0.4,
            color="GENRE",
            color_discrete_map={
                "F": "#ff4b4b",
                "M": "#1f77b4"
            }
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # =================================================
    # TABLEAU FINAL
    # =================================================

    st.subheader("📂 Détails des données")

    st.dataframe(
        df_selection,
        use_container_width=True
    )

# =====================================================
# GESTION DES ERREURS
# =====================================================

except Exception as e:
    st.error(f"❌ Erreur : {e}")


# =====================================================
# COMMANDE D’EXÉCUTION
# =====================================================

# python -m streamlit run app.py