import os
from pipeline.bronze_ingestion import ingerer_bronze
from pipeline.silver_transform import charger_depuis_bronze, executer_transformations
from pipeline.silver_nlp import extraire_competences, sauvegarder_silver
from pipeline.gold_aggregation import construire_gold

def main():
    print("=" * 50)
    print(" Démarrage du Pipeline Mexora RH - Data Lake")
    print("=" * 50)

    data_lake_root = "data_lake"
    source_file = "../data_miniprojet2/offres_emploi_it_maroc.json"
    referentiel_file = "../data_miniprojet2/referentiel_competences_it.json"

    # BRONZE
    print("\n--- ÉTAPE 1 : INGESTION BRONZE ---")
    ingerer_bronze(source_file, data_lake_root)

    # SILVER
    print("\n--- ÉTAPE 2 : TRANSFORMATION SILVER ---")
    df_raw = charger_depuis_bronze(data_lake_root)
    df_clean = executer_transformations(df_raw)
    
    # NLP
    print("\n--- ÉTAPE 3 : EXTRACTION NLP ---")
    df_competences = extraire_competences(df_clean, referentiel_file)
    sauvegarder_silver(df_clean, df_competences, data_lake_root)

    # GOLD
    print("\n--- ÉTAPE 4 : AGRÉGATION GOLD ---")
    construire_gold(data_lake_root)

    print("\nPipeline terminé avec succès.")

if __name__ == "__main__":
    main()
