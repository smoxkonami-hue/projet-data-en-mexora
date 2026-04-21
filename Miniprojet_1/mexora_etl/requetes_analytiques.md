# Requêtes Analytiques (Tableaux de Bord)

Ce document liste les requêtes SQL permettant de générer les KPIs analytiques sur l'entrepôt de données (Metabase ready).

### Q1 : Évolution Mensuelle des revenus (12 mois glissants / YoY)
**Insight** : Mesurer l’évolution globale de la capacité de Mexora à générer du CA par mois et de suivre sa croissance vs la même période l’an passé.
```sql
SELECT 
    mois,
    annee,
    SUM(ca_total) AS ca_actuel,
    LAG(SUM(ca_total), 12) OVER (ORDER BY annee, mois) AS ca_annee_precedente,
    ROUND(
      ((SUM(ca_total) - LAG(SUM(ca_total), 12) OVER (ORDER BY annee, mois)) / 
      NULLIF(LAG(SUM(ca_total), 12) OVER (ORDER BY annee, mois), 0)
      ) * 100, 2
    ) AS yoy_growth_percentage
FROM reporting_mexora.mv_ca_mensuel
GROUP BY annee, mois
ORDER BY annee, mois;
```

### Q2 : Top 10 produits par trimestre pour Tanger
**Insight** : Identifier finement, sur le créneau du nord, quels produits locaux ou populaires sont en tendance et adapter les stocks en conséquence.
```sql
WITH RankedProducts AS (
    SELECT 
        p.nom AS produit,
        t.annee,
        t.trimestre,
        SUM(f.montant_total) AS revenu_total,
        ROW_NUMBER() OVER(PARTITION BY t.annee, t.trimestre ORDER BY SUM(f.montant_total) DESC) as rang
    FROM dwh_mexora.fait_ventes f
    JOIN dwh_mexora.dim_temps t ON f.date_id = t.date_id
    JOIN dwh_mexora.dim_region r ON f.cle_region = r.cle_region
    JOIN dwh_mexora.dim_produit p ON f.produit_sk = p.produit_sk
    WHERE r.nom_ville_standard = 'Tanger'
    GROUP BY p.nom, t.annee, t.trimestre
)
SELECT produit, annee, trimestre, revenu_total
FROM RankedProducts
WHERE rang <= 10
ORDER BY annee, trimestre, rang;
```

### Q3 : Valeur Moyenne et Panier (AOV) par Segment 
**Insight** : Vérifier que notre segmentation `Silver` / `Gold` est pertinente. Concrètement, est-ce que nos clients Gold dépensent foncièrement plus _par commande_ que nos clients Bronze ?
```sql
SELECT 
    c.segment,
    ROUND(SUM(f.montant_total) / COUNT(DISTINCT f.id_commande), 2) AS aov_valeur_panier_moyen
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_client c ON f.client_sk = c.client_sk
GROUP BY c.segment
ORDER BY aov_valeur_panier_moyen DESC;
```

### Q4 : Taux de retour par catégorie
**Insight** : Trouver s'il y a une catégorie particulière de produits qui pose problème aux consommateurs (problèmes qualité "Electronique" vs problème de tailles "Mode").
```sql
SELECT 
    p.categorie,
    COUNT(CASE WHEN f.statut = 'Retourné' THEN 1 END) AS nombre_retours,
    COUNT(*) AS volume_commandes_total,
    ROUND(COUNT(CASE WHEN f.statut = 'Retourné' THEN 1 END) * 100.0 / COUNT(*), 2) AS taux_retour_pourcentage
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_produit p ON f.produit_sk = p.produit_sk
GROUP BY p.categorie
ORDER BY taux_retour_pourcentage DESC;
```

### Q5 : Poids des Ventes Alimentaires au Ramadan (2024: 11 mars - 9 avril)
**Insight** : Vérifier l'hypothèse d'une surconsommation dans l'Alimentation lors du Ramadan par rapport aux ventes courantes pour ajuster l'approvisionnement logistique.
```sql
SELECT 
    CASE 
        WHEN t.date_complete BETWEEN '2024-03-11' AND '2024-04-09' THEN 'Pendant Ramadan 2024'
        ELSE 'Hors Ramadan'
    END AS periode,
    SUM(f.quantite) AS volume_articles_vendus,
    SUM(f.montant_total) AS revenu_total_genere
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_temps t ON f.date_id = t.date_id
JOIN dwh_mexora.dim_produit p ON f.produit_sk = p.produit_sk
WHERE p.categorie = 'Alimentation' AND t.annee = 2024
GROUP BY 
    CASE 
        WHEN t.date_complete BETWEEN '2024-03-11' AND '2024-04-09' THEN 'Pendant Ramadan 2024'
        ELSE 'Hors Ramadan'
    END;
```
