import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import re
import numpy as np
import pandas as pd
import os
from flask import Flask,jsonify
# from pyaadhaar.utils import Qr_img_to_text, isSecureQr
import xml.etree.ElementTree as ET

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_all_lang_text(image_path):
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

 # Recognize text with tesseract for python
    
 
    # language_codes = ['eng', 'guj', 'hin', 'kan', 'tam', 'mal']
    # languages = '+'.join(language_codes)
 
    # # Set up Tesseract engine
    # custom_config = f'--oem 3 --psm 6 -l {languages}'
    # image = Image.open(image_path)
    # result = pytesseract.image_to_string(image, config=custom_config)
    
    # pattern = r'Government of India\s*(.*)'
 
    # # Use regex to match the pattern
    # match = re.search(pattern, result, re.DOTALL)
 
    # if match:
    #     # Get the captured group which contains everything after "Government of India"
    #     result = match.group(1).strip()
 
    # return result

def extract_only_english_text(image_path):
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
 
# Example usage

# def modify_image():

# print("english try ||||||||| ,",text_only_english)

# Aadhar pattern
def get_addhar_number(extracted_text,text_only_english,simple_text_blank_remove):
    aadhaar_pattern = r'\b\d{4}\s\d{4}\s\d{4}\b'
    addhar_number = ""
    aadhar_match = re.search(aadhaar_pattern, extracted_text)
    if aadhar_match != None:
        addhar_number = aadhar_match.group()
    else:
        addhar_number = "Unknown"


    if addhar_number == "Unknown":
        aadhar_match = re.search(aadhaar_pattern, text_only_english)
        if aadhar_match != None:
            addhar_number = aadhar_match.group()
        else:
            addhar_number = "Unknown"

    if addhar_number == "Unknown":
        aadhar_match = re.search(aadhaar_pattern, simple_text_blank_remove)
        if aadhar_match != None:
            addhar_number = aadhar_match.group()
        else:
            addhar_number = "Unknown"

    return addhar_number


# Gender Get
def get_gender_main(extracted_text,text_only_english,simple_text_blank_remove):
    gender_pattern = re.compile(r'\bFemale|Male\b', re.IGNORECASE)
    gender_match = gender_pattern.search(extracted_text)
    # Search for patterns in the string
    gender_final = ""

    if gender_match != None:
        gender_group = gender_match.group()
        gender_final = gender_group
    else:
        gender_final ='Unknown'


    if gender_final == "Unknown":
        gender_Check_english = gender_pattern.search(text_only_english)
        if gender_Check_english != None:
            gender_final = gender_Check_english.group()

    if gender_final == "Unknown":
        gender_Check_english = gender_pattern.search(simple_text_blank_remove)
        if gender_Check_english != None:
            gender_final = gender_Check_english.group()

    return gender_final

# print("Gender = " , get_gender_main(extracted_text))


# DOB Pattern 
def get_dob_main(extracted_text,text_only_english,simple_text_blank_remove):
    dob_pattern = re.compile(r'\b\s*(\d{2}/\d{2}/\d{4})')
    year_of_birth_pattern = re.compile(r"Year of Birth\s*:\s*(\d{4})")

    year_birth_matches = year_of_birth_pattern.findall(extracted_text)
   
    # Search for the pattern in the string
    dob_match = dob_pattern.search(extracted_text)
    final_dob = "Unknown"

    if dob_match != None:
        final_dob = dob_match.group()
    else:
        if year_birth_matches != []:
            final_dob = year_birth_matches[0]
        else:
            final_dob= 'Unknown'


    if final_dob == "Unknown":
        match_final_dob = dob_pattern.search(text_only_english)
        if match_final_dob != None:
            final_dob = match_final_dob.group()

    if final_dob == "Unknown":
        match_final_dob = dob_pattern.search(simple_text_blank_remove)
        if match_final_dob != None:
            final_dob = match_final_dob.group()


    return final_dob





# get local text for father & husband name
def get_local_text_for_father_husband_name(aadhaar_string, keyword):

    # Split the string into lines
    lines = aadhaar_string.split('\n')
    # Iterate through the lines to find the keyword
    for i in range(len(lines)):
        if keyword in lines[i]:
            if i >= 1:
                return lines[i - 1]
            else:
                return 'Not found'
    
    return 'Not found'

# get english line
def get_english_line_for_name(aadhaar_string, keyword):

    # Split the string into lines
    lines = aadhaar_string.split('\n')
    names1 = ""
    # Iterate through the lines to find the keyword
    for i in range(len(lines)):
        if keyword in lines[i]:
            if i >= 2:
                names1 = lines[i - 2]
                break
    
    return names1


 # get local line 
