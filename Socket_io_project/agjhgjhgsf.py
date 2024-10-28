from flask import Flask, render_template, url_for , jsonify , request
from flask_socketio import SocketIO, emit
import requests
import threading
import time
from pymongo import MongoClient

from bson import ObjectId

# Live DB
database = MongoClient("mongodb://regtech-live:zwSZCkcoWOCRiN51pBzkBNpxRd2tJGQvEToLAHV2nxjfEDURRVDR4Ink8QKust4TXzSOn5yg2Fj6ACDbiqD4nw%3D%3D@regtech-live.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@regtech-live@")
# Testing My Side
Regtch_services_UAT = database['Regtech']

ML_kit_value_storage_db = Regtch_services_UAT['Google_ml_kit_Storage']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# @app.route('/')
# def index():
#     # Render the frontend HTML
#     return render_template('index.html')

@socketio.on('trigger_api')
def handle_trigger_api(data):
    print("----------------")
    ML_kit_value_storage_db.update_one({"_id":ObjectId(data['objids'])},
                                        {"$set": {"message":data['message']}})



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
    

    inseted_objid = ML_kit_value_storage_db.insert_one({"status":"loading.......",
                                                        "message":""}).inserted_id
    socketio.emit('image_updates', {'image_url': data,"objid":str(inseted_objid)})

    socketio.sleep(7)



    check_db_log = ML_kit_value_storage_db.find_one({"_id":ObjectId(inseted_objid)})
    if check_db_log != None:

        if check_db_log['message'] != "":
            # print("Document found:", check_db_log['json_data'])
            store_response = {"image_To_text":check_db_log['message'],"Objid_id":str(check_db_log['_id'])} 
        else:
            store_response = {}

        return store_response
    else:
        return jsonify({"data":"Something Went Wrong!"})



if __name__ == '__main__':
    socketio.run(app, debug=True)
