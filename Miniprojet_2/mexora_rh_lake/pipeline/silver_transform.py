import pandas as pd
import re
import json
from pathlib import Path

def charger_depuis_bronze(data_lake_root: str) -> pd.DataFrame:
    """Charge et consolide toutes les offres depuis la zone Bronze."""
    all_offres = []
    bronze_path = Path(data_lake_root) / 'bronze'
    for json_file in bronze_path.rglob('offres_raw.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_offres.extend(data.get('offres', []))
    df = pd.DataFrame(all_offres)
    print(f"[SILVER] {len(df)} offres chargées depuis Bronze")
    return df

def nettoyer_titres_postes(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise les intitulés de poste en familles de profils IT."""
    mapping_profils = {
        r'data\s*eng(ineer|ineer\w*|\.)?|ingénieur\s+data|dev\s+data\s+eng': 'Data Engineer',
        r'etl\s*dev|pipeline\s*dev|ingénieur\s+etl': 'Data Engineer',
        r'data\s*anal(yst|yste|ytics)|analyste?\s+data|bi\s+anal': 'Data Analyst',
        r'business\s+intel(ligence)?|ingénieur\s+bi|développeur\s+bi': 'Data Analyst',
        r'reporting\s+(anal|spec|officer)': 'Data Analyst',
        r'data\s*sci(entist|ence)|machine\s*learn|ml\s*eng|ia\s*eng': 'Data Scientist',
        r'deep\s*learn|nlp\s*eng|computer\s*vision': 'Data Scientist',
        r'full\s*stack|fullstack': 'Développeur Full Stack',
        r'back[\s-]*end|backend': 'Développeur Backend',
        r'front[\s-]*end|frontend': 'Développeur Frontend',
        r'dev(eloppeur|eloper)?\s+mobile|ios\s+dev|android\s+dev': 'Développeur Mobile',
        r'devops|sre|site\s*reliab': 'DevOps / SRE',
        r'cloud\s*(arch|eng|admin)|aws\s+eng|gcp\s+eng|azure\s+eng': 'Cloud Engineer',
        r'sys(admin|tème)|réseau\s+inf|network\s+eng': 'Admin Systèmes & Réseaux',
        r'cyber|sécurité\s+info|pentester|soc\s+anal': 'Cybersécurité',
        r'chef\s+de\s+proj(et)?|project\s+man|scrum\s*master': 'Chef de Projet IT',
        r'architect(e)?\s+(log|tech|data|cloud|sol)': 'Architecte IT',
    }
    df['profil_normalise'] = 'Autre IT'
    df['profil_source'] = df['titre_poste'].astype(str).str.lower().str.strip()
    
    for pattern, profil in mapping_profils.items():
        masque = df['profil_source'].str.contains(pattern, regex=True, na=False)
        df.loc[masque, 'profil_normalise'] = profil
        
    non_classes = (df['profil_normalise'] == 'Autre IT').sum()
    print(f"[SILVER] Titres : {non_classes} offres classées 'Autre IT' sur {len(df)}")
    return df

def normaliser_salaires(df: pd.DataFrame) -> pd.DataFrame:
    """Extrait et normalise les salaires en MAD mensuel brut."""
    TAUX_EUR_MAD = 10.8
    def parser_salaire(valeur):
        if pd.isna(valeur) or str(valeur).lower() in ['null', 'confidentiel', 'selon profil', '']:
            return None, None, False
        s = str(valeur).lower().replace(' ', '').replace('\u202f', '')
        est_eur = 'eur' in s or '€' in s
        s = s.replace('eur', '').replace('€', '').replace('mad', '').replace('dh', '')
        s = re.sub(r'(\d+(?:\.\d+)?)k', lambda m: str(int(float(m.group(1)) * 1000)), s)
        nombres = re.findall(r'\d+(?:\.\d+)?', s)
        if not nombres: return None, None, False
        montants = [float(n) for n in nombres]
        if est_eur: montants = [m * TAUX_EUR_MAD for m in montants]
        if len(montants) >= 2:
            sal_min = min(montants[:2])
            sal_max = max(montants[:2])
        else:
            sal_min = sal_max = montants[0]
        if sal_min < 3000 or sal_max > 100000:
            return None, None, False
        return sal_min, sal_max, True

    resultats = df['salaire_brut'].apply(lambda x: pd.Series(parser_salaire(x), index=['salaire_min_mad', 'salaire_max_mad', 'salaire_connu']))
    df = pd.concat([df, resultats], axis=1)
    df['salaire_median_mad'] = (df['salaire_min_mad'] + df['salaire_max_mad']) / 2
    pct_connu = df['salaire_connu'].mean() * 100
    print(f"[SILVER] Salaires : {pct_connu:.1f}% des offres ont un salaire renseigné")
    return df

def normaliser_experience(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme l'expérience en valeur numérique."""
    def parser_experience(valeur):
        if pd.isna(valeur): return None, None
        s = str(valeur).lower()
        if any(mot in s for mot in ['débutant', 'junior', 'stage', 'sans expérience']): return 0, 2
        if any(mot in s for mot in ['senior', 'confirmé', 'expert', 'lead']): return 5, None
        fourchette = re.search(r'(\d+)\s*[-àa]\s*(\d+)', s)
        if fourchette: return int(fourchette.group(1)), int(fourchette.group(2))
        min_seul = re.search(r'(\d+)\s*(?:ans?|years?)', s)
        if min_seul: return int(min_seul.group(1)), None
        return None, None

    resultats = df['experience_requise'].apply(lambda x: pd.Series(parser_experience(x), index=['experience_min_ans', 'experience_max_ans']))
    df = pd.concat([df, resultats], axis=1)
    return df

def normaliser_villes_et_contrat(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise les champs simples comme la ville, le type de contrat et la date (ajout)."""
    df['ville_std'] = df['ville'].astype(str).str.capitalize().str.strip()
    df.loc[df['ville_std'].isin(['Casa', 'Casablanca']), 'ville_std'] = 'Casablanca'
    df.loc[df['ville_std'].isin(['Tanja', 'Tanger']), 'ville_std'] = 'Tanger'
    df.loc[df['ville_std'].isin(['Rbat', 'Rabat']), 'ville_std'] = 'Rabat'
    
    df['type_contrat_std'] = df['type_contrat'].astype(str).str.upper().str.strip()
    df.loc[df['type_contrat_std'].str.contains('CDI|INDÉTERMINÉE|PERMANENT|INDEFINITE', na=False), 'type_contrat_std'] = 'CDI'
    df.loc[df['type_contrat_std'].str.contains('CDD|DÉTERMINÉE', na=False), 'type_contrat_std'] = 'CDD'
    df.loc[df['type_contrat_std'].str.contains('FREELANCE|INDEPENDANT', na=False), 'type_contrat_std'] = 'FREELANCE'

    # Extract annee and mois directly here as well to simplify
    df['date_pub_dt'] = pd.to_datetime(df['date_publication'], errors='coerce')
    df['annee'] = df['date_pub_dt'].dt.year
    df['mois'] = df['date_pub_dt'].dt.month
    
    # We also add region admin mock for the example
    regions = {
        'Casablanca': 'Casablanca-Settat',
        'Rabat': 'Rabat-Salé-Kénitra',
        'Tanger': 'Tanger-Tétouan-Al Hoceima',
        'Marrakech': 'Marrakech-Safi',
        'Fès': 'Fès-Meknès'
    }
    df['region_admin'] = df['ville_std'].map(regions).fillna('Autre')

    return df

def executer_transformations(df: pd.DataFrame) -> pd.DataFrame:
    df = nettoyer_titres_postes(df)
    df = normaliser_salaires(df)
    df = normaliser_experience(df)
    df = normaliser_villes_et_contrat(df)
    return df
