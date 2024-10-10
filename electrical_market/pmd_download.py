import pandas as pd
import sys
import os
from datetime import datetime
import calendar


# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
from .ree_request import get_data_from_api

csv_file_path = os.path.join(os.getcwd(), 'data', 'BDD_electricalmarket_PMD.csv')

def update_ree():
    ####
    #time = datetime.now()
    #print(f"Comienzo: {time}")
    ####
    
    # Verificar si el archivo existe
    if os.path.exists(csv_file_path):
        # Leer el CSV en un DataFrame
        df = pd.read_csv(csv_file_path, parse_dates=['Fecha']) 
        max_date = df['Fecha'].max() - timedelta(days=10)
    else:
        # Restar dos años a la fecha actual y fijarla al 1 de enero
        max_date = datetime(datetime.now().year - 2, 1, 1)
    
    #At the maximum ecfah, the request can be made for a maximum of 180 days.
    # Subsequently, if more is needed, the user must make a request again for 6 more months.
    start_date = max_date.date()
    end_date = start_date + timedelta(days=180)
    last_day_of_month = calendar.monthrange(end_date.year, end_date.month)[1]
    end_date = datetime(end_date.year, end_date.month, last_day_of_month).date()

    if end_date >= datetime.now().date():
        if datetime.now().hour >=15:
            end_date = datetime.now().date() + timedelta(days=1)
        else:
            end_date = datetime.now().date()
                
    print(f"Comienzo descarga PMD: {start_date}")
    print(f"Fin descarga PMD: {end_date}")
    
    if start_date > end_date:
        print("No hay datos nuevos")
        return False


    # URL for daily market price indicator (OMIE_PMD - indicator 600)
    omiepmd_url = f"https://api.esios.ree.es/indicators/600?start_date={start_date}T00:00&end_date={end_date}T23:59"

    print(omiepmd_url)
    # Obtain and process daily market data
    omiepmd_data = get_data_from_api(omiepmd_url)
    omiepmd_df = process_data(omiepmd_data)
    response = save_file(omiepmd_df)
    return response

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
                df_pivot = df_pivot.drop(columns=['Horario_orden'])

                return df_pivot
            else:
                print("Expected columns not found in data PMD")
                return None
        except Exception as e:
            print(f"Error processing data: {e}")
            return None
    else:
        return None
    
def save_file(omiepmd_df):
    response = False

    # Si el archivo existe, cargar los datos y hacer merge
    if os.path.exists(csv_file_path):
        existing_df = pd.read_csv(csv_file_path)
        
        # Unir los datos existentes con el nuevo DataFrame
        merged_df = pd.concat([existing_df, omiepmd_df], ignore_index=True)
        
        #print("DataFrame inicial:", merged_df.head(25))
        #print("DataFrame inicial:", merged_df.info())
        # Eliminar duplicados basándose en todas las columnas (o puedes especificar columnas clave)
        merged_df.drop_duplicates(subset=merged_df.columns[1:], inplace=True)# Excluyendo la primera columna de index
        
        # Guardar el DataFrame actualizado
        merged_df.to_csv(csv_file_path, index=False, encoding='utf-8')
        
        print(f"Datos actualizados y guardados en: {csv_file_path}")
    else:
        # Si no existe el archivo, guardar directamente el DataFrame recibido
        omiepmd_df.to_csv(csv_file_path, index=False, encoding='utf-8')
        
        print(f"Nuevo archivo guardado en: {csv_file_path}")

    response = True
    
    return response

def return_price(start_date, end_date, only_spain):
    
    # Check if the file exists
    if os.path.exists(csv_file_path):
        # Read the CSV into a DataFrame
        df = pd.read_csv(csv_file_path, parse_dates=['Fecha'])
        #print("DataFrame inicial:", df.head(300))
        #print("Información del DataFrame:", df.info())

        if not df.empty:
            if only_spain:
                df = df[['Fecha', 'Hora', 'Horario', 'España']].rename(columns={'España': 'PMD'})
            df_filtered = df[(df['Fecha'] >= start_date) & (df['Fecha'] <= end_date)]
            return df_filtered
        else:
            print("El archivo no existe.")
            return None
    else:
        print("El archivo no existe.")
        return None

def return_price_minandmax():
    
    if os.path.exists(csv_file_path):
        # Leer el CSV en un DataFrame
        df = pd.read_csv(csv_file_path, parse_dates=['Fecha'])  # Asume que tienes una columna 'Fecha'

        min_date = df['Fecha'].min()
        max_date = df['Fecha'].max()
        num_distinct_days = df['Fecha'].nunique()
        num_total_days = (max_date - min_date).days + 1
        label_text = f"PMD {min_date.strftime('%d/%m/%Y')}-{max_date.strftime('%d/%m/%Y')}"
        if num_total_days > num_distinct_days:
            label_text = f"{label_text}. Con huecos"

    else:
        label_text = "El archivo no existe."
    
    return label_text
