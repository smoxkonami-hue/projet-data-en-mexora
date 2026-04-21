import os
import sys

# Ensure proper package importing
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from extract import extractor
from transform import cleaners, build_dimensions
from load import loader

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("=========================================")
    logging.info("--- Début du pipeline ETL Mexora ---")
    logging.info("=========================================")
    
    # 1. Extraction
    logging.info("Extraction des données sources...")
    df_clients = extractor.extract_csv(settings.CLIENTS_FILE)
    df_commandes = extractor.extract_csv(settings.COMMANDES_FILE)
    df_produits = extractor.extract_json(settings.PRODUITS_FILE)
    df_regions = extractor.extract_csv(settings.REGIONS_FILE)
    
    if df_clients.empty or df_commandes.empty or df_produits.empty or df_regions.empty:
        logging.error("L'extraction a échoué pour au moins un fichier critique. Arrêt de l'ETL.")
        sys.exit(1)
        
    # 2. Transformation - Nettoyage
    logging.info("Nettoyage des données...")
    df_regions_clean = cleaners.clean_regions(df_regions)
    df_clients_clean = cleaners.clean_clients(df_clients)
    df_produits_clean = cleaners.clean_produits(df_produits)
    df_cmd_clean = cleaners.clean_commandes(df_commandes, df_clients_clean)
    
    # 3. Transformation - Dimensions & Faits
    logging.info("Construction des dimensions et table de faits...")
    dim_temps = build_dimensions.build_dim_temps(df_cmd_clean)
    dim_region = build_dimensions.build_dim_region(df_regions_clean, df_cmd_clean)
    dim_client = build_dimensions.build_dim_client_scd(df_clients_clean, df_cmd_clean)
    dim_produit = build_dimensions.build_dim_produit_scd(df_produits_clean)
    dim_livreur = build_dimensions.build_dim_livreur(df_cmd_clean)
    
    fait_ventes = build_dimensions.build_fait_ventes(df_cmd_clean, dim_temps, dim_client, dim_produit, dim_region, dim_livreur)
    
    # 4. Chargement en base de données
    logging.info("Chargement dans le Data Warehouse (PostgreSQL)...")
    try:
        engine = loader.get_engine(settings.DB_URI)
        loader.load_dimension(dim_temps, 'dim_temps', engine)
        loader.load_dimension(dim_region, 'dim_region', engine)
        loader.load_dimension(dim_client, 'dim_client', engine)
        loader.load_dimension(dim_produit, 'dim_produit', engine)
        loader.load_dimension(dim_livreur, 'dim_livreur', engine)
        loader.load_fact(fait_ventes, 'fait_ventes', engine)
        
        logging.info("Chargement réussi avec base de données !")
        
    except Exception as e:
        logging.warning(f"Erreur de connexion DB ({e}).")
        logging.info("Fallback : Écriture des résultats dans un dossier local (dwh_exports/)")
        
        export_dir = os.path.join(settings.BASE_DIR, 'dwh_exports')
        os.makedirs(export_dir, exist_ok=True)
        
        dim_temps.to_csv(os.path.join(export_dir, 'dim_temps.csv'), index=False)
        dim_region.to_csv(os.path.join(export_dir, 'dim_region.csv'), index=False)
        dim_client.to_csv(os.path.join(export_dir, 'dim_client.csv'), index=False)
        dim_produit.to_csv(os.path.join(export_dir, 'dim_produit.csv'), index=False)
        dim_livreur.to_csv(os.path.join(export_dir, 'dim_livreur.csv'), index=False)
        fait_ventes.to_csv(os.path.join(export_dir, 'fait_ventes.csv'), index=False)
        logging.info(f"Fichiers de secours générés dans : {export_dir}")
        
    logging.info("--- Fin du pipeline ETL ---")

if __name__ == '__main__':
    main()
