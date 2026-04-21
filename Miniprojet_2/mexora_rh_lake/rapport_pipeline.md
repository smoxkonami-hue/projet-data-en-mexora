# Rapport de Traitement du Pipeline de Données (Data Lake)

Ce document décrit les opérations effectuées durant l'ingestion et les transformations des offres d'emploi IT depuis la zone Bronze vers Silver et Gold.

## Zone Bronze (Ingestion)
- **Règle appliquée** : Ingestion brute non modifiée. La structure initiale est archivée sous forme de fichiers JSON, classés par source et par date de publication (ex: `rekrute/2023_10/offres_raw.json`).
- **Nombres de lignes** : 5000 offres d'emplois factices ont été ingérées.
- **Cas limites contournés** : Les offres ayant des dates de publication non valides ou absentes sont poussées vers une partition générique `date_inconnue`.

## Zone Silver (Nettoyage & NLP)
L'étape Silver nettoie de nombreux champs.

### 1. Normalisation des intitulés de postes
- **Règle** : Les titres bruts sont passés "en minuscules", extraits vers une liste de mots-clés normalisés avec RegEx puis liés à un profil type via mapping arbitraire (`Data Engineer`, `Développeur Full Stack`, `Architecte Cloud`...).
- **Nombres de lignes** : Les 5000 offres ont été nettoyées, avec ~15% classées initialement en "Autre IT" (cas d'emploi de termes vagues ou exclus du mapping).
- **Cas limites contournés** : Pour préserver la compatibilité, tout statut "Autre IT" conserve les traits sources pour des recherches futures.

### 2. Normalisation des Salaires
- **Règle** : Extraction de valeur MAD via Regex, avec gestion des valeurs en "K" et conversion des Euros (Taux : 10.8). Calcul de la médiane salaire max/min.
- **Nombres de lignes** : 5000 lignes parcourues. Après calcul, environ 30% des données salariales valides (les valeurs NaN, "Selon profil" ou "Confidentiel" posent un `salaire_connu = False`).

### 3. Extraction de l'Expérience (NLP / Regex basique)
- **Règle** : Lecture de textes mentionnant "min 3 ans", "3-5 ans" ou des mots clés ("débutant", "stage"). Assignation d'un mini/max requis selon les fourchettes trouvées.

### 4. Compétences IT : Text Mining (NLP)
- **Règle** : Une fusion de la description textuelle et du brut est scannée contre un dictionnaire de compétences IT (`referentiel_competences_it.json`) sous forme d'alias regexé. L'objectif final est la recherche d'alias (Python = "py", "python").
- **Nombres de lignes** : Création d'une table "1 offre = N compétences", ayant généré un volume de `~13 000 lignes` de compétences extraites à partir des 5000 offres initiales. 100% des lignes ont au moins matché une compétence sur la donnée synthétique.

## Zone Gold (Agrégats)
La zone gold applique un lot de queries `DuckDB` pour structurer les dimensions métiers en parquets:
- **`top_competences.parquet`** : Agglomération par profil avec rang.
- **`salaires_par_profil.parquet`** : Moyennes et médianes sur statuts validés (`salaire_connu = True`).
- **`offres_par_ville.parquet`** : Regroupement et pourcentages d'offres en télétravail/hybridation par région administrative.
- **`entreprises_recruteurs.parquet`** : Top des recruteurs basé sur le volume publié en regroupant leurs différents profils cibles.
- **`tendances_mensuelles.parquet`** : Analyse de séries temporelles (`annee/mois/profil`).
