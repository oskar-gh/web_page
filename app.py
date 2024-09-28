from datetime import datetime, timedelta
from flask import Flask, render_template, request
from electrical_market import pmd_download

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/coins_index')
def coins_index():
    return render_template('coins_index.html')

@app.route('/cv_index_spanish')
def cv_index_spanish():
    return render_template('cv_index_spanish.html')

@app.route('/cv_index_english')
def cv_index_english():
    return render_template('cv_index_english.html')

@app.route('/family_index')
def family_index():
    return render_template('family_index.html')

@app.route('/electrical_market_index', methods=['GET', 'POST'])
def electrical_market_index():
    
    if request.method == 'GET':
        # Get tomorrow's date
        if datetime.now().hour >= 15:
            start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            start_date = (datetime.now()).strftime('%Y-%m-%d')
        end_date = start_date
    else:
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
       
    df_all = pmd_download.pmd_download(start_date, end_date)
    
    print("DataFrame inicial:", df_all.head(30))
    
    # Seleccionar solo los precios de España
    df_spain = df_all[['Fecha', 'Hora', 'Horario', 'España']]  # Seleccionar solo la columna de 'España'
    
    # Convertir a listas para el gráfico solo  España
    spain_dates = df_spain.apply(lambda row: f"{row['Fecha']} {row['Hora']}", axis=1).tolist()  # Fecha y Hora combinadas
    spain_prices_data = df_spain['España'].tolist()  # Precios de España
    
    # Convertir a listas para el gráfico de todo
    all_dates = df_spain.apply(lambda row: f"{row['Fecha']} {row['Hora']}", axis=1).tolist()  # Fecha y Hora combinadas
    all_prices_data = {country: df_all[country].tolist() for country in df_all.columns if country not in ['Fecha', 'Hora', 'Horario']}

    # Renderizar la plantilla con los dos DataFrames y datos para el gráfico
    return render_template('electrical_market_index.html', 
                        all_prices=df_all.to_html(classes='data'), 
                        spain_prices=df_spain.to_html(classes='data'), 
                        spain_dates=spain_dates, 
                        spain_prices_data=spain_prices_data,
                        all_dates=all_dates, 
                        all_prices_data=all_prices_data,
                        start_date=start_date, 
                        end_date=end_date)

if __name__ == '__main__':
    app.run(debug=True)
