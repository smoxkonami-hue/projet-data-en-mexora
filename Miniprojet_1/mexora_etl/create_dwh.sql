-- ==========================================
-- Etape 3 : Implémentation PostgreSQL (DWH)
-- ==========================================

-- Création des schémas
CREATE SCHEMA IF NOT EXISTS staging_mexora;
CREATE SCHEMA IF NOT EXISTS dwh_mexora;
CREATE SCHEMA IF NOT EXISTS reporting_mexora;

-- ==========================================
-- Création des tables dimensionnelles
-- ==========================================

-- 1. dim_temps
CREATE TABLE IF NOT EXISTS dwh_mexora.dim_temps (
    date_id INT PRIMARY KEY,
    date_complete DATE,
    jour INT,
    mois INT,
    annee INT,
    trimestre INT,
    jour_semaine INT,
    est_weekend BOOLEAN
);

-- 2. dim_region
CREATE TABLE IF NOT EXISTS dwh_mexora.dim_region (
    cle_region INT PRIMARY KEY,
    code_ville VARCHAR(10),
    nom_ville_standard VARCHAR(100),
    province VARCHAR(100),
    region_admin VARCHAR(100),
    zone_geo VARCHAR(50),
    population INT,
    code_postal VARCHAR(20)
);

-- 3. dim_produit (SCD Type 2)
CREATE TABLE IF NOT EXISTS dwh_mexora.dim_produit (
    produit_sk SERIAL PRIMARY KEY,
    id_produit VARCHAR(20),
    nom VARCHAR(200),
    categorie VARCHAR(100),
    prix_catalogue NUMERIC(10, 2),
    date_debut TIMESTAMP,
    date_fin TIMESTAMP,
    est_actif BOOLEAN
);

-- 4. dim_client (SCD Type 2)
CREATE TABLE IF NOT EXISTS dwh_mexora.dim_client (
    client_sk SERIAL PRIMARY KEY,
    id_client VARCHAR(20),
    nom VARCHAR(100),
    prenom VARCHAR(100),
    email VARCHAR(200),
    segment VARCHAR(50),
    ville VARCHAR(100),
    date_debut TIMESTAMP,
    date_fin TIMESTAMP,
    est_actif BOOLEAN
);

-- 5. dim_livreur
CREATE TABLE IF NOT EXISTS dwh_mexora.dim_livreur (
    livreur_sk SERIAL PRIMARY KEY,
    id_livreur INT,
    nom_livreur VARCHAR(100)
);

-- ==========================================
-- Création de la table de faits
-- ==========================================

-- 6. fait_ventes
CREATE TABLE IF NOT EXISTS dwh_mexora.fait_ventes (
    client_sk INT REFERENCES dwh_mexora.dim_client(client_sk),
    produit_sk INT REFERENCES dwh_mexora.dim_produit(produit_sk),
    livreur_sk INT REFERENCES dwh_mexora.dim_livreur(livreur_sk),
    cle_region INT REFERENCES dwh_mexora.dim_region(cle_region),
    date_id INT REFERENCES dwh_mexora.dim_temps(date_id),
    id_commande VARCHAR(50),
    quantite INT,
    prix_unitaire NUMERIC(10, 2),
    montant_total NUMERIC(10, 2),
    statut VARCHAR(50)
);

-- ==========================================
-- Optimisations / Index
-- ==========================================
CREATE INDEX idx_fait_ventes_date ON dwh_mexora.fait_ventes(date_id);
CREATE INDEX idx_fait_ventes_client ON dwh_mexora.fait_ventes(client_sk);
CREATE INDEX idx_fait_ventes_produit ON dwh_mexora.fait_ventes(produit_sk);

-- ==============================================
-- Vues matérialisées - Reporting
-- ==============================================

-- 1. mv_ca_mensuel: CA mensuel par région et catégorie
CREATE MATERIALIZED VIEW reporting_mexora.mv_ca_mensuel AS
SELECT 
    t.annee,
    t.mois,
    r.region_admin,
    p.categorie,
    SUM(f.montant_total) AS ca_total,
    COUNT(DISTINCT f.id_commande) AS nombre_commandes
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_temps t ON f.date_id = t.date_id
JOIN dwh_mexora.dim_region r ON f.cle_region = r.cle_region
JOIN dwh_mexora.dim_produit p ON f.produit_sk = p.produit_sk
GROUP BY t.annee, t.mois, r.region_admin, p.categorie;

-- 2. mv_top_produits: Top produits par trimestre
CREATE MATERIALIZED VIEW reporting_mexora.mv_top_produits AS
SELECT 
    t.annee,
    t.trimestre,
    p.nom,
    p.categorie,
    SUM(f.quantite) AS quantite_vendue,
    SUM(f.montant_total) AS ca_genere
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_temps t ON f.date_id = t.date_id
JOIN dwh_mexora.dim_produit p ON f.produit_sk = p.produit_sk
GROUP BY t.annee, t.trimestre, p.nom, p.categorie
ORDER BY ca_genere DESC;

-- 3. mv_performance_livreurs
CREATE MATERIALIZED VIEW reporting_mexora.mv_performance_livreurs AS
SELECT 
    l.nom_livreur,
    COUNT(DISTINCT f.id_commande) AS total_commandes,
    SUM(CASE WHEN f.statut = 'Livré' THEN 1 ELSE 0 END) AS commandes_livrees,
    SUM(CASE WHEN f.statut = 'Annulé' THEN 1 ELSE 0 END) AS commandes_annulees
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_livreur l ON f.livreur_sk = l.livreur_sk
GROUP BY l.nom_livreur;
