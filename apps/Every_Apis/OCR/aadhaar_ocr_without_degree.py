import math
from typing import Tuple, Union
from PIL import Image, ImageFilter , ImageEnhance
import cv2
import numpy as np
import os , re
from deskew import determine_skew
import pytesseract
import subprocess
import xml.etree.ElementTree as ET

# tessract path
from tesseract_path import *


def rotate(
        image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)


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


def Regex_Search(bounding_boxes,aadhaar_string):
    possible_UIDs = []
    aadhaar_number = []
    Result = ""

    for character in range(len(bounding_boxes)):
        if len(bounding_boxes[character]) != 0:
            Result += bounding_boxes[character][0]
        else:
            Result += '?'

 

    matches = [match.span() for match in re.finditer(r'\d{12}', Result)]
    for match in matches:
        UID = int(Result[match[0]:match[1]])

        if compute_checksum(UID) == 0 and UID % 10000 != 1947:
            possible_UIDs.append([UID, match[0]])
            aadhaar_number.append(UID)

    possible_UIDs = np.array(possible_UIDs)

    if len(possible_UIDs) == 0:
        aadhaar_pattern = r"\b\d{4}\s*\d{4}\s*\d{4}\b"
        matchs = re.search(aadhaar_pattern, aadhaar_string)
        if matchs:
            aadhaar_numbers = matchs.group(0)
            aadhaar_number.append(aadhaar_numbers)
    
    return aadhaar_number 



# QR COde read
def QR_code_data_Read(xml_string):
    try:
        xml_string = xml_string.replace('</?xml', '<?xml').strip()
        root = ET.fromstring(xml_string)
        print(root.attrib)



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


# Get Address From Aadhaar String
def get_Address(address_image,get_address_all_sting):
    try:

        # if get_address_all_sting:
        #     address_pattern = r"(?:[A-Za-z0-9\s,.()/-]+(?:Street|St|Road|Raiway|Station|Flat|Floor|Apariment|M.C|Garden)[A-Za-z0-9\s,.()/-]*)+"

        #     # Use re.search to find the address in the text
        #     match = re.search(address_pattern, get_address_all_sting)
        #     # print(match)
        #     if match:
        #         address = match.group()

        #         return address


        if 'VIC' in get_address_all_sting:
            address = ""
            vic_pattern = r'VIC:\s*([\w\s]+),'
            po_pattern = r'PO:\s*([\w\s]+),'
            district_pattern = r'District:\s*([\w\s]+),'
            state_pattern = r'State:\s*([\w\s]+),'
            pincode_pattern = r'PIN Code:\s*(\d{6}),'

            # Extract values using regex
            vic = re.search(vic_pattern, get_address_all_sting)
            po = re.search(po_pattern, get_address_all_sting)
            district = re.search(district_pattern, get_address_all_sting)
            state = re.search(state_pattern, get_address_all_sting)
            pincode = re.search(pincode_pattern, get_address_all_sting)

            if vic:
                address += vic.group(1).strip() + " "

            if po:
                address += po.group(1).strip() + " "
            
            if district:
                address += district.group(1).strip() + " "
            
            if state:
                address += state.group(1).strip() + " "

            if pincode:
                address += ",PIN Code " + pincode.group(1).strip()

            return address

        else:
            # address_image = cv2.imread(address_image)

            gray = cv2.cvtColor(address_image, cv2.COLOR_BGR2GRAY)
            sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpen = cv2.filter2D(gray, -1, sharpen_kernel)

            # img_pil = Image.fromarray(image_rgb)
            # img_pil.show()

            # 0 degree Image
            angle = determine_skew(sharpen,angle_pm_90=True)    
            rotated = rotate(address_image, angle, (0, 0, 0))

            height, width = rotated.shape[:2]
            if height > 1000 or width > 1000:
                rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

            # Use pytesseract to get bounding boxes around text
            data = pytesseract.image_to_data(rotated, output_type=pytesseract.Output.DICT)



            left_margin = 15  # Increase this value to widen the left side
            right_margin = 500  # Increase this value to widen the right side
            top_margin = 10  # Increase this value to widen the top side
            bottom_margin = 1000 

            for i in range(len(data['text'])):
                text = data['text'][i].strip()  # Get the text and remove extra spaces
                confidence = data['conf'][i]
                
                
                # Check if confidence is a valid number and greater than threshold
                try:
                    if "enrol" in text.lower():
                        left_margin = 150  # Increase this value to widen the left side
                        right_margin = 500  # Increase this value to widen the right side
                        top_margin = 200  # Increase this value to widen the top side
                        bottom_margin = 400 

                        keyword_found = True
                        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                        x_new = max(x - left_margin, 0)  # Ensure x does not go below 0
                        y_new = max(y - top_margin, 0)  # Ensure y does not go below 0
                        w_new = w + left_margin + right_margin  # Increase width
                        h_new = h + top_margin + bottom_margin  # Increase height

                        # Crop the image using the adjusted bounding box
                        cropped_image = rotated[y_new:y_new + h_new, x_new:x_new + w_new]
                        
                        # cropped_image = image[y:y + 500, x:x + 500]
                        cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
                        # cropped_image_pil.save(f'cropped_image_{i}.png')

                        enhancer = ImageEnhance.Sharpness(cropped_image_pil)
                        sharp_image = enhancer.enhance(2.0)

                        # Save and display the sharpened image
                        # cv2.imshow('sharpened_image.jpg', sharp_image)
                        address = pytesseract.image_to_string(sharp_image)
                        # print("****** ", address)

                        # Optionally, display the cropped image
                        # cropped_image_pil.show()
                    
                        address_pattern = re.compile(r"(?:\$/O|S/O|S/0) [^\n]+\n([\s\S]+?)\n(?:Ty|\d{10})")

                        match = address_pattern.search(address)
                        if match:
                            address = match.group(1)
                            return address
                       
        

                    # print(text.lower())
                    # Check if the text matches any of the specified keywords
                    if "addr" in text.lower():
                        keyword_found = True
                        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                        x_new = max(x - left_margin, 0)  # Ensure x does not go below 0
                        y_new = max(y - top_margin, 0)  # Ensure y does not go below 0
                        w_new = w + left_margin + right_margin  # Increase width
                        h_new = h + top_margin + bottom_margin  # Increase height

                        # Crop the image using the adjusted bounding box
                        cropped_image = rotated[y_new:y_new + h_new, x_new:x_new + w_new]
                        
                        # cropped_image = image[y:y + 500, x:x + 500]
                        cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
                        # cropped_image_pil.save(f'cropped_image_{i}.png')

                        enhancer = ImageEnhance.Sharpness(cropped_image_pil)
                        sharp_image = enhancer.enhance(2.0)

                        # Save and display the sharpened image
                        # cv2.imwrite('sharpened_image.jpg', sharpened_image)
                        string_aadhaar = pytesseract.image_to_string(sharp_image)

                        pattern = r'(?:Address|Addresst|Adaress)[^A-Za-z0-9]*([\s\S]*?)(?=\n\n|$)'

                        # Find all matches
                        addresses = re.findall(pattern, string_aadhaar)

                        # print("*****" , string_aadhaar)

                        # Clean and display addresses
                        for address in addresses:
                            addresss = re.sub(r'^\s?.\n', '', address.strip()).strip()
                            return addresss
                        

                
                except ValueError:
                    # Handle cases where conversion to float fails (e.g., invalid confidence value)
                    print(f"Invalid confidence value for index {i}: {confidence}")
    except:
        pass

