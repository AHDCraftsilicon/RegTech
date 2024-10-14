import math
from typing import Tuple, Union
from PIL import Image, ImageFilter , ImageEnhance
import cv2
import numpy as np
import os , re
from deskew import determine_skew
import pytesseract


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


def Regex_Search(bounding_boxes):
    possible_UIDs = []
    aadhaar_number = []
    Result = ""

    for character in range(len(bounding_boxes)):
        if len(bounding_boxes[character]) != 0:
            Result += bounding_boxes[character][0]
        else:
            Result += '?'

    # print(Result)

    matches = [match.span() for match in re.finditer(r'\d{12}', Result)]
    for match in matches:
        UID = int(Result[match[0]:match[1]])

        if compute_checksum(UID) == 0 and UID % 10000 != 1947:
            possible_UIDs.append([UID, match[0]])
            aadhaar_number.append(UID)

    possible_UIDs = np.array(possible_UIDs)
    
    return aadhaar_number 


# Normal Image to Text Also Validate aadhaar number present or not
def Image_to_text(image_array):
    masked_image_pil = Image.fromarray(image_array)


    # Image to without lan
    bounding_boxes = pytesseract.image_to_boxes(masked_image_pil).split(" 0\n")
    possible_UIDs = Regex_Search(bounding_boxes)

    # Image to string
    aadhaar_string = pytesseract.image_to_string(masked_image_pil)
    # masked_image_pil.save('aadhaar_address.jpg')


    # With English Lan
    if len(possible_UIDs) == 0:
        language_codes = ['eng']
        languages = '+'.join(language_codes)
        custom_config = f'--oem 3 --psm 6 -l {languages}'
        bounding_boxes = pytesseract.image_to_boxes(masked_image_pil, config=custom_config).split(" 0\n")
        possible_UIDs = Regex_Search(bounding_boxes)

        # Image to string
        aadhaar_string = pytesseract.image_to_string(masked_image_pil, config=custom_config)

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


    print("========= ", possible_UIDs)
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

    return final_dob

# Get Gender From Aadhaar String
def get_gender(aadhaar_string):
    gender_pattern = re.compile(r'\bFEMALE|FEMALE|male|female|Male|Female|Famale\b', re.IGNORECASE)
    
    gender = ""
    if gender_pattern.search(aadhaar_string) != None:
        gender = gender_pattern.search(aadhaar_string).group()
    else:
        gender = ""
    
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

# Get Address From Aadhaar String
def get_Address(address_image,degree):
   
    np_arr = np.frombuffer(address_image, np.uint8)
    address_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(address_image, cv2.COLOR_BGR2GRAY)
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(gray, -1, sharpen_kernel)

    # 0 degree Image
    angle = determine_skew(sharpen,angle_pm_90=True)    
    rotated = rotate(address_image, angle, (0, 0, 0))

    height, width = rotated.shape[:2]
    if height > 1000 or width > 1000:
        rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

    if degree == 180:
        angle = determine_skew(sharpen,angle_pm_90=True)+180   
        rotated = rotate(address_image, angle, (0, 0, 0))
        height, width = rotated.shape[:2]
        if height > 1000 or width > 1000:
            rotated = cv2.resize(rotated, (int(width/2), int(height/2)))
    

    if degree == 360:
        angle = determine_skew(sharpen,angle_pm_90=True)+180   
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

                # print(string_aadhaar)

                # cropped_image_pil.show()

                pattern = r'(?:Address|Addresst)[^A-Za-z0-9]*([\s\S]*?)(?=\n\n|$)'

                # Find all matches
                addresses = re.findall(pattern, string_aadhaar)

                # Clean and display addresses
                for address in addresses:
                    addresss = re.sub(r'^\s?.\n', '', address.strip()).strip()
                    return addresss
                
        
        except ValueError:
            # Handle cases where conversion to float fails (e.g., invalid confidence value)
            return ""


