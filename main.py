import flask

from secure_execution import secure_execute_program

app = flask.Flask(__name__)


@app.route('/', methods = ['GET'])
def index_front():
    return flask.render_template('interpreter.html')

@app.route('/', methods = ['POST'])
def index_back():
    data = flask.request.get_json()
    lang = data.get('language')
    code = data.get('code')
    stdin = data.get('input')
    stdout, stderr, status_code = secure_execute_program.start_program(code, stdin, lang)
    return flask.jsonify({'stdout': stdout, 'stderr': stderr, 'status_code': status_code})


if __name__ == '__main__':
    app.run('0.0.0.0', 5005)

