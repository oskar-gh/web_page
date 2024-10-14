import pandas as pd
import sys
import os
from datetime import datetime
import calendar


# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
from .ree_request import get_data_from_api

csv_file_path = os.path.join(os.getcwd(), 'data', 'BDD_electricalmarket_PVPC.csv')
numdaysreturn = 10
numdaysfuture = 180
monthcomplet = True

def update_ree():
    ####
    #time = datetime.now()
    #print(f"Comienzo: {time}")
    ####
    
    if os.path.exists(csv_file_path):
        df = pd.read_csv(csv_file_path, parse_dates=['Fecha']) 
        if not df.empty:
            max_date = df['Fecha'].max() - timedelta(days=numdaysreturn)
        else:
            max_date = datetime(datetime.now().year - 2, 1, 1)
    else:
        columns = ['Fecha', 'Hora', 'Horario', 'Península', 'Canarias', 'Baleares', 'Ceuta', 'Melilla']
        df_empty = pd.DataFrame(columns=columns)
        df_empty.to_csv(csv_file_path, index=False)
        max_date = datetime(datetime.now().year - 2, 1, 1)

    start_date = max_date.date()
    end_date = start_date + timedelta(days=numdaysfuture)
    if monthcomplet:
        last_day_of_month = calendar.monthrange(end_date.year, end_date.month)[1]
        end_date = datetime(end_date.year, end_date.month, last_day_of_month).date()

    if end_date >= datetime.now().date():
        if datetime.now().hour >=15:
            end_date = datetime.now().date() + timedelta(days=1)
        else:
            end_date = datetime.now().date()
    
    print(f"Comienzo descarga PVPC: {start_date}")
    print(f"Fin descarga PVPC: {end_date}")
    
    if start_date > end_date:
        print("No hay datos nuevos")
        return False


    #IMPORTANT
    #For some reason, the API works poorly for 23-hour days (only that day),
    # sometimes returning incorrect UTC date formats, which when making a pivoted table did not match the dates well. 
    #An API call is made for each system, and then a whole merge is made to store in the csv    
    #IMPORTANT

    # URL for daily market price indicator (PVPC - indicator 10391 - 8741 geo_id PENINSULA)
    pvpc_url = f"https://api.esios.ree.es/indicators/10391?start_date={start_date}T00:00&end_date={end_date}T23:59&geo_ids[]=8741"
    # Obtain and process daily market data
    pvpc_data_8741 = get_data_from_api(pvpc_url)
    pvpc_df_8741 = process_data(pvpc_data_8741)
    pvpc_url = f"https://api.esios.ree.es/indicators/10391?start_date={start_date}T00:00&end_date={end_date}T23:59&geo_ids[]=8742"
    # Obtain and process daily market data
    pvpc_data_8742 = get_data_from_api(pvpc_url)
    pvpc_df_8742 = process_data(pvpc_data_8742)
    pvpc_url = f"https://api.esios.ree.es/indicators/10391?start_date={start_date}T00:00&end_date={end_date}T23:59&geo_ids[]=8743"
    # Obtain and process daily market data
    pvpc_data_8743 = get_data_from_api(pvpc_url)
    pvpc_df_8743 = process_data(pvpc_data_8743)
    pvpc_url = f"https://api.esios.ree.es/indicators/10391?start_date={start_date}T00:00&end_date={end_date}T23:59&geo_ids[]=8744"
    # Obtain and process daily market data
    pvpc_data_8744 = get_data_from_api(pvpc_url)
    pvpc_df_8744 = process_data(pvpc_data_8744)
    pvpc_url = f"https://api.esios.ree.es/indicators/10391?start_date={start_date}T00:00&end_date={end_date}T23:59&geo_ids[]=8745"
    # Obtain and process daily market data
    pvpc_data_8745 = get_data_from_api(pvpc_url)
    pvpc_df_8745 = process_data(pvpc_data_8745)
    
    pvpc_df_8741 = pvpc_df_8741.dropna(axis=1, how='all')
    pvpc_df_8742 = pvpc_df_8742.dropna(axis=1, how='all')
    pvpc_df_8743 = pvpc_df_8743.dropna(axis=1, how='all')
    pvpc_df_8744 = pvpc_df_8744.dropna(axis=1, how='all')
    pvpc_df_8745 = pvpc_df_8745.dropna(axis=1, how='all')
    
    pvpc_df = pd.merge(pvpc_df_8741, pvpc_df_8742, on=['Fecha', 'Hora', 'Horario'], how='outer')
    #print("DataFrame inicial:", pvpc_df.head(25))
    pvpc_df = pd.merge(pvpc_df, pvpc_df_8743, on=['Fecha', 'Hora', 'Horario'], how='outer')
    #print("DataFrame inicial:", pvpc_df.head(25))
    pvpc_df = pd.merge(pvpc_df, pvpc_df_8744, on=['Fecha', 'Hora', 'Horario'], how='outer')
    #print("DataFrame inicial:", pvpc_df.head(25))
    pvpc_df = pd.merge(pvpc_df, pvpc_df_8745, on=['Fecha', 'Hora', 'Horario'], how='outer')
    #print("DataFrame inicial:", pvpc_df.head(25))

    pvpc_df = pvpc_df[['Fecha', 'Hora', 'Horario', 'Península', 'Canarias', 'Baleares', 'Ceuta', 'Melilla']]
    
    response = save_file(pvpc_df)
    return response




