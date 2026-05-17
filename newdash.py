import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================================
# 1. CONFIGURATION DE LA PAGE
# ======================================================
# Définit le titre affiché dans l’onglet du navigateur
# et utilise toute la largeur de la page
st.set_page_config(page_title="Performance Bac 2024", layout="wide")


# ======================================================
# 2. CHARGEMENT ET FUSION DES DONNÉES
# ======================================================

# @st.cache_data permet de garder les données en mémoire
# pour éviter de recharger les fichiers à chaque interaction
@st.cache_data
def load_and_merge_data():
    try:
        # --------------------------------------------------
        # Lecture des fichiers CSV
        # --------------------------------------------------
        df_inscrits = pd.read_csv("datasetbac.csv", sep=";")
        df_admis = pd.read_csv("admis-bac-2024.csv", sep=";")
        
        # --------------------------------------------------
        # Nettoyage et standardisation des données
        # --------------------------------------------------
        for data in [df_inscrits, df_admis]:

            # Supprime les espaces et met les noms de colonnes en majuscule
            data.columns = data.columns.str.strip().str.upper()

            # Convertit EFFECTIF en nombre
            # Les erreurs sont remplacées par 0
            data['EFFECTIF'] = pd.to_numeric(
                data['EFFECTIF'],
                errors='coerce'
            ).fillna(0)

            # Nettoyage des colonnes texte
            for col in ['CRE', 'SECTION', 'GENRE']:

                # Vérifie si la colonne existe
                if col in data.columns:

                    # Supprime les espaces et met en majuscule
                    data[col] = (
                        data[col]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                    )

        # --------------------------------------------------
        # Fusion des données INSCRITS + ADMIS
        # --------------------------------------------------

        # Regroupe les inscrits par région, section et genre
        inscrits_grouped = (
            df_inscrits
            .groupby(['CRE', 'SECTION', 'GENRE'])['EFFECTIF']
            .sum()
            .reset_index()
        )

        # Regroupe les admis
        admis_grouped = (
            df_admis
            .groupby(['CRE', 'SECTION', 'GENRE'])['EFFECTIF']
            .sum()
            .reset_index()
            .rename(columns={'EFFECTIF': 'ADMIS'})
        )

        # Fusion des deux tableaux
        df_perf = pd.merge(
            inscrits_grouped,
            admis_grouped,
            on=['CRE', 'SECTION', 'GENRE'],
            how='left'
        ).fillna(0)

        # --------------------------------------------------
        # Calcul du taux de réussite
        # --------------------------------------------------
        df_perf['TAUX'] = (
            df_perf['ADMIS'] /
            df_perf['EFFECTIF'] * 100
        ).fillna(0)

        # Retourne les deux datasets
        return df_inscrits, df_perf

    except Exception as e:

        # Affiche l’erreur dans Streamlit
        st.error(f"Erreur de chargement : {e}")

        return None, None


# Appel de la fonction
df_inscrits, df_perf = load_and_merge_data()


# ======================================================
# 3. AFFICHAGE DU DASHBOARD
# ======================================================

