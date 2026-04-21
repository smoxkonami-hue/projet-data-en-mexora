import pandas as pd
from datetime import datetime

def build_dim_temps(df_commandes):
    """
    Creates the Time dimension from the date range in commands.
    """
    # Ensure datetime format just in case
    df_commandes['date_commande'] = pd.to_datetime(df_commandes['date_commande'])
    min_date = df_commandes['date_commande'].min()
    max_date = df_commandes['date_commande'].max()
    
    # Generate continuous date range
    date_range = pd.date_range(start=min_date, end=max_date)
    dim_temps = pd.DataFrame({
        'date_id': date_range.strftime('%Y%m%d').astype(int),
        'date_complete': date_range,
        'jour': date_range.day,
        'mois': date_range.month,
        'annee': date_range.year,
        'trimestre': date_range.quarter,
        'jour_semaine': date_range.dayofweek + 1,  # mapping 1-7
        'est_weekend': date_range.dayofweek >= 5
    })
    return dim_temps

def build_dim_region(df_regions, df_commandes):
    """
    Creates the Region dimension and defines a surrogate key.
    """
    dim_region = df_regions.copy()
    dim_region.reset_index(drop=True, inplace=True)
    dim_region['cle_region'] = dim_region.index + 1
    return dim_region

def build_dim_client_scd(df_clients, df_commandes):
    """
    Creates the Client dimension handling Slowly Changing Dimensions Type 2
    and defining the Gold/Silver/Bronze tiers based on total amount spent.
    (Simplified initial load approach)
    """
    # Compute total spend per client to proxy their current tier segmentation
    spend_per_client = df_commandes.groupby('id_client')['prix_unitaire'].sum() * df_commandes.groupby('id_client')['quantite'].sum()
    
    def assign_segment(ca):
        if pd.isna(ca): return 'Bronze'
        if ca >= 5000: return 'Gold'
        elif ca >= 1000: return 'Silver'
        else: return 'Bronze'
        
    df_clients = df_clients.copy()
    df_clients['segment'] = df_clients['id_client'].map(spend_per_client).apply(assign_segment)
    
    # SCD 2 Columns definition
    df_clients['client_sk'] = range(1, len(df_clients) + 1)
    df_clients['date_debut'] = datetime(1900, 1, 1)
    df_clients['date_fin'] = datetime(9999, 12, 31)
    df_clients['est_actif'] = True
    
    return df_clients[['client_sk', 'id_client', 'nom', 'prenom', 'email', 'segment', 'ville', 'date_debut', 'date_fin', 'est_actif']]

def build_dim_produit_scd(df_produits):
    """
    Creates the Product dimension supporting SCD Type 2.
    """
    df_produits = df_produits.copy()
    
    # SCD 2 Surrogate key generation
    df_produits['produit_sk'] = range(1, len(df_produits) + 1)
    df_produits['date_debut'] = datetime(1900, 1, 1)
    df_produits['date_fin'] = datetime(9999, 12, 31)
    df_produits['est_actif'] = True
    
    return df_produits[['produit_sk', 'id_produit', 'nom', 'categorie', 'prix_catalogue', 'date_debut', 'date_fin', 'est_actif']]

def build_dim_livreur(df_commandes):
    """
    Creates the Delivery person dimension directly derived from orders presence.
    """
    livreurs = df_commandes['id_livreur'].unique()
    dim_livreur = pd.DataFrame({'id_livreur': livreurs})
    dim_livreur['nom_livreur'] = 'Livreur ' + dim_livreur['id_livreur'].astype(str)
    dim_livreur.loc[dim_livreur['id_livreur'] == -1, 'nom_livreur'] = 'Inconnu'
    
    dim_livreur['livreur_sk'] = range(1, len(dim_livreur) + 1)
    return dim_livreur

def build_fait_ventes(df_cmd, dim_temps, dim_client, dim_produit, dim_region, dim_livreur):
    """
    Builds the main Fact Table using surrogate keys from dimensions
    and handles fact-specific business logics (total price).
    """
    fact = df_cmd.copy()
    
    fact['date_id'] = fact['date_commande'].dt.strftime('%Y%m%d').astype(int)
    
    # Merges to fetch Surrogate Keys
    fact = fact.merge(dim_client[['id_client', 'client_sk']], on='id_client', how='inner')
    fact = fact.merge(dim_produit[['id_produit', 'produit_sk', 'prix_catalogue']], on='id_produit', how='inner')
    fact = fact.merge(dim_livreur[['id_livreur', 'livreur_sk']], on='id_livreur', how='inner')
    
    # Impute missing/0 price unit values fetching strictly from dim product catalog pricing
    fact.loc[fact['prix_unitaire'] == 0, 'prix_unitaire'] = fact['prix_catalogue']
    fact['montant_total'] = fact['quantite'] * fact['prix_unitaire']
    
    # Standardize city names referencing regions dimension to pick final regional sk
    def map_ville(v):
        v = str(v).lower()
        if any(substring in v for substring in ['tng', 'tang', 'tnja']): return 'TNG'
        if any(substring in v for substring in ['cas', 'cbl']): return 'CAS'
        if any(substring in v for substring in ['rab', 'rbat']): return 'RBA'
        if any(substring in v for substring in ['aga']): return 'AGA'
        return 'CAS' # default imputation
        
    fact['code_ville_mapped'] = fact['ville_livraison'].apply(map_ville)
    fact = fact.merge(dim_region[['code_ville', 'cle_region']], left_on='code_ville_mapped', right_on='code_ville', how='inner')
    
    fact = fact[['client_sk', 'produit_sk', 'livreur_sk', 'cle_region', 'date_id', 'id_commande', 'quantite', 'prix_unitaire', 'montant_total', 'statut']]
    return fact
