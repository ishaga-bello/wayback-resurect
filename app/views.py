from flask import render_template, request
from app import app
import wayback_resurrect as wr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    url = request.form['url']
    logs = {
      'wpUN': request.form['wpUN'],
      'wpPW': request.form['wpPW'],
      'wpDomain': request.form['wpDomain'],
    }
    result = wr.recover(url, logs)  # Call your function with the URL

    return render_template('result.html', result=result)
