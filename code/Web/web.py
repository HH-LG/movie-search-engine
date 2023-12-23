from flask import Flask, request, render_template
import sys
sys.path.append('..')
from index import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query = request.form['query']
        index_name = request.form['type']
        response = search_index(index_name, query, 10)
        for hit in response['hits']['hits']:
            results.append(hit['_source'])
    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)