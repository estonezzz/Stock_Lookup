from flask import Flask, render_template, request, redirect

test_app = Flask(__name__)

@test_app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    test_app.run(debug=True)
