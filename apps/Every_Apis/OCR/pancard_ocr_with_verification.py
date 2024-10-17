import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import re
import numpy as np
import pandas as pd
import os
from flask import Flask,jsonify
from io import BytesIO
import time , os , io
from deskew import determine_skew
from typing import Tuple, Union
import math


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


def extract_pan_number(result,english_lan_sting):
    # Define regex pattern to extract PAN number
    pan_number = ""
    

    pan_pattern = r'[A-Z]{5}\d{4}[A-Z]'
    pan_match = re.search(pan_pattern, result)
    if pan_match:
        pan_number = pan_match.group(0)
        pan_number = pan_number.upper()

      

    if pan_number == "":
        pan_pattern = r'[A-Z]{5}\d{4}[A-Z]'
        pan_match = re.search(pan_pattern, english_lan_sting)
        if pan_match:
            pan_number = pan_match.group(0)
    


        # pan_pattern = r'[A-Z]{5}\d{4}[A-Z]'
    
    if pan_number == "":
        result = result.upper()
        pan_match = re.search(pan_pattern, result)
        if pan_match:
            pan_number = pan_match.group(0)
            pan_number = pan_number.lower()

            # Replace lowercase 'l' with 'I'
            pan_number = pan_number.replace('l', 'i')
            pan_number = pan_number.upper()

    
    if pan_number == "":
        pan_pattern = r'\b[a-zA-Z]{5}[0-9]{4}[a-zA-Z]\b'
        match = re.search(pan_pattern, result)

        if match:
            pan_number = match.group(0)

    return pan_number
 
def extract_date_of_birth(result):
    # Define regex pattern to extract Date of Birth (assuming format dd/mm/yyyy)
    dob_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    dob_match = re.search(dob_pattern, result)
    if dob_match:
        return dob_match.group(0)
    return ""


def get_father_name(result,get_pan_number,string_store_all_deggre):
    father_pattern = r"Father's Name\n([A-Z ]+)\n([A-Z]+)"
    fathers_name = ""
    match = re.search(father_pattern, result)
    if match:
        fathers_name = f"{match.group(1)} {match.group(2)}"
    
    if fathers_name == "":
        pattern = r"Father's Name\s*([\w\s]+!)\s*([\w\s]+)"

        # Search for the pattern in the text
        match = re.search(pattern, result)

        if match:
            fathers_name = match.group(1).strip() + " " + match.group(2).strip()

    if fathers_name == "":
        escaped_pan = re.escape(get_pan_number)
        # name_pattern = r'{}\s+([A-Za-z\s]+)'.format(escaped_pan)
        name_pattern = r'{}\n(?:[A-Z\s]+\n)([A-Z\s]+)'.format(escaped_pan)
        match = re.search(name_pattern, result)

        # Check if a match was found and print it
        if match:
            fathers_name = match.group(1).strip()


    try:
        if fathers_name == "":
            lines = result.split('\n')
            date_of_birth = extract_date_of_birth(result)
            for i in range(len(lines)):
                if "Fathe" in lines[i]:
                    if i >= 1:
                        fathers_name = lines[i + 1]
    except:
        pass

    try:
        if fathers_name == "":
            lines = result.split('\n')
            for i in range(len(lines)):
                if date_of_birth in lines[i]:
                    if i >= 1:
                        fathers_name = lines[i - 1]
    except:
        pass

    
    if fathers_name == "":
        father_name_pattern = r"Fathar's Name\s*([A-Za-z\s]+)"
        match = re.search(father_name_pattern, result, re.IGNORECASE)
        if match:
            fathers_name = match.group(1).strip()
            # print("Father's Name:", father_name)

    if ":" in fathers_name:
        father_name_pattern = r"Fathar's Name\s*([A-Za-z\s]+)"
        match = re.search(father_name_pattern, result, re.IGNORECASE)
        if match:
            fathers_name = match.group(1).strip()

    if "‘" in fathers_name:
        father_name_pattern = r"er's Name\s*([A-Za-z\s]+)"
        father_match = re.search(father_name_pattern, result, re.IGNORECASE)
        if father_match:
            fathers_name = father_match.group(1).strip()

    print("----------" , "Application" in fathers_name)

    if "Application" in fathers_name:
        pattern = r"Father's Name\s*([\w\s]+!)\s*([\w\s]+)"

        # Search for the pattern in the text
        match = re.search(pattern, string_store_all_deggre)

        if match:
            fathers_name = match.group(1).strip() + " " + match.group(2).strip()


    if "Permanent Acc" in fathers_name:
        fathers_name = ""

    return fathers_name


