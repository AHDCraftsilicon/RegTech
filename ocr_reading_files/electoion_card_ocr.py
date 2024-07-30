import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import re
import numpy as np
import os
import pandas as pd
import os
from flask import Flask,jsonify

 
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def all_language_text(image_path):
    result = ''
    extracted_texts = {}

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

    language_codes = ['eng', 'guj', 'hin', 'kan', 'tam', 'mal']
    languages = '+'.join(language_codes)
    custom_config = f'--oem 3 --psm 6 -l {languages}'

    for rotation in rotations:

        cv2.imwrite('rotated_grayscale.png', rotation[0])
        result = pytesseract.image_to_string(Image.open(
            'rotated_grayscale.png'), config=custom_config)
        break
    return result


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
 

# Voter number get 
def get_voter_number(all_lan_text,english_lan_text,simple_text):
    
    final_voter_id = ""
    voter_id_pattern = r'\b[A-Z]{3}\d{7}\b'
    voter_match = re.search(voter_id_pattern, all_lan_text)
    if voter_match:
        final_voter_id =  voter_match.group()
    
    else:
        if 'UPI' in all_lan_text:
            pattern = r'UPI\d{13}'
            # Search for the pattern in the text
            voter_match = re.search(pattern, all_lan_text)
            if voter_match:
                final_voter_id =  voter_match.group()
        if 'UPI' in simple_text:
            if final_voter_id == "":
                voter_match = re.search(r"UPI\d{13}", simple_text)
                if voter_match:
                    final_voter_id =  voter_match.group()


    if final_voter_id == "":
        voter_match = re.search(voter_id_pattern, english_lan_text)
        if voter_match:
            final_voter_id =  voter_match.group()
        else:
            if 'UPI' in all_lan_text:
                pattern = r'UPI\d{14}'
                # Search for the pattern in the text
                voter_match = re.search(pattern, all_lan_text)
                if voter_match:
                    final_voter_id =  voter_match.group()

    if final_voter_id == "":
        voter_match = re.search(voter_id_pattern, simple_text)
        if voter_match:
            final_voter_id =  voter_match.group()
        else:
            if 'UPI' in all_lan_text:
                pattern = r'UPI\d{14}'
                # Search for the pattern in the text
                voter_match = re.search(pattern, all_lan_text)
                if voter_match:
                    final_voter_id =  voter_match.group()


    return final_voter_id


# Gender Get
def get_gender_main(all_lan_text,english_lan_text,simple_text):
    gender_pattern = re.compile(r'\bFemale|Male|Sex F|Sex M\b|महिला|पुरुष', re.IGNORECASE)
    gender_match = gender_pattern.search(all_lan_text)
    # Search for patterns in the string
    gender_final = ""

    if gender_match != None:
        gender_group = gender_match.group()
        gender_final = gender_group
    else:
        gender_final ='Unknown'


    if gender_final == "Unknown":
        gender_Check_english = gender_pattern.search(english_lan_text)
        if gender_Check_english != None:
            gender_final = gender_Check_english.group()

    return gender_final


# DOB
def get_dob_main(all_lan_text,english_lan_text,simple_text):
    dob_pattern = re.compile(r'/(?P<year>\d{4})\b|Date of Birth\s*:\s*(\d{2}-\d{2}-\d{4})|\b\d{2}/\d{2}/\d{4}\b', re.IGNORECASE)
    year_of_birth_pattern = re.compile(r"Year of Birth\s*:\s*(\d{4})|Date of Birth\s*:\s*(\d{2}-\d{2}-\d{4})", re.IGNORECASE)

    year_birth_matches = year_of_birth_pattern.findall(all_lan_text)
   
    # Search for the pattern in the string
    dob_match = dob_pattern.search(all_lan_text)
    final_dob = "Unknown"

    if dob_match != None:
        final_dob = dob_match.group()
    else:
        if year_birth_matches != []:
            final_dob = year_birth_matches[0]
        else:
            final_dob= 'Unknown'


    if final_dob == "Unknown":
        lines = english_lan_text.split('\n')
        # Iterate through the lines to find the keyword
        gender = get_gender_main(all_lan_text,english_lan_text,simple_text)
            # Iterate through the lines to find the keyword
        for i in range(len(lines)):
            if gender in lines[i]:
                if i >= 1:
                   final_dob =  lines[i + 1]
                   if final_dob != "":
                       break 

            # print(final_dob)
        if final_dob == "Unknown":
            match_final_dob = dob_pattern.search(english_lan_text)
            if match_final_dob != None:
                final_dob = match_final_dob.group()
    
    if final_dob == "Unknown":
        dob_pattern_new = re.compile(r'\b(\d{2}-\d{2}-\d{4})\b|Date of Birth\s*:\s*(\d{XX}-\d{XX}-\d{4})', re.IGNORECASE)
        dob_match = dob_pattern_new.search(english_lan_text)
        if dob_match:
            final_dob = dob_match.group()

    if "¢" in final_dob:
        final_dob = final_dob.split("¢")[1]




    return final_dob



