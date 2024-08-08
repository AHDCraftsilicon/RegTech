import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import re
import numpy as np
import pandas as pd
from io import BytesIO
from flask_jwt_extended import JWTManager
from werkzeug.utils import secure_filename

 
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'




def get_all_language_formate_string(image_path):
    result = ''
    nparr = np.frombuffer(image_path, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    img2 = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv2.INTER_LANCZOS4)  # Resize by x2 using LANCZOS4 interpolation method.

    cv2.imwrite('image3.png', img2)

    language_codes = ['eng']
    languages = '+'.join(language_codes)
    custom_config = f'--oem 3 --psm 6 -l {languages}'
    result = pytesseract.image_to_string(Image.open('image3.png'), config=custom_config)

    return result

def get_english_formate_string(image_path):
    result = ''
    nparr = np.frombuffer(image_path, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    img2 = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv2.INTER_LANCZOS4)  # Resize by x2 using LANCZOS4 interpolation method.

    cv2.imwrite('image2.png', img2)
    result = pytesseract.image_to_string(Image.open('image2.png'))

    return result


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


# Voter number get 
def string_to_get_voter_number(normal_string,english_string):
    
    final_voter_id = ""
    voter_id_pattern = r'\b[A-Z]{3}\d{7}\b'
    voter_match = re.search(voter_id_pattern, normal_string)
    if voter_match:
        final_voter_id =  voter_match.group()
    
    else:
        if 'UPI' in normal_string:
            pattern = r'UPI\d{13}'
            # Search for the pattern in the text
            voter_match = re.search(pattern, normal_string)
            if voter_match:
                final_voter_id =  voter_match.group()
        if 'UPI' in english_string:
            if final_voter_id == "":
                voter_match = re.search(r"UPI\d{13}", english_string)
                if voter_match:
                    final_voter_id =  voter_match.group()


    if final_voter_id == "":
        voter_match = re.search(voter_id_pattern, english_string)
        if voter_match:
            final_voter_id =  voter_match.group()
        else:
            if 'UPI' in english_string:
                pattern = r'UPI\d{14}'
                # Search for the pattern in the text
                voter_match = re.search(pattern, normal_string)
                if voter_match:
                    final_voter_id =  voter_match.group()

    return final_voter_id


# Date Of Birth
def string_to_get_dob(normal_string,english_string,all_lan_string):
    dob_pattern = re.compile(r'/(?P<year>\d{4})\b|Date of Birth\s*:\s*(\d{2}-\d{2}-\d{4})|\b\d{2}/\d{2}/\d{4}\b|Dateof Birth (\d{2}-\d{2}-\d{4})|Date of Birth /Age\s*:\s*(\d+)', re.IGNORECASE)
    year_of_birth_pattern = re.compile(r"Year of Birth\s*:\s*(\d{4})|Date of Birth\s*:\s*(\d{2}-\d{2}-\d{4})|Dateof Birth (\d{2}-\d{2}-\d{4})", re.IGNORECASE)

    year_birth_matches = year_of_birth_pattern.findall(all_lan_string)
   
    # Search for the pattern in the string
    dob_match = dob_pattern.search(all_lan_string)
    final_dob = "Unknown"

    if dob_match != None:
        final_dob = dob_match.group()
    else:
        if year_birth_matches != []:
            final_dob = year_birth_matches[0]
        else:
            final_dob= 'Unknown'


    if final_dob == "Unknown":
        lines = english_string.split('\n')
        # Iterate through the lines to find the keyword
        gender = string_to_get_gender(normal_string,english_string)
            # Iterate through the lines to find the keyword
        for i in range(len(lines)):
            if gender in lines[i]:
                if i >= 1:
                   final_dob =  lines[i + 1]
                   if final_dob != "":
                       break 

            # print(final_dob)
        if final_dob == "Unknown":
            match_final_dob = dob_pattern.search(english_string)
            if match_final_dob != None:
                final_dob = match_final_dob.group()
    
    if final_dob == "Unknown":
        dob_pattern_new = re.compile(r'\b(\d{2}-\d{2}-\d{4})\b|Date of Birth\s*:\s*(\d{XX}-\d{XX}-\d{4})', re.IGNORECASE)
        dob_match = dob_pattern_new.search(english_string)
        if dob_match:
            final_dob = dob_match.group()

    if "¢" in final_dob:
        final_dob = final_dob.split("¢")[1]

    return final_dob



# Elector's name
def string_to_get_elector_name(normal_string,english_string,all_lan_string):
    electors_name = ""
    electors_pattern = r"Elector's Name\s*:\s*([A-Za-z\s]+)|Elector's name\s*:\s*([A-Za-z\s]+)|B NAME :\s*([\w\s]+)\s*\.|Name\s*:\s*([A-Za-z\s]+)\s*\d*\s*\."

    elector_match = re.search(electors_pattern, english_string)

    if elector_match:
        electors_name = elector_match.group()

    if electors_name == "":
        elector_match = re.search(electors_pattern, normal_string)


        if elector_match != None:
            electors_name = elector_match.group()
    
    if 'Husband' in electors_name:
        electors_name = electors_name.split('Husband')[0]

    if electors_name == "":
        new_pattern = r"Eleciors name\s*:\s*([A-Za-z\s]+)|Elector's name\s*:\s*([A-Za-z\s]+)|Elecic’sname\s*:\s*([A-Za-z\s,]+)"
        elector_match = re.search(new_pattern, all_lan_string)

        if elector_match:
            electors_name = elector_match.group()
        else:
            elector_match = re.search(electors_pattern, all_lan_string)
            if elector_match:
                electors_name = elector_match.group()

    if ":" in electors_name:
        electors_name = electors_name.split(':')[1]


    return electors_name


# Husband Name 
def string_to_get_husband_name(normal_string,english_string,all_lan_string):
    husband_name = ""
    husband_pattern = r"Husband's Name\s*:\s*([A-Za-z\s]+)|Husband's Name\s*-\s*([A-Za-z\s]+)|Husband's Name;\s*([A-Za-z\s]+)"

    husband_match = re.search(husband_pattern, english_string)

    if husband_match:
        husband_name = husband_match.group()

    if husband_name == "":
        husband_match = re.search(husband_pattern, normal_string)

        if husband_match:
            husband_name = husband_match.group()
    
    # if 'Husband' in husband_name:
    #     husband_name = husband_name.split('Husband')[0]

    if husband_name == "":
        new_pattern = r"Husband's Name\s*:\s*([A-Za-z\s]+)|Husband's Name\s*([A-Za-z\s]+)|Husband's Name;\s*([A-Za-z\s]+)"
        husband_match = re.search(new_pattern, str(all_lan_string))


        if husband_match:
            husband_name = husband_match.group()
        else:
            husband_match = re.search(husband_pattern, all_lan_string)
            if husband_match:
                husband_name = husband_match.group()

    if husband_name == "":
        
        gender = string_to_get_gender(normal_string,english_string)
        if gender != "":
            lines = all_lan_string.split('\n')
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
def string_to_get_father_name(normal_string,english_string,all_lan_string):
    father_name = ""
    father_pattern = r"Father's Name\s*:\s*([A-Za-z\s]+)"

    father_match = re.search(father_pattern, english_string)

    if father_match:
        father_name = father_match.group(1).strip()

    if father_name == "":
        father_match = re.search(father_pattern, normal_string)

        if father_match:
            father_name = father_match.group(1).strip()
    
    if 'Father' in father_name:
        father_name = father_name.split('Father')[0]

    if father_name == "":
        new_pattern = r"Father's Name\s*:\s*([A-Za-z\s]+)"
        father_match = re.search(new_pattern, all_lan_string)

        if father_match:
            father_name = father_match.group(1).strip()
        else:
            father_match = re.search(father_pattern, all_lan_string)
            if father_match:
                father_name = father_match.group(1).strip()

    if father_name == "":
        gender = string_to_get_gender(normal_string,english_string)
        if gender != "":
            lines = all_lan_string.split('\n')
            for i in range(len(lines)):
                if gender in lines[i]:
                    if i >= 1:
                        father_name =  lines[i - 1]
    
    if ":" in father_name:
        father_name = father_name.split(':')[1]
                   


    return father_name



