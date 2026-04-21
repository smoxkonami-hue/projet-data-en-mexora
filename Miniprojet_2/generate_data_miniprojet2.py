import json
import csv
import random
import os
from datetime import datetime, timedelta

os.makedirs('data_miniprojet2', exist_ok=True)

# 1. referentiel_competences_it.json
referentiel = {
  "familles": {
    "langages": {
      "python": ["python", "python3", "py"],
      "javascript": ["javascript", "js", "node.js", "nodejs", "node"],
      "java": ["java", "java8", "java11", "java17"],
      "sql": ["sql", "mysql", "postgresql", "postgres", "oracle", "tsql"],
      "r": ["r", "rlang", "r-studio"]
    },
    "frameworks_web": {
      "react": ["react", "reactjs", "react.js"],
      "angular": ["angular", "angularjs"],
      "django": ["django", "django rest"],
      "spring": ["spring", "spring boot", "springboot"]
    },
    "data_engineering": {
      "spark": ["spark", "apache spark", "pyspark"],
      "kafka": ["kafka", "apache kafka"],
      "airflow": ["airflow", "apache airflow"],
      "dbt": ["dbt", "data build tool"],
      "hadoop": ["hadoop", "hdfs", "mapreduce"]
    },
    "cloud": {
      "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
      "gcp": ["gcp", "google cloud", "bigquery", "cloud storage"],
      "azure": ["azure", "microsoft azure", "synapse"]
    },
    "bi_analytics": {
      "power_bi": ["power bi", "powerbi", "pbi"],
      "tableau": ["tableau", "tableau desktop"],
      "metabase": ["metabase"],
      "looker": ["looker", "looker studio"]
    }
  }
}
with open('data_miniprojet2/referentiel_competences_it.json', 'w', encoding='utf-8') as f:
    json.dump(referentiel, f, indent=4, ensure_ascii=False)


# 2. entreprises_it_maroc.csv
entreprises = [
    {"nom_entreprise": "TechMaroc SARL", "secteur": "Informatique / Télécom", "taille": "PME", "ville_siege": "Casablanca", "site_web": "techmaroc.ma", "type": "SSII"},
    {"nom_entreprise": "DataCorp", "secteur": "Informatique / Télécom", "taille": "Startup", "ville_siege": "Tanger", "site_web": "datacorp.ma", "type": "Produit"},
    {"nom_entreprise": "BankAl", "secteur": "Banque", "taille": "Grande Entreprise", "ville_siege": "Casablanca", "site_web": "bankal.ma", "type": "Banque"},
    {"nom_entreprise": "DevAgency", "secteur": "Informatique / Télécom", "taille": "PME", "ville_siege": "Rabat", "site_web": "devagency.ma", "type": "SSII"},
    {"nom_entreprise": "TelecomSA", "secteur": "Telecom", "taille": "Grande Entreprise", "ville_siege": "Rabat", "site_web": "telecomsa.ma", "type": "Telecom"},
    {"nom_entreprise": "SysAdminMaroc", "secteur": "Conseil", "taille": "ETI", "ville_siege": "Casablanca", "site_web": "sysadmin.ma", "type": "Conseil"},
    {"nom_entreprise": "InnoSoft", "secteur": "Informatique / Télécom", "taille": "Startup", "ville_siege": "Marrakech", "site_web": "innosoft.ma", "type": "Produit"},
    {"nom_entreprise": "WebSolutions", "secteur": "Informatique / Télécom", "taille": "PME", "ville_siege": "Tanger", "site_web": "websolutions.ma", "type": "SSII"},
    {"nom_entreprise": "FinTechOps", "secteur": "Banque", "taille": "Startup", "ville_siege": "Casablanca", "site_web": "fintechops.ma", "type": "Produit"},
    {"nom_entreprise": "CloudNet", "secteur": "Informatique / Télécom", "taille": "ETI", "ville_siege": "Fès", "site_web": "cloudnet.ma", "type": "SSII"}
]
with open('data_miniprojet2/entreprises_it_maroc.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=entreprises[0].keys())
    writer.writeheader()
    writer.writerows(entreprises)


# 3. offres_emploi_it_maroc.json
sources = ["rekrute", "marocannonce", "linkedin"]
titres = [
    "Développeur Full Stack React/Node.js", "Dev Data", "Ingénieur Big Data", "Data Eng.", "Développeur BI", 
    "Data Engineer Junior", "Data Analyst", "Data Scientist", "DevOps", "Architecte Cloud", 
    "Ingénieur cybersécurité", "Développeur Python", "Frontend Angular", "Backend Java Spring"
]
competences_list = [
    "React, Node.js, PostgreSQL", "Python, SQL, Tableau", "Spark, Kafka, AWS", "Python, AWS",
    "Java, Spring Boot, MySQL", "Power BI, SQL", "Django, React, Docker", "Javascript, Node.js", 
    "dbt, Airflow", "Hadoop, MapReduce", "Angular, SQL"
]
entreprises_noms = [e["nom_entreprise"] for e in entreprises]
villes_flaws = ["Casablanca", "casa", "CASABLANCA", "Rabat", "Tanger", "tanger", "TANGER", "Marrakech", "Fès"]
types_contrat = ["CDI", "cdi", "Contrat à durée indéterminée", "Permanent", "Freelance", "CDD"]
experiences = ["3-5 ans", "3 à 5 ans", "min 3 ans", "Débutant accepté", "Senior (7+ ans)", None]
salaires_brut = ["15000-20000 MAD", "15K-20K", "Selon profil", None, "Confidentiel", "2000-3000 EUR", "6000-8000 MAD", "30K-40K", "10000-15000 MAD", "25K-35K"]

offres = []
for i in range(1, 5001):
    source = random.choice(sources)
    date_pub = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 690))
    if random.random() < 0.05:
        date_exp = date_pub - timedelta(days=random.randint(1, 10))
    else:
        date_exp = date_pub + timedelta(days=random.randint(15, 60))
        
    comp = random.choice(competences_list)
    desc = f"Nous recherchons un candidat pour le poste de {random.choice(titres)} maitrisant {comp}. "
    if random.random() < 0.5:
        desc += "Missions variées en methodologie Agile."
        
    offre = {
        "id_offre": f"OFFRE-{2023 if date_pub.year == 2023 else 2024}-{str(i).zfill(5)}",
        "source": source,
        "titre_poste": random.choice(titres),
        "description": desc,
        "competences_brut": comp + (", Agile, Git" if random.random() < 0.5 else " / Linux"),
        "entreprise": random.choice(entreprises_noms) if random.random() > 0.05 else None,
        "ville": random.choice(villes_flaws),
        "type_contrat": random.choice(types_contrat),
        "experience_requise": random.choice(experiences),
        "salaire_brut": random.choice(salaires_brut),
        "niveau_etudes": random.choice(["Bac+5", "Bac+3", "Bac+2", "Autodidacte"]),
        "secteur": "Informatique / Télécom",
        "date_publication": date_pub.strftime("%Y-%m-%d"),
        "date_expiration": date_exp.strftime("%Y-%m-%d"),
        "nb_postes": random.randint(1, 5),
        "teletravail": random.choice(["Hybride", "Télétravail total", "Remote", "Présentiel"]),
        "langue_requise": ["Français", "Anglais"] if random.random() > 0.5 else ["Français"]
    }
    offres.append(offre)

with open('data_miniprojet2/offres_emploi_it_maroc.json', 'w', encoding='utf-8') as f:
    json.dump({"offres": offres}, f, indent=2, ensure_ascii=False)

print(f"5000 offres d'emploi générées dans data_miniprojet2/")
