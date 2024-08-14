from flask import Blueprint, request, jsonify
import cv2
import numpy as np
import regex as re
from PIL import Image
import pytesseract
import os
from werkzeug.utils import secure_filename
import time
import base64,io
from flask_jwt_extended import  jwt_required
from data_base_string import *
from datetime import datetime
import random
import string


# Blueprint
adhar_masking_bp = Blueprint("adhar_masking_bp",
                        __name__,
                        url_prefix="/",
                        static_folder='static')

# Tesseract exe path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# os.environ['TESSDATA_PREFIX'] = '/usr/local/share/tessdata/'
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Update with your path


# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history_test"]



multiplication_table = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0))

permutation_table = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8))

# ---------------------------------------------------------------------------------------------------------#


def compute_checksum(number):
    """Calculate the Verhoeff checksum over the provided number. The checksum
    is returned as an int. Valid numbers should have a checksum of 0."""

    # transform number list
    number = tuple(int(n) for n in reversed(str(number)))
    # print(number)

    # calculate checksum
    checksum = 0

    for i, n in enumerate(number):
        checksum = multiplication_table[checksum][permutation_table[i % 8][n]]

    # print(checksum)
    return checksum



def Regex_Search(bounding_boxes):
    possible_UIDs = []
    Result = ""

    for character in range(len(bounding_boxes)):
        if len(bounding_boxes[character]) != 0:
            Result += bounding_boxes[character][0]
        else:
            Result += '?'
    # print(Result)

    matches = [match.span() for match in re.finditer(
        r'\d{12}', Result, overlapped=True)]

    for match in matches:

        UID = int(Result[match[0]:match[1]])

        if compute_checksum(UID) == 0 and UID % 10000 != 1947:
            possible_UIDs.append([UID, match[0]])

    possible_UIDs = np.array(possible_UIDs)
    return possible_UIDs



def Mask_UIDs(image_path, possible_UIDs, bounding_boxes, rtype, SR=False, SR_Ratio=[1, 1]):

    img = cv2.imread(image_path)

    if rtype == 2:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rtype == 3:
        img = cv2.rotate(img, cv2.ROTATE_180)
    elif rtype == 4:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    height = img.shape[0]

    if SR == True:
        height *= SR_Ratio[1]

    for UID in possible_UIDs:

        digit1 = bounding_boxes[UID[1]].split()
        digit8 = bounding_boxes[UID[1] + 7].split()

        h1 = min(height-int(digit1[4]), height-int(digit8[4]))
        h2 = max(height-int(digit1[2]), height-int(digit8[2]))

        if SR == False:
            top_left_corner = (int(digit1[1]), h1)
            bottom_right_corner = (int(digit8[3]), h2)
            botton_left_corner = (int(digit1[1]), h2-3)
            thickness = h1-h2

        else:
            top_left_corner = (
                int(int(digit1[1])/SR_Ratio[0]), int((h1)/SR_Ratio[1]))
            bottom_right_corner = (
                int(int(digit8[3])/SR_Ratio[0]), int((h2)/SR_Ratio[1]))
            botton_left_corner = (
                int(int(digit1[1])/SR_Ratio[0]), int((h2)/SR_Ratio[1]-3))
            thickness = int((h1)/SR_Ratio[1])-int((h2)/SR_Ratio[1])

        img = cv2.rectangle(img, top_left_corner,
                            bottom_right_corner, (0, 0, 0), -1)

    if rtype == 2:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif rtype == 3:
        img = cv2.rotate(img, cv2.ROTATE_180)
    elif rtype == 4:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # print(img)
    # file_name = image_path.split(
    #     '/')[-1].split('.')[0]+"_masked"+"."+image_path.split('.')[-1]
    # cv2.imwrite(file_name, img)
    retval, buffer = cv2.imencode('.png', img)
    jpg_as_text = base64.b64encode(buffer)

    # Convert bytes to string for storing/transmitting (if needed)
    data = jpg_as_text.decode('utf-8')

    if data != "":
        return data
    else:
        return ""



def Extract_and_Mask_UIDs(image_path, SR=False, sr_image_path=None, SR_Ratio=[1, 1]):

    if SR == False:
        img = cv2.imread(image_path)
    else:
        img = cv2.imread(sr_image_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    rotations = [[gray, 1],
                 [cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE), 2],
                 [cv2.rotate(gray, cv2.ROTATE_180), 3],
                 [cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE), 4],
                 [cv2.GaussianBlur(gray, (5, 5), 0), 1],
                 [cv2.GaussianBlur(cv2.rotate(
                     gray, cv2.ROTATE_90_COUNTERCLOCKWISE), (5, 5), 0), 2],
                 [cv2.GaussianBlur(cv2.rotate(
                     gray, cv2.ROTATE_180), (5, 5), 0), 3],
                 [cv2.GaussianBlur(cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE), (5, 5), 0), 4]]

    settings = ('-l eng --oem 3 --psm 11')

    for rotation in rotations:

        cv2.imwrite('rotated_grayscale.png', rotation[0])

        bounding_boxes = pytesseract.image_to_boxes(Image.open(
            'rotated_grayscale.png'), config=settings).split(" 0\n")

        possible_UIDs = Regex_Search(bounding_boxes)

        if len(possible_UIDs) == 0:
            continue
        else:

            if SR == False:
                masked_img = Mask_UIDs(
                    image_path, possible_UIDs, bounding_boxes, rotation[1])
            else:
                masked_img = Mask_UIDs(
                    image_path, possible_UIDs, bounding_boxes, rotation[1], True, SR_Ratio)

            return (masked_img, possible_UIDs)

    return (None, None)



