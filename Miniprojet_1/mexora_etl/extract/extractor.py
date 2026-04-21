import pandas as pd
import json
import logging

def extract_csv(filepath):
    """
    Reads a CSV file into a pandas DataFrame.
    Returns an empty DataFrame if the file doesn't exist to prevent crashing.
    """
    try:
        logging.info(f"Extracting CSV from {filepath}")
        return pd.read_csv(filepath)
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return pd.DataFrame()

def extract_json(filepath):
    """
    Reads a JSON file into a pandas DataFrame.
    Expects either a list of records or a dictionary with a 'produits' key.
    """
    try:
        logging.info(f"Extracting JSON from {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Parse based on expected Mexora structure
        if 'produits' in data:
            return pd.DataFrame(data['produits'])
        return pd.DataFrame(data)
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return pd.DataFrame()