# Elector's Name get English
def get_electors_name_english(all_lan_text,english_lan_text,simple_text):
    electors_name = ""
    electors_pattern = r"Elector's Name\s*:\s*([A-Za-z\s]+)|Elector's name\s*:\s*([A-Za-z\s]+)"

    elector_match = re.search(electors_pattern, english_lan_text)

    if elector_match:
        electors_name = elector_match.group()

    if electors_name == "":
        elector_match = re.search(electors_pattern, simple_text)

        print(elector_match)

        if elector_match != None:
            electors_name = elector_match.group()
    
    if 'Husband' in electors_name:
        electors_name = electors_name.split('Husband')[0]

    if electors_name == "":
        new_pattern = r"Eleciors name\s*:\s*([A-Za-z\s]+)|Elector's name\s*:\s*([A-Za-z\s]+)"
        elector_match = re.search(new_pattern, all_lan_text)

        if elector_match:
            electors_name = elector_match.group()
        else:
            elector_match = re.search(electors_pattern, all_lan_text)
            if elector_match:
                electors_name = elector_match.group()

    if ":" in electors_name:
        electors_name = electors_name.split(':')[1]


    return electors_name



# Get Husband Name English
def get_husband_name_english(all_lan_text,english_lan_text,simple_text):
    husband_name = ""
    husband_pattern = r"Husband's Name\s*:\s*([A-Za-z\s]+)|Husband's Name\s*-\s*([A-Za-z\s]+)"

    husband_match = re.search(husband_pattern, english_lan_text)

    if husband_match:
        husband_name = husband_match.group()

    if husband_name == "":
        husband_match = re.search(husband_pattern, simple_text)

        if husband_match:
            husband_name = husband_match.group()
    
    # if 'Husband' in husband_name:
    #     husband_name = husband_name.split('Husband')[0]

    if husband_name == "":
        new_pattern = r"Husband's Name\s*:\s*([A-Za-z\s]+)|Husband's Name\s*([A-Za-z\s]+)"
        husband_match = re.search(new_pattern, str(all_lan_text))


        if husband_match:
            husband_name = husband_match.group()
        else:
            husband_match = re.search(husband_pattern, all_lan_text)
            if husband_match:
                husband_name = husband_match.group()

    if husband_name == "":
        
        gender = get_gender_main(all_lan_text,english_lan_text,simple_text)
        if gender != "":
            lines = all_lan_text.split('\n')
            # Iterate through the lines to find the keyword
            for i in range(len(lines)):
                if gender in lines[i]:
                    if i >= 1:
                        husband_name =  lines[i - 1]
    
    if ":" in husband_name:
        husband_name = husband_name.split(':')[1]

    if "-" in husband_name:
        husband_name = husband_name.split('-')[1]
                   


    return husband_name


# Get Father NAme English
def get_father_name_english(all_lan_text,english_lan_text,simple_text):
    father_name = ""
    father_pattern = r"Father's Name\s*:\s*([A-Za-z\s]+)"

    father_match = re.search(father_pattern, english_lan_text)

    if father_match:
        father_name = father_match.group(1).strip()

    if father_name == "":
        father_match = re.search(father_pattern, simple_text)

        if father_match:
            father_name = father_match.group(1).strip()
    
    if 'Father' in father_name:
        father_name = father_name.split('Father')[0]

    if father_name == "":
        new_pattern = r"Father's Name\s*:\s*([A-Za-z\s]+)"
        father_match = re.search(new_pattern, all_lan_text)

        if father_match:
            father_name = father_match.group(1).strip()
        else:
            father_match = re.search(father_pattern, all_lan_text)
            if father_match:
                father_name = father_match.group(1).strip()

    if father_name == "":
        gender = get_gender_main(all_lan_text,english_lan_text,simple_text)
        if gender != "":
            lines = all_lan_text.split('\n')
            # Iterate through the lines to find the keyword
            for i in range(len(lines)):
                if gender in lines[i]:
                    if i >= 1:
                        father_name =  lines[i - 1]
    
    if ":" in father_name:
        father_name = father_name.split(':')[1]
                   


    return father_name


# Address
def get_address_english(all_lan_text,english_lan_text,simple_text):

    address_pattern = re.compile(r"(Address\s*:\s*.*?\b\d{6}\b)", re.DOTALL)
    address = "Unknown"

    # Search for the pattern in the text
    match = address_pattern.search(all_lan_text)

    if match:
        address = match.group(1).strip()

    if address == "Unknown":
        address_pattern = re.compile(r"Address\s*:\s*(.*?)(?:\n\n|$)", re.DOTALL)

        # Search for the pattern in the text
        match = address_pattern.search(english_lan_text)

        if match:
            address = match.group(1).strip()
            print("Address:", address)

    if address == "Unknown":
        address_pattern = re.compile(r"Address\s*(.*?)(?=Facsimile Signature|Place\s*:|$)", re.DOTALL)

        # Search for the pattern in the text
        match = address_pattern.search(simple_text)

        if match:
            address = match.group(1).strip()
            print("Address:", address)

    return address



def voter_id_read(image_path):

    voter_list = {}
    all_lan_text = all_language_text(image_path)
    english_lan_text = english_language_text(image_path)


    simple_image_string = pytesseract.image_to_string(Image.open(image_path))
    simple_text_blank_remove = "\n".join(line for line in simple_image_string.split('\n') if line.strip())

    voter_number = get_voter_number(all_lan_text , english_lan_text,simple_text_blank_remove)
    if voter_number != "":
        voter_list["Voter No"] = voter_number


    elector_name_english = get_electors_name_english(all_lan_text,english_lan_text,simple_text_blank_remove)
    if elector_name_english != "":
        voter_list["Name"] = elector_name_english.replace('\n', ' ')

    if "Husban" in all_lan_text or "Husban" in english_lan_text or "Husban" in simple_text_blank_remove:
        
        husband_name_english = get_husband_name_english(all_lan_text,english_lan_text,simple_text_blank_remove)
        if husband_name_english != "":
            voter_list['Husband Name'] = husband_name_english.split('\n', 1)[0]

    if "Fathe" in all_lan_text or "Fathe" in english_lan_text or "Fathe" in simple_text_blank_remove:
        father_name_english = get_father_name_english(all_lan_text,english_lan_text,simple_text_blank_remove)
        if father_name_english != "":
            voter_list['Father Name'] = father_name_english.split('\n', 1)[0]
    

    gender = get_gender_main(all_lan_text,english_lan_text,simple_text_blank_remove)
    if gender != "Unknown":
        voter_list['Gender'] = gender

    DOBs = get_dob_main(all_lan_text,english_lan_text,simple_text_blank_remove)
    if DOBs != "Unknown":
        voter_list['DOB'] = DOBs

    address = get_address_english(all_lan_text,english_lan_text,simple_text_blank_remove)
    if address != "Unknown":
        voter_list["Address1"] = address
    
    # os.remove(image_path)
    if voter_list != {}:
        return jsonify({"response": "200",
            "message": "Success",
            "responseValue": {
                "Table1": [
                    {
                        "DocumentResponse": voter_list
                    }
                ]
            }
        }),200
    
    else:
        return jsonify({"response": "400",
            "message": "Error",
            "responseValue": "Invalid image! Please upload a clear and readable image!"
        }),400


