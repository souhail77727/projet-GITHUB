import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuration de la page
st.set_page_config(page_title="Performance Bac 2024", layout="wide")

# 2. Chargement et fusion des données
@st.cache_data
def load_and_merge_data():
    try:
        # Lecture des fichiers
        df_inscrits = pd.read_csv("datasetbac.csv", sep=";")
        df_admis = pd.read_csv("admis-bac-2024.csv", sep=";")
        
        # Nettoyage et standardisation
        for data in [df_inscrits, df_admis]:
            data.columns = data.columns.str.strip().str.upper()
            data['EFFECTIF'] = pd.to_numeric(data['EFFECTIF'], errors='coerce').fillna(0)
            for col in ['CRE', 'SECTION', 'GENRE']:
                if col in data.columns:
                    data[col] = data[col].astype(str).str.strip().str.upper()

        # Fusion pour le calcul de performance
        df_perf = pd.merge(
            df_inscrits.groupby(['CRE', 'SECTION', 'GENRE'])['EFFECTIF'].sum().reset_index(),
            df_admis.groupby(['CRE', 'SECTION', 'GENRE'])['EFFECTIF'].sum().reset_index().rename(columns={'EFFECTIF': 'ADMIS'}),
            on=['CRE', 'SECTION', 'GENRE'], 
            how='left'
        ).fillna(0)
        
        df_perf['TAUX'] = (df_perf['ADMIS'] / df_perf['EFFECTIF'] * 100).fillna(0)
        return df_inscrits, df_perf
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        return None, None

df_inscrits, df_perf = load_and_merge_data()

if df_inscrits is not None:
    # --- FILTRES SIDEBAR ---
    st.sidebar.header("🔍 Options de filtrage")
    region = st.sidebar.selectbox("Choisir une région (CRE) :", ["TOUTES"] + sorted(df_inscrits["CRE"].unique().tolist()))
    
    # Application des filtres
    df_ins_filtered = df_inscrits.copy()
    df_perf_filtered = df_perf.copy()
    
    if region != "TOUTES":
        df_ins_filtered = df_ins_filtered[df_ins_filtered["CRE"] == region]
        df_perf_filtered = df_perf_filtered[df_perf_filtered["CRE"] == region]

    # --- TITRE ET KPI ---
    st.title("🎓 Dashboard de Performance Bac 2024")
    
    col_k1, col_k2, col_k3 = st.columns(3)
    total_ins = int(df_ins_filtered['EFFECTIF'].sum())
    total_adm = int(df_perf_filtered['ADMIS'].sum())
    
    col_k1.metric("Total Candidats", f"{total_ins:,}")
    col_k2.metric("Total Admis", f"{total_adm:,}")
    taux_global = (total_adm / total_ins * 100) if total_ins > 0 else 0
    col_k3.metric("Taux de Réussite Global", f"{taux_global:.2f} %")

    st.markdown("---")

    # --- LIGNE 1 : VOLUMES ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 1. Filières les plus choisies")
        fig1 = px.bar(df_ins_filtered.groupby("SECTION")["EFFECTIF"].sum().reset_index().sort_values("EFFECTIF", ascending=False), 
                     x="SECTION", y="EFFECTIF", color="SECTION", text_auto='.2s')
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.subheader("📊 2. Répartition des Inscrits par Genre")
        fig2 = px.pie(df_ins_filtered.groupby("GENRE")["EFFECTIF"].sum().reset_index(), values="EFFECTIF", names="GENRE", hole=0.4,
                     color_discrete_sequence=["#e74c3c", "#3498db"]) # Rouge pour F, Bleu pour M
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # --- LIGNE 2 : PERFORMANCE PAR GENRE ET SECTION ---
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("🏆 3. Taux de Réussite par Genre")
        df_genre_perf = df_perf_filtered.groupby("GENRE").agg({"EFFECTIF":"sum", "ADMIS":"sum"}).reset_index()
        df_genre_perf["TAUX"] = (df_genre_perf["ADMIS"] / df_genre_perf["EFFECTIF"] * 100)
        fig3 = px.bar(df_genre_perf, x="GENRE", y="TAUX", color="GENRE", text_auto=".1f",
                     color_discrete_map={"F": "#e74c3c", "M": "#3498db"},
                     labels={'TAUX': 'Taux de Réussite (%)'})
        st.plotly_chart(fig3, use_container_width=True)
        
    with col4:
        st.subheader("🏆 4. Taux de Réussite par Section")
        df_sec = df_perf_filtered.groupby("SECTION").agg({"EFFECTIF":"sum", "ADMIS":"sum"}).reset_index()
        df_sec["TAUX"] = (df_sec["ADMIS"] / df_sec["EFFECTIF"] * 100)
        fig4 = px.bar(df_sec, x="SECTION", y="TAUX", color="TAUX", color_continuous_scale="RdYlGn", text_auto=".1f")
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # --- LIGNE 3 : PERFORMANCE PAR RÉGION ---
    st.subheader("📍 5. Performance par Région (CRE)")
    df_reg = df_perf_filtered.groupby("CRE").agg({"EFFECTIF":"sum", "ADMIS":"sum"}).reset_index()
    df_reg["TAUX"] = (df_reg["ADMIS"] / df_reg["EFFECTIF"] * 100)
    fig5 = px.bar(df_reg.sort_values("TAUX", ascending=False), x="CRE", y="TAUX", color="TAUX", color_continuous_scale="Viridis", text_auto=".1f")
    st.plotly_chart(fig5, use_container_width=True)

    # TABLEAU DE DÉTAIL
    with st.expander("📂 Voir le détail des données fusionnées"):
        st.dataframe(df_perf_filtered, use_container_width=True)
    #python -m streamlit run newdash.py