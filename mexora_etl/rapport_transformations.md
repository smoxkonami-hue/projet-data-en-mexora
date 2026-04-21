# Rapport de Transformations (ETL Pipeline)

## 1. Description Générale
Le pipeline s'articule autour de l'architecture d'un projet professionnel avec le découpage classique:
- **`config/`** : Modération des chemins et des configurations (URI de la DB).
- **`extract/`** : Chargement des fichiers sources vers des objets DataFrame.
- **`transform/`** : Nettoyage métier sur les données et construction de la structure multidimensionnelle.
- **`load/`** : Chargement final en base de données.

## 2. Processus de Nettoyage appliqués (Cleaners)
Plusieurs "problèmes intentionnels" étaient présents dans les données sources. Voici comment notre layer de Cleaning (`transform/cleaners.py`) a répondu aux anomalies :

* **Fichier Clients** (`clients_mexora.csv`) :
  * **Doublons** : Nous supprimons les lignes ayant la même adresse `email` (conserve le premier id_client rattaché).
  * **Dates Invalides** : Toute date de naissance aberrante (<1920 ou >2010), issue d’erreurs de frappes intentionnels, est fixée en valeur vide (NaT) pour éviter de biaiser la moyenne de l'âge de nos clients.
  * **Emails mal formés** : Un filtre avec expression régulière (`regex`) efface tous les emails qui ne contiennent pas un '@' suivi d'un vrai domaine.
  * **Sexe** : Unification des valeurs "m", "1", "Homme" vers "M", et de "f", "0", "Femme" vers "F". Les autres valeurs tombent à "Inconnu".

* **Fichier Commandes** (`commandes_mexora.csv`) :
  * **Dates désordonnées** : Utilisation d'une fonction Python balayant 3 formats (`d/m/Y`, `Y-m-d` et `b d Y`) pour tout normaliser et harmoniser au format timestamp de Pandas.
  * **Quantités Négatives** : Redressement mathématique en appliquant une valeur absolue.
  * **Statuts** : Mapping strict de normalisation (par ex. "OK" et "DONE" ramenés à "Livré").
  * **Intégrité Référentielle** : Seuls les clients rescapés du nettoyage sont conservés dans cette table afin d’éviter l'insertion dans la structure `fait_ventes` de références sans ancrage `client_sk`.

* **Fichier Produits** (`produits_mexora.json`) :
  * **Catégorie** : Ajustement de la casse (tout en minuscules puis la 1ère lettre en majuscule).
  * **Prix manquants** : Imputation par la **médiane** des prix des objets au sein de *la même catégorie* (cela permet de ne pas chuter ou biaiser le revenu par une imputation par 0).

## 3. Construction des Dimensions (`build_dimensions.py`)

* **Génération Surrogate Keys** : Chaque entité reçoit une clé technique pour désolidariser l'entrepôt du système de production.
* **Segmentation dynamique** : Dans la dimension de clients, une logique de calcul sur le revenu historique accorde à chaque client le grade de `Bronze`, `Silver` ou `Gold` (proxy calculé).
* **Harmonisation des régions** : Dans la table des faits, les noms de villes imparfaits (`Tanja`, `Cbl`) sont associés à l'ID `cle_region` via une fonction heuristique.
* **Ventes (Fact)** : La finalité des prix est récupérée de la dimension produit si elle est à 0 dans le json des commandes de production. Le Chiffre d'affaires total est calculé juste avant d'insérer dans l'entrepôt.
