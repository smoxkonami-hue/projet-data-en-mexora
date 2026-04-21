import os

# Define the root of the ETL project and target data directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Ensure the paths are easily testable
CLIENTS_FILE = os.path.join(DATA_DIR, 'clients_mexora.csv')
COMMANDES_FILE = os.path.join(DATA_DIR, 'commandes_mexora.csv')
PRODUITS_FILE = os.path.join(DATA_DIR, 'produits_mexora.json')
REGIONS_FILE = os.path.join(DATA_DIR, 'regions_maroc.csv')

# Database connection details - Switched to local SQLite since no Postgres server is available
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), 'mexora_dwh.sqlite')
# We put it in the project root folder
DB_URI = f"sqlite:///{DB_PATH}"
