import pandas as pd
import sys
import os


# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
from .ree_request import get_data_from_api
#from utils.utils import create_csv_inlocal, create_csv_inbuffer

def pmd_download(start_date, end_date):
   
    start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        
    # URL for daily market price indicator (OMIE_PMD - indicator 600)
    omiepmd_url = f"https://api.esios.ree.es/indicators/600?start_date={start_date}T00:00&end_date={end_date}T23:59"

    # Obtain and process daily market data
    omiepmd_data = get_data_from_api(omiepmd_url)
    omiepmd_df = process_data(omiepmd_data)

    if omiepmd_df is not None:
        #create_csv_inlocal(omiepmd_df,"C:/Users/hp/Documents/Óscar","precios_omiepmd.csv")
        #csv_buffer = create_csv_inbuffer(omiepmd_df)
        return omiepmd_df
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
            #print("DataFrame inicial:", df.head(300))
            #print("Información del DataFrame:", df.info())

            # Add country column
            if 'geo_id' in df.columns and 'datetime' in df.columns and 'value' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime_utc']).dt.tz_convert('Europe/Madrid')
                df['Fecha'] = df['datetime'].dt.date
                df['Hora'] = df['datetime'].dt.hour + 1
                df['Horario'] = df['datetime'].apply(lambda x: 'Verano' if x.dst() != pd.Timedelta(0) else 'Invierno')
                df['Horario_orden'] = df['datetime'].apply(lambda x: 0 if x.dst() != pd.Timedelta(0) else 1).astype(int)
                df['Precio'] = df['value'].astype(float)
                df['País'] = df['geo_id'].map(geo_mapping)

                #df_sorted = df.sort_values(by=['Fecha', 'Hora', 'Horario_orden'])
                
                # Pivot the DataFrame
                df_pivot = df.pivot_table(index=['Fecha', 'Hora', 'Horario_orden', 'Horario'], columns='País', values='Precio', aggfunc='first')
                
                #print("DataFrame inicial:", df_pivot.head(300))
                
                
                # Reorder the columns, ensuring that 'Spain' is the first
                if 'España' in df_pivot.columns:
                    # Replace 'Spain' in first position
                    cols = ['España'] + [col for col in df_pivot.columns if col != 'España']
                    df_pivot = df_pivot[cols]

                
                df_pivot.reset_index(inplace=True)
                df_pivot.index = df_pivot.index + 1
                df_pivot.columns.name = "Contador Registros"
                df_pivot = df_pivot.drop(columns=['Horario_orden'])

                return df_pivot
            else:
                print("Expected columns not found in data")
                return None
        except Exception as e:
            print(f"Error processing data: {e}")
            return None
    else:
        return None