def get_local_lan_name(aadhaar_string, keyword):

    # Split the string into lines
    lines = aadhaar_string.split('\n')
    # Iterate through the lines to find the keyword
    for i in range(len(lines)):
        if keyword in lines[i]:
            if i >= 3:
                return lines[i - 3]
            else:
                return 'Not found'
    
    return 'Not found'
        

def get_normal_img_english_name(aadhaar_string, keyword):
    # Split the string into lines

    print(keyword)
   
    lines = aadhaar_string.split('\n')
    for i in range(len(lines)):
        # print(lines[i + 3])
        if str(keyword) in lines[i]:
            if i >= 1:
                return lines[i - 1] 
            else:
                return 'Not found'
    return 'Not found'

def get_normal_img_local_name(aadhaar_string, keyword):
    # Split the string into lines
    lines = aadhaar_string.split('\n')
    name1 = "Not found"
    for i in range(len(lines)):
        # print(lines[i + 3])
        if str(keyword) in lines[i]:
            if i >= 2:
                name1 =  lines[i - 2] 
    return name1


def father_name_detact(father_keyword_check,extracted_text,text_only_english):
    all_details_list = []
    if father_keyword_check == True:

        father_pattern = re.compile(r'Father\s*[-:]\s*([A-Za-z\s]+)', re.IGNORECASE)

        # Search for the pattern in the string
        match = father_pattern.search(extracted_text)

        if match:
            father_keyword_check = match.group(1).strip()
        else:
            father_keyword_check = 'Not found'

        if father_keyword_check == "Not found":
            pass
        else:
            all_details_list.append({'Father_Name_English' : father_keyword_check.split('\n')[0]})


        # English NAme
        english_text_blank_remove = "\n".join(line for line in text_only_english.split('\n') if line.strip())
        name_english = get_english_line_for_name(english_text_blank_remove, 'Father')
        if name_english == "Not found":
            pass
        else:
            all_details_list.append({'Name2' : name_english})

        # Local Father name
        local_father_name  = get_local_text_for_father_husband_name(extracted_text, 'Father')
        if local_father_name == "Not found":
            pass
        else:
            all_details_list.append({'Father_Name' : local_father_name})

        # Local Name
        local_name  = get_local_lan_name(extracted_text, 'Father')
        if local_name == "Not found":
            pass
        else:
            all_details_list.append({'Name1' : local_name})
    
    return all_details_list


def husband_name_detact(husband_keyword_check,extracted_text,text_only_english):

    all_Details = []

    if husband_keyword_check == True:

        husband_pattern = re.compile(r'Husband\s*[-:]\s*([A-Za-z\s]+)', re.IGNORECASE)

        # Search for the pattern in the string
        match = husband_pattern.search(extracted_text)

        if match:
            husband_keyword_check = match.group(1).strip()
        else:
            husband_keyword_check = 'Not found'

        if husband_keyword_check != "Not found":
            all_Details.append({'husband_name_english':husband_keyword_check.split('\n')[0]})


        local_husband_name  = get_local_text_for_father_husband_name(extracted_text, 'Husband')
        modify_husband_name = re.search(r'पति\s*:\s*([^|]+)', local_husband_name)

        if modify_husband_name != None:
            modify_husband_name = modify_husband_name.group(1).strip()
            all_Details.append({'husband_name_local':modify_husband_name})

        english_text_blank_remove = "\n".join(line for line in text_only_english.split('\n') if line.strip())
        name_english = get_english_line_for_name(english_text_blank_remove, 'Husband')
        if name_english == "Not found":
            pass
        else:
            all_Details.append({'Name2' : name_english})

        local_name  = get_local_lan_name(extracted_text, 'Husband')
        if local_name == "Not found":
            pass
        else:
            all_Details.append({'Name1' : local_name})

    return all_Details


def all_details_detact(all_lan_text,dob_date,text_only_english,simple_text_blank_remove):
    simple_name_list = []
    if dob_date != "Unknown":
        local_name = get_normal_img_local_name(all_lan_text,dob_date)
        # print("get local name = " , local_name)

        if local_name != "Not found":
            simple_name_list.append({"Name1": local_name})

        remove_blank_line = "\n".join(line for line in text_only_english.split('\n') if line.strip())
        english_name = get_normal_img_english_name(remove_blank_line,dob_date)
        if english_name == "Not found":
            # print(simple_text_blank_remove)
            english_name = get_normal_img_english_name(simple_text_blank_remove,dob_date)
            # print(simple_name_list)
            simple_name_list.append({"Name2 = ":english_name})
        else:
            simple_name_list.append({"Name2": english_name})

    return simple_name_list

# path = "./check_addhar"
# dir_list = os.listdir(path)

def aadhar_address(without_modify_image,only_english,with_lan):
    addhar_Address = ""

    address_pattern = re.compile(r'Address\..*?(?=\d{4} \d{4} \d{4})|Address\s*:\s*(.*?)\n\n|Address\s*(.*?)$', re.DOTALL)

    # Search for the pattern in the input string
    match = address_pattern.search(without_modify_image)
    if match:
        addhar_Address = match.group(0)

    if addhar_Address == "":
        address_pattern = re.compile(r'Address\s*:\s*(.*?)\n\n|Address\s*(.*?)$', re.DOTALL)

        # Search for the pattern in the input string

        match = address_pattern.search(only_english)
        if match:
            addhar_Address = match.group(0)
    
    if addhar_Address == "":
        address_pattern = re.compile(r'Address\s*:\s*(.*?)\n\n|Address\s*(.*?)$', re.DOTALL)

        # Search for the pattern in the input string

        match = address_pattern.search(with_lan)
        if match:
            addhar_Address = match.group(0)


    return addhar_Address



# Python addhar reading using QR code
# def addhar_reading_by_qr(image_path):
#     img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Read image as grayscale.
#     img2 = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv2.INTER_LANCZOS4)  # Resize by x2 using LANCZOS4 interpolation method.

#     cv2.imwrite('image2.png', img2)

#     qrData = Qr_img_to_text('image2.png')
#     # print(qrData)

#     return qrData


def addhar_card_read(image_path):
    mainlist = {}
    
    dob_date = ""
    gender_get = ""
    father_name_english = ""
    father_name = ""
    name1 = ""
    name2 = ""
    husband_name_english = ""
    husband_name = ""
    dob_date = ""
    addhar_number = ""
    gender_get = ""
    addhar_address = ""
    
    # addhar_qr_code = addhar_reading_by_qr(image_path)
    # if addhar_qr_code:
    #     root = ET.fromstring(addhar_qr_code[0])
    #     address_merge = ""
    #     mainlist['Name2'] = root.attrib.get('name')
    #     mainlist['DOB'] = root.attrib.get('dob')
    #     mainlist['Gender'] = root.attrib.get('gender')
    #     mainlist['AdharID'] = root.attrib.get('uid')

    #     try:
    #         address_merge +=root.attrib.get('co') + ","
    #     except:
    #         pass

    #     try:
    #         address_merge +=root.attrib.get('house') + ","
    #     except:
    #         pass

    #     try:
    #         address_merge +=root.attrib.get('street') + ","
    #     except:
    #         pass

    #     try:
    #         address_merge +=root.attrib.get('lm') + ","
    #     except:
    #         pass

    #     try:
    #         address_merge +=root.attrib.get('loc')+ ","
    #     except:
    #         pass

    #     try:
    #         address_merge +=root.attrib.get('vtc')+ ","
    #     except:
    #         pass

    #     try:
    #         address_merge +=root.attrib.get('po')+ ","
    #     except:
    #         pass

    #     try:
    #         address_merge +=root.attrib.get('dist')+ ","
    #     except:
    #         pass

    #     try:
    #         address_merge +=root.attrib.get('subdist')+ ","
    #     except:
    #         pass

    #     try:
    #         address_merge +=root.attrib.get('state')+ ","
    #     except:
    #         pass

    #     try:
    #         address_merge +=root.attrib.get('pc')+ ","
    #     except:
    #         pass

    #     mainlist['Address1'] =   address_merge



    #     return jsonify({"response": "000",
    #         "message": "Success",
    #         "responseValue": {
    #             "Table1": [
    #                 {
    #                     "DocumentResponse": mainlist
    #                 }
    #             ]
    #         }
    #     })

    all_lan_text = extract_all_lang_text(image_path)

    # print('************ \n' ,all_lan_text)

    text_only_english = extract_only_english_text(image_path)
    # print(text_only_english)

    img = Image.open(image_path)
        # Use pytesseract to do OCR on the image
    simple_image_string = pytesseract.image_to_string(img)
    simple_text_blank_remove = "\n".join(line for line in simple_image_string.split('\n') if line.strip())
    # print(simple_text_blank_remove)
    dob_date = get_dob_main(all_lan_text,text_only_english,simple_text_blank_remove)
    addhar_number = get_addhar_number(all_lan_text,text_only_english,simple_text_blank_remove)
    gender_get = get_gender_main(all_lan_text,text_only_english,simple_text_blank_remove)




    if 'Address' in all_lan_text or \
        'Address' in text_only_english or \
        'Address' in simple_text_blank_remove:

        addhat = aadhar_address(simple_text_blank_remove,text_only_english,all_lan_text)
        # aadhar_address_local = aadhar_local_lan_address(simple_text_blank_remove,text_only_english,all_lan_text)

        if addhar_number in addhat:
            address_part  = addhat.split(addhar_number)
            addhar_address = address_part[0]

        else:
            addhar_address = addhat

        if addhar_number != "Unknown":
                mainlist['AdharID'] = addhar_number
        if addhar_address != "":
                mainlist['Address1'] = addhar_address

        

    elif addhar_address == "":
        if 'Father' in all_lan_text:
                get_details = father_name_detact(True,all_lan_text,text_only_english)
                for x in get_details:
                    try:
                        father_name_english = x['Father_Name_English']
                    except:
                        pass

                    try:
                        father_name = x['Father_Name']
                    except:
                        pass

                    try:
                        name1 = x['Name1']
                    except:
                        pass

                    try:
                        name2 = x['Name2']
                    except:
                        pass


        else:
            if 'Father' in text_only_english:
                simple_text_blank_remove = "\n".join(line for line in text_only_english.split('\n') if line.strip())
                get_details = father_name_detact(True,simple_text_blank_remove,text_only_english)
                for x in get_details:
                    try:
                        father_name_english = x['Father_Name_English']
                    except:
                        pass

                    try:
                        father_name = x['Father_Name']
                    except:
                        pass

                    try:
                        name1 = x['Name1']
                    except:
                        pass

                    try:
                        name2 = x['Name2']
                    except:
                        pass

        if 'Husband' in all_lan_text:
            get_details = husband_name_detact(True,text_only_english,text_only_english)
            for x in get_details:
                try:
                    husband_name_english = x['husband_name_english']
                except:
                    pass

                try:
                    husband_name = x['husband_name_local']
                except:
                    pass

                try:
                    name1 = x['Name1']
                except:
                    pass

                try:
                    name2 = x['Name2']
                except:
                    pass

        else:
            if 'Husband' in text_only_english:
                simple_text_blank_remove = "\n".join(line for line in text_only_english.split('\n') if line.strip())
                get_details = husband_name_detact(True,simple_text_blank_remove,text_only_english)
                for x in get_details:
                    try:
                        husband_name_english = x['husband_name_english']
                    except:
                        pass

                    try:
                        husband_name = x['husband_name_local']
                    except:
                        pass

                    try:
                        name1 = x['Name1']
                    except:
                        pass

                    try:
                        name2 = x['Name2']
                    except:
                        pass

        
        

        if name1 == "":
            get_details = all_details_detact(all_lan_text,dob_date,text_only_english,simple_text_blank_remove)
            for x in get_details:
                try:
                    name1 = x['Name1']
                except:
                    pass

        english_txt_blank_remove = "\n".join(line for line in text_only_english.split('\n') if line.strip())
        get_detailss = all_details_detact(english_txt_blank_remove,dob_date,text_only_english,simple_text_blank_remove)
        if name2 == "":
            for x in get_detailss:
                try:
                    name2 = x['Name2']
                except:
                    pass
        

        
        if  dob_date == "Unknown" and addhar_number == "Unknown" and \
            gender_get == "Unknown" and father_name_english == "" and \
            father_name == "" and name1 == "" and name2 == "" and \
            husband_name_english == "" and husband_name == "":
                return jsonify({"response": "999",
                                "message": "Error",
                                "responseValue": "Error Processing your request"
                            })
                
        else:
            if dob_date != "Unknown":
                mainlist['DOB'] = dob_date
            
            if addhar_number != "Unknown":
                mainlist['AdharID'] = addhar_number

            if gender_get != "Unknown":
                mainlist['Gender'] = gender_get
            
            if father_name_english != "":
                mainlist['Father Name English'] = father_name_english

            if father_name != "":
                if ":" in father_name:
                    mainlist['Father Name'] = father_name.split(":")[1]
                else:
                    mainlist['Father Name'] = father_name
            
            if name1 != "":
                mainlist['Name1'] = name1
            
            if name2 != "":
                mainlist['Name2'] = name2

            if husband_name_english != "":
                mainlist['Husband Name English'] = husband_name_english

            if husband_name != "":
                mainlist['Husband Name'] = husband_name

    
    else:
        if mainlist == {}:
            return jsonify({"response": "999",
                                "message": "Error",
                                "responseValue": "Error Processing your request"
                            })
            
    if mainlist != {}:
        return jsonify({"response": "000",
            "message": "Success",
            "responseValue": {
                "Table1": [
                    {
                        "DocumentResponse": mainlist
                    }
                ]
            }
        })


    

    