def get_another_details(aadhaar_string,orignal_img,degree,aadhaar_number):
    # Extracting the name


    husband_name = ""
    Father_name = ""
    Name = ""
    address = ""
    
    

    # Extracting the DOB
    DOB = get_DOB(aadhaar_string)

    # Extracting the Gender
    gender = get_gender(aadhaar_string)

    # Extracting the VID
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


    # Get Aadhaar Address

    
    if "addr" in aadhaar_string.lower():
        # Extracting the Address
        address = get_Address(orignal_img,degree)


    
    aadhaar_details = []

    aadhaar_details.append({"Address":address,
                            "DOB":DOB.strip(),
                            "Gender":gender.strip(),
                            "Husband_name":clean_name(husband_name),
                            "Father_name":clean_name(Father_name),
                            "Name":clean_name(Name),
                            "VID" : VID_Info.strip(),
                            "AadharID" : aadhaar_number[0],
                            })

    # print("Name = ", clean_name(Name))
    # print("DOB = ", DOB.strip())
    # print("gender = ", gender.strip())
    # print("VID_Info = ", VID_Info.strip())
    # print("Father_name = ", clean_name(Father_name))
    # print("husband_name = ", clean_name(husband_name))
    # print("address = ", address)

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

        validate_number ,aadhaar_string=  Image_to_text(rotated)

        # 180 degree Image
        if len(validate_number) == 0:
            print("180 degree")
            angle = determine_skew(sharpen,angle_pm_90=True)+180   
            rotated = rotate(image, angle, (0, 0, 0))
            degree = 180

            height, width = rotated.shape[:2]
            if height > 1000 or width > 1000:
                rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

            validate_number , aadhaar_string =  Image_to_text(rotated)

        # 13p degree Image
        if len(validate_number) == 0:
            print("120 degree")
            angle = determine_skew(sharpen,angle_pm_90=True)+360   
            rotated = rotate(image, angle, (0, 0, 0))
            degree = 360

            height, width = rotated.shape[:2]
            if height > 1000 or width > 1000:
                rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

            validate_number , aadhaar_string =  Image_to_text(rotated)

        if len(validate_number) != 0:   

            print("Aadhaar Number", validate_number)
            # print(aadhaar_string)

            if validate_number[0]:
                basic_aadhaar_details = get_another_details(aadhaar_string,orignal_img,degree,validate_number)

                return basic_aadhaar_details

            # cv2.imshow('Target Image', rotated)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            return validate_number
        else:
            return []
    else:
        # 0 degree Image
        angle = determine_skew(image,angle_pm_90=True)    
        rotated = rotate(image, angle, (0, 0, 0))

        degree = 0

        height, width = rotated.shape[:2]
        if height > 1000 or width > 1000:
            rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

        validate_number , aadhaar_string =  Image_to_text(rotated)

        # 180 degree Image
        if len(validate_number) == 0:
            print("180 degree")
            angle = determine_skew(image,angle_pm_90=True)+180   
            rotated = rotate(image, angle, (0, 0, 0))
            degree = 180

            height, width = rotated.shape[:2]
            if height > 1000 or width > 1000:
                rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

            validate_number , aadhaar_string =  Image_to_text(rotated)

        # 13p degree Image
        if len(validate_number) == 0:
            print("120 degree")
            angle = determine_skew(image,angle_pm_90=True)+360   
            rotated = rotate(image, angle, (0, 0, 0))
            degree = 360

            height, width = rotated.shape[:2]
            if height > 1000 or width > 1000:
                rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

            validate_number, aadhaar_string =  Image_to_text(rotated)

        if len(validate_number) != 0:   

            print("Aadhaar Number", validate_number)
            # print(aadhaar_string)

            if validate_number[0]:
                basic_aadhaar_details = get_another_details(aadhaar_string,orignal_img,degree,validate_number)

                return basic_aadhaar_details


            return validate_number
        else:
            return []


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



def Aadhaar_main(image_path):
       # for x in os.listdir('./check_addhar/'):
    # print("-----  " , image_path)
    np_arr = np.frombuffer(image_path, np.uint8)
    target_image_path =  image_path
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # cv2.imshow('Original Image', image)
    # cv2.waitKey(0)  # Wait for a key press to continue

    aadhaar_details =  image_rotate_and_check_number(image,target_image_path,grayscale=True)

    # Improve Image Quality and also check Rotation
    if len(aadhaar_details) == 0:
        # print("Improve Quality")
        aadhaar_details = improve_image_quality(image,target_image_path)
        
    if len(aadhaar_details) == 0:
        return []
    else:
        return aadhaar_details[0]
        
