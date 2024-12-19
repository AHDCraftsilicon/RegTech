import cv2
import pytesseract
import numpy as np
from PIL import Image
import re , os
import base64
from io import BytesIO
import shutil , time
from werkzeug.utils import secure_filename


# tessract path
from tesseract_path import *


tessdata_dir = "/home/RegtechLive/"

invalid_keywords = ['INCOMETAXDEPARTMENT','TAX','INCOME','DEPARTMENT','election','elector',
                    'commission','identity','elecr']

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
    Result = ""

    for character in range(len(bounding_boxes)):
        if len(bounding_boxes[character]) != 0:
            Result += bounding_boxes[character][0]
        else:
            Result += '?'

    Result = Result.lower()
    # print(Result)

    
    if any(keyword.lower() in Result for keyword in invalid_keywords):
        return "Invalid image. Please upload a valid Aadhaar image."



    matches = [match.span() for match in re.finditer(r'\d{12}', Result)]
    for match in matches:
        UID = int(Result[match[0]:match[1]])

        if compute_checksum(UID) == 0 and UID % 10000 != 1947:
            possible_UIDs.append([UID, match[0]])

    possible_UIDs = np.array(possible_UIDs)
    
    return possible_UIDs



# Image to base64 convert
def image_to_base64(image_path):
    # Open the image file
    with Image.open(image_path) as img:
        # Create a BytesIO object to hold the image data
        buffered = BytesIO()
        # Save the image data to the BytesIO object in the desired format
        img.save(buffered, format="PNG")  # You can change the format if needed
        # Get the Base64 encoded string
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


# Rotate Image on angle wise
def map_coords_to_original(coords, scaled_shape, original_shape, angle):
    """ Maps bounding box coordinates from scaled/rotated image back to original image. """
    x1, y1, x2, y2 = coords
    scale_x = original_shape[1] / scaled_shape[1]
    scale_y = original_shape[0] / scaled_shape[0]
    
    # Rescale the coordinates back to the original size
    orig_x1 = int(x1 * scale_x)
    orig_y1 = int(y1 * scale_y)
    orig_x2 = int(x2 * scale_x)
    orig_y2 = int(y2 * scale_y)

    # Apply rotation adjustment if necessary
    if angle == 90:
        orig_x1, orig_y1 = original_shape[1] - orig_y1, orig_x1
        orig_x2, orig_y2 = original_shape[1] - orig_y2, orig_x2
    elif angle == 180:
        orig_x1, orig_y1 = original_shape[1] - orig_x1, original_shape[0] - orig_y1
        orig_x2, orig_y2 = original_shape[1] - orig_x2, original_shape[0] - orig_y2
    elif angle == 270:
        orig_x1, orig_y1 = orig_y1, original_shape[0] - orig_x1
        orig_x2, orig_y2 = orig_y2, original_shape[0] - orig_x2

    return orig_x1, orig_y1, orig_x2, orig_y2


# Normal add mask
def Simple_way_Quality_Mask(base64_image):

    # Base64 image decode
    image_data = base64.b64decode(base64_image)

    # after decode open image for masking
    pil_image = Image.open(BytesIO(image_data))
    masked_image_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


    bounding_boxes = pytesseract.image_to_boxes(pil_image ,config=  r' -c tessedit_create_boxfile=1').split(" 0\n")

    possible_UIDs = Regex_Search(bounding_boxes)

    if isinstance(possible_UIDs, str):  # This checks if it's the error message, not a list of UIDs
        return possible_UIDs ,[]

    for uid, start_index in possible_UIDs:
        for i in range(8):  # Mask only the first 8 characters
            char_box = bounding_boxes[start_index + i].split()

            x1 = int(char_box[1])
            y1 = int(char_box[2])
            x2 = int(char_box[3])
            y2 = int(char_box[4])

            cv2.rectangle(masked_image_cv, (x1, masked_image_cv.shape[0] - y1), 
                          (x2, masked_image_cv.shape[0] - y2), (255, 255, 255), -1)

    masked_image_path = 'Simple_way_masked.jpg'
    cv2.imwrite(masked_image_path, masked_image_cv)

    _, buffer = cv2.imencode('.jpg', masked_image_cv)
    masked_image_base64 = base64.b64encode(buffer).decode('utf-8')

    return masked_image_base64, possible_UIDs


