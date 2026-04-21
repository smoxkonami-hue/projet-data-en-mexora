from sqlalchemy import create_engine
import pandas as pd
import logging

def get_engine(uri):
    """
    Returns an SQLAlchemy database engine for the provided postgres URI.
    """
    return create_engine(uri)

def load_dimension(df, table_name, engine):
    """
    Loads a dimension table onto the warehouse. 
    Simulates simple Replace load approach for the initial run.
    """
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info(f"Loaded Dimension {table_name} into Postgres successfully ({len(df)} rows)")
    except Exception as e:
        logging.error(f"Failed to load dimension {table_name}: {e}")
        raise e

def load_fact(df, table_name, engine):
    """
    Loads fact table leveraging standard append logic or replacement.
    A complete robust pipeline would utilize an Upsert pattern via temp table insertions.
    """
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info(f"Loaded Fact Table {table_name} into Postgres successfully ({len(df)} rows)")
    except Exception as e:
        logging.error(f"Failed to load fact table {table_name}: {e}")
        raise e
