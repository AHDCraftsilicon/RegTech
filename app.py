from apps import crete_app

app = crete_app()
#small change .

if __name__ == "__main__":
    app.run(debug=True,port=8000)


# from flask import Flask
# app = Flask(__name__)
# @app.route("/")
# def helloworld():
#     return "<h1>Hello World!</h1>"
# if __name__ == "__main__":
#     app.run(port=8000)