# Get Name From Aadhaar String
def get_name(aadhaar_string):
    try:
        cleaned_text = re.sub(r'\n\s*\n', '\n', aadhaar_string.strip())
        lines_list = cleaned_text.splitlines()

        previous_line_text = ""
        name = ""

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

        return name
    except:
        pass



# Get DOB From Aadhaar String
def get_DOB(aadhaar_string):
    try:
        dob_match = re.compile(r'\b\s*(\d{2}/\d{2}/\d{4})').search(aadhaar_string)
        final_dob = ""

        if dob_match != None:
            final_dob = dob_match.group()
        else:
            if re.compile(r"Year of Birth\s*:\s*(\d{4})").findall(aadhaar_string) != []:
                final_dob = re.compile(r"Year of Birth\s*:\s*(\d{4})").findall(aadhaar_string)[0]
            else:
                final_dob= ""

        if final_dob == "":
            dob_match = re.compile(r'\b\s*(\d{2}/\d{2}/\d{4})').search(aadhaar_string)
            final_dob = ""

            if dob_match != None:
                final_dob = dob_match.group()
            else:
                if re.compile(r"Year of Birth\s*:\s*(\d{4})").findall(aadhaar_string) != []:
                    final_dob = re.compile(r"Year of Birth\s*:\s*(\d{4})").findall(aadhaar_string)[0]
                else:
                    final_dob= ""

        

        return final_dob
    except:
        pass

# Get Gender From Aadhaar String
def get_gender(aadhaar_string):
    try:
        gender_pattern = re.compile(r'\bFEMALE|FEMALE|male|female|Male|Female|Famale\b', re.IGNORECASE)
        
        gender = ""
        if gender_pattern.search(aadhaar_string) != None:
            gender = gender_pattern.search(aadhaar_string).group()


        if gender == "":
            if gender_pattern.search(aadhaar_string) != None:
                gender = gender_pattern.search(aadhaar_string).group()

        return gender
    except:
        pass


