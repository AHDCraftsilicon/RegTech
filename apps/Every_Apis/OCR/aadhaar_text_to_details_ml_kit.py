import math
from typing import Tuple, Union
import cv2
import numpy as np
import os , re
from deskew import determine_skew
import subprocess
import xml.etree.ElementTree as ET
from spellchecker import SpellChecker


# Initialize the spell checker
spell = SpellChecker()


# Get Aadhaar Number From Aadhaar String
def get_aadhaar_number(aadhaar_string):
    aadhaar_number = ""

    try:
        # \b\d{4}\s*\d{4}\s*\d{4}\b
        aadhaar_pattern = r"\b\d{4} \d{4} \d{4}\b"
        matchs = re.search(aadhaar_pattern, aadhaar_string)
        if matchs:
            aadhaar_number = matchs.group(0)

        print("-------- ", aadhaar_number)
        
        return aadhaar_number 
    except:
        pass


# Ger VID From Aadhaar String
def get_VID(aadhaar_string):
    vid_match = re.search(r'VID\s*:\s*(\d{8} \d{4} \d{4}|\d{4} \d{4} \d{4} \d{4})', aadhaar_string)

    try:
        vid_number = ""
        if vid_match:
            vid_number = vid_match.group(1)
        
        return vid_number
    except:
        pass



# Get Gender From Aadhaar String
def get_gender(aadhaar_string):
    aadhaar_string = aadhaar_string.lower()
    gender_pattern = re.compile(r'\bFEMALE|FEMALE|male|female|Male|Female|Famale|Femala\b', re.IGNORECASE)
    
    try:
        gender = ""
        if gender_pattern.search(aadhaar_string) != None:
            gender = gender_pattern.search(aadhaar_string).group()
            if 'fem' in gender:
                gender = 'Female'
            else:
                gender = 'Male'
            
        return gender
    except:
        pass

# Get DOB From Aadhaar String
def get_DOB(aadhaar_string):
    dob_match = re.compile(r'DOB:\s*(\d{2}/\d{2}[\|/]\d{4})').search(aadhaar_string)
    dob_date = ""

    try:
        if dob_match != None:
            dob_date = dob_match.group(1).replace('|', '/')
        else:
            if "Year of Birth" in aadhaar_string:
                if re.compile(r"Year of Birth\s*:\s*(\d{4})").findall(aadhaar_string) != []:
                    dob_date = re.compile(r"Year of Birth\s*:\s*(\d{4})").findall(aadhaar_string)[0]

        return dob_date
    except:
        pass


# Get Name From Aadhaar String
def get_name(aadhaar_string):
    try:
        cleaned_text = re.sub(r'\n\s*\n', '\n', aadhaar_string.strip())
        lines_list = cleaned_text.splitlines()

        previous_line_text = ""
        name = ""
        prev_line_text = ""

        # Iterate through the lines
        for line in lines_list:
            if "dob" in line.lower(): 
                name =  re.sub(r'[^a-zA-Z\s]', '', previous_line_text.strip()).strip()
                break 
            previous_line_text = line 
        else:
            name = ""

        if name == "":
            for line in lines_list:
                if "year" in line.lower(): 
                    name =  re.sub(r'[^a-zA-Z\s]', '', previous_line_text.strip()).strip()
                    break 
                previous_line_text = line 
            else:
                name = ""


        if name == "TTR" or name == "YuMale":
            for line in lines_list:
                if "dob" in line.lower(): 
                    name =  re.sub(r'[^a-zA-Z\s]', '', previous_line_text.strip()).strip()
                    break 
                previous_line_text = prev_line_text 
                prev_line_text = line

        if name == "YoH":
            matches = re.findall(r'^\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\s*$', aadhaar_string, re.MULTILINE)

            if matches:
                for names in matches:
                    name = names
                
        return name
    except:
        pass


# Father & Husband KeyWord Name From Aadhaar String
def get_keyword_name(aadhaar_string,keyword):

    try:
        cleaned_text = re.sub(r'\n\s*\n', '\n', aadhaar_string.strip())
        lines_list = cleaned_text.splitlines()

        name = ""

        prev_prev_line_text = ""  # Variable to store the line before the previous one
        prev_line_text = "" 
        
        for line in lines_list:
            if str(keyword).lower() in line.lower(): 
                name =  re.sub(r'[^a-zA-Z\s]', '', prev_prev_line_text.strip()).strip()
                break 
            prev_prev_line_text = line  # Move previous to two lines ago
            # prev_line_text = line

        if "GOVERNMENT OF INDIA" in name:
            for line in lines_list:
                if str(keyword).lower() in line.lower(): 
                    name =  re.sub(r'[^a-zA-Z\s]', '', prev_prev_line_text.strip()).strip()
                    break 
                prev_prev_line_text = prev_line_text  # Move previous to two lines ago
                prev_line_text = line
        
        return name
    except:
        pass


# Get Father name From Aadhaar String
def get_father_name(aadhaar_string):
    try:
        father_name_match = re.compile(r'Father\s*:\s*([A-Za-z\s]+)(?=\n)', re.IGNORECASE).search(aadhaar_string)
        
        father_name = ""
        if father_name_match:
            father_name = father_name_match.group(1).strip()

        return father_name
    except:
        pass

# Get Husband name from Aadhaar String
def get_husband_name(aadhaar_string):
    try:
        match_husband_string = re.compile(r'Husband\s*[-:]\s*([A-Za-z\s]+)(?=\n)|Husband\s*:\s*([A-Z\s]+)(?=\n)', re.IGNORECASE).search(aadhaar_string)
        husband_name = ""
        if match_husband_string:
            husband_name = match_husband_string.group(1).strip()

        return husband_name
    except:
        pass

# Get Enrollment Number from Aadhaar String
def get_enrollment_number(aadhaar_string):
    try:
        enrolment_pattern = r"Enrolment No\.\s*:\s*(\d{4}/\d{5}/\d{5})"
        enrolment_match = re.search(enrolment_pattern, aadhaar_string)

        enrolment_no = ""
        if enrolment_match:
            enrolment_no = enrolment_match.group(1)

        return enrolment_no
    except:
        pass

# get Address From Aadhaar String
def get_address(aadhaar_string):
    try:

        address = ""
        if "To" in aadhaar_string:
            address_match = re.search(r"To\s+(.*?\b\d{6}\b)", aadhaar_string, re.DOTALL)
            address = address_match.group(1).strip() if address_match else ""

        if address == "":
            if 'S/O' in aadhaar_string:
                address_match = re.search(r"S/O\s*:\s*(.*?\d{6})", aadhaar_string, re.DOTALL)
                if address:
                    address = address_match.group(0).strip()
                        

        if address == "":
            if 'Addr' in aadhaar_string:
                address_pattern = r'Address\s*:\s*(.*?)(\d{6})'
                address_match = re.search(address_pattern, aadhaar_string, re.DOTALL)
                if address_match:
                    address = address_match.group(1).strip().replace('\n', ', ')  # Clean up newlines
                    pincode = address_match.group(2).strip()
                    address = f"{address}, {pincode}"

        if address != "":
            address = ' '.join(address.splitlines())
            address = address.replace("Government of India", "")
        
        return address
    except:
        pass

# get Father Name From Aadhaar String
def get_father_name_from_address(aadhaar_string):
    try:
        father_name = ""
        
        if 'S/O' in aadhaar_string:
            father_pattern = r'S/O\s+([A-Za-z\s.]+)'
            father_match = re.search(father_pattern, aadhaar_string)
            if father_match:
                father_name = father_match.group(1).strip()

        if 'C/O' in aadhaar_string:
            father_pattern = r'C/O\s+([A-Za-z\s]+?),'
            father_match = re.search(father_pattern, aadhaar_string)
            if father_match:
                father_name = father_match.group(1).strip()

        return father_name
    except:
        pass

# Get Name From Address String
def get_name_from_address(aadhaar_string):
    try:
        name_pattern = r'To\s*(.+?)\s*\n'  # Matches the line immediately after "To"
        name = ""
        # Search for the name in the text
        name_match = re.search(name_pattern, aadhaar_string, re.DOTALL)

        if name_match:
            name = name_match.group(1).strip()
        
        return name
    except:
        pass


# Remove Extra Keywords from address
def address_extra_keyword(aadhaar_address):
    # Split the text into words
    words = aadhaar_address.split()

    results = []

    for index, word in enumerate(words):
        # Get candidates for the current word
        candidates = spell.candidates(word)
        
        # If there are candidates, take the first one; otherwise, keep the original word
        if candidates:
            corrected_word = next(iter(candidates))
        else:
            corrected_word = word
            

        # Append a dictionary with original word, corrected word, and its position
        results.append({
            'old_word': word,
            'corrected_word': corrected_word,
            'position': index
        })

    # Output the results
    headers_keyword = []
    for result in results:
        if result['corrected_word'] == "Unique":
            headers_keyword.append(result['old_word'])

        if result['corrected_word'] == "identification":
            headers_keyword.append(result['old_word'])

        if result['corrected_word'] == "Authority":
            headers_keyword.append(result['old_word'])

        if result['corrected_word'] == "of":
            headers_keyword.append(result['old_word'])

        if result['corrected_word'] == "india":
            headers_keyword.append(result['old_word'])


    return headers_keyword


#  Aadhaar Details Final
def aadhaar_details(aadhaar_string):

    aadhaar_strings = aadhaar_string.replace("VIO","VID").replace("wIO","W/O").replace("SIO","S/O")\
        .replace("1947","S/O").replace("S/Ó","S/O").replace("UNIOUE DENTTEICATION AUTHORIIY OFINDIA","")\
        .replace("Unique ldentification Authority of India","").replace("Unique tdentification Authority of ndia","")\
        .replace("Unique ldentification Authority of fndia","").replace("SO",'S/O').replace("help@uidai.gov.in","")
    # aadhaar_strings = aadhaar_strings

    # if 'government of' in aadhaar_string.lower():
    #     print("Document is Aadhaar Card")

    father_name = ""
    husband_name = ""
    
    gender = get_gender(aadhaar_strings)
    DOB = get_DOB(aadhaar_strings)
    aadhaar_number = get_aadhaar_number(aadhaar_strings)
    VID = get_VID(aadhaar_strings)
    
    address = get_address(aadhaar_strings)
    enrollment_number = get_enrollment_number(aadhaar_strings)
    

    if "fath" in aadhaar_string.lower():
        father_name = get_father_name(aadhaar_strings)
        name = get_keyword_name(aadhaar_strings,'fath')
    
    elif 'hus' in aadhaar_string.lower():
        husband_name = get_husband_name(aadhaar_strings)
        name = get_keyword_name(aadhaar_strings,'hus')

    else:
        father_name = get_father_name_from_address(address)
        name = get_name(aadhaar_strings)

    if name == "" and address != "":
        name = get_name_from_address(aadhaar_string)

    if address != "":
        father_name = get_father_name_from_address(address)
        address_test = address_extra_keyword(address)
        # print(address_test)

        for address_keyword in address_test:
            address = address.replace(address_keyword,"")

        address = address.replace(name,"")
        address = address.replace("S/O","")
        address = address.replace("C/O","")
        address = address.replace(father_name ,"")
        address = address.replace("3ITETR" ,"")
        address = address.replace(enrollment_number ,"")
        address = address.replace(":" ,"")
        address = address.replace("Enrolment No." ,"")
        address = re.sub(r'\s+', ' ', address).strip()
        
        

        # first_comma_index = address.find(',')
        # if first_comma_index != -1:
        #     address = address[:first_comma_index] + address[first_comma_index + 1:].strip()

        

    # print("Gender = ", gender)
    # print("DOB = ", DOB)
    # print("Aadhaar Number = ", aadhaar_number)
    # print("VID = ", VID)
    # print("Name = ", name)
    # print("Address = ", address)
    # print("Father Name = ", father_name)
    # print("Husband Name = ", husband_name)

    if address == "" and DOB == "" and gender == "" and husband_name == "" and \
        father_name == "" and name == "" and VID == "" and aadhaar_number == "":
        return []
    else:


        aadhaar_details = []
        aadhaar_details.append({"Address":address,
                            "DOB":DOB.strip(),
                            "Gender":gender.strip(),
                            "Husband_name":husband_name,
                            "Father_name":father_name,
                            "Name":name,
                            "VID" : VID,
                            "AadharID" : aadhaar_number,
                            })

        return aadhaar_details


# QR COde read
def QR_code_data_Read(xml_string):
    try:
        xml_string = xml_string.replace('</?xml', '<?xml').strip()
        root = ET.fromstring(xml_string)
        # print(root.attrib)



        address_merge = ""

        try:
            address_merge +=root.attrib.get('co') + ","
        except:
            pass

        try:
            address_merge +=root.attrib.get('house') + ","
        except:
            pass

        try:
            address_merge +=root.attrib.get('street') + ","
        except:
            pass

        try:
            address_merge +=root.attrib.get('lm') + ","
        except:
            pass

        try:
            address_merge +=root.attrib.get('loc')+ ","
        except:
            pass

        try:
            address_merge +=root.attrib.get('vtc')+ ","
        except:
            pass

        try:
            address_merge +=root.attrib.get('po')+ ","
        except:
            pass

        try:
            address_merge +=root.attrib.get('dist')+ ","
        except:
            pass

        try:
            address_merge +=root.attrib.get('subdist')+ ","
        except:
            pass

        try:
            address_merge +=root.attrib.get('state')+ ","
        except:
            pass

        try:
            address_merge +=root.attrib.get('pc')+ ","
        except:
            pass
        
        aadhaar_details = []
        Address = address_merge
        Name = root.attrib.get('name')
        DOB = root.attrib.get('dob')
        Gender = root.attrib.get('gender')
        AadharID = root.attrib.get('uid')
        if Gender == 'M':
            Gender = "Male"
        elif Gender == 'F':
            Gender = "Female"

        
        aadhaar_details.append({"Address":Address,
                                "DOB":DOB,
                                "Gender":Gender,
                                "Husband_name":"",
                                "Father_name":"",
                                "Name":Name,
                                "VID" : "",
                                "AadharID" : AadharID,
                                })
        
        return aadhaar_details
    except:
        return []




#  Aadhaar Qr Code
def aadhaar_Qr_scan(image_path):
    np_arr = np.frombuffer(image_path, np.uint8)
    # target_image_path =  image_path
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    cv2.imwrite('Qr_image.png', image)
    xml_string = subprocess.run(['zbarimg', '--raw', 'Qr_image.png'], capture_output=True)
    # print(xml_string)
    
    if xml_string.returncode  == 0:
        xml_string = xml_string.stdout.decode('utf-8')
        qr_code_details = QR_code_data_Read(xml_string)
        if len(qr_code_details) != 0:
            return  qr_code_details
        

    # # if xml_string != "":
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(gray, -1, sharpen_kernel)
    cv2.imwrite('Qr_image.png', sharpen)
    result = subprocess.run(['zbarimg', '--raw', 'Qr_image.png'], capture_output=True)
    xml_string = result.stdout.decode('utf-8')

    if xml_string != "":
        qr_code_details = QR_code_data_Read(xml_string)
        if len(qr_code_details) != 0:
            return qr_code_details
        
    return {}

