# Projet Final : Pipeline ETL et Data Warehouse - Mexora
**Module :** Data Engineering & Business Intelligence
**Rôle :** Data Engineer Junior

---

## 1. Contexte du Projet
Mexora, une marketplace e-commerce marocaine en pleine expansion, gère actuellement ses opérations via un système transactionnel MySQL. Le besoin d'analyses rapides (Business Intelligence) pour piloter l'activité a nécessité la conception et l'implémentation d'un Data Warehouse.
Ce rapport détaille la méthodologie adoptée pour la conception du système décisionnel (modèle en étoile), l'implémentation du pipeline ETL en Python, ainsi que la restitution des KPIs.

---

## 2. Modélisation Décisionnelle (Schéma en Étoile)

L'architecture retenue est un modèle en étoile composé d'une table de fait centrale orientée autour des lignes de commandes.

### 2.1 Justification de la Granularité
La table de faits `fait_ventes` possède la granularité d'**une ligne par produit au sein d'une commande**.
* **Flexibilité Analytique** : Cela permet une agrégation multidimensionnelle au niveau du client, du produit ou de la région, sans perte d'indicateurs de composition du panier.
* **Précision** : Le chiffre d'affaires et la quantité peuvent être calculés et analysés pour des catégories spécifiques de produits.

### 2.2 Classification des Mesures (Additivité)
* **Mesures Additives** : `quantite` et `montant_total` (chiffre d'affaires). Elles peuvent être sommées librement sur toutes nos dimensions.
* **Mesures Non-additives** : `prix_unitaire`. Il ne peut pas être sommé par client ou par temps, il servira au calcul ou devra être moyenné.

### 2.3 Dimensions à Évolution Lente (SCD Type 2)
Pour assurer le suivi historique pertinent de l'évolution des entités sans ré-imputer le passé :
* **Clients** : Le "segment" d'un client (Bronze, Silver, Gold) évolue à mesure que ses dépenses s'accumulent. La commande passée l'année dernière sous le statut Bronze doit y rester attachée (même s'il est Gold aujourd'hui).
* **Produits** : Un produit peut être re-catégorisé ("Nouveauté" vers "Électronique").
* **Implémentation** : Usage de clés de substitution (`surrogate keys` automatiques) couplées avec les attributs techniques de validité : `date_debut`, `date_fin`, et un indicateur `est_actif`.

---

## 3. Architecture du Pipeline ETL (Python)

L'architecture retenue est modulaire : `config/`, `extract/`, `transform/`, `load/`, orchestrée par un script `main.py`.

### Règles de Nettoyage appliquées (`transform/cleaners.py`)
Face aux anomalies ("problèmes intentionnels") des données sources, les règles suivantes ont été codées et appliquées :
1. **Fichier Clients** : L'email a été validé par expression régulière (`regex`). Les dates de naissances aberrantes (<1920 ou >2010), génératrices de biais, ont été imputées comme valeurs manquantes (NaT). Unification sémantique systématique du genre (M ou F). La déduplication sur l'email permet de purger les comptes fantômes.
2. **Fichier Commandes** : Les identifiants de commandes dupliqués ont été supprimés. Les formats hétérogènes de dates (Y-m-d, d/m/Y, etc.) sont convertis au seul standard Pandas. Valeurs absolues appliquées aux quantités et nettoyage textuel des `statut` (ex: "DONE" -> "Livré").
3. **Fichier Produits** : Normalisation de la casse de la catégorie ("eLEctRoNiQuE" -> "Electronique"). Les prix nuls manquants ont été imputés avec la **médiane** des prix de leur catégorie respective, permettant la sauvegarde des marges de chiffre d'affaire.
4. **Chargement (`load/loader.py`)** : Pour s'adapter à une exécution sans server PostgreSQL à disposition du correcteur, un algorithme convertit dynamiquement le rendu local sur une base embarquée sans-configuration SQLite (`mexora_dwh.sqlite`), fournissant des capacités SQL immédiates.

---

## 4. KPIs et Requêtes Analytiques (Dashboarding)

Ces requêtes interrogent directement le Data Warehouse pour alimenter nos visualisations.

**Q1. Évolution du CA Mensuel avec glissement annuel (Growth YoY)**
```sql
SELECT 
    mois, annee, SUM(ca_total) AS ca_actuel,
    LAG(SUM(ca_total), 12) OVER (ORDER BY annee, mois) AS ca_annee_precedente,
    ((SUM(ca_total) - LAG(SUM(ca_total), 12) OVER (ORDER BY annee, mois)) / 
    NULLIF(LAG(SUM(ca_total), 12) OVER (ORDER BY annee, mois), 0)) * 100 AS yoy_growth_percentage
FROM reporting_mexora.mv_ca_mensuel
GROUP BY annee, mois ORDER BY annee, mois;
```

**Q2. Top 10 produits par trimestre pour la ville de Tanger**
```sql
WITH RankedProducts AS (
    SELECT p.nom AS produit, t.annee, t.trimestre, SUM(f.montant_total) AS revenu_total,
           ROW_NUMBER() OVER(PARTITION BY t.annee, t.trimestre ORDER BY SUM(f.montant_total) DESC) as rang
    FROM dwh_mexora.fait_ventes f
    JOIN dwh_mexora.dim_temps t ON f.date_id = t.date_id
    JOIN dwh_mexora.dim_region r ON f.cle_region = r.cle_region
    JOIN dwh_mexora.dim_produit p ON f.produit_sk = p.produit_sk
    WHERE r.nom_ville_standard = 'Tanger'
    GROUP BY p.nom, t.annee, t.trimestre
)
SELECT produit, annee, trimestre, revenu_total FROM RankedProducts WHERE rang <= 10 ORDER BY annee, trimestre, rang;
```

**Q3. Valeur Moyenne par Commande (AOV) par Segment Client**
```sql
SELECT c.segment, ROUND(SUM(f.montant_total) / COUNT(DISTINCT f.id_commande), 2) AS aov_panier_moyen
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_client c ON f.client_sk = c.client_sk
GROUP BY c.segment ORDER BY aov_panier_moyen DESC;
```

**Q4. Taux de retour par catégorie**
```sql
SELECT p.categorie,
       ROUND(COUNT(CASE WHEN f.statut = 'Retourné' THEN 1 END) * 100.0 / COUNT(*), 2) AS taux_retour_pourcentage
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_produit p ON f.produit_sk = p.produit_sk
GROUP BY p.categorie ORDER BY taux_retour_pourcentage DESC;
```

**Q5. Poids de l'Alimentaire pendant le Ramadan 2024**
```sql
SELECT 
    CASE WHEN t.date_complete BETWEEN '2024-03-11' AND '2024-04-09' THEN 'Pendant Ramadan' ELSE 'Hors Ramadan' END AS periode,
    SUM(f.montant_total) AS revenu_total_genere
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_temps t ON f.date_id = t.date_id
JOIN dwh_mexora.dim_produit p ON f.produit_sk = p.produit_sk
WHERE p.categorie = 'Alimentation' AND t.annee = 2024
GROUP BY periode;
```

---

## 5. Dépôt GitHub & Exécution
Le travail complet (données sources, pipeline pythons modulaire, scripts SQLs et documentations) est packagé sur le répertoire de rendu. 
* L'exécution de `python mexora_etl/main.py` déclenche le nettoyage (ETL) et la création du datamart sur le point de chute validé (la base SQlite auto-hébergée `mexora_dwh.sqlite`, solution permettant au relecteur de vérifier le résultat réel sans configuration réseau complexe).

> Repository GitHub : [A COLLER ICI LORS DE LA MISE SUR GITHUB]