def masking_file(input_path):
    masked_img, possible_UIDs = Extract_and_Mask_UIDs(input_path)

    if masked_img == "":
        s = jsonify({'data':"Please Upload Valid Aadhar Card"})
    else:

        s = masked_img
    return s


# Generate Random Number
def generate_random_alphanumeric(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

@adhar_masking_bp.route('/api/v1/adharMasking/adharmasking',methods=['POST'])
# @jwt_required()
def addhar_masking_main():
    if request.method == 'POST':
        api_call_start_time = datetime.now()
        data = request.get_json()
        random_uniqu = generate_random_alphanumeric()
        keys_to_check = ['UniqueID', 'CorporateID', 'addhar_img']

        # Check for missing keys and items can't be empty

        for key in keys_to_check:
            if key not in data or not data[key]:
                # UniqueID Check 
                if key == "UniqueID":
                    store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": key +" cannot be null or empty."
                        }
                    return jsonify(store_response), 400
               
                else:
                    check_log_db = Api_request_history_db.find_one({"unique_id":random_uniqu})
                    
                    if check_log_db != None:
                        api_call_end_time = datetime.now()
                        duration = api_call_end_time - api_call_start_time
                        duration_seconds = duration.total_seconds()
                        store_response = {"response": 400,
                                        "message": "Error",
                                        "responseValue": "Request with the same unique ID has already been processed!"
                                    }

                        Api_request_history_db.insert_one({
                                        "corporate_id":data["CorporateID"],
                                        "unique_id":random_uniqu,
                                        "api_name":"Aadhar_Masking",
                                        "api_start_time":api_call_start_time,
                                        "api_end_time":datetime.now(),
                                        "status": "Fail",
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "request_data":str(data),
                                        "response_data" :str(store_response),
                                        "creadte_date":datetime.now(),
                                    })
                        
                        return jsonify(store_response),400
                    
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    # CorporateId
                    if key == "CorporateID":
                        store_response = {"response": 400,
                                "message": "Error",
                                "responseValue": key +" cannot be null or empty."
                            }
                        
                        Api_request_history_db.insert_one({
                                        "unique_id":random_uniqu,
                                        "api_name":"Aadhar_Masking",
                                        "api_start_time":api_call_start_time,
                                        "api_end_time":datetime.now(),
                                        "status": "Fail",
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "request_data":str(data),
                                        "response_data" :str(store_response),
                                        "creadte_date":datetime.now(),
                                    })
                        
                    else:
                        store_response = {"response": 400,
                                "message": "Error",
                                "responseValue": key +" cannot be null or empty."
                            }
                        
                        Api_request_history_db.insert_one({
                                        "unique_id":random_uniqu,
                                        "corporate_id":data["CorporateID"],
                                        "api_name":"Aadhar_Masking",
                                        "api_start_time":api_call_start_time,
                                        "api_end_time":datetime.now(),
                                        "status": "Fail",
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "request_data":str(data),
                                        "response_data" :str(store_response),
                                        "creadte_date":datetime.now(),
                                    })

                    
                    return jsonify(store_response), 400

        # Check UniqueID
        check_log_db = Api_request_history_db.find_one({"unique_id":random_uniqu})
        
        
        if check_log_db == None:
            base64_string = data['addhar_img']
            if base64_string.startswith('data:image/jpeg;base64,'):
                base64_string = base64_string.replace('data:image/jpeg;base64,', '')

            # Decode the base64 string into bytes
            image_bytes = base64.b64decode(base64_string)

            # Convert bytes data to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            filename_img = str(time.time()).replace(".", "")
            static_file_name = filename_img+".png"
            image.save(os.path.join('apps/static/addhar_masksing_img', secure_filename(static_file_name)))
            
            image = masking_file("apps/static/addhar_masksing_img/" +static_file_name)
            if image != "":
                os.remove("apps/static/addhar_masksing_img/" +static_file_name)   
            
            # Valid Image Message
            if image == None:
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": 400,
                            "message": "Error",'responseValue':"Please Upload Valid Aadhar Card"}
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":random_uniqu,
                                "api_name":"Aadhar_Masking",
                                "api_start_time":api_call_start_time,
                                "api_end_time":datetime.now(),
                                "status": "Fail",
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "request_data":str(data),
                                "response_data" :str(store_response),
                                "creadte_date":datetime.now(),
                            })
            
                return jsonify(store_response), 400
            
            # Success Response
            else:
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": 200,
                                "message": "Success",
                                "responseValue": {
                                    "Table1": [{
                                            "Image": "data:image/png;base64,"+image}]}}
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":random_uniqu,
                                "api_name":"Aadhar_Masking",
                                "api_start_time":api_call_start_time,
                                "api_end_time":datetime.now(),
                                "status": "Success",
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "request_data":str(data),
                                "response_data" :str(store_response),
                                "creadte_date":datetime.now(),
                            })
            
                return jsonify(store_response), 200

        else:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": "Request with the same unique ID has already been processed!"
                        }

            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":random_uniqu,
                            "api_name":"Aadhar_Masking",
                            "api_start_time":api_call_start_time,
                            "api_end_time":datetime.now(),
                            "status": "Fail",
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "request_data":str(data),
                            "response_data" :str(store_response),
                            "creadte_date":datetime.now(),
                        })
            
            return jsonify(store_response),400