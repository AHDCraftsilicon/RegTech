from apps import crete_app ,socketios

app = crete_app()


if __name__ == "__main__":
    # app.run(debug=True,port=8000)

    cert_path = "/etc/letsencrypt/live/regtech.blubeetle.ai/fullchain.pem"
    key_path = "/etc/letsencrypt/live/regtech.blubeetle.ai/privkey.pem"
    socketios.run(app, debug=True,port=8000, ssl_context=(cert_path, key_path))