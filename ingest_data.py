#!/usr/bin/env python
import os
import pandas as pd
from sqlalchemy import create_engine
from time import time
import click
from tqdm.auto import tqdm

# Define explicit types to ensure data consistency
# (Moved outside the function for readability)
DTYPES = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

PARSE_DATES = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]


@click.command()
@click.option('--user', required=True, help='User name for postgres')
@click.option('--password', required=True, help='Password for postgres')
@click.option('--host', required=True, help='Host for postgres')
@click.option('--port', required=True, help='Port for postgres')
@click.option('--db', required=True, help='Database name for postgres')
@click.option('--table_name', required=True, help='Name of the table to write results to')
@click.option('--url', required=True, help='URL of the csv file')
def ingest_data(user, password, host, port, db, table_name, url):
    """
    Ingests CSV data from a URL into a PostgreSQL database.
    """
    
    # 1. Create the database connection
    # Note: Using f-strings for cleaner connection string formatting
    connection_string = f'postgresql+psycopg://{user}:{password}@{host}:{port}/{db}'
    engine = create_engine(connection_string)
    
    click.echo(f'Downloading and processing data from: {url}')

    # 2. Create the Iterator
    # We don't read the whole file. We prepare an iterator to read it in chunks.
    df_iter = pd.read_csv(
        url, 
        dtype=DTYPES, 
        parse_dates=PARSE_DATES, 
        iterator=True, 
        chunksize=50000
    )

    # 3. Handle the first chunk separately to create the table schema
    # We fetch the first chunk to get the column names/types correct.
    try:
        df = next(df_iter)
        
        # Create the table header (replace if exists)
        df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
        
        # Insert the first chunk
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        click.echo("Table initialized and first chunk inserted.")
        
    except StopIteration:
        click.echo("Error: The source CSV appears to be empty.")
        return

    # 4. Loop through the rest of the chunks
    # We use tqdm for a nice progress bar
    try:
        with tqdm(desc="Processing chunks") as pbar:
            for chunk in df_iter:
                t_start = time()
                
                chunk.to_sql(name=table_name, con=engine, if_exists='append', index=False)
                
                t_end = time()
                pbar.update(1)
                
        click.echo(f'Finished successfully! Data ingested into table "{table_name}".')

    except Exception as e:
        click.echo(f"An error occurred during insertion: {e}")

if __name__ == '__main__':
    ingest_data()