def get_pancard_holder_name(result,get_pan_number,string_store_all_deggre):
    # Split the string into lines
    holder_name = ""
    lines = result.split('\n')
    # Iterate through the lines to find the keyword
    for i in range(len(lines)):
        if "Father's Name" in lines[i]:
            if i >= 1:
                holder_name = lines[i - 1]


    if "Father's Name" in string_store_all_deggre:
    
        if holder_name == "":
            lines = string_store_all_deggre.split('\n')
            # Iterate through the lines to find the keyword
            for i in range(len(lines)):
                if "Father's Name" in lines[i]:
                    if i >= 1:
                        holder_name = lines[i - 1]

    

    try:
        if holder_name == "":
            date_of_birth = extract_date_of_birth(result)
            for i in range(len(lines)):
                if date_of_birth in lines[i]:
                    if i >= 2:
                        holder_name = lines[i - 2]
    except:
        pass

    if holder_name == "" :
        escaped_pan = re.escape(get_pan_number)
        # name_pattern = r'{}\s+([A-Za-z\s]+)'.format(escaped_pan)
        name_pattern = r'{}(?:\n|\s)([A-Z\s]+)'.format(escaped_pan)
        match = re.search(name_pattern, result)

        # Check if a match was found and print it
        if match:
            holder_name = match.group(1).strip()



        
    

    return holder_name

# Name Clean Extra Character remove
def clean_name(text):
    # Define the keywords to be removed
    # keywords = r'\b(?:[Hh]usband|[Hh]usb\w*|[Ff]ather)\b'
    
    # # Remove single-character word at the beginning
    cleaned_text = re.sub(r'\b\w\b', '', text).strip()
    # Replace multiple spaces with a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    cleaned_text = re.sub(r'\d+', '', cleaned_text)
    
    # Remove unwanted keywords (husband, father, etc.)
    # cleaned_text = re.sub(keywords, '', cleaned_text)
    
    # Remove single-character word at the end
    cleaned_text = cleaned_text.lstrip("'").strip()

    # Remove extra spaces
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text

string_store_all_deggre = ""
# Extract other details
def get_another_details(image_to_string,english_lan_sting,get_pan_number):
    # print(image_to_string)
    # print(english_lan_sting)
    global string_store_all_deggre

    print(string_store_all_deggre)

    # DOB
    dOB_date = extract_date_of_birth(image_to_string)

    # Father name
    father_name = get_father_name(image_to_string,get_pan_number,string_store_all_deggre)

    if "Date of" in father_name:
        father_name = ""

    # Holder Name
    holder_name = get_pancard_holder_name(image_to_string,get_pan_number,string_store_all_deggre)

    list_details = []

    list_details.append({"PAN_no":get_pan_number,
                         "DOB" : dOB_date,
                         "Father_name" : clean_name(father_name),
                         "Name" : clean_name(holder_name),
                         })

    # print("pan_number = ", get_pan_number)
    # print("dOB_date = ", dOB_date)
    # print("father_name = ", clean_name(father_name))
    # print("holder_name = ", clean_name(holder_name))
    string_store_all_deggre = ""

    return list_details



