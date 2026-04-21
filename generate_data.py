import csv
import json
import random
import os
from datetime import datetime, timedelta

# Création du dossier data s'il n'existe pas
os.makedirs('data', exist_ok=True)

# ==========================================
# 1. RÉFÉRENTIEL : regions_maroc.csv
# ==========================================
regions = [
    {"code_ville": "TNG", "nom_ville_standard": "Tanger", "province": "Tanger-Assilah", "region_admin": "Tanger-Tétouan-Al Hoceima", "zone_geo": "Nord", "population": 1200000, "code_postal": "90000"},
    {"code_ville": "CAS", "nom_ville_standard": "Casablanca", "province": "Casablanca", "region_admin": "Casablanca-Settat", "zone_geo": "Centre", "population": 3500000, "code_postal": "20000"},
    {"code_ville": "RBA", "nom_ville_standard": "Rabat", "province": "Rabat", "region_admin": "Rabat-Salé-Kénitra", "zone_geo": "Centre-Nord", "population": 600000, "code_postal": "10000"},
    {"code_ville": "AGA", "nom_ville_standard": "Agadir", "province": "Agadir-Ida-Ou-Tanane", "region_admin": "Souss-Massa", "zone_geo": "Sud", "population": 450000, "code_postal": "80000"}
]

with open('data/regions_maroc.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=regions[0].keys())
    writer.writeheader()
    writer.writerows(regions)

# ==========================================
# 2. PRODUITS : produits_mexora.json
# ==========================================
categories_flaws = ["electronique", "Electronique", "ELECTRONIQUE", "Mode", "mode", "Alimentation", "alimentation"]
produits = []
for i in range(1, 51):
    cat = random.choice(categories_flaws)
    actif = random.choices([True, False], weights=[0.8, 0.2])[0]
    # Quelques prix null [cite: 1682]
    prix = round(random.uniform(50, 5000), 2) if random.random() > 0.05 else None 
    
    produits.append({
        "id_produit": f"P{str(i).zfill(3)}",
        "nom": f"Produit_Test_{i}",
        "categorie": cat,
        "sous_categorie": "Sous_Cat_Test",
        "marque": "Marque_Test",
        "fournisseur": "Fournisseur_Test",
        "prix_catalogue": prix,
        "origine_pays": random.choice(["Maroc", "Chine", "USA", "France"]),
        "date_creation": (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
        "actif": actif
    })

with open('data/produits_mexora.json', 'w', encoding='utf-8') as f:
    json.dump({"produits": produits}, f, indent=4)

# ==========================================
# 3. CLIENTS : clients_mexora.csv
# ==========================================
sexes_flaws = ["m", "f", "1", "0", "Homme", "Femme"]
villes_flaws = ["tanger", "TNG", "TANGER", "Tnja", "casa", "CASABLANCA", "cbl", "rbat", "RABAT", "Agadir"]

clients = []
for i in range(1, 10001): # 10 000 clients
    # Dates de naissance aberrantes (<0 ou >120 ans) [cite: 1687]
    if random.random() < 0.02:
        annee_naiss = random.choice([1850, 2030])
    else:
        annee_naiss = random.randint(1950, 2005)
        
    email = f"client{i}@email.com"
    # Emails mal formatés [cite: 1688]
    if random.random() < 0.05:
        email = random.choice([f"client{i}email.com", f"client{i}@", f"client{i}@email"])

    clients.append({
        "id_client": f"C{str(i).zfill(5)}",
        "nom": f"Nom_{i}",
        "prenom": f"Prenom_{i}",
        "email": email,
        "date_naissance": f"{annee_naiss}-05-15",
        "sexe": random.choice(sexes_flaws),
        "ville": random.choice(villes_flaws),
        "telephone": f"+2126{random.randint(10000000, 99999999)}",
        "date_inscription": (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 700))).strftime("%Y-%m-%d"),
        "canal_acquisition": random.choice(["Social", "Organic", "Paid", "Direct"])
    })

# Doublons (même email, id différent) [cite: 1687]
for i in range(300):
    doublon = clients[i].copy()
    doublon["id_client"] = f"C{str(10000+i).zfill(5)}"
    clients.append(doublon)

with open('data/clients_mexora.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=clients[0].keys())
    writer.writeheader()
    writer.writerows(clients)

# ==========================================
# 4. COMMANDES : commandes_mexora.csv
# ==========================================
statuts_flaws = ["livré", "annulé", "en_cours", "retourné", "OK", "KO", "DONE"]
dates_formats = ["%d/%m/%Y", "%Y-%m-%d", "%b %d %Y"] # 'Nov 15 2024'

commandes = []
for i in range(1, 50001): # 50 000 commandes
    date_cmd_obj = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 330))
    date_fmt = random.choice(dates_formats)
    date_commande = date_cmd_obj.strftime(date_fmt)
    
    # Quantités négatives [cite: 1658]
    quantite = random.randint(1, 5)
    if random.random() < 0.01: quantite = random.randint(-5, -1)
        
    # Prix unitaire à 0 [cite: 1658]
    prix_unitaire = round(random.uniform(50, 5000), 2)
    if random.random() < 0.01: prix_unitaire = 0.0
        
    # id_livreur manquant (7%) [cite: 1657]
    id_livreur = random.randint(1, 20)
    if random.random() < 0.07: id_livreur = ""

    commandes.append({
        "id_commande": f"CMD{str(i).zfill(6)}",
        "id_client": random.choice(clients)["id_client"],
        "id_produit": random.choice(produits)["id_produit"],
        "date_commande": date_commande,
        "quantite": quantite,
        "prix_unitaire": prix_unitaire,
        "statut": random.choice(statuts_flaws),
        "ville_livraison": random.choice(villes_flaws),
        "mode_paiement": random.choice(["Carte", "Espèces", "Virement"]),
        "id_livreur": id_livreur,
        "date_livraison": (date_cmd_obj + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d")
    })

# Création de doublons sur id_commande (~3%) [cite: 1656]
doublons_cmd = random.sample(commandes, 1500)
commandes.extend(doublons_cmd)

with open('data/commandes_mexora.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=commandes[0].keys())
    writer.writeheader()
    writer.writerows(commandes)

print("Succès ! Les 4 fichiers de données ont été générés dans le dossier 'data/'.")