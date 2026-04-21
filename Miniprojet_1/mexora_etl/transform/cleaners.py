import pandas as pd
import numpy as np
import logging

def clean_regions(df):
    """
    Cleans the regions dataset. Assumes basic deduplication.
    """
    return df.drop_duplicates()

def clean_clients(df):
    """
    Cleans the clients dataset by handling logic for duplicates, 
    anomalous dates, bad emails, and standardized genders.
    """
    initial_rows = len(df)
    
    # 1. Deduplication based on the email address (keep the first occurrence)
    df = df.drop_duplicates(subset=['email'], keep='first').copy()
    
    # 2. Anomalous dates of birth (<1920 or >2010 replaced by missing values to be handled if needed)
    df['date_naissance'] = pd.to_datetime(df['date_naissance'], errors='coerce')
    df.loc[(df['date_naissance'].dt.year < 1920) | (df['date_naissance'].dt.year > 2010), 'date_naissance'] = pd.NaT
    
    # 3. Bad email formats (regex validation)
    df = df[df['email'].str.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)]
    
    # 4. Standardizing the gender column
    def clean_sexe(val):
        val = str(val).lower().strip()
        if val in ['m', '1', 'homme']: return 'M'
        if val in ['f', '0', 'femme']: return 'F'
        return 'Inconnu'
        
    df['sexe'] = df['sexe'].apply(clean_sexe)
    
    logging.info(f"Clients cleaned: {initial_rows} -> {len(df)} rows")
    return df

def clean_produits(df):
    """
    Cleans the products dataset, handling category standardization and missing values.
    """
    initial_rows = len(df)
    
    # Clean the category text (e.g. 'eLEctRoNiQuE' -> 'Electronique')
    df['categorie'] = df['categorie'].str.lower().str.capitalize()
    
    # Impute missing prices with the median of the respective category
    df['prix_catalogue'] = df.groupby('categorie')['prix_catalogue'].transform(lambda x: x.fillna(x.median()))
    
    logging.info(f"Produits cleaned: {initial_rows} -> {len(df)} rows")
    return df

def clean_commandes(df, clients_df):
    """
    Cleans the orders dataset. Handles dates formats, negative amounts,
    0 prices, and fixes statuses.
    """
    initial_rows = len(df)
    
    # 1. Deduplication on order ID
    df = df.drop_duplicates(subset=['id_commande']).copy()
    
    # 2. Standardize dates from multiple potential formats
    def parse_date(d):
        try:
            return pd.to_datetime(d, format='%d/%m/%Y')
        except:
            pass
        try:
            return pd.to_datetime(d, format='%Y-%m-%d')
        except:
            pass
        try:
            return pd.to_datetime(d, format='%b %d %Y')
        except:
            return pd.NaT
            
    df['date_commande'] = df['date_commande'].apply(parse_date)
    
    # 3. Fix negative quantities (taking absolute value)
    df['quantite'] = df['quantite'].abs()
    
    # 4. Missing livreurs fallback to -1 (Inconnu)
    df['id_livreur'] = pd.to_numeric(df['id_livreur'], errors='coerce').fillna(-1).astype(int)
    
    # 5. Correct and standardize statuses
    mapping_status = {
        "livré": "Livré", "ok": "Livré", "done": "Livré",
        "annulé": "Annulé", "ko": "Annulé",
        "en_cours": "En cours", 
        "retourné": "Retourné"
    }
    df['statut'] = df['statut'].str.lower().map(mapping_status).fillna("Inconnu")
    
    # 6. Referential integrity checks: Only keep orders whose clients exist in cleaned dimensions
    if not clients_df.empty:
        df = df[df['id_client'].isin(clients_df['id_client'])]
    
    logging.info(f"Commandes cleaned: {initial_rows} -> {len(df)} rows")
    return df
