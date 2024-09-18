import requests
import pandas as pd
import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
from utils.utils import create_csv_inlocal, create_csv_inbuffer
from ree_request import get_data_from_api

def pmd_download():
    # Get tomorrow's date
    if datetime.now().hour >= 15:
        target_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        target_date = (datetime.now()).strftime('%Y-%m-%d')
    
    # URL for daily market price indicator (OMIE_PMD - indicator 600)
    omiepmd_url = f"https://api.esios.ree.es/indicators/600?start_date={target_date}T00:00&end_date={target_date}T23:59"

    # Obtain and process daily market data
    omiepmd_data = get_data_from_api(omiepmd_url)
    omiepmd_df = process_data(omiepmd_data)

    if omiepmd_df is not None:
        #create_csv_inlocal(omiepmd_df,"C:/Users/hp/Documents/Óscar","precios_omiepmd.csv")
        csv_buffer = create_csv_inbuffer(omiepmd_df)
        return csv
        print("File 'prices_omiepmd.csv' created.")

# Process data in a DataFrame
def process_data(data):
    if data:
        try:
            # Mapping geo_id to country name
            geo_mapping = {
                1: "Portugal",
                2: "Francia",
                3: "España",
                8824: "Reino Unido",
                8825: "Italia",
                8826: "Alemania",
                8827: "Bélgica",
                8828: "Países Bajos"
            }

            values = data['indicator']['values'] if 'indicator' in data and 'values' in data['indicator'] else data
            df = pd.DataFrame(values)
            
            # Print the DataFrame for debugging
            # print("DataFrame inicial:", df.head())

            # Add country column
            if 'geo_id' in df.columns and 'datetime' in df.columns and 'value' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['Fecha'] = df['datetime'].dt.date
                df['Hora'] = df['datetime'].dt.hour
                df['Precio'] = df['value'].astype(float)
                df['País'] = df['geo_id'].map(geo_mapping)
                
                # Pivot the DataFrame
                df_pivot = df.pivot_table(index=['Fecha', 'Hora'], columns='País', values='Precio')
                df_pivot.reset_index(inplace=True)
                
                return df_pivot
            else:
                print("Expected columns not found in data")
                return None
        except Exception as e:
            print(f"Error processing data: {e}")
            return None
    else:
        return None