# Mexora RH Intelligence - Data Lake & Analyse du Marché de l'Emploi IT

Ce miniprojet met en place un pipeline de données pour récupérer, nettoyer et enrichir les données des offres d'emploi IT au Maroc, afin de les rendre exploitables à des fins analytiques (Data Lake : Bronze -> Silver -> Gold).

## Structure du Projet

```text
mexora_rh_lake/
├── pipeline/
│   ├── bronze_ingestion.py      # Chargement brut dans la zone Bronze
│   ├── silver_transform.py      # Nettoyage et standardisation → Silver
│   ├── silver_nlp.py            # Extraction de compétences (NLP) → Silver
│   ├── gold_aggregation.py      # Calcul des agrégats → Gold
│   └── __init__.py              
├── analysis/
│   └── analyse_marche_it_maroc.ipynb # Notebook interactif d'analyse avec graphiques
├── data_lake/                   # Répertoire principal du Data Lake généré en local (Bronze/Silver/Gold)
├── main.py                      # Orchestrateur du pipeline
├── rapport_pipeline.md          # Documentation sur les règles de transformations et NLP
├── README.md                    # Instructions de déploiement (vous êtes ici)
└── requirements.txt             # Dépendances Python
```

## Instructions pour reproduire le pipeline

1. **Environnement virtuel (Optionnel mais recommandé)**
   ```sh
   python -m venv venv
   source venv/Scripts/activate  # Sur Windows
   ```

2. **Installation des dépendances**
   ```sh
   pip install -r requirements.txt
   ```

3. **Exécution du Pipeline**
   Pour ingérer, nettoyer, appliquer le NLP et aggréger les métriques dans le Data Lake, lancez le fichier `main.py` à la racine :
   ```sh
   python main.py
   ```
   *Ceci générera les différentes couches (bronze, silver, gold) dans le dossier dynamique `data_lake/`.*

4. **Analyse de Marché Interactive**
   Ouvrez le notebook Jupyter situé sous `analysis/analyse_marche_it_maroc.ipynb` pour consulter l'analyse :
   ```sh
   jupyter notebook analysis/analyse_marche_it_maroc.ipynb
   ```
