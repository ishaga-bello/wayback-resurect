from flask import render_template, request
from app import app
# from your_script import your_function  # Import your script function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    url = request.form['url']
    result = your_function(url)  # Call your function with the URL

    return render_template('result.html', result=result)
