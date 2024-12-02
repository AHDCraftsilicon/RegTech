from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
import re
from bson import ObjectId
from datetime import datetime
from flask_socketio import emit, SocketIO
import io , json , time
import requests


# DataBase
from data_base_string import *

ML_kit_value_storage_db = Regtch_services_UAT['Google_ml_kit_Storage']

 
# def init_socketio(socketios):
    
#     # Get user objid and return response user flag
#     @socketios.on('trigger_api')
#     def handle_trigger_api(data):
#         print("----------------" , data)
#         # ML_kit_value_storage_db.update_one({"_id":ObjectId(data['objids'])},
#         #                                     {"$set": {"message":data['message']}})

# Blueprint
websocket_bp_for_AML = Blueprint("websocket_bp_for_AML",
                        __name__,
                        url_prefix="/AML/",
                        template_folder="templates")


@websocket_bp_for_AML.route("/Goole/kit/flutter",methods=['POST'])
def OCR_reading_with_AML():

    if request.method == 'POST':

        data = request.json
        print(data)

        # websocket_bp_for_AML.socketios.emit('base64_image_pass', data)


        return jsonify({"data":{
                            "status_code":200,
                            "status": "Success",
                            "response":"socket emit successfully!"
                            }})


def another_way_get_func(data):
    print(data)
    websocket_bp_for_AML.socketios.emit('base64_image_pass', data)
    websocket_bp_for_AML.socketios.sleep(7)

    return {"data":{
                    "status_code":200,
                    "status": "Success",
                    "response":"socket emit successfully!"
                    }}


@websocket_bp_for_AML.route("/Goe/id_pass",methods=['POST'])
def db_store_Api():

    details  = request.form['objid']
    text_details  = request.form['text_details']

    print(details , text_details)
    if details != "":
        ML_kit_value_storage_db.update_one({"_id":ObjectId(details)},
                                        {"$set": {"message":text_details}})


        return jsonify({"data":{"status_code":200}})
    else:
        return jsonify({"data":{"status_code":400,
                                "status": "Error",
                                "response":"Objid is Empty!"
                                                    }})


