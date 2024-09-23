import io

def create_csv_inlocal(df, path, filename):
    try:
        # Specify the full path if you want to save to a specific directory
        full_path = f"{path}/{filename}"
        df.to_csv(full_path, index=False, encoding='utf-8')
        print(f"CSV file saved in: {full_path}")
    except Exception as e:
        print(f"Error creating CSV file locally: {e}")
        
def create_csv_inbuffer(df):
    try:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        print(f"Return CSV file")
        return csv_buffer
    except Exception as e:
        print(f"Error creating CSV file in buffer: {e}")