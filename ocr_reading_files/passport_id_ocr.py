import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import re
import numpy as np
import os
import pandas as pd
import os
from flask import Flask,jsonify

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



def english_language_text(image_path):
    result = ''

    img = cv2.imread(image_path)
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
    english_result = ""
    for rotation in rotations:

        cv2.imwrite('english_rotated_grayscale.png', rotation[0])
        result = pytesseract.image_to_string(Image.open('english_rotated_grayscale.png'))
        
        english_result += result
    return english_result
 


def get_name(english_text,simple_text):
    name_pattern = r"P<IND([A-Z]+)<<([A-Z]+)<([A-Z]+)<<|<<(.*?)<|CC(.*?)C"
    full_name = ""
    name_match = re.search(name_pattern, english_text,re.MULTILINE)

    if name_match:
        try:
            full_name = name_match.group().strip().replace("<"," ").replace("IND","").replace("P","")
        except:
            full_name = name_match.group().replace("<","")



    if full_name == "":
        name_match = re.search(r'([A-Z\s]+)\s+([A-Z\s]+)', simple_text)
 
        if name_match:
            full_name = name_match.group()

    return full_name


def get_surname(result):
    name_pattern = r"P<IND([A-Z]+)<<([A-Z]+)<([A-Z]+)<<|([A-Z\s]+)\s([A-Z\s]+)$"
    surname = ""
    name_match = re.search(name_pattern, result)
    if name_match:
        surname = name_match.group().strip().replace("<"," ").replace("IND","").replace("P","")

    if surname == "":
        name_match = re.search(r"IND(.*?)CC|IND(.*?)<<", result)
        if name_match:
            try:
                surname = name_match.group().strip().replace("IND","").replace("<<"," ").replace("CC","")
            except:
                
                surname = name_match.group().replace("IND","").replace("<<","").replace("CC","")

    return surname


def get_dob(result):
    dob_pattern = r"(\d{2}/\d{2}/\d{4})"

    dob_match = re.search(dob_pattern, result)
    dob = ""
    if dob_match:
        dob = dob_match.group(1)

    return dob

def birth_place(result):
    birthplace_pattern = r"(\b[A-Z]+\b [A-Z]+,[A-Z]+)|(.+),\s([A-Z\s]+)$"
    birthplace_match = re.search(birthplace_pattern, result,re.MULTILINE)

    birthplace = ""
    if birthplace_match:
        birthplace = birthplace_match.group()

    if birthplace == "":

        # Find all matches of the pattern in the text
        places = re.findall(r'^[A-Z\s,]+$', result, re.MULTILINE)

        # Print the extracted places
        for place in places:
            birthplace = place.strip()

    return birthplace


def pass_port_number(english_text):
    passport_pattern = r"[A-Z]\d{7}$"
    passport_numbers = ""
    # Extract passport number using regex
    passport_match = re.search(passport_pattern, english_text,re.MULTILINE)
    if passport_match:
        passport_numbers = passport_match.group()

    return passport_numbers


def passport_main(image_path):
    passport_list = {}
    simple_image_string = pytesseract.image_to_string(Image.open(image_path))
    simple_text_blank_remove = "\n".join(line for line in simple_image_string.split('\n') if line.strip())

    english_lan_text = english_language_text(image_path)

    pass_name = get_name(english_lan_text,simple_text_blank_remove)
    if pass_name != "":
        passport_list["Name1"] = pass_name


    surname = get_surname(english_lan_text)
    if surname != "":
        passport_list["Surname"] = surname

    dob = get_dob(english_lan_text)
    if dob != "":
        passport_list["DOB"] = dob

    birth_place_name = birth_place(english_lan_text)
    if birth_place_name != "":
        passport_list["Place Name"] = birth_place_name

    passport_number = pass_port_number(english_lan_text)
    if birth_place_name != "":
        passport_list["Passport No"] = passport_number

    # os.remove(image_path)
    if passport_list != {}:
        return jsonify({"response": "200",
            "message": "Success",
            "responseValue": {
                "Table1": [
                    {
                        "DocumentResponse": passport_list
                    }
                ]
            }
        }),200
    
    else:
        return jsonify({"response": "400",
            "message": "Error",
            "responseValue": "Invalid image! Please upload a clear and readable image!"
        }),400



