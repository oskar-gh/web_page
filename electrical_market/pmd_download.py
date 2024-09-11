import requests
import pandas as pd
from datetime import datetime, timedelta

# Función para obtener datos de la API
def get_data_from_api(url, api_key):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-api-key': api_key  # Incluye la clave API en el encabezado
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Procesar los datos en un DataFrame
def process_data(data):
    if data:
        try:
            # Mapeo de geo_id a nombre del país
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

            # Ajusta esta línea según el formato de los datos que obtienes
            values = data['indicator']['values'] if 'indicator' in data and 'values' in data['indicator'] else data
            df = pd.DataFrame(values)
            
            # Imprimir el DataFrame para depuración
            print("DataFrame inicial:", df.head())

            # Añadir columna de país
            if 'geo_id' in df.columns and 'datetime' in df.columns and 'value' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['Fecha'] = df['datetime'].dt.date
                df['Hora'] = df['datetime'].dt.hour
                df['Precio'] = df['value'].astype(float)
                df['País'] = df['geo_id'].map(geo_mapping)
                
                # Pivotar el DataFrame
                df_pivot = df.pivot_table(index=['Fecha', 'Hora'], columns='País', values='Precio')
                df_pivot.reset_index(inplace=True)
                
                return df_pivot
            else:
                print("Columnas esperadas no encontradas en los datos")
                return None
        except Exception as e:
            print(f"Error al procesar los datos: {e}")
            return None
    else:
        return None

# Crear archivos CSV
def create_csv(df, filename):
    try:
        # Especifica la ruta completa si deseas guardar en un directorio específico
        full_path = f"C:/Users/hp/Documents/Óscar/{filename}"
        df.to_csv(full_path, index=False, encoding='utf-8')
        print(f"Archivo CSV guardado en: {full_path}")
    except Exception as e:
        print(f"Error al crear el archivo CSV: {e}")

def main():
    # Clave API (asegúrate de sustituirla por la tuya)
    api_key = "fbfd13345575ac521663e367df30483d271e0a8cab8fc83ff0d61607754ddf17" 
    
    # Obtener la fecha de mañana
    #tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = (datetime.now()).strftime('%Y-%m-%d')

    # URL para el indicador de precios del mercado diario (OMIE_PMD - indicador 600)
    omiepmd_url = f"https://api.esios.ree.es/indicators/600?start_date={tomorrow}T00:00&end_date={tomorrow}T23:59"

    # Obtener y procesar datos del mercado diario (OMIE_PMD)
    omiepmd_data = get_data_from_api(omiepmd_url, api_key)
    omiepmd_df = process_data(omiepmd_data)

    if omiepmd_df is not None:
        create_csv(omiepmd_df, "precios_omiepmd.csv")
        print("Archivo precios_omiepmd.csv creado.")

if __name__ == "__main__":
    main()