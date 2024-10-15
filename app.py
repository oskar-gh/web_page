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
    

    df_PMD = pmd_download.return_price(start_date, end_date, False)
    df_PVPC = pvpc_download.return_price(start_date, end_date, False)
    label_text = pmd_download.return_price_minandmax()
    label_text = "-->" + label_text + " --- " + pvpc_download.return_price_minandmax() + "<--"

    #save csv to future downloads
    csv_file_path = os.path.join('data', 'download.csv')
    df_PMD.to_csv(csv_file_path, index=False)
    #print("DataFrame inicial:", df_PVPC.head(30))
    
    # Convert to lists for the chart
    PMD_dates = df_PMD.apply(lambda row: f"{row['Fecha']} {row['Hora']}", axis=1).tolist()
    format_dates = []
    for date_str in PMD_dates:
        # format date XX/XX/XXXX 0:00:00 1, for a date without hours
        format_dates.append(f"{datetime.strptime(date_str.split()[0], '%Y-%m-%d').strftime('%d/%m/%Y')} {date_str.split()[2]}")
    PMD_dates = format_dates

    PVPC_dates = df_PVPC.apply(lambda row: f"{row['Fecha']} {row['Hora']}", axis=1).tolist()
    format_dates = []
    for date_str in PVPC_dates:
        # format date XX/XX/XXXX 0:00:00 1, for a date without hours
        format_dates.append(f"{datetime.strptime(date_str.split()[0], '%Y-%m-%d').strftime('%d/%m/%Y')} {date_str.split()[2]}")
    PVPC_dates = format_dates
    #The chart format is the same for all prices
    PVPC_dates = PVPC_dates
    
    #PMD_prices_data = df_PMD['PMD'].tolist() 
    PMD_prices_data = {type_price: df_PMD[type_price].tolist() for type_price in df_PMD.columns if type_price not in ['Fecha', 'Hora', 'Horario']}
    PVPC_prices_data = {country: df_PVPC[country].tolist() for country in df_PVPC.columns if country not in ['Fecha', 'Hora', 'Horario']}
       
    # Renderizar la plantilla con los dos DataFrames y datos para el gráfico
    return render_template('electrical_market_index.html', 
                        label_text=label_text,
                        register_counter_spainprices = "NumRegistros: " + str(len(df_PMD)),
                        register_counter_allprices = "NumRegistros: " + str(len(df_PVPC)),
                        spain_prices=df_PMD.to_html(classes='data', index=False), 
                        all_prices=df_PVPC.to_html(classes='data', index=False), 
                        PMD_dates=PMD_dates, 
                        PMD_prices_data=PMD_prices_data,
                        PVPC_dates=PVPC_dates, 
                        PVPC_prices_data=PVPC_prices_data,
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
