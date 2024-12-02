from apps import crete_app ,socketios

app = crete_app()


if __name__ == "__main__":
    # app.run(debug=True,port=8000)
    socketios.run(app, debug=True,port=8000)