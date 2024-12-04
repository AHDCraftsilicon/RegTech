from apps import crete_app ,socketios
import ssl
import eventlet


app = crete_app()


if __name__ == "__main__":
    # app.run(debug=True,port=8000)

    cert_path = "/etc/letsencrypt/live/regtech.blubeetle.ai/fullchain.pem"
    key_path = "/etc/letsencrypt/live/regtech.blubeetle.ai/privkey.pem"

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    socketios.run(app, debug=True,port=8000, ssl_context=ssl_context)
    # eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen(('0.0.0.0', 8000)), certfile=cert_path, keyfile=key_path), app)