# Vérifie que les données existent
if df_inscrits is not None:

    # --------------------------------------------------
    # FILTRES SIDEBAR
    # --------------------------------------------------
    st.sidebar.header("🔍 Options de filtrage")

    # Liste déroulante des régions
    region = st.sidebar.selectbox(
        "Choisir une région (CRE) :",
        ["TOUTES"] + sorted(df_inscrits["CRE"].unique().tolist())
    )

    # --------------------------------------------------
    # APPLICATION DES FILTRES
    # --------------------------------------------------
    df_ins_filtered = df_inscrits.copy()
    df_perf_filtered = df_perf.copy()

    # Si une région spécifique est choisie
    if region != "TOUTES":

        # Filtrage des inscrits
        df_ins_filtered = (
            df_ins_filtered[
                df_ins_filtered["CRE"] == region
            ]
        )

        # Filtrage des performances
        df_perf_filtered = (
            df_perf_filtered[
                df_perf_filtered["CRE"] == region
            ]
        )

    # --------------------------------------------------
    # TITRE PRINCIPAL
    # --------------------------------------------------
    st.title("🎓 Dashboard de Performance Bac 2024")

    # --------------------------------------------------
    # KPI (INDICATEURS PRINCIPAUX)
    # --------------------------------------------------
    col_k1, col_k2, col_k3 = st.columns(3)

    # Nombre total d’inscrits
    total_ins = int(df_ins_filtered['EFFECTIF'].sum())

    # Nombre total d’admis
    total_adm = int(df_perf_filtered['ADMIS'].sum())

    # KPI 1
    col_k1.metric("Total Candidats", f"{total_ins:,}")

    # KPI 2
    col_k2.metric("Total Admis", f"{total_adm:,}")

    # Calcul du taux global
    taux_global = (
        total_adm / total_ins * 100
    ) if total_ins > 0 else 0

    # KPI 3
    col_k3.metric(
        "Taux de Réussite Global",
        f"{taux_global:.2f} %"
    )

    st.markdown("---")

    # ==================================================
    # LIGNE 1 : ANALYSE DES INSCRITS
    # ==================================================
    col1, col2 = st.columns(2)

    # --------------------------------------------------
    # Graphique des filières
    # --------------------------------------------------
    with col1:

        st.subheader("📊 1. Filières les plus choisies")

        fig1 = px.bar(
            df_ins_filtered
            .groupby("SECTION")["EFFECTIF"]
            .sum()
            .reset_index()
            .sort_values("EFFECTIF", ascending=False),

            x="SECTION",
            y="EFFECTIF",
            color="SECTION",
            text_auto='.2s'
        )

        st.plotly_chart(fig1, use_container_width=True)

    # --------------------------------------------------
    # Graphique genre
    # --------------------------------------------------
    with col2:

        st.subheader("📊 2. Répartition des Inscrits par Genre")

        fig2 = px.pie(
            df_ins_filtered
            .groupby("GENRE")["EFFECTIF"]
            .sum()
            .reset_index(),

            values="EFFECTIF",
            names="GENRE",
            hole=0.4,

            # Couleurs personnalisées
            color_discrete_sequence=[
                "#e74c3c",
                "#3498db"
            ]
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ==================================================
    # LIGNE 2 : PERFORMANCE
    # ==================================================
    col3, col4 = st.columns(2)

    # --------------------------------------------------
    # Taux par genre
    # --------------------------------------------------
    with col3:

        st.subheader("🏆 3. Taux de Réussite par Genre")

        # Regroupement
        df_genre_perf = (
            df_perf_filtered
            .groupby("GENRE")
            .agg({
                "EFFECTIF": "sum",
                "ADMIS": "sum"
            })
            .reset_index()
        )

        # Calcul taux
        df_genre_perf["TAUX"] = (
            df_genre_perf["ADMIS"] /
            df_genre_perf["EFFECTIF"] * 100
        )

        # Graphique
        fig3 = px.bar(
            df_genre_perf,

            x="GENRE",
            y="TAUX",
            color="GENRE",
            text_auto=".1f",

            color_discrete_map={
                "F": "#e74c3c",
                "M": "#3498db"
            },

            labels={
                'TAUX': 'Taux de Réussite (%)'
            }
        )

        st.plotly_chart(fig3, use_container_width=True)

    # --------------------------------------------------
    # Taux par section
    # --------------------------------------------------
    with col4:

        st.subheader("🏆 4. Taux de Réussite par Section")

        # Regroupement
        df_sec = (
            df_perf_filtered
            .groupby("SECTION")
            .agg({
                "EFFECTIF": "sum",
                "ADMIS": "sum"
            })
            .reset_index()
        )

        # Calcul taux
        df_sec["TAUX"] = (
            df_sec["ADMIS"] /
            df_sec["EFFECTIF"] * 100
        )

        # Graphique
        fig4 = px.bar(
            df_sec,

            x="SECTION",
            y="TAUX",

            color="TAUX",
            color_continuous_scale="RdYlGn",

            text_auto=".1f"
        )

        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # ==================================================
    # LIGNE 3 : PERFORMANCE PAR RÉGION
    # ==================================================

    st.subheader("📍 5. Performance par Région (CRE)")

    # Regroupement des données
    df_reg = (
        df_perf_filtered
        .groupby("CRE")
        .agg({
            "EFFECTIF": "sum",
            "ADMIS": "sum"
        })
        .reset_index()
    )

    # Calcul taux
    df_reg["TAUX"] = (
        df_reg["ADMIS"] /
        df_reg["EFFECTIF"] * 100
    )

    # Graphique
    fig5 = px.bar(
        df_reg.sort_values("TAUX", ascending=False),

        x="CRE",
        y="TAUX",

        color="TAUX",
        color_continuous_scale="Viridis",

        text_auto=".1f"
    )

    st.plotly_chart(fig5, use_container_width=True)

    # ==================================================
    # TABLEAU DES DONNÉES
    # ==================================================

    # Zone dépliable
    with st.expander("📂 Voir le détail des données fusionnées"):

        # Affichage du dataframe
        st.dataframe(
            df_perf_filtered,
            use_container_width=True
        )

# ======================================================
# COMMANDE D’EXÉCUTION
# ======================================================

# Exécuter le projet avec :
# python -m streamlit run newdash.py