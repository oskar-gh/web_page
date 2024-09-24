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

@app.route('/electrical_market_index')
def electrical_market_index():
    # Get tomorrow's date
    if datetime.now().hour >= 15:
        target_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        target_date = (datetime.now()).strftime('%Y-%m-%d')
       
    df = pmd_download.pmd_download(target_date, target_date)
    return render_template('electrical_market_index.html', prices=df.to_html(classes='data'))

@app.route('/electrical_market_rangeprice', methods=['POST'])
def consultar_precios():
    # Obtener las fechas del formulario
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    print(f"Start Date: {start_date}, End Date: {end_date}")

    df = pmd_download.pmd_download(start_date, end_date)
    return render_template('electrical_market_index.html',
                           prices=df.to_html(classes='data'), 
                           start_date=start_date, 
                           end_date=end_date)

if __name__ == '__main__':
    app.run(debug=True)