# Ger VID From Aadhaar String
def get_VID(aadhaar_string):
    try:
        vid_match = re.search(r'(\d{4}\s\d{4}\s\d{4}\s\d{4})', aadhaar_string)

        if vid_match:
            vid_number = vid_match.group(1)
            return vid_number
        else:
            return ""
    except:
        pass

def check_blur_and_clarity(image_path):
    # Read the image
    # img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image_path, cv2.COLOR_BGR2GRAY)
    
    # Calculate Laplacian variance
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Set a threshold for determining if the image is blurry
    threshold = 150  # You can adjust this value based on your requirements
    
    # Check if the image is blurry
    if laplacian_var < threshold:
        return "The image is blurry"
    else:
       return "The image is clear"
    

# Gender through name get
def keyword_name(aadhaar_string,keywords,genders=False,Father=False):
    try:
        cleaned_text = re.sub(r'\n\s*\n', '\n', aadhaar_string.strip())
        lines_list = cleaned_text.splitlines()
        prev_prev_line_text = ""  # Variable to store the line before the previous one
        prev_line_text = ""   
        
        name = ""
        if genders:
            for line in lines_list:
                if str(keywords) in line: 
                    name =  re.sub(r'[^a-zA-Z\s]', '', prev_prev_line_text.strip()).strip()
                    break 
                prev_prev_line_text = prev_line_text  # Move previous to two lines ago
                prev_line_text = line
            else:
                name = "" 
        

            return name
        
        if Father:
            for line in lines_list:
                if str(keywords).lower() in line.lower(): 
                    name =  re.sub(r'[^a-zA-Z\s]', '', prev_prev_line_text.strip()).strip()
                    break 
                prev_prev_line_text = prev_line_text  # Move previous to two lines ago
                prev_line_text = line
            else:
                name = "" 
        
            return name
    except:
        pass

# Ger Father Name From Aadhaar String
def Father_husband_name(aadhaar_string,keyword):

    try:
        husband_keyword_check = ""
        father_keyword_check = ""
        if keyword == "husband":
            match_husband_string = re.compile(r'Husband\s*[-:]\s*([A-Za-z\s]+)|Husband\s*:\s*([A-Z\s]+)', re.IGNORECASE).search(aadhaar_string)
            
            if match_husband_string:
                husband_keyword_check = match_husband_string.group(1).strip()

        
        elif keyword == "father":
            match = re.compile(r'Father\s*[-:]\s*([A-Za-z\s]+)', re.IGNORECASE).search(aadhaar_string)

            if match:
                father_keyword_check = match.group(1).strip()
            
        return husband_keyword_check.strip(), father_keyword_check.strip()
    except:
        pass

def father_name_from_address(address):
    # Regex pattern to find 'S/O' followed by the father's name
    try:
        pattern = r"S/O\s*:\s*(.*?)(?:,|\n|$)|S/O\s+(.*?)(?:\.\s|,|$)|S/0 ([^\n]+)"
        father_name = ""
        match = re.search(pattern, address, re.IGNORECASE)
        if match:
            father_name = match.group()  # Extract and clean the name
            return father_name
        return ""
    except:
        pass

def husband_name_from_address(address):
    try:
        pattern = r"W/O:\s*(.*?)(?:\n|,|$)"
        
        match = re.search(pattern, address, re.IGNORECASE)
        if match:
            father_name = match.group(1)  # Extract and clean the name
            return father_name
        return ""
    except:
        pass

# Name Clean Extra Character remove
def clean_name(text):
    # Define the keywords to be removed
    keywords = r'\b(?:[Hh]usband|[Hh]usb\w*|[Ff]ather)\b'
    
    # Remove single-character word at the beginning
    cleaned_text = re.sub(r'\b\w\b', '', text)
    
    # Remove unwanted keywords (husband, father, etc.)
    cleaned_text = re.sub(keywords, '', cleaned_text)
    
    # Remove single-character word at the end
    # cleaned_text = re.sub(r'\b\w\b$', '', cleaned_text).strip()

    # Remove extra spaces
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text


def Image_to_text(image_array,image):
    string_store_all_deggre = ""
    masked_image_pil = Image.fromarray(image_array)

    aadhaar_string = ""
    # Image to without lan
    bounding_boxes = pytesseract.image_to_boxes(masked_image_pil).split(" 0\n")
    possible_UIDs = Regex_Search(bounding_boxes,aadhaar_string)

    # Image to string
    aadhaar_string = pytesseract.image_to_string(masked_image_pil)
    
    string_store_all_deggre += aadhaar_string

    language_codes = ['eng']
    languages = '+'.join(language_codes)
    custom_config = f'--oem 3 --psm 6 -l {languages}'
    aadhaar_string = pytesseract.image_to_string(masked_image_pil, config=custom_config)
    string_store_all_deggre += aadhaar_string

    if len(possible_UIDs) == 0:
        language_codes = ['eng']
        languages = '+'.join(language_codes)
        custom_config = f'--oem 3 --psm 6 -l {languages}'
        bounding_boxes = pytesseract.image_to_boxes(masked_image_pil, config=custom_config).split(" 0\n")
        possible_UIDs = Regex_Search(bounding_boxes,aadhaar_string)
        
    # Get details
    address = ""
    husband_name = ""
    Father_name = ""
    Name = ""

    DOB_date = get_DOB(string_store_all_deggre)
    gender = get_gender(string_store_all_deggre)

    if 'add' or 'VIC' in string_store_all_deggre:
        address = get_Address(image,string_store_all_deggre)

    aadhaar_number = ""
    if len(possible_UIDs) != 0:
        aadhaar_number = possible_UIDs[0]

    # if len(possible_UIDs) != 0:
    #     aadhaar_number = possible_UIDs[0]


    if "Father" in aadhaar_string:
        Name = keyword_name(aadhaar_string,"fath",genders=False,Father=True)
        husband_name ,Father_name = Father_husband_name(aadhaar_string,"father")

    elif "Husb" in aadhaar_string:
        Name = keyword_name(aadhaar_string,"husb",genders=False,Father=True)
        husband_name ,Father_name = Father_husband_name(aadhaar_string,"husband")
    else:
        if Name == "":
            Name = get_name(string_store_all_deggre)
            if Name == "":
                Name = keyword_name(aadhaar_string,gender,genders=True,Father=False)

    if address == None:
        address = ""
    
    address = address.replace("S/0","S/O")
    if 'S/O' in address:
        # print("---------------")
        Father_name = father_name_from_address(address)
    
    Father_name = Father_name.replace("S/O","").replace("S/0","")

    if 'W/O' in address:
        husband_name = husband_name_from_address(address)

    aadhaar_details = []

    if aadhaar_number == "" and  gender == "" and Name == "" and DOB_date == "" and \
            address == "" and husband_name == "" and Father_name == "":
        
        return []
    else:
        if gender == "" and Name == "" and DOB_date == "" and \
            address == "" and husband_name == "" and Father_name == "":
            return []
        else:
            aadhaar_details.append({"Address":address.strip(),
                                "DOB":DOB_date.strip(),
                                "Gender":gender.strip(),
                                "Husband_name":clean_name(husband_name),
                                "Father_name":clean_name(Father_name),
                                "Name":clean_name(Name),
                                # "VID" : VID_Info.strip(),
                                "AadharID" : aadhaar_number,
                                })
            return aadhaar_details

    #     print("Aadhaar number = " , aadhaar_number)
    #     print("gender = " , gender)
    #     print("name = " , Name)
    #     print("DOB_date = " , DOB_date)
    #     print("Address = " , address)
    #     print("husband_name = " , husband_name)
    #     print("Father_name = " , Father_name)


    # return possible_UIDs , aadhaar_string


def image_rotate_and_check_number(image):

    check_quality = check_blur_and_clarity(image)

    if check_quality == "The image is blurry":
        return []
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpen = cv2.filter2D(gray, -1, sharpen_kernel)
        degree = 0

        # 0 degree Image
        angle = determine_skew(sharpen,angle_pm_90=True)    
        rotated = rotate(image, angle, (0, 0, 0))

        height, width = rotated.shape[:2]
        if height > 1000 or width > 1000:
            rotated = cv2.resize(rotated, (int(width/2), int(height/2)))
            
        aadhaar_details =  Image_to_text(rotated,image)


        # cv2.imshow('Target Image', rotated)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return aadhaar_details

        # basic_aadhaar_details = get_another_details(aadhaar_string,orignal_img,degree,validate_number)


def Aadhaar_main(image_path):
    
       # for x in os.listdir('./check_addhar/'):
    # print("-----  " , image_path)
    # target_image_path = image_path
    # image = cv2.imread(image_path)
    np_arr = np.frombuffer(image_path, np.uint8)
    target_image_path =  image_path
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # QR code decode
    cv2.imwrite('Qr_image.png', image)
    xml_string = subprocess.run(['zbarimg', '--raw', 'Qr_image.png'], capture_output=True)

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
        
    aadhaar_details = image_rotate_and_check_number(image)
    if len(aadhaar_details) == 0:
        return []
    else:
        return aadhaar_details
    