from flask import Flask, render_template, url_for , jsonify , request
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    # Render the frontend HTML
    return render_template('index.html')

@socketio.on('trigger_api')
def handle_trigger_api(data):
    print("----------------")
    print(data)
    socketio.emit('text_Data', {'data': data})



@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")


@app.route('/image-api',methods=['POST'])
# @socketio.on('trigger_apis')
def api_Calling():
    data = request.json
    


    socketio.emit('image_updates', {'image_url': data})

    return jsonify({"data":"Sent Successfully!"})



if __name__ == '__main__':
    socketio.run(app, debug=True)
