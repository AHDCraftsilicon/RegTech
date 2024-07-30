from apps import crete_app

app = crete_app()
#small change

if __name__ == "__main__":
    app.run(debug=True,port=8000)

