from flask import Flask, request, render_template
import sys
sys.path.append('..')
from index import *
from database import get_most_common_queries

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    pop_query = get_most_common_queries(10)
    return render_template('index.html', pop_query=pop_query)

@app.route('/result', methods=['GET','POST'])
def result():
    query = request.args.get('q')
    return '<h1>Hello %s !</h1>' % query

if __name__ == '__main__':
    app.run(debug=True)