from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_file, jsonify
from electrical_market import pmd_download, pvpc_download
import os
import pandas as pd

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/coins_index')
def coins_index():
    #return render_template('coins/coins_index.html')
    return render_template('shared/underconstruction.html')

@app.route('/cv_index_spanish')
def cv_index_spanish():
    #return render_template('cv/cv_index_spanish.html')
    return render_template('shared/underconstruction.html')

@app.route('/cv_index_english')
def cv_index_english():
    #return render_template('cv/cv_index_english.html')
    return render_template('shared/underconstruction.html')

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

    # Convert to lists for the chart
    PMD_dates = df_PMD.apply(lambda row: f"{row['Fecha']} {row['Hora']}", axis=1).tolist()
    format_dates = []
    for date_str in PMD_dates:
        # format date XX/XX/XXXX 0:00:00 1, for a date without hours
        format_dates.append(f"{datetime.strptime(date_str.split()[0], '%Y-%m-%d').strftime('%d/%m/%Y')} {date_str.split()[2]}")
    PMD_dates = format_dates
    #The chart format is the same for all prices
    PMD_prices_data = {country: df_PMD[country].tolist() for country in df_PMD.columns if country not in ['Fecha', 'Hora', 'Horario']}

    PVPC_dates = df_PVPC.apply(lambda row: f"{row['Fecha']} {row['Hora']}", axis=1).tolist()
    format_dates = []
    for date_str in PVPC_dates:
        # format date XX/XX/XXXX 0:00:00 1, for a date without hours
        format_dates.append(f"{datetime.strptime(date_str.split()[0], '%Y-%m-%d').strftime('%d/%m/%Y')} {date_str.split()[2]}")
    PVPC_dates = format_dates
    #The chart format is the same for all prices
    PVPC_prices_data = {systemelec: df_PVPC[systemelec].tolist() for systemelec in df_PVPC.columns if systemelec not in ['Fecha', 'Hora', 'Horario']}

    df_PMD_filtered = df_PMD[['Fecha', 'Hora', 'Horario', 'España']]
    df_PVPC_filtered = df_PVPC[['Fecha', 'Hora', 'Horario', 'Península']]
    df_prices = pd.merge(df_PMD_filtered, df_PVPC_filtered, on=['Fecha', 'Hora', 'Horario'], how='inner')
    df_prices = df_prices.rename(columns={"España": "PMD","Península": "PVPC"})
    prices_dates = df_prices.apply(lambda row: f"{row['Fecha']} {row['Hora']}", axis=1).tolist()
    format_dates = []
    for date_str in prices_dates:
        # format date XX/XX/XXXX 0:00:00 1, for a date without hours
        format_dates.append(f"{datetime.strptime(date_str.split()[0], '%Y-%m-%d').strftime('%d/%m/%Y')} {date_str.split()[2]}")
    #The chart format is the same for all prices
    prices_dates = format_dates
    prices_data = {pricetype: df_prices[pricetype].tolist() for pricetype in df_prices.columns if pricetype not in ['Fecha', 'Hora', 'Horario']}


    #save excel to future downloads
    excel_file_path = os.path.join('data', 'download.xlsx')
    with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
        df_prices.to_excel(writer, sheet_name='Precios', index=False)
        df_PMD.to_excel(writer, sheet_name='PMD', index=False)
        df_PVPC.to_excel(writer, sheet_name='PVPC', index=False)
    
       
    # Renderizar la plantilla con los dos DataFrames y datos para el gráfico
    return render_template('electricalmarket/electrical_market_index.html', 
                        start_date=start_date, 
                        end_date=end_date,
                        label_text=label_text,
                        register_counter_prices = "NumRegistros: " + str(len(df_prices)),
                        register_counter_PMDprices = "NumRegistros: " + str(len(df_PMD)),
                        register_counter_PVPCprices = "NumRegistros: " + str(len(df_PVPC)),
                        PMD_prices=df_PMD.to_html(classes='data', index=False), 
                        PMD_dates=PMD_dates, 
                        PMD_prices_data=PMD_prices_data,
                        PVPC_prices=df_PVPC.to_html(classes='data', index=False), 
                        PVPC_dates=PVPC_dates, 
                        PVPC_prices_data=PVPC_prices_data,
                        prices_prices=df_prices.to_html(classes='data', index=False), 
                        prices_dates=prices_dates, 
                        prices_data=prices_data
                        )

@app.route('/download_excel')
def download_excel():
    excel_file_path = os.path.join(os.getcwd(), 'data', 'download.xlsx')
    return send_file(excel_file_path, as_attachment=True)

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
