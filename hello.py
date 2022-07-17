from bottle import Bottle, run

app = Bottle()

@app.route('/hello')
def hello():
    return "Hello World 4"

run(app, host='localhost', port=8080, debug=True, reloader=True)
