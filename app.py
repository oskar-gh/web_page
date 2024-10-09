from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_file, jsonify
from electrical_market import pmd_download, pvpc_download
import os

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

###############################################
###############################################
###############################################
#
#   ELECTRICAL MARKET
#
###############################################
###############################################
###############################################

@app.route('/electrical_market_index', methods=['GET', 'POST'])
def electrical_market_index():
    
    #time = datetime.now()
    #print(f"Consulta iniciada a las: {time}")
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
    

    df_spain = pmd_download.return_price(start_date, end_date, True)
    df_all = pmd_download.return_price(start_date, end_date, False)
    label_text = pmd_download.return_price_minandmax()
    label_text = "-->" + label_text + " --- " + pvpc_download.return_price_minandmax() + "<--"

    #TODO --> Controlar si no existen ficheros
    
    #save csv to future downloads
    csv_file_path = os.path.join('data', 'download.csv')
    df_all.to_csv(csv_file_path, index=False)
    #print("DataFrame inicial:", df_all.head(30))
    
    # Convert to lists for the chart
    spain_dates = df_spain.apply(lambda row: f"{row['Fecha']} {row['Hora']}", axis=1).tolist()
    format_dates = []
    for date_str in spain_dates:
        # format date XX/XX/XXXX 0:00:00 1, for a date without hours
        format_dates.append(f"{datetime.strptime(date_str.split()[0], '%Y-%m-%d').strftime('%d/%m/%Y')} {date_str.split()[2]}")
    spain_dates = format_dates
    #The chart format is the same for all prices
    all_dates = spain_dates
    
    #spain_prices_data = df_spain['PMD'].tolist() 
    spain_prices_data = {type_price: df_spain[type_price].tolist() for type_price in df_spain.columns if type_price not in ['Fecha', 'Hora', 'Horario']}
    all_prices_data = {country: df_all[country].tolist() for country in df_all.columns if country not in ['Fecha', 'Hora', 'Horario']}
       
    # Renderizar la plantilla con los dos DataFrames y datos para el gráfico
    return render_template('electrical_market_index.html', 
                        label_text=label_text,
                        spain_prices=df_spain.to_html(classes='data'), 
                        all_prices=df_all.to_html(classes='data'), 
                        spain_dates=spain_dates, 
                        spain_prices_data=spain_prices_data,
                        all_dates=all_dates, 
                        all_prices_data=all_prices_data,
                        start_date=start_date, 
                        end_date=end_date)

@app.route('/download_csv')
def download_csv():
    csv_file_path = os.path.join(os.getcwd(), 'data', 'download.csv')
    return send_file(csv_file_path, as_attachment=True)

@app.route('/updateRee')
def updateRee():
    #time = datetime.now()
    #print(f"Consulta iniciada a las: {time}")
    response = pmd_download.update_ree()
    response = pvpc_download.update_ree()
    new_label_text = pmd_download.return_price_minandmax()
    new_label_text = "-->" + new_label_text + " --- " + pvpc_download.return_price_minandmax() + "<--"
    return jsonify({'label_text': new_label_text})
    #return "", 204  # Código 204 No Content para indicar que la solicitud se procesó correctamente sin contenido

    

###############################################
###############################################
###############################################
#
#   ELECTRICAL MARKET
#
###############################################
###############################################
###############################################

if __name__ == '__main__':
    app.run(debug=True)
