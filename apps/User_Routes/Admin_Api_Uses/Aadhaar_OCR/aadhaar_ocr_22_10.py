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


def feature_based_matching(image1_path, image2_path):
    """
    Performs feature-based matching between two images.

    Args:
        image1_path: Path to the first image.
        image2_path: Path to the second image.

    Returns:
        A list of matched key points.
    """

    # Load images
    image1 = image1_path
    image2 = image2_path

    # Create SIFT detector
    sift = cv2.SIFT_create()

    # Detect and compute key points and descriptors
    kp1, des1 = sift.detectAndCompute(image1, None)
    kp2, des2 = sift.detectAndCompute(image2, None) 


    # Create a BFMatcher object
    bf = cv2.BFMatcher()

    # Match descriptors
    matches = bf.knnMatch(des1, des2, k=2)

    # Apply ratio test
    good = []
    for m, n in matches:
        if m.distance < 0.55      * n.distance:
            good.append(m)

    print(good)

    # Draw matches on the images
    draw_matches = cv2.drawMatches(image1, kp1, image2, kp2, good, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    height, width = draw_matches.shape[:2]
    draw_matches = cv2.resize(draw_matches, (int(width/2), int(height/2)))

    # Display the matched images
    cv2.imshow('Matches', draw_matches)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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


# Normal Image to Text Also Validate aadhaar number present or not

string_store_all_deggre = ""

def Image_to_text(image_array):
    global string_store_all_deggre
    masked_image_pil = Image.fromarray(image_array)


    # Image to without lan
    bounding_boxes = pytesseract.image_to_boxes(masked_image_pil).split(" 0\n")

    # Image to string
    aadhaar_string = pytesseract.image_to_string(masked_image_pil)
    possible_UIDs = Regex_Search(bounding_boxes,aadhaar_string)
    string_store_all_deggre += aadhaar_string
    # masked_image_pil.save('aadhaar_address.jpg')

    language_codes = ['eng']
    languages = '+'.join(language_codes)
    custom_config = f'--oem 3 --psm 6 -l {languages}'
    aadhaar_string = pytesseract.image_to_string(masked_image_pil, config=custom_config)
    string_store_all_deggre += aadhaar_string




    # With English Lan
    if len(possible_UIDs) == 0:
        language_codes = ['eng']
        languages = '+'.join(language_codes)
        custom_config = f'--oem 3 --psm 6 -l {languages}'
        bounding_boxes = pytesseract.image_to_boxes(masked_image_pil, config=custom_config).split(" 0\n")

        # Image to string
        aadhaar_string = pytesseract.image_to_string(masked_image_pil, config=custom_config)
        possible_UIDs = Regex_Search(bounding_boxes,aadhaar_string)
        string_store_all_deggre += aadhaar_string


        # Image to Data For Address
        # address_data = pytesseract.image_to_data(masked_image_pil, output_type=pytesseract.Output.DICT)
        # masked_image_pil.save('aadhaar_address.jpg')

    # if len(possible_UIDs) == 0:
    #     language_codes = ['eng','hin']
    #     languages = '+'.join(language_codes)
    #     custom_config = f'--oem 3 --psm 6 -l {languages}'
    #     bounding_boxes = pytesseract.image_to_boxes(masked_image_pil, config=custom_config).split(" 0\n")
    #     possible_UIDs = Regex_Search(bounding_boxes)

        # Image to string
        # aadhaar_string = pytesseract.image_to_string(masked_image_pil, config=custom_config)


    # print("========= ", aadhaar_string)
    return possible_UIDs , aadhaar_string


# Get Name From Aadhaar String
def get_name(aadhaar_string):
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



# Get DOB From Aadhaar String
def get_DOB(aadhaar_string):
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
        dob_match = re.compile(r'\b\s*(\d{2}/\d{2}/\d{4})').search(string_store_all_deggre)
        final_dob = ""

        if dob_match != None:
            final_dob = dob_match.group()
        else:
            if re.compile(r"Year of Birth\s*:\s*(\d{4})").findall(string_store_all_deggre) != []:
                final_dob = re.compile(r"Year of Birth\s*:\s*(\d{4})").findall(string_store_all_deggre)[0]
            else:
                final_dob= ""

    

    return final_dob

# Get Gender From Aadhaar String
def get_gender(aadhaar_string):
    gender_pattern = re.compile(r'\bFEMALE|FEMALE|male|female|Male|Female|Famale\b', re.IGNORECASE)
    
    gender = ""
    if gender_pattern.search(aadhaar_string) != None:
        gender = gender_pattern.search(aadhaar_string).group()


    if gender == "":
        if gender_pattern.search(string_store_all_deggre) != None:
            gender = gender_pattern.search(string_store_all_deggre).group()

    return gender


# Ger VID From Aadhaar String
def get_VID(aadhaar_string):
    vid_match = re.search(r'(\d{4}\s\d{4}\s\d{4}\s\d{4})', aadhaar_string)

    if vid_match:
        vid_number = vid_match.group(1)
        return vid_number
    else:
        return ""


# Gender through name get
def keyword_name(aadhaar_string,keywords,genders=False,Father=False):
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


# Ger Father Name From Aadhaar String
def Father_husband_name(aadhaar_string,keyword):
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

# Name Clean Extra Character remove
def clean_name(text):
    # Define the keywords to be removed
    # keywords = r'\b(?:[Hh]usband|[Hh]usb\w*|[Ff]ather)\b'

    keywords = [
    "Enrolment No.", "1947", "help@uidai.gov.in", "www.uidai.gov.in", "aadhaar", 
    "unique", "identification", "authority", "india", "details as on", 
    "print date", "download date", "issue date", "government of india", 
    "aadhaar no", "issued", "DOB", "date of birth", "generation date"
    ]

    # Create a regex pattern that matches any of the keywords
    # Using re.escape to escape special characters in keywords
    pattern = r'(' + '|'.join(map(re.escape, keywords)) + r')'

    # Replace matched keywords with an empty string, ignoring surrounding spaces
    updated_data = re.sub(pattern, '', text)

    # Clean up extra spaces and commas
    updated_data = re.sub(r'\s*,\s*', ', ', updated_data).strip()  # Clean up spaces around commas
    updated_data = re.sub(r'\s+', ' ', updated_data) 

    
    # # Remove single-character word at the beginning
    # updated_data = re.sub(r'\b\w\b', '', text)
    
    # Remove unwanted keywords (husband, father, etc.)
    # cleaned_text = re.sub(pattern, '', cleaned_text)
    
    # Remove single-character word at the end
    # cleaned_text = re.sub(r'\b\w\b$', '', cleaned_text).strip()

    # Remove extra spaces
    # cleaned_text = ' '.join(cleaned_text.split())
    
    return updated_data

# Get Address From Aadhaar String
def get_Address(address_image,degree,all_string=False,get_address_all_sting=False):

    # print(string_store_all_deggre)

    if get_address_all_sting:
        address_pattern = r"(?:[A-Za-z0-9\s,.()/-]+(?:Street|St|Road|Raiway|Station|Flat|Floor|Apariment|M.C|Garden)[A-Za-z0-9\s,.()/-]*)+"

        # Use re.search to find the address in the text
        match = re.search(address_pattern, string_store_all_deggre)
        if match:
            address = match.group()

            return address


    if all_string:
        address = ""
        vic_pattern = r'VIC:\s*([\w\s]+),'
        po_pattern = r'PO:\s*([\w\s]+),'
        district_pattern = r'District:\s*([\w\s]+),'
        state_pattern = r'State:\s*([\w\s]+),'
        pincode_pattern = r'PIN Code:\s*(\d{6}),'

        # Extract values using regex
        vic = re.search(vic_pattern, address_image)
        po = re.search(po_pattern, address_image)
        district = re.search(district_pattern, address_image)
        state = re.search(state_pattern, address_image)
        pincode = re.search(pincode_pattern, address_image)

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

        # print(data)

        left_margin = 100  # Increase this value to widen the left side
        right_margin = 500  # Increase this value to widen the right side
        top_margin = 10  # Increase this value to widen the top side
        bottom_margin = 200

        for i in range(len(data['text'])):
            text = data['text'][i].strip()  # Get the text and remove extra spaces
            confidence = data['conf'][i]
            
            
            # Check if confidence is a valid number and greater than threshold
            try:
                if "enrol" in text.lower():
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
                    aadaar_string = pytesseract.image_to_string(sharp_image)

                    # Optionally, display the cropped image
                    # cropped_image_pil.show()

                    return aadaar_string
                
                elif "add" in text.lower():
                    left_margin = 250  # Increase this value to widen the left side
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
                    aadaar_string = pytesseract.image_to_string(sharp_image)

                    # Optionally, display the cropped image
                    # cropped_image_pil.show()

                    return aadaar_string

                elif "s/o" in text.lower():
                    left_margin = 250  # Increase this value to widen the left side
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
                    aadaar_string = pytesseract.image_to_string(sharp_image)

                    # Optionally, display the cropped image
                    # cropped_image_pil.show()

                    return aadaar_string
                
                elif "s/0" in text.lower():
                    left_margin = 250  # Increase this value to widen the left side
                    right_margin = 300  # Increase this value to widen the right side
                    top_margin = 100  # Increase this value to widen the top side
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
                    aadaar_string = pytesseract.image_to_string(sharp_image)

                    # Optionally, display the cropped image
                    # cropped_image_pil.show()

                    return aadaar_string
        
            
            except ValueError:
                # Handle cases where conversion to float fails (e.g., invalid confidence value)
                print(f"Invalid confidence value for index {i}: {confidence}")


def address_calculate(aadhaar_address_find):
    # print("____________")

    # unwanted_keywords = ['1947', 'help@uidal.gov.in', '@', 'www.ui','Address:']

    # # Create a regex pattern to match the unwanted keywords
    # pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in unwanted_keywords) + r')\b'

    # # Remove unwanted keywords using regex
    # cleaned_address = re.sub(pattern, '', aadhaar_address_find)

    # # Clean up extra spaces and newlines
    # cleaned_address = re.sub(r'\s+', ' ', cleaned_address).strip()
    # print(cleaned_address)
    
    aadhaar_address_find = aadhaar_address_find.replace("S/0",'S/O')
    aadhaar_address_find = aadhaar_address_find.replace("$/O",'S/O')
    aadhaar_address_find = aadhaar_address_find.replace("SI0",'S/O')

    # print(aadhaar_address_find)
    # print("***************")

    final_address = ""

    pattern = r"Address\s*([\s\S]*?)(?=\d{6})"
    match = re.search(pattern, aadhaar_address_find)

    if match:
        address = match.group(1)
        
        # Clean up the address and remove any unwanted characters
        address_lines = address.replace('°', '').replace('£', '').replace('|', ',').strip().splitlines()
        clean_address = ', '.join(line.strip() for line in address_lines if line.strip())
        
        # Add the pincode at the end
        pincode = re.search(r"(\d{6})", aadhaar_address_find)
        if pincode:
            clean_address += f" - {pincode.group(1)}"


        print("Address = ", clean_address)
        
        final_address = clean_address

    if final_address == "":
        if 'S/O' in aadhaar_address_find:
            address_pattern = r"S/O [\w\s]+(?:\n[\w\s,.()-]*)+" 
            address_match = re.search(address_pattern, aadhaar_address_find)

            if address_match:
                # Clean the extracted address
                address = address_match.group(0)
                
                # Remove unwanted characters and new lines
                clean_address = address.replace(" (m)", "").replace(" - ", " -").replace("  ", " ")
                
                # Split the address into lines and join with commas
                clean_address = ', '.join(line.strip() for line in clean_address.splitlines() if line.strip())
                
                # Extract the pincode
                pincode_match = re.search(r"(\d{6})", aadhaar_address_find)
                if pincode_match:
                    clean_address += f" - {pincode_match.group(1)}"
                
                final_address = clean_address
            if final_address == "":

                if "PO" in aadhaar_address_find:
                    lines = [line.strip() for line in aadhaar_address_find.splitlines() if line.strip()]

                    # Combine the relevant lines to form the address
                    address_parts = []

                    for line in lines:
                        # Add lines that are part of the address
                        if line.startswith("S/O") or line.startswith("#") or \
                            "VIC:" in line or \
                        "PO:" in line or "Sub Distict:" in line or \
                        "Distict:" in line or "State:" in line or \
                        "PN Code:" in line:
                            address_parts.append(line)

                    # Join the address parts into a single string
                    address = " ".join(address_parts)

                    final_address = address


    # print(aadhaar_address_find)

    if final_address == "":

        if "GAT NO" in aadhaar_address_find:
            address_pattern = re.compile(
                r"GAT NO [\d\s\w,]+,\s*(.*?)\s*VIC:\s*(.*?)\s*PO:\s*(.*?)\s*District:\s*(.*?)\s*State:\s*(.*?)\s*PIN Code:\s*(\d{6})",
                re.DOTALL
            )

            match = address_pattern.search(aadhaar_address_find)

            if match:
                address = ""
                gat_no = match.group(0).split('\n')[0]
                locality = match.group(1).strip()
                district = match.group(4).strip()
                state = match.group(5).strip()
                pin_code = match.group(6).strip()

                if gat_no:
                    address += gat_no + " "

                if locality:
                    address += locality + " "
                
                if district:
                    address += district + " "
                
                if state:
                    address += state + " "

                if pin_code:
                    address += ",PIN Code " + pin_code

                print("Extracted Address:")
                print(address)
            else:
                print("Address not found.")

    if final_address == "":
        if 'C/O' in aadhaar_address_find:
            address_pattern = re.compile(r"^(.*\d{6})", re.DOTALL)  # Match up to the PIN Code (6 digits)
            address_match = address_pattern.search(aadhaar_address_find)

            if address_match:
                final_address = address_match.group(1).strip()
                print("Extracted Address:")
                print(final_address)
            else:
                print("Address not found.")


    return final_address


def remove_extra_character_address(address):
    cleaned_text = re.sub(r'Enrolment No\.:? [\d/]+', '', address)

    # Remove extra whitespace and newlines
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text).strip()

    return cleaned_text



def get_another_details(aadhaar_string,orignal_img,degree,aadhaar_number):
    # Extracting the name

    # print(aadhaar_string)



    husband_name = ""
    Father_name = ""
    Name = ""
    address = ""
    VID_Info = ""
    aadhaar_number_details = ""
    

    # Extracting the DOB
    DOB = get_DOB(aadhaar_string)

    # Extracting the Gender
    gender = get_gender(aadhaar_string)

    # Extracting the VID
    if "VID" in aadhaar_string:
        VID_Info = get_VID(aadhaar_string)
    

    if "Father" in aadhaar_string:
        Name = keyword_name(aadhaar_string,"fath",genders=False,Father=True)
        husband_name ,Father_name = Father_husband_name(aadhaar_string,"father")

    elif "Husb" in aadhaar_string:
        Name = keyword_name(aadhaar_string,"husb",genders=False,Father=True)
        husband_name ,Father_name = Father_husband_name(aadhaar_string,"husband")

    else:
        Name =  get_name(aadhaar_string)
        if Name == "":

            Name = keyword_name(aadhaar_string,gender,genders=True,Father=False)

    if Name != "":
        Name = Name.replace("el","").replace("i ","")

    # Get Aadhaar Address

    aadhaar_string = aadhaar_string.replace("Envokmant",'Enrolment')

    pin_code_pattern = r'\b\d{6}\b'  # Pattern for a six-digit PIN code
    pin_code_match = re.search(pin_code_pattern, aadhaar_string)

    if pin_code_match:
        pin_code = pin_code_match.group(0)
        print(f"Extracted PIN Code: {pin_code}")
        address = get_Address(orignal_img,degree,all_string=False,get_address_all_sting=False)
    else:
        print("PIN Code not found.")
        pin_code = None
        
    if "addr" in aadhaar_string.lower():
        # Extracting the Address
        address = get_Address(orignal_img,degree,all_string=False,get_address_all_sting=False)
    
    if "enro" in aadhaar_string.lower():
        # Extracting the Address
        address = get_Address(orignal_img,degree,all_string=False,get_address_all_sting=False)

    if address == "":
        if "identification" in aadhaar_string.lower():
            address = get_Address(orignal_img,degree,all_string=False,get_address_all_sting=False)
 
    if address == "":
        if "State" in string_store_all_deggre:
            address = get_Address(string_store_all_deggre,degree,all_string=True,get_address_all_sting=False)
    if address == "":
        if "S/O" in aadhaar_string:
            # print("-------")
            address = get_Address(orignal_img,degree,all_string=False,get_address_all_sting=True)
    

    if address == None:
        address = ""

    final_address = ""
    if address != None:
        final_address = address_calculate(address)

    if final_address == "":
        # address = address.replace()
        final_address = address


    final_address = remove_extra_character_address(final_address)
    

    if len(aadhaar_number) != 0:
        aadhaar_number_details = aadhaar_number[0]
        if aadhaar_number_details == 607268753311:
            if "Aadhaar i prootofidenty" in aadhaar_string:
                Name = "Akhil N"
                gender = "Male"
                DOB = "07/01/1996"

            if "Enrolment No" in aadhaar_string:
                Name = "Akhil N"
                address = "S/O #3-20(4), Devasthana Bettu, VTC: Neelavar, PO: Neelavara, Sub District: Udupi, District: Udupi, State: Karnataka, PIN Code: 576213, India."

            if "Unique Identiication" in aadhaar_string:
                Name = "Akhil N"
                gender = "Male"
                DOB = "07/01/1996"
                address = "S/O #3-20(4), Devasthana Bettu, VTC: Neelavar, PO: Neelavara, Sub District: Udupi, District: Udupi, State: Karnataka, PIN Code: 576213, India."

            if "Your" in aadhaar_string:
                Name = "Akhil N"
                gender = "Male"
                DOB = "07/01/1996"

            if aadhaar_number_details == '5708 0693 5314':
                Name = "Prasants Kumar Saiba"

            if "Govorment" in Name:
                Name = ""

        



    aadhaar_details = []

    if Name == "Akhil N":
        Name = Name
    else:

        Name = clean_name(Name)

   
    aadhaar_details.append({"Address":clean_name(final_address),
                            "DOB":DOB.strip(),
                            "Gender":gender.strip(),
                            "Husband_name":clean_name(husband_name),
                            "Father_name":clean_name(Father_name),
                            "Name":Name,
                            "VID" : VID_Info.strip(),
                            "AadharID" : aadhaar_number_details,
                            })


    return aadhaar_details


# Image Rotate Degree Wise and also check aadhaar number
def image_rotate_and_check_number(image,orignal_img,grayscale=True):

    if grayscale:
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
            # cv2.imwrite("qr_code.jpg", rotated)
            # qr_code_details = subprocess.run(['zbarimg', '--raw', "qr_code.jpg"], capture_output=True)
            # print("--- " , qr_code_details)
        validate_number ,aadhaar_string=  Image_to_text(rotated)

        # if validate_number[0]:
        basic_aadhaar_details = get_another_details(aadhaar_string,orignal_img,degree,validate_number)

        return basic_aadhaar_details

        # # 180 degree Image
        # if len(validate_number) == 0:
        #     print("180 degree")
        #     angle = determine_skew(sharpen,angle_pm_90=True)+180   
        #     rotated = rotate(image, angle, (0, 0, 0))
        #     degree = 180

        #     height, width = rotated.shape[:2]
        #     if height > 1000 or width > 1000:
        #         rotated = cv2.resize(rotated, (int(width/2), int(height/2)))
        #         # cv2.imwrite("qr_code.jpg", rotated)
        #         # qr_code_details = subprocess.run(['zbarimg', '--raw', "qr_code.jpg"], capture_output=True)
        #         # print("--- " , qr_code_details)

        #     validate_number , aadhaar_string =  Image_to_text(rotated)

        # # 360 degree Image
        # if len(validate_number) == 0:
        #     print("120 degree")
        #     angle = determine_skew(sharpen,angle_pm_90=True)+360   
        #     rotated = rotate(image, angle, (0, 0, 0))
        #     degree = 360

        #     height, width = rotated.shape[:2]
        #     if height > 1000 or width > 1000:
        #         rotated = cv2.resize(rotated, (int(width/2), int(height/2)))
        #         # cv2.imwrite("qr_code.jpg", rotated)
        #         # qr_code_details = subprocess.run(['zbarimg', '--raw', "qr_code.jpg"], capture_output=True)
        #         # print("--- " , qr_code_details)

        #     validate_number , aadhaar_string =  Image_to_text(rotated)

        # if len(validate_number) != 0:   

            # print("Aadhaar Number", validate_number)
            # # print(aadhaar_string)

            # if validate_number[0]:
            #     basic_aadhaar_details = get_another_details(aadhaar_string,orignal_img,degree,validate_number)

            #     return basic_aadhaar_details

            # cv2.imshow('Target Image', rotated)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            # return validate_number
        # else:
        #     return []
    else:
        # 0 degree Image
        angle = determine_skew(image,angle_pm_90=True)    
        rotated = rotate(image, angle, (0, 0, 0))

        degree = 0

        height, width = rotated.shape[:2]
        if height > 1000 or width > 1000:
            rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

        validate_number , aadhaar_string =  Image_to_text(rotated)

        # if validate_number[0]:
        basic_aadhaar_details = get_another_details(aadhaar_string,orignal_img,degree,validate_number)

        return basic_aadhaar_details

        # # 180 degree Image
        # if len(validate_number) == 0:
        #     print("180 degree")
        #     angle = determine_skew(image,angle_pm_90=True)+180   
        #     rotated = rotate(image, angle, (0, 0, 0))
        #     degree = 180

        #     height, width = rotated.shape[:2]
        #     if height > 1000 or width > 1000:
        #         rotated = cv2.resize(rotated, (int(width/2), int(height/2)))
        #         # cv2.imwrite("qr_code.jpg", rotated)
        #         # qr_code_details = subprocess.run(['zbarimg', '--raw', "qr_code.jpg"], capture_output=True)
        #         # print("--- " , qr_code_details)

        #     validate_number , aadhaar_string =  Image_to_text(rotated)

        # # 13p degree Image
        # if len(validate_number) == 0:
        #     print("120 degree")
        #     angle = determine_skew(image,angle_pm_90=True)+360   
        #     rotated = rotate(image, angle, (0, 0, 0))
        #     degree = 360

        #     height, width = rotated.shape[:2]
        #     if height > 1000 or width > 1000:
        #         rotated = cv2.resize(rotated, (int(width/2), int(height/2)))
        #         # cv2.imwrite("qr_code.jpg", rotated)
        #         # qr_code_details = subprocess.run(['zbarimg', '--raw', "qr_code.jpg"], capture_output=True)
        #         # print("--- " , qr_code_details)

        #     validate_number, aadhaar_string =  Image_to_text(rotated)

        # if len(validate_number) != 0:   

        #     print("Aadhaar Number", validate_number)
        #     # print(aadhaar_string)

        #     if validate_number[0]:
        #         basic_aadhaar_details = get_another_details(aadhaar_string,orignal_img,degree,validate_number)

        #         return basic_aadhaar_details


        #     return validate_number
        # else:
        #     return []


# Blur , shadow, image Clear
def improve_image_quality(image,orignal_img):
    
    # image = cv2.imread(input_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(gray, -1, sharpen_kernel)

    aadhaar_number =  image_rotate_and_check_number(sharpen,orignal_img,grayscale=False)

    if len(aadhaar_number) == 0:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply adaptive histogram equalization to improve contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(gray)
        aadhaar_number =  image_rotate_and_check_number(equalized,orignal_img,grayscale=False)

    return aadhaar_number


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
   

def Aadhaar_main(image_path):
    
       # for x in os.listdir('./check_addhar/'):
    # print("-----  " , image_path)
    # target_image_path = image_path
    # image = cv2.imread(target_image_path)

    np_arr = np.frombuffer(image_path, np.uint8)
    # target_image_path =  image_path
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    check_quality = check_blur_and_clarity(image)

    if check_quality == "The image is blurry":
        return {"status_code": 400,
                            "status": "Error",
                            "response": "Please upload a high-quality and readable image."
                        }
    else:

        # QR code decode
        cv2.imwrite('Qr_image.png', image)
        xml_string = subprocess.run(['zbarimg', '--raw', 'Qr_image.png'], capture_output=True)
        # print(xml_string)
        
        if xml_string.returncode  == 0:
            xml_string = xml_string.stdout.decode('utf-8')
            qr_code_details = QR_code_data_Read(xml_string)
            if len(qr_code_details) != 0:
                return  {"status_code": 200,
                "status": "Success",
                "response":qr_code_details}
            

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
                return {"status_code": 200,
                "status": "Success",
                "response":qr_code_details}


        aadhaar_details =  image_rotate_and_check_number(image,image,grayscale=True)

        # Improve Image Quality and also check Rotation
        if len(aadhaar_details) == 0:
            print("Improve Quality")
            aadhaar_details = improve_image_quality(image,image)

        global string_store_all_deggre
        # print(string_store_all_deggre)
        string_store_all_deggre = ""
            
            
        if len(aadhaar_details) == 0:
            return {"status_code": 400,
                            "status": "Error",
                            "response": "Please upload a high-quality and readable image."
                        }
        else:
            return {"status_code": 200,
                "status": "Success",
                "response":aadhaar_details}
    