# Address get 
def string_to_get_address_details(normal_string,english_string,all_lan_string):

    address_pattern = re.compile(r"(Address\s*:\s*.*?\b\d{6}\b)", re.DOTALL)
    address = "Unknown"

    # Search for the pattern in the text
    match = address_pattern.search(all_lan_string)

    if match:
        address = match.group(1).strip()

    if address == "Unknown":
        address_pattern = re.compile(r"Address\s*:\s*(.*?)(?:\n\n|$)", re.DOTALL)

        # Search for the pattern in the text
        match = address_pattern.search(english_string)
        if match:
            address = match.group(1).strip()

    if address == "Unknown":
        address_pattern = re.compile(r"Address\s*(.*?)(?=Facsimile Signature|Place\s*:|$)", re.DOTALL)

        # Search for the pattern in the text
        match = address_pattern.search(normal_string)

        if match:
            address = match.group(1).strip()
            print("Address:", address)

    return address




def voter_ocr_main(image_path):

    with open(image_path, 'rb') as image_files:
        image_data = image_files.read()

    normal_string = pytesseract.image_to_string(Image.open(BytesIO(image_data)))
    normal_string = "\n".join(line for line in normal_string.split('\n') if line.strip())

    english_string = get_english_formate_string(image_data)
    all_lan_string = get_all_language_formate_string(image_data)
    # print(normal_string , "----------\n")
    # print(english_string , "----------\n")
    # print(all_lan_string , "----------\n")
  
    voter_data = {}

    # Voter Id DEtails Get
    gender = string_to_get_gender(normal_string,english_string)
    if gender != "" and gender != "Unknown":
        voter_data['Gender'] = gender

    voter_number = string_to_get_voter_number(normal_string,english_string)
    if voter_number != "":
        voter_data["Voter_No"] = voter_number


    dob_date = string_to_get_dob(normal_string,english_string,all_lan_string)
    if dob_date != "Unknown":
        voter_data["DOB"] = dob_date



    electors_name = string_to_get_elector_name(normal_string,english_string,all_lan_string)
    if electors_name != "":
        voter_data["Name"] = electors_name.strip()


    if "Husban" in normal_string or "Husban" in english_string or "Husban" in all_lan_string:
        huband_name =  string_to_get_husband_name(normal_string,english_string,all_lan_string)
        if huband_name != "":
            if "Name" in huband_name:
                voter_data["Husband_Name"] = huband_name.split("Name")[1].replace(";","").replace(".","").strip()
            else:
                huband_name = huband_name.split("\n")
                voter_data["Husband_Name"] = re.sub(r'\n', '', huband_name[0]).replace(";","").replace(".","").strip()

    if "Fathe" in normal_string or "Fathe" in english_string or "Fathe" in all_lan_string:
        father_name = string_to_get_father_name(normal_string,english_string,all_lan_string)
        if father_name != "":
            if "Name" in father_name:
                voter_data["Father_Name"] = father_name.split("Name")[1].strip()
            else:
                voter_data["Father_Name"] = father_name.strip()

    address = string_to_get_address_details(normal_string,english_string,all_lan_string)
    if address != "Unknown":
        voter_data["Address1"] = address

    if voter_data != {}:
        return {"response": 200,
            "message": "Success",
            "responseValue": {
                "Table1": [{
                        "DocumentResponse": voter_data
                    }]}}
    else:
        return {"response": 400,
            "message": "Error",
            "responseValue": "Please upload a high-quality and readable image."
        }
    