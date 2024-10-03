import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import re
import numpy as np
import pandas as pd
import os , base64
from flask import Flask,request,jsonify
from io import BytesIO
from flask_jwt_extended import JWTManager
import time , os , io
from werkzeug.utils import secure_filename
# import subprocess
# import xml.etree.ElementTree as ET


# Tesseract exe path local
try:
    os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except:
    # Linux Server
    os.environ['TESSDATA_PREFIX'] = '/usr/local/share/tessdata/'
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' 




def get_all_language_formate_string(image_path):
    result = ''
    # nparr = np.frombuffer(image_path, np.uint8)
    # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # img2 = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv2.INTER_LANCZOS4)  # Resize by x2 using LANCZOS4 interpolation method.

    # # cv2.imwrite('./apps/static/ocr_image/image3.png', img2)
    # img_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

    # cv2.imwrite('./apps/static/ocr_image/image2.png', img2)
    language_codes = ['eng']
    languages = '+'.join(language_codes)
    custom_config = f'--oem 3 --psm 6 -l {languages}'
    result = pytesseract.image_to_string(image_path, config=custom_config)

    return result

def get_english_formate_string(image_path):
    result = ''
    # nparr = np.frombuffer(image_path, np.uint8)
    # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # img2 = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv2.INTER_LANCZOS4)  # Resize by x2 using LANCZOS4 interpolation method.
    # img_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

    # cv2.imwrite('./apps/static/ocr_image/image2.png', img2)
    result = pytesseract.image_to_string(image_path)

    return result


# Date Of Birth
def string_to_get_dob(normal_string,english_string):
       
    # Search for the pattern in the string
    dob_match = re.compile(r'\b\s*(\d{2}/\d{2}/\d{4})').search(normal_string)
    final_dob = "Unknown"

    if dob_match != None:
        final_dob = dob_match.group()
    else:
        if re.compile(r"Year of Birth\s*:\s*(\d{4})").findall(normal_string) != []:
            final_dob = re.compile(r"Year of Birth\s*:\s*(\d{4})").findall(normal_string)[0]
        else:
            final_dob= 'Unknown'

    if final_dob == "Unknown":
        if re.compile(r'\b\s*(\d{2}/\d{2}/\d{4})').search(english_string) != None:
            final_dob = re.compile(r'\b\s*(\d{2}/\d{2}/\d{4})').search(english_string).group()

    return final_dob


# Gender 
def string_to_get_gender(normal_string,english_string):
    gender_pattern = re.compile(r'\bFEMALE|FEMALE|male|female|Male|Female\b', re.IGNORECASE)
    # Search for patterns in the string
    gender_final = ""

    if gender_pattern.search(normal_string) != None:
        gender_final = gender_pattern.search(normal_string).group()
    else:
        gender_final ='Unknown'

    if gender_final == "Unknown":
        if gender_pattern.search(english_string) != None:
            gender_final = gender_pattern.search(english_string).group()

    return gender_final


# Addhar Number
def string_to_get_aadhar_number(normal_string,english_string,all_lan_string):
    addhar_number = "Unknown"
    aadhar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', normal_string)
    if aadhar_match != None:
        addhar_number = aadhar_match.group()
    else:
        addhar_number = "Unknown"


    if addhar_number == "Unknown":
        aadhar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', english_string)
        if aadhar_match != None:
            addhar_number = aadhar_match.group()
        else:
            addhar_number = "Unknown"

    if addhar_number == "Unknown":
        aadhar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', all_lan_string)
        if aadhar_match != None:
            addhar_number = aadhar_match.group()
        else:
            addhar_number = "Unknown"

    return addhar_number


# Addhar Address
def string_to_get_address(normal_string,english_string):
    addhar_Address = ""

    address_pattern = re.compile(r'Address\..*?(?=\d{4} \d{4} \d{4})|Address\s*:\s*(.*?)\n\n|Address\s*(.*?)$', re.DOTALL)

    # Search for the pattern in the input string
    if address_pattern.search(english_string):
        addhar_Address = address_pattern.search(english_string).group(0)

    if addhar_Address == "":
        # Search for the pattern in the input string
        if address_pattern.search(normal_string):
            addhar_Address = address_pattern.search(normal_string).group(0)

    return addhar_Address


