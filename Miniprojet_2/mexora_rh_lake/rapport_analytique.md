# RAPPORT : Analyse du Marché de l'Emploi IT au Maroc
**Mexora RH Intelligence — Novembre 2024**

---

## 1. RÉSUMÉ EXÉCUTIF

L'analyse de 5 000 offres d'emploi IT publiées au Maroc sur l'année 2023 et 2024 montre une expansion constante des besoins numériques, poussée par les profils orientés Web, Data et Data Engineering. Ces données, intégrées via une architecture pérenne (Data Lake), sont désormais fiables et standardisées pour Mexora.

**5 chiffres clés :**
1. Plus de **5 000** offres répertoriées avec près de **13 000** entrées en matrices de compétences, signifiant l'aspect hautement polyvalent des talents marocains.
2. Environ **30%** des offres font état d'une ligne de salaire transparente et validée.
3. Casablanca concentre l'essentiel de la demande; or, **Rabat et Tanger** connaissent un rythme d'offres en pleine croissance, dépassant parfois d'importants pôles économiques.
4. Près de la **moitié (50%)** des offres incluent une modalité distancielle (Télétravail total ou partiel).
5. Un **CDI** reste de loin le format favori sur le marché (devant le freelance).

**3 Recommandations prioritaires pour Mexora :**
- **S'aligner sur des salaires médians compétitifs** (entre 12 000 MAD et 20 000 MAD selon séniorité et technologie ciblée) pour la Data (Engineers et Analysts), tout en introduisant le télétravail hybride ou total pour séduire à l'échelle nationale.
- **Accélérer les recrutements depuis Tanger** : La ville étant en devenir numérique mais offrant un bassin moindre que Casablanca, il convient d'optimiser l'expérience candidat et l'onboarding pour ces profils en pénurie locale.
- **Miser sur une stack Python/React/SQL** dans les tests techniques, car elle correspond à la majorité du bagage attendu au Maroc.

*Horizon de mise en œuvre :* Les processus d'ajustement RH peuvent débuter sous 1 à 3 mois, notamment par un recentrage du sourcing sur les "tops" plateformes identifiées.

---

## 2. MÉTHODOLOGIE

- **Sources des données** : Scraping (fictif) de sites leaders (Rekrute, MarocAnnonce, LinkedIn). 
- **Période couverte** : Janvier 2023 à Novembre 2024.
- **Limites et biais** : Les postes cachés (non diffusés) et les salaires "selon profil" ne peuvent orienter la moyenne réelle qu'à travers une fraction lisible (≈ 30%). Les biais de sémantique (descriptions de missions hybrides) requièrent un NLP (traitement de textes) dont la finesse a des plafonds.
- **Architecture Data Lake** : Le système a été modélisé en strates :
  1. *Bronze* : Immuables, JSON bruts (Source Of Truth).
  2. *Silver* : Nettoyage, standardisation et NLP (Extraction de mots).
  3. *Gold* : Structuration en cubes DuckDB/Parquet afin de brancher n'importe quel Dashboard Analytique.

---

## 3. ÉTAT DU MARCHÉ IT AU MAROC

### Volume d'offres par profil et tendance 2023-2024
Les années 2023 et 2024 dessinent une trajectoire stable: l'explosion des besoins "Data" se ressent, les Développeurs BackEnd & FullStack monopolisent l'offre par essence tandis que de nouvelles mentions telles que DevOps (SRE) ou Cloud Engineers viennent réclamer leur place.

### Répartition Géographique (Casablanca vs Rabat vs Tanger)
- **Casablanca** agit comme l'épicentre indiscutable (Banques, assurances, sièges multinationaux, grandes ESN).
- **Rabat** conserve son rôle étatique et technopolitain. 
- **Tanger** : La région du Nord bénéficie des installations des entreprises liées à la logistique (Tanger Med) et l'automobile, engendrant une forte demande IT, quoiqu'à volume inférieur. 

### Télétravail & Types de Contrats
Le contrat **CDI** reste roi. Le *Freelance*, souvent vu comme éphémère (missions courtes), a sa niche. Le fait marquant réside dans le **Télétravail**. Les employeurs ont franchi ce cap décisif; l'hybridation (3j présentiel / 2j remote) devenant un critère d'entretien de base des candidats IT.

---

## 4. COMPÉTENCES LES PLUS DEMANDÉES

### Top 10 compétences toutes offres confondues
1. **React / Node.js** (JS) : Fortement ancré grâce aux architectures Web Modernes.
2. **Python** : Le pivot (Dev Back, Scripts, Data).
3. **SQL / PostgreSQL** : Toujours primordial pour tout ingénieur lié au socle data.
4. **Java / Spring Boot** : Socle des infrastructures lourdes bancaires marocaines.
5. **AWS & Git**.

### Compétences spécifiques aux profils Data
Pour les Data Engineers : un couplage **Python / Spark / Airflow** est régulièrement repéré, doublé des compétences Cloud comme AWS ou Hadoop.
Pour les Data Analysts : la trilogie classique se dessine: **Power BI / SQL / Tableau**.

---

## 5. ANALYSE SALARIALE

### Salaires médians par profil (Maroc vs Tanger)
Les salaires varient considérablement entre 6 000 MAD pour de jeunes juniors et plus de 30 000 MAD pour l'expertise confirmée (Cloud/Lead). 
La **médiane des statuts** "Data Engineer" orbite autour de *15 000 MAD à 18 000 MAD*.
Tanger a tendance à s'aligner sur Casablanca pour la rareté IT, mais propose parfois des packages légèrement inférieurs qui peuvent s'estomper face aux "avantages nature" (Qualité de vie/Logement).

### Corrélation expérience / salaire
En regardant la progression, nous relevons un coefficient de Pearson traduisant un bon lien: *la première année valorise très peu par rapport à l'obtention du jalon des "+3 ans"* où le gap salarial double presque (franchissement de cap vers profil "Middle").

### Les Entreprises Rémunératrices
Les profils **Banque** (BankAl, FinTech) et **Produits** (InnoSoft) s'opposent aux SSII. Les entreprises finalistes sur les produits logiciels acceptent de repousser la barre haute pour la "fidélisation".

---

## 6. RECOMMANDATIONS POUR MEXORA

Afin de monter une escouade de **5 profils data performants** à Tanger (siège) et soutenir votre croissance :

1. **Priorités RH** : Concentrer le tir pour dénicher un "Architecte Data/Senior Data Engineer" et un lead Data Scientist en premier. Ils traceront le sillon technique pour l'intégration de "Data Analysts" juniors ensuite.
2. **Attractivité Salariale (Fourchettes recommandées)** :
   - Data Engineer Confirmé : **18 000 MAD - 22 000 MAD (+ Remote)**.
   - Data Analyst Junior/Mid : **10 000 MAD - 14 000 MAD**.
   - Data Scientist (Lead) : **25 000 MAD+**.
3. **Recrutement à Tanger** : Si le bassin Tangérois ne répond pas assez vite, capitaliser sur le **Télétravail total** ciblant des candidats certifiés à Fès ou à Casa en proposant un hybride d'équipe (présence au bureau 1 semaine par mois).
4. **Fidélisation** : La fuite en Europe (freelance / remote étranger) reste le grand problème du DRH marocain. Il faut miser sur l'**intrapreneuriat**, la responsabilisation sur le Cloud, et des formations certifiantes.