# Rotate without any lan
def Extract_and_Mask_UIDs(base64_image, counts, SR=False, sr_image_path=None, SR_Ratio=[1, 1]):

    # Base64 image decode
    image_data = base64.b64decode(base64_image)

    # Load and preprocess the original image (unmodified)
    original_image_pil = Image.open(BytesIO(image_data))
    original_image_cv = cv2.cvtColor(np.array(original_image_pil), cv2.COLOR_RGB2BGR)
    
    # Rotation angles to check
    rotation_angles = [0, 90, 180, 270]
    
    check_aadhar_status = False
    return_image_number = None
    final_masked_image_path = None
    
    # Loop through each angle for OCR
    for angle in rotation_angles:
        rotated_image = original_image_cv
        
        # Apply rotation based on the angle
        if angle == 90:
            rotated_image = cv2.rotate(original_image_cv, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            rotated_image = cv2.rotate(original_image_cv, cv2.ROTATE_180)
        elif angle == 270:
            rotated_image = cv2.rotate(original_image_cv, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        # Step 1: Blur the rotated image
        blurred_image = cv2.GaussianBlur(rotated_image, (5, 5), 0)
    
        # Step 2: Scale the image if SR (Super Resolution) is requested
        if SR:
            width = int(blurred_image.shape[1] * SR_Ratio[0])
            height = int(blurred_image.shape[0] * SR_Ratio[1])
            dim = (width, height)
            scaled_image = cv2.resize(blurred_image, dim, interpolation=cv2.INTER_AREA)
        else:
            scaled_image = blurred_image

        # Convert back to PIL for OCR processing
        scaled_image_pil = Image.fromarray(cv2.cvtColor(scaled_image, cv2.COLOR_BGR2RGB))
    
        # Step 3: Extract bounding boxes using Tesseract
        bounding_boxes = pytesseract.image_to_boxes(scaled_image_pil, config= r' -c tessedit_create_boxfile=1').split(" 0\n")
    
        # Step 4: Find possible UIDs using regex
        possible_UIDs = Regex_Search(bounding_boxes)

        if isinstance(possible_UIDs, str):  # This checks if it's the error message, not a list of UIDs
            return possible_UIDs, [], False, None
        
        # Step 5: Mask the original image based on bounding boxes from rotated image
        for uid, start_index in possible_UIDs:
            for i in range(8):  # Mask only the first 8 characters
                char_box = bounding_boxes[start_index + i].split()
                if char_box[1] != "0":
                    check_aadhar_status = True
                    return_image_number = str(counts)

                # Get the bounding box coordinates
                x1 = int(char_box[1])
                y1 = int(char_box[2])
                x2 = int(char_box[3])
                y2 = int(char_box[4])

                # Map the coordinates back to the original image
                orig_x1, orig_y1, orig_x2, orig_y2 = map_coords_to_original(
                    (x1, y1, x2, y2), scaled_image.shape, original_image_cv.shape, angle
                )

                # Apply the mask on the original image (not the rotated/scaled one)
                cv2.rectangle(original_image_cv, (orig_x1, original_image_cv.shape[0] - orig_y1), 
                              (orig_x2, original_image_cv.shape[0] - orig_y2), (255, 255, 255), -1)

        # store in buffer the final masked image for the current rotation angle

        _, buffer = cv2.imencode('.jpg', original_image_cv)
        masked_image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Check if Aadhar number is found and exit if true
        if check_aadhar_status:
            # print(f"Aadhar number found and masked at angle {angle}. Exiting loop.")
            break  # Exit the loop if an Aadhar number is found and masked
    
    return masked_image_base64, possible_UIDs, check_aadhar_status, return_image_number

# Rotate with lan
def Extract_Law_Quality_Mask_UIDS(base64_image, counts):

    # Base64 image decode
    image_data = base64.b64decode(base64_image)

    language_codes = ['eng']
    languages = '+'.join(language_codes)
    custom_config = f'--oem 3 --psm 6 -l {languages}'

    # Decode image from bytes
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    original_img = img.copy()  # Keep a copy of the original image

    # Rotation angles to check
    rotation_angles = [0, 90, 180, 270, 360]

    check_addhar_status = False
    return_image_number = None
    final_masked_image_path = None
    
    # Loop through each angle
    for angle in rotation_angles:
        rotated_image = img

        # Apply rotation based on the angle
        if angle == 90:
            rotated_image = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            rotated_image = cv2.rotate(img, cv2.ROTATE_180)
        elif angle == 270:
            rotated_image = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # No need to rotate for 0 and 360 degrees

        # Resize by x2 using LANCZOS4 interpolation method
        img2 = cv2.resize(rotated_image, (rotated_image.shape[1] * 2, rotated_image.shape[0] * 2), interpolation=cv2.INTER_LANCZOS4)

        # Extract bounding boxes using Tesseract
        bounding_boxes = pytesseract.image_to_boxes(img2,lang='eng',config= r' -c tessedit_create_boxfile=1').split(" 0\n")
        possible_UIDs = Regex_Search(bounding_boxes)

        if isinstance(possible_UIDs, str):  # This checks if it's the error message, not a list of UIDs
            return possible_UIDs, [], False, None

        # If no UIDs found, retry without custom config
        if len(possible_UIDs) == 0:
            bounding_boxes = pytesseract.image_to_boxes(img2,config= r' -c tessedit_create_boxfile=1').split(" 0\n")
            possible_UIDs = Regex_Search(bounding_boxes)

            if isinstance(possible_UIDs, str):  # This checks if it's the error message, not a list of UIDs
                return possible_UIDs, [], False, None

        # Mask possible UIDs on the original image using the transformed coordinates
        for uid, start_index in possible_UIDs:
            for i in range(8):  # Mask only the first 8 characters
                char_box = bounding_boxes[start_index + i].split()
                print(char_box)

                if char_box[1] != "0":
                    check_addhar_status = True
                    return_image_number = str(counts)

                x1 = int(char_box[1])
                y1 = int(char_box[2])
                x2 = int(char_box[3])
                y2 = int(char_box[4])

                # Map the bounding box back to the original image using rotation
                orig_x1, orig_y1, orig_x2, orig_y2 = map_coords_to_original(
                    (x1, y1, x2, y2), img2.shape, rotated_image.shape, angle
                )

                # Apply the mask on the original image (not the rotated image)
                cv2.rectangle(original_img, (orig_x1, original_img.shape[0] - orig_y1), (orig_x2, original_img.shape[0] - orig_y2), (255, 255, 255), -1)

        # Save the masked original image for the current rotation angle
        # final_masked_image_path = f"./apps/static/Aadhaar_Masking/Aadhar_Rotate_images/__rotate_masked_image_{counts}_angle_{angle}.jpg"
        # cv2.imwrite(final_masked_image_path, original_img)

        _, buffer = cv2.imencode('.jpg', original_img)
        masked_image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Check if Aadhar number is found and break the loop
        if check_addhar_status:
            print(f"Aadhar number found and masked at angle {angle}. Exiting loop.")
            break  # Exit the loop when an Aadhar number is found and masked

    return masked_image_base64, possible_UIDs, check_addhar_status, return_image_number



def addhar_mask(image_path, SR=False, SR_Ratio=[1, 1]):

    base64_string = image_to_base64(image_path)

    counts = 0

    # simple way to mask
    masked_image, possible_UIDs = Simple_way_Quality_Mask(base64_string)
    # print(masked_image)

    if isinstance(masked_image, str) and "Invalid image" in masked_image:
        return { "status_code": 400,
                        "status": "Error",
                        "response": "Invalid Aadhaar image. Please upload a clear and valid Aadhaar card image!"}
    else:
        if len(possible_UIDs) != 0:
            return {"status_code": 200,
                "status": "Success",
                "response":"data:image/png;base64,"+masked_image}

        # Rotate without any lan
        else:
            masked_image, possible_UIDs ,status_check , image_count = Extract_and_Mask_UIDs(base64_string,counts, SR, SR_Ratio)

            if isinstance(masked_image, str) and "Invalid image" in masked_image:
                return { "status_code": 400,
                                "status": "Error",
                                "response": "Invalid Aadhaar image. Please upload a clear and valid Aadhaar card image!"}
            else:
                if len(possible_UIDs) != 0:
                    return {"status_code": 200,
                        "status": "Success",
                        "response":"data:image/png;base64,"+masked_image}
                
                # Rotate with eng lan
                else:
                    masked_image, possible_UIDs , status_check , image_count= Extract_Law_Quality_Mask_UIDS(base64_string , counts)
                    
                    if isinstance(masked_image, str) and "Invalid image" in masked_image:
                        return { "status_code": 400,
                                "status": "Error",
                                "response": "Invalid Aadhaar image. Please upload a clear and valid Aadhaar card image!"}
                    else:
                        if len(possible_UIDs) != 0:
                            return {"status_code": 200,
                                "status": "Success",
                                "response":"data:image/png;base64,"+masked_image}
                        
                        # image inside add alpha
                        else:
                            # Base64 image decode
                            image_data = base64.b64decode(base64_string)
                            
                            # Step 2: Convert the binary data to a NumPy array
                            nparr = np.frombuffer(image_data, np.uint8)
                            
                            # Step 3: Decode the NumPy array to an OpenCV image
                            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            alpha = 1.95  # Contrast control (1.0-3.0)
                            beta = 0      # Brightness control (0-100)

                            # Apply contrast and brightness
                            manual_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
                            
                            # Convert into base64 that's why store in buffer
                            _, buffer = cv2.imencode('.jpg', manual_result)
                            # Convert the buffer to Base64
                            base64_result = base64.b64encode(buffer).decode('utf-8')

                            # base64 image add on masked func
                            masked_image, possible_UIDs , status_check , image_count= Extract_Law_Quality_Mask_UIDS(base64_result , counts)
                            
                            if isinstance(masked_image, str) and "Invalid image" in masked_image:
                                return { "status_code": 400,
                                        "status": "Error",
                                        "response": "Invalid Aadhaar image. Please upload a clear and valid Aadhaar card image!"}
                            else:
                                if len(possible_UIDs) != 0:
                                    return {"status_code": 200,
                                        "status": "Success",
                                        "response":"data:image/png;base64,"+masked_image}
                                
                                # apply on image greyscale
                                else:

                                    # Base64 image decode
                                    image_data = base64.b64decode(base64_string)
                                    # Convert bytes to a NumPy array
                                    nparr = np.frombuffer(image_data, np.uint8)

                                    # Decode the NumPy array to an image
                                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                                    # Convert to grayscale
                                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                                    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                                    sharpen = cv2.filter2D(gray, -1, sharpen_kernel)
                                    # Apply edge detection
                                    edges = cv2.Canny(sharpen, 50, 150, apertureSize=3)

                                    # Detect lines using Hough Transform to find skew angle
                                    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
                                    angles = []

                                    for line in lines:
                                        x1, y1, x2, y2 = line[0]
                                        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                                        angles.append(angle)

                                    # Compute the median angle
                                    median_angle = np.median(angles)

                                    # Rotate the image to correct the skew
                                    (h, w) = image.shape[:2]
                                    center = (w // 2, h // 2)
                                    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                                    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                                    
                                    # Convert into base64 that's why store in buffer
                                    _, buffer = cv2.imencode('.jpg', rotated)
                                    # Convert the buffer to Base64
                                    base64_result = base64.b64encode(buffer).decode('utf-8')
                                    
                                    # base64 image add on masked func
                                    masked_image, possible_UIDs , status_check , image_count= Extract_Law_Quality_Mask_UIDS(base64_result , counts)

                                    if isinstance(masked_image, str) and "Invalid image" in masked_image:
                                        return { "status_code": 400,
                                                "status": "Error",
                                                "response": "Invalid Aadhaar image. Please upload a clear and valid Aadhaar card image!"}
                                    else:
                                        if len(possible_UIDs) != 0:
                                            return {"status_code": 200,
                                                "status": "Success",
                                                "response":"data:image/png;base64,"+masked_image}

                                        else:
                                            return { "status_code": 400,
                                                    "status": "Error",
                                                    "response": "Please upload a clear and legible image of the entire document in JPEG, PNG format."}

