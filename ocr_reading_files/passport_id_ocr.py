import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import re
import numpy as np
import os
import pandas as pd
import os
from flask import Flask,jsonify
from passporteye import read_mrz
from io import BytesIO

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



def passport_main(image_path):
    mrz = read_mrz(BytesIO(image_path))

    passport_json_data = {}
    if mrz is not None:
        passport_data = mrz.to_dict()

        if passport_data['personal_number'] != "":
            passport_json_data['personal_number'] = passport_data['personal_number']

        if passport_data['raw_text'] != "":
            passport_json_data['raw_text'] = passport_data['raw_text']

        if passport_data['names'] != "":
            passport_json_data['name'] = passport_data['names']

        if passport_data['number'] != "":
            passport_json_data['number'] = passport_data['number']

        if passport_data['surname'] != "":
            passport_json_data['surname'] = passport_data['surname']

        if passport_data['country'] != "":
            passport_json_data['country'] = passport_data['country']
        
        if passport_data['valid_score'] != "":
            passport_json_data['valid_score'] = passport_data['valid_score']

        if passport_data['sex'] != "":
            passport_json_data['sex'] = passport_data['sex']

        if passport_data['mrz_type'] != "":
            passport_json_data['mrz_type'] = passport_data['mrz_type']

        
        if passport_json_data != {}:
            return {"response": 200,
                    "message": "Success",
                    "responseValue": {
                        "Table1": [
                            {
                                "DocumentResponse": passport_json_data
                            }
                        ]
                    }
                }
        else:
            return {"response": 400,
                                "message": "Error",
                                "responseValue": "Please upload a high-quality and readable image."
                            }
    else:
        return {"response": 400,
                                "message": "Error",
                                "responseValue": "Please upload a high-quality and readable image."
                            }



