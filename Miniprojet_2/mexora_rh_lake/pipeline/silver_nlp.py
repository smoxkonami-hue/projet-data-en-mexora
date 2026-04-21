import pandas as pd
import json
import re
from pathlib import Path

def extraire_competences(df: pd.DataFrame, referentiel_path: str) -> pd.DataFrame:
    """Extrait les compétences IT depuis texte libre."""
    with open(referentiel_path, 'r', encoding='utf-8') as f:
        referentiel = json.load(f)
        
    dict_competences = {}
    for famille, competences in referentiel['familles'].items():
        for nom_normalise, aliases in competences.items():
            for alias in aliases:
                dict_competences[alias.lower()] = {
                    'competence': nom_normalise,
                    'famille': famille
                }
                
    aliases_tries = sorted(dict_competences.keys(), key=len, reverse=True)
    resultats = []
    
    for _, offre in df.iterrows():
        texte_complet = ' '.join(filter(None, [
            str(offre.get('competences_brut', '') or ''),
            str(offre.get('description', '') or '')
        ])).lower()
        
        competences_trouvees = set()
        for alias in aliases_tries:
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, texte_complet):
                info = dict_competences[alias]
                cle = info['competence']
                if cle not in competences_trouvees:
                    competences_trouvees.add(cle)
                    resultats.append({
                        'id_offre':      offre['id_offre'],
                        'profil':        offre.get('profil_normalise'),
                        'ville':         offre.get('ville_std'),
                        'competence':    info['competence'],
                        'famille':       info['famille'],
                        'date_pub':      offre.get('date_publication'),
                        'annee':         str(offre.get('date_publication', ''))[:4],
                        'mois':          str(offre.get('date_publication', ''))[5:7],
                    })
        if not competences_trouvees:
            resultats.append({
                'id_offre':      offre['id_offre'],
                'profil':        offre.get('profil_normalise'),
                'ville':         offre.get('ville_std'),
                'competence':    'non_détecté',
                'famille':       'inconnu',
                'date_pub':      offre.get('date_publication'),
                'annee':         str(offre.get('date_publication', ''))[:4],
                'mois':          str(offre.get('date_publication', ''))[5:7],
            })
            
    df_competences = pd.DataFrame(resultats)
    nb_offres_avec = df_competences[df_competences['competence'] != 'non_détecté']['id_offre'].nunique()
    print(f"[SILVER NLP] {len(df_competences)} lignes compétences extraites")
    print(f"[SILVER NLP] {nb_offres_avec}/{len(df)} offres ont au moins 1 compétence")
    return df_competences

def sauvegarder_silver(df_offres: pd.DataFrame, df_competences: pd.DataFrame, data_lake_root: str):
    """Sauvegarde les données Silver au format Parquet."""
    silver_path = Path(data_lake_root) / 'silver'
    
    chemin_offres = silver_path / 'offres_clean' / 'offres_clean.parquet'
    chemin_offres.parent.mkdir(parents=True, exist_ok=True)
    df_offres.drop(columns=['date_pub_dt'], errors='ignore').to_parquet(chemin_offres, index=False, engine='pyarrow')
    print(f"[SILVER] offres_clean.parquet sauvegardé")

    chemin_comp = silver_path / 'competences_extraites' / 'competences.parquet'
    chemin_comp.parent.mkdir(parents=True, exist_ok=True)
    df_competences.to_parquet(chemin_comp, index=False, engine='pyarrow')
    print(f"[SILVER] competences.parquet sauvegardé")