# Get addhar Person Name for father name & husband name
def string_to_get_person_name(aadhaar_string, keyword):

    # Split the string into lines
    lines = aadhaar_string.split('\n')
    names1 = ""

    for i in range(len(lines)):
        if keyword in lines[i]:
            if i >= 1:
                # print(lines[i - 1])
                names1 =  lines[i - 1]
                break
    
    # print("************* " , names1)

    if ":"  in names1:
        for i in range(len(lines)):
            if keyword in lines[i]:
                if i >= 2:
                    # print(lines[i - 1])
                    names1 =  lines[i - 2]
                    break
    
    return names1


# Husband Name
def string_to_get_husband_father_name(normal_string,english_string,keyword):
    all_Details = []
    husband_keyword_check = ""
    name_english = ""

    father_keyword_check = ""
    if keyword == "Husband":

        # Search for the pattern in the string
        match_husband_string = re.compile(r'Husband\s*[-:]\s*([A-Za-z\s]+)|Husband\s*:\s*([A-Z\s]+)', re.IGNORECASE).search(english_string)
        
        if match_husband_string:
            husband_keyword_check = match_husband_string.group(1).strip()
      

        if husband_keyword_check != "":
            all_Details.append({'husband_name':husband_keyword_check.split('\n')[0]})


        english_text_blank_remove = "\n".join(line for line in english_string.split('\n') if line.strip())
        name_english = string_to_get_person_name(english_text_blank_remove, 'Husband')
  
        if name_english == "":
            pass
        else:
            all_Details.append({'Addhar_person_name' : name_english})

    elif keyword == "Father":

        # Search for the pattern in the string
        match = re.compile(r'Father\s*[-:]\s*([A-Za-z\s]+)', re.IGNORECASE).search(english_string)

        if match:
            father_keyword_check = match.group(1).strip()
       

        if father_keyword_check == "":
            pass
        else:
            all_Details.append({'father_name' : father_keyword_check.split('\n')[0]})


        english_text_blank_remove = "\n".join(line for line in english_string.split('\n') if line.strip())
        name_english = string_to_get_person_name(english_text_blank_remove, 'Fath')
        
        if name_english == "":
            pass
        else:
            all_Details.append({'Addhar_person_name' : name_english})

    return all_Details


# Get Addhar Person NAme From List Through
def string_to_get_personname_list(aadhaar_string, keyword_values,keyword):
    lines = aadhaar_string.split('\n')

    get_person_name = ""
    if keyword == "DOB":
        for i in range(len(lines)):
            if str(keyword_values) in lines[i]:
                if i >= 1:
                    get_person_name = lines[i - 1] 
                    break
    
    if keyword == "Birth":
        for i in range(len(lines)):
            if str(keyword_values) in lines[i]:
                if i >= 1:
                    get_person_name = lines[i - 1] 
                    break

    elif keyword == "Gender":
        for i in range(len(lines)):
            if str(keyword_values) in lines[i]:
                if i >= 2:
                    get_person_name = lines[i - 2] 
                    break

    # print("*** ", get_person_name)

    return get_person_name




# Get Addhar Person Name (This Name From Using DOB)
def string_to_get_Only_person_name(normal_string,english_string,all_lan_string,dob_key_word,gender_keyword):
    simple_name = ""
    if dob_key_word !=  "Unknown":

        remove_blank_line = "\n".join(line for line in english_string.split('\n') if line.strip())

        get_name_english_String = string_to_get_personname_list(remove_blank_line,dob_key_word,"DOB")
        if get_name_english_String == "":
            get_name_normal_string = string_to_get_personname_list(normal_string,dob_key_word,"DOB")
            simple_name = get_name_normal_string
        else:
            simple_name = get_name_english_String

        if simple_name == "":
            get_name_all_lan_string = string_to_get_personname_list(all_lan_string,dob_key_word,"DOB")
            simple_name = get_name_all_lan_string

    if simple_name == "":
        if gender_keyword != "Unknown":
            remove_blank_line = "\n".join(line for line in english_string.split('\n') if line.strip())
            get_name_english_String = string_to_get_personname_list(remove_blank_line,gender_keyword,"Gender")

            if get_name_english_String == "":
                get_name_normal_string = string_to_get_personname_list(normal_string,gender_keyword,"Gender")
                simple_name = get_name_normal_string
            else:
                simple_name = get_name_english_String

            if simple_name == "":
                get_name_all_lan_string = string_to_get_personname_list(all_lan_string,gender_keyword,"Gender")
                simple_name = get_name_all_lan_string

    return simple_name



