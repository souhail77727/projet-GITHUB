import pandas as pd

def explorer_donnees_bac(path_inscrits, path_admis):
    # Configuration de l'affichage
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    datasets = {
        "INSCRITS": pd.read_csv(path_inscrits, sep=";"),
        "ADMIS": pd.read_csv(path_admis, sep=";")
    }

    for label, df in datasets.items():
        print(f"\n{'='*20} ANALYSE DU DATASET : {label} {'='*20}")

        # 1. Aperçu et Dimensions
        print(f"\n--- Dimensions : {df.shape[0]} lignes, {df.shape[1]} colonnes")
        print("\n--- Aperçu (5 premières lignes) :")
        print(df.head(5))

        # 2. Qualité des données
        print("\n--- Analyse technique des colonnes :")
        info_df = pd.DataFrame({
            'Type': df.dtypes,
            'Valeurs Manquantes': df.isnull().sum(),
            'Valeurs Uniques': df.nunique()
        })
        print(info_df)

        print(f"\n--- Doublons détectés : {df.duplicated().sum()}")
        df.drop_duplicates(inplace=True)

        # 3. Nettoyage et Standardisation
        df['EFFECTIF'] = pd.to_numeric(df['EFFECTIF'], errors='coerce').fillna(0)
        # Nettoyage des colonnes textuelles pour la cohérence
        text_cols = ['CRE', 'SECTION', 'GENRE']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()

        # 4. Statistiques Descriptives
        print("\n--- Statistiques de l'EFFECTIF :")
        print(df['EFFECTIF'].describe())

        # 5. Analyses Métiers
        print("\n--- Répartition par Section (Top 5) :")
        print(df.groupby('SECTION')['EFFECTIF'].sum().sort_values(ascending=False).head(5))

        print("\n--- Répartition par Région (CRE) - Top 5 :")
        print(df.groupby('CRE')['EFFECTIF'].sum().sort_values(ascending=False).head(5))

        if 'GENRE' in df.columns:
            print("\n--- Répartition par Genre :")
            print(df.groupby('GENRE')['EFFECTIF'].sum())

    # 6. Analyse de Cohérence entre les deux fichiers
    print(f"\n{'='*20} ANALYSE DE COHERENCE INTER-FICHIERS {'='*20}")
    
    sections_inscrits = set(datasets["INSCRITS"]['SECTION'].unique())
    sections_admis = set(datasets["ADMIS"]['SECTION'].unique())
    
    diff = sections_inscrits.symmetric_difference(sections_admis)
    if not diff:
        print("\n[OK] Les sections sont identiques dans les deux fichiers.")
    else:
        print(f"\n[ATTENTION] Écart de nomenclature détecté dans les sections : {diff}")

    # 7. KPI de Performance Préliminaire
    total_inscrits = datasets["INSCRITS"]['EFFECTIF'].sum()
    total_admis = datasets["ADMIS"]['EFFECTIF'].sum()
    
    if total_inscrits > 0:
        taux_global = (total_admis / total_inscrits) * 100
        print(f"\n--- Performance Globale Estimée ---")
        print(f"Total Inscrits : {int(total_inscrits)}")
        print(f"Total Admis    : {int(total_admis)}")
        print(f"Taux de Réussite National : {taux_global:.2f}%")

if __name__ == "__main__":
    explorer_donnees_bac("datasetbac.csv", "admis-bac-2024.csv")