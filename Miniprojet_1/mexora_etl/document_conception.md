# Justifications de Modélisation (Modèle en Étoile)

## 1. Justification de la Granularité
La table de faits `fait_ventes` est conçue avec la granularité suivante : **une ligne représente un produit vendu au sein d'une commande spécifique**.
Cette granularité fine, dite "ligne de commande", offre plusieurs avantages :
* **Flexibilité Analytique** : Il est possible d'agréger les données à n'importe quel niveau supérieur (par commande, client, jour, produit, ou région). Si la granularité était au niveau de la commande globale, on perdrait les détails sur les produits spécifiques achetés, rendant l'analyse des catégories ou des performances produits impossible.
* **Précision des Mesures** : Les métriques comme le chiffre d'affaires, la quantité et les remises peuvent être calculées précisément par article et croisées facilement avec la `dim_produit`.

## 2. Classification des Mesures (Additivité)
Dans le modèle d'entrepôt de données, les mesures se comportent de manière différente lorsqu'elles sont agrégées à travers les dimensions.

* **Mesures Additives** :
  * `quantite` : Peut être sommée sur toutes les dimensions (par temps, par région, par produit).
  * `montant_total` (chiffre d'affaires de la ligne) : Totalement additif. Il peut être sommé à tous les niveaux.
* **Mesures Semi-additives** :
  * Les niveaux de stocks (qui n'existent pas ici mais qui le seraient) sont typiques. Si on ajoutait un solde de fidélité client par commande, ce serait semi-additif (sommable par client mais pas par temps).
* **Mesures Non-additives** :
  * `prix_unitaire` : Vous ne pouvez pas sommer les prix unitaires de différents produits. Ils doivent être utilisés comme attributs de fait ou moyennés (AOV).
  * Les pourcentages (e.g. taux de réduction, taux de marge si inclus).

## 3. Dimensions à Évolution Lente (SCD)
Nous utilisons le **Slowly Changing Dimension Type 2 (SCD Type 2)** pour traquer les historiques, en particulier pour les tables `dim_produit` et `dim_client`.

* **Pourquoi le SCD Type 2 ?**
  * **Pour les Produits** : Si un produit change de catégorie (par exemple, de "Nouveautés" à "Électronique générale"), nous voulons que les faits (ventes) historiques soient rattachés à l'ancienne catégorie, tandis que les faits futurs seront associés à la nouvelle, permettant des rapports précis basés sur l'état du produit au moment de l'achat.
  * **Pour les Clients** : Le segment des clients (Bronze, Silver, Gold) évolue inévitablement avec leurs habitudes d'achat. Le SCD Type 2 assure que nous ne réécrivons pas le passé. Si un client passe au statut "Gold", ses achats passés resteront rattachés à son entité "Silver" de ce jour-là, gardant ainsi la base de données consistante historiquement.
* **Implémentation** : Nous utiliserons une clé de substitution (`surrogate key` générée telle que `client_sk` ou `produit_sk`) en la combinant avec `date_debut`, `date_fin`, et un flag `est_actif`.