def remove_special_characters(s):
    # This regular expression matches any character that is not a letter, digit, or space
    return re.sub(r'[^a-zA-Z0-9\s]', '', s)


# Function to get the dictionary with more details
def get_most_detailed_dict(data):
    max_details = {}
    
    for item in data:
        if item['status_code'] == 200 and isinstance(item['response'], dict):
            current_details = item['response']
            # Check if the current dictionary has more keys than the previously found one
            if len(current_details) > len(max_details):
                max_details = item
                
    return max_details

def aadhar_ocr_image_read_main(image_path):
   
    rotation_angles = [0, 90, 180, 270, 360]
    
    responce_store = []

    # with open(image_path, 'rb') as f:
    #     image_bytes = f.read()
    
    image = Image.open(io.BytesIO(image_path))

    for angle in rotation_angles:
        rotated_image = image.rotate(angle, expand=True)  # Rotate the image
        extracted_text = pytesseract.image_to_string(rotated_image)  # Extract text

        addhar_details_list = {}
    
        normal_string = pytesseract.image_to_string(rotated_image)

        english_string = get_english_formate_string(rotated_image)

        all_lan_string = get_all_language_formate_string(rotated_image)

        # print(extracted_text)
        # print(normal_string)
        # print(all_lan_string)

        # Starting Check Condition From Here.

        # Address Check
        if 'Address' in english_string or 'Address' in normal_string:
            address = string_to_get_address(normal_string,english_string)
            
            addhar_details_list['Address1'] = address

        # Without Address Get
        else:

            date_of_birth = string_to_get_dob(normal_string,english_string)
            if date_of_birth != "Unknown":
                addhar_details_list['DOB'] = date_of_birth

            gender = string_to_get_gender(normal_string,english_string)
            if gender != "Unknown":
                addhar_details_list['Gender'] = gender

            addhar_number = string_to_get_aadhar_number(normal_string,english_string,all_lan_string)
            if addhar_number != "Unknown":
                addhar_details_list['AadharID'] = addhar_number


            if 'Husband' in english_string:
                # Get Husband Name and Addhar Person Name 
                get_husband_name_addhar_name = string_to_get_husband_father_name(normal_string,english_string, "Husband")
                for get_names in get_husband_name_addhar_name:
                    try:
                        addhar_details_list['Husband_name'] = get_names['husband_name']
                    except:
                        pass
                    
                    try:
                        addhar_details_list['Name1'] = get_names['Addhar_person_name']
                    except:
                        pass
            
            # Get Father Name & Addhar Person Name
            elif 'Fath' in english_string:
                get_father_name_addhar_name = string_to_get_husband_father_name(normal_string,english_string, "Father")
                for get_names_father in get_father_name_addhar_name:                    
                    try:
                        addhar_details_list['father_name'] = get_names_father['father_name']
                    except:
                        pass
                    
                    try:
                        addhar_details_list['Name1'] = get_names_father['Addhar_person_name']
                    except:
                        pass

            else:
                if date_of_birth != "Unknown":
                    get_addhar_person_name = string_to_get_Only_person_name(normal_string,english_string,all_lan_string,date_of_birth,gender)
                    if get_addhar_person_name != "":
                        clean_string = remove_special_characters(get_addhar_person_name)


                        addhar_details_list['Name1'] = clean_string

        responce = ""
        if addhar_details_list != {}:
            responce =  {"status_code": 200,
                "status": "Success",
                "response":addhar_details_list}
        else:
            if addhar_details_list == {}:
                responce = {"status_code": 400,
                            "status": "Error",
                            "response": "Please upload a high-quality and readable image."
                        }
                
        responce_store.append(responce)

    # print(responce_store)

    most_detailed_dict = get_most_detailed_dict(responce_store)

    # print(most_detailed_dict)

    if most_detailed_dict == {}:
        return {"status_code": 400,
                "status": "Error",
                "response": "Please upload a high-quality and readable image."}
    
    else:
        return most_detailed_dict

