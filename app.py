from flask import Flask, render_template, request, jsonify, make_response

# init flask app
app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def home():
    return "Hello, I am the metric connector. Try a POST to /api/v1/deploy"

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/api/v1/deploy/', methods=['GET'])
def deploy():
    if not request.json or not 'title' in request.json:
        print("Something is wrong here")
        return
    else:
        print("##DEBUG")
        print(request.json)
        print("##DEBUG")

if __name__ == '__main__':
    app.run(port=8080)