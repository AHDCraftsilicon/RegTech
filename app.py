from apps import crete_app ,socketios
import ssl
import eventlet


app = crete_app()


if __name__ == "__main__":
    socketios.run(app, debug=True, port=8000)

    # cert_path = "/etc/letsencrypt/live/regtech.blubeetle.ai/fullchain.pem"
    # key_path = "/etc/letsencrypt/live/regtech.blubeetle.ai/privkey.pem"

    # ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    # eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 443)), app, ssl_context=ssl_context)

    # socketios.run(app, debug=True,port=8000, ssl_context=ssl_context)
    # listener = eventlet.listen(8000)  # Set the listening address and port
    # ssl_listener = eventlet.wrap_ssl(listener, ssl_context=ssl_context)  # Wrap the listener with SSL
    # eventlet.wsgi.server(ssl_listener, app)