def process_data(data):
    if data:
        try:
            # Mapping geo_id to country name
            geo_mapping = {
                8741: "Península",
                8742: "Canarias",
                8743: "Baleares",
                8744: "Ceuta",
                8745: "Melilla"
            }

            values = data['indicator']['values'] if 'indicator' in data and 'values' in data['indicator'] else data
            df = pd.DataFrame(values)
            
            # Print the DataFrame for debugging
            #print("DataFrame inicial:", df.head(300))
            #print(df.iloc[:300].to_string())
            #print("Información del DataFrame:", df.info())

            # Add country column
            if 'geo_id' in df.columns and 'datetime' in df.columns and 'value' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime_utc']).dt.tz_convert('Europe/Madrid')
                df['Fecha'] = df['datetime'].dt.date
                df['Hora'] = df['datetime'].dt.hour + 1
                df['Horario'] = df['datetime'].apply(lambda x: 'Verano' if x.dst() != pd.Timedelta(0) else 'Invierno')
                df['Horario_orden'] = df['datetime'].apply(lambda x: 0 if x.dst() != pd.Timedelta(0) else 1).astype(int)
                df['Precio'] = df['value'].astype(float)
                df['Sistema'] = df['geo_id'].map(geo_mapping)
            
                # Pivot the DataFrame
                df_pivot = df.pivot_table(index=['Fecha', 'Hora', 'Horario_orden', 'Horario'], columns='Sistema', values='Precio', aggfunc='first')
                
                #print("DataFrame inicial:", df_pivot.head(300))
                
                df_pivot.reset_index(inplace=True)
                df_pivot = df_pivot.drop(columns=['Horario_orden'])

                return df_pivot
            else:
                print("Expected columns not found in data PVPC")
                return None
        except Exception as e:
            print(f"Error processing data: {e}")
            return None
    else:
        return None
    
    
    
def save_file(pvpc_df):

    if os.path.exists(csv_file_path):
        existing_df = pd.read_csv(csv_file_path)
        merged_df = pd.concat([existing_df, pvpc_df], ignore_index=True)
        #print("DataFrame inicial:", merged_df.head(25))
        #print("DataFrame inicial:", merged_df.info())
        # Drop duplicate
        merged_df.drop_duplicates(subset=merged_df.columns[1:], inplace=True)# Exclude first column
        merged_df.to_csv(csv_file_path, index=False, encoding='utf-8')
        print(f"Datos actualizados y guardados en: {csv_file_path}")
    else:
        pvpc_df.to_csv(csv_file_path, index=False, encoding='utf-8')
        print(f"Nuevo archivo guardado en: {csv_file_path}")
    return True



def return_price(start_date, end_date, only_peninsula):
    
    if os.path.exists(csv_file_path):
        df = pd.read_csv(csv_file_path, parse_dates=['Fecha'])  # Asume que tienes una columna 'Fecha'
        if not df.empty:
            if only_peninsula:
                df = df[['Fecha', 'Hora', 'Horario', 'Península']].rename(columns={'Península': 'PVPC'})
            df_filtered = df[(df['Fecha'] >= start_date) & (df['Fecha'] <= end_date)]
            return df_filtered
        else:
            print("El archivo no tiene datos.")
            return None
    else:
        print("El archivo no existe.")
        return None



def return_price_minandmax():
    
    if os.path.exists(csv_file_path):
        df = pd.read_csv(csv_file_path, parse_dates=['Fecha']) 
        if not df.empty:
            min_date = df['Fecha'].min()
            max_date = df['Fecha'].max()
            num_distinct_days = df['Fecha'].nunique()
            num_total_days = (max_date - min_date).days + 1
            label_text = f"PVPC {min_date.strftime('%d/%m/%Y')}-{max_date.strftime('%d/%m/%Y')}"
            if num_total_days > num_distinct_days:
                label_text = f"{label_text}. Con huecos"
        else:
            label_text = "El archivo no tiene datos."    
    else:
        label_text = "El archivo no existe."
    
    return label_text
