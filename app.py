from flask import Flask, render_template
from electrical_market import pmd_download

app = Flask(__name__, static_url_path='/css', static_folder='css')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/coins')
def coins_index():
    return render_template('coins_index.html')

@app.route('/cv_spanish')
def cv_index_spanish():
    return render_template('cv_index_spanish.html')

@app.route('/cv_english')
def cv_index_english():
    return render_template('cv_index_english.html')

@app.route('/family')
def family_index():
    return render_template('family_index.html')

@app.route('/electrical_market')
def electrical_market_index():
    df = pmd_download.pmd_download()
    return render_template('electrical_market_index.html', prices=df.to_html(classes='data'))

if __name__ == '__main__':
    app.run(debug=True)
