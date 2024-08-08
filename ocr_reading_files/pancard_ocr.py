import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import re
import numpy as np
import pandas as pd
import os
from flask import Flask,jsonify



#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



def extract_pan_number(result):
    # Define regex pattern to extract PAN number
    pan_pattern = r'[A-Z]{5}\d{4}[A-Z]'
    pan_match = re.search(pan_pattern, result)
    if pan_match:
        return pan_match.group(0)
    return ""
 
def extract_date_of_birth(result):
    # Define regex pattern to extract Date of Birth (assuming format dd/mm/yyyy)
    dob_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    dob_match = re.search(dob_pattern, result)
    if dob_match:
        return dob_match.group(0)
    return None


def get_father_name(result):
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

    return fathers_name


def get_pancard_holder_name(result):
    # Split the string into lines
    holder_name = ""
    lines = result.split('\n')
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


    return holder_name


def pancard_main(image_path):
    pancard_list ={}

    simple_image_string = pytesseract.image_to_string(Image.open(image_path))
    simple_text_blank_remove = "\n".join(line for line in simple_image_string.split('\n') if line.strip())

    pancard_number = extract_pan_number(simple_text_blank_remove)
    if pancard_number != "":
        pancard_list["PAN NO"] = pancard_number
    
    date_of_birth = extract_date_of_birth(simple_text_blank_remove)
    if date_of_birth != None:
        pancard_list["DOB"] = date_of_birth

    fathers_name = get_father_name(simple_text_blank_remove)
    if fathers_name != "":
        pancard_list["Father Name"] = fathers_name

    holder_name = get_pancard_holder_name(simple_text_blank_remove)
    if holder_name != "":
        pancard_list["Name"] = holder_name

    if pancard_list != {}:
        return {"response": 200,
            "message": "Success",
            "responseValue": {
                "Table1": [
                    {
                        "DocumentResponse": pancard_list
                    }
                ]
            }
        }
    
    else:
        return {"response": 400,
            "message": "Error",
            "responseValue": "Please upload a high-quality and readable image."
        }