# Image text
def Image_to_text(image_path):
    # masked_image_pil = Image.fromarray(image_path)
    global string_store_all_deggre
    simple_image_string = pytesseract.image_to_string(image_path)
    simple_text_blank_remove = "\n".join(line for line in simple_image_string.split('\n') if line.strip())

    string_store_all_deggre += simple_image_string


    # English Lang
    language_codes = ['eng']
    languages = '+'.join(language_codes)
    custom_config = f'--oem 3 --psm 6 -l {languages}'
    english_string = pytesseract.image_to_string(image_path ,config=custom_config)
    string_store_all_deggre += english_string
    # print(simple_text_blank_remove , english_string)

    get_pan_number =  extract_pan_number(simple_text_blank_remove,english_string)
     
    if get_pan_number != "":
        get_pan_details = get_another_details(simple_text_blank_remove,english_string,get_pan_number)


        return get_pan_details


    return get_pan_number


# Bright & Contrast Add
def convertScale(img, alpha, beta):
    """Add bias and gain to an image with saturation arithmetics. Unlike
    cv2.convertScaleAbs, it does not take an absolute value, which would lead to
    nonsensical results (e.g., a pixel at 44 with alpha = 3 and beta = -210
    becomes 78 with OpenCV, when in fact it should become 0).
    """

    new_img = img * alpha + beta
    new_img[new_img < 0] = 0
    new_img[new_img > 255] = 255
    return new_img.astype(np.uint8)


def image_rotate_and_check_number(image,grayscale=False):
    if grayscale:
        pan_number = ""
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

        pan_number =  Image_to_text(rotated)


        if pan_number == "":
            angle = determine_skew(sharpen,angle_pm_90=True)+180   
            rotated = rotate(image, angle, (0, 0, 0))
            degree = 180

            height, width = rotated.shape[:2]
            if height > 1000 or width > 1000:
                rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

            pan_number =  Image_to_text(rotated)

        if pan_number == "":
            angle = determine_skew(sharpen,angle_pm_90=True)+360   
            rotated = rotate(image, angle, (0, 0, 0))
            degree = 180

            height, width = rotated.shape[:2]
            if height > 1000 or width > 1000:
                rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

            pan_number =  Image_to_text(rotated)

        

        # print("pan_details = ",  pan_number)

        # cv2.imshow('Target Image', rotated)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return pan_number
    else:
        # image = cv2.imread(image)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        angle = determine_skew(image,angle_pm_90=True)    
        rotated = rotate(image, angle, (0, 0, 0))

        degree = 0

        height, width = rotated.shape[:2]
        if height > 1000 or width > 1000:
            rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

        pan_number =  Image_to_text(rotated)

        if pan_number == "":
            print("180 degree")
            angle = determine_skew(image,angle_pm_90=True)+180   
            rotated = rotate(image, angle, (0, 0, 0))
            degree = 180

            height, width = rotated.shape[:2]
            if height > 1000 or width > 1000:
                rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

            pan_number =  Image_to_text(rotated)

        if pan_number == "":
            print("180 degree")
            angle = determine_skew(image,angle_pm_90=True)+360   
            rotated = rotate(image, angle, (0, 0, 0))
            degree = 360

            height, width = rotated.shape[:2]
            if height > 1000 or width > 1000:
                rotated = cv2.resize(rotated, (int(width/2), int(height/2)))

            pan_number =  Image_to_text(rotated)

        # print("pan_details = ",  pan_number)

        # cv2.imshow('Target Image', rotated)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return pan_number



def automatic_brightness_and_contrast(image, clip_hist_percent=25):
    image = cv2.imread(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray],[0],None,[256],[0,256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index -1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum/100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size -1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha


    auto_result = convertScale(image, alpha=alpha, beta=beta)
    # image = cv2.imread(auto_result)
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    pan_number = image_rotate_and_check_number(auto_result,grayscale=False)

    return pan_number







def pancard_main(image_path):

    np_arr = np.frombuffer(image_path, np.uint8)
    target_image_path =  image_path
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    target_image_path = image
    # image = cv2.imread(image)


    # 
    # image = cv2.imread('./Pan_Card/'+image)
    pan_details = image_rotate_and_check_number(image,grayscale=True)
    
    if pan_details == "":
        pan_details = automatic_brightness_and_contrast(target_image_path)
        

    global string_store_all_deggre
    string_store_all_deggre = ""

    if pan_details == "":
        return []
    else:
        return pan_details






