# import cv2
# import pytesseract
# import numpy as np
# from PIL import Image
# import re , os
# import base64
# from io import BytesIO
# import shutil , time
# from werkzeug.utils import secure_filename


# try:
#     os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
#     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# except:
#     # Linux Server
#     os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/'
#     pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  


# multiplication_table = (
#     (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
#     (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
#     (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
#     (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
#     (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
#     (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
#     (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
#     (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
#     (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
#     (9, 8, 7, 6, 5, 4, 3, 2, 1, 0))

# permutation_table = (
#     (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
#     (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
#     (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
#     (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
#     (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
#     (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
#     (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
#     (7, 0, 4, 6, 9, 1, 3, 2, 5, 8))


# def compute_checksum(number):
#     """Calculate the Verhoeff checksum over the provided number. The checksum
#     is returned as an int. Valid numbers should have a checksum of 0."""

#     # transform number list
#     number = tuple(int(n) for n in reversed(str(number)))
#     # print(number)

#     # calculate checksum
#     checksum = 0

#     for i, n in enumerate(number):
#         checksum = multiplication_table[checksum][permutation_table[i % 8][n]]

#     # print(checksum)
#     return checksum


# def Extract_and_Mask_UIDs(image_path,counts , SR=False, sr_image_path=None, SR_Ratio=[1, 1]):
#     # Load and preprocess the image
#     masked_image_pil = Image.open(image_path)
#     masked_image_cv = cv2.cvtColor(np.array(masked_image_pil), cv2.COLOR_RGB2BGR)
    
#     # Rotation angles to check
#     rotation_angles = [0, 90, 180, 270, 360]
    
#     check_addhar_status = False
#     return_image_number = None
#     final_masked_image_path = None
    
#     # Loop through each angle
#     for angle in rotation_angles:
#         rotated_image = masked_image_cv

#         # Apply rotation based on the angle
#         if angle == 90:
#             rotated_image = cv2.rotate(masked_image_cv, cv2.ROTATE_90_CLOCKWISE)
#         elif angle == 180:
#             rotated_image = cv2.rotate(masked_image_cv, cv2.ROTATE_180)
#         elif angle == 270:
#             rotated_image = cv2.rotate(masked_image_cv, cv2.ROTATE_90_COUNTERCLOCKWISE)
#         # No need to rotate if the angle is 0 or 360

#         # Step 1: Blur the image
#         blurred_image = cv2.GaussianBlur(rotated_image, (5, 5), 0)
    
#         # Step 2: Scale the image if required
#         if SR:
#             width = int(blurred_image.shape[1] * SR_Ratio[0])
#             height = int(blurred_image.shape[0] * SR_Ratio[1])
#             dim = (width, height)
#             scaled_image = cv2.resize(blurred_image, dim, interpolation=cv2.INTER_AREA)
#         else:
#             scaled_image = blurred_image

#         # Convert back to PIL for OCR
#         scaled_image_pil = Image.fromarray(cv2.cvtColor(scaled_image, cv2.COLOR_BGR2RGB))
    
#         # Step 3: Extract bounding boxes using Tesseract
#         bounding_boxes = pytesseract.image_to_boxes(scaled_image_pil, config='-c tessedit_create_boxfile=1').split(" 0\n")
    
#         # Step 4: Find possible UIDs and mask them
#         possible_UIDs = Regex_Search(bounding_boxes)
        
#         for uid, start_index in possible_UIDs:
#             for i in range(8):  # Mask only the first 8 characters
#                 char_box = bounding_boxes[start_index + i].split()
#                 if char_box[1] != "0":
#                     check_addhar_status = True
#                     return_image_number = str(counts)

#                 x1 = int(char_box[1])
#                 y1 = int(char_box[2])
#                 x2 = int(char_box[3])
#                 y2 = int(char_box[4])

#                 cv2.rectangle(scaled_image, (x1, scaled_image.shape[0] - y1), (x2, scaled_image.shape[0] - y2), (255, 255, 255), -1)

#         # Step 5: Save the final masked image with the angle in the file name
#         final_masked_image_path = f"apps/static/Aadhaar_Masking/Aadhar_Rotate_images/rotate_masked_image_{counts}_angle_{angle}.jpg"
#         cv2.imwrite(final_masked_image_path, scaled_image)

#         # Check if Aadhar number is found and break the loop if true
#         if check_addhar_status:
#             print(f"Aadhar number found and masked at angle {angle}. Exiting loop.")
#             break  # Exit the loop when an Aadhar number is found and masked
    
#     return final_masked_image_path, possible_UIDs, check_addhar_status, return_image_number

# def Regex_Search(bounding_boxes):
#     possible_UIDs = []
#     Result = ""

#     for character in range(len(bounding_boxes)):
#         if len(bounding_boxes[character]) != 0:
#             Result += bounding_boxes[character][0]
#         else:
#             Result += '?'

#     # print(Result)

#     matches = [match.span() for match in re.finditer(r'\d{12}', Result)]
#     for match in matches:
#         UID = int(Result[match[0]:match[1]])

#         if compute_checksum(UID) == 0 and UID % 10000 != 1947:
#             possible_UIDs.append([UID, match[0]])

#     possible_UIDs = np.array(possible_UIDs)
    
#     return possible_UIDs


# def Extract_Law_Quality_Mask_UIDS(image_path , counts):

#     with open(image_path, 'rb') as f:
#         image_bytes = f.read()

#     language_codes = ['eng']
#     languages = '+'.join(language_codes)
#     custom_config = f'--oem 3 --psm 6 -l {languages}'

#     # Decode image from bytes
#     nparr = np.frombuffer(image_bytes, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#     # Rotation angles to check
#     rotation_angles = [0, 90, 180, 270, 360]

#     check_addhar_status = False
#     return_image_number = None
#     final_masked_image_path = None
    
#     # Loop through each angle
#     for angle in rotation_angles:
#         rotated_image = img

#         # Apply rotation based on the angle
#         if angle == 90:
#             rotated_image = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
#         elif angle == 180:
#             rotated_image = cv2.rotate(img, cv2.ROTATE_180)
#         elif angle == 270:
#             rotated_image = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
#         # No need to rotate for 0 and 360 degrees
        
#         # Resize by x2 using LANCZOS4 interpolation method
#         img2 = cv2.resize(rotated_image, (rotated_image.shape[1] * 2, rotated_image.shape[0] * 2), interpolation=cv2.INTER_LANCZOS4)
#         # img_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

#         # Step 3: Extract bounding boxes using Tesseract
#         bounding_boxes = pytesseract.image_to_boxes(img2, config=custom_config).split(" 0\n")

#         # Search for possible UIDs
#         possible_UIDs = Regex_Search(bounding_boxes)

#         # If no UIDs found, retry without custom config
#         if len(possible_UIDs) == 0:
#             bounding_boxes = pytesseract.image_to_boxes(img2).split(" 0\n")
#             possible_UIDs = Regex_Search(bounding_boxes)

#         # Step 4: Mask possible UIDs
#         for uid, start_index in possible_UIDs:
#             for i in range(8):  # Mask only the first 8 characters
#                 char_box = bounding_boxes[start_index + i].split()

#                 if char_box[1] != "0":
#                     check_addhar_status = True
#                     return_image_number = str(counts)

#                 x1 = int(char_box[1])
#                 y1 = int(char_box[2])
#                 x2 = int(char_box[3])
#                 y2 = int(char_box[4])

#                 cv2.rectangle(img2, (x1, img2.shape[0] - y1), (x2, img2.shape[0] - y2), (255, 255, 255), -1)

#         # Step 5: Save the masked image for the current rotation angle
#         final_masked_image_path = f"apps/static/Aadhaar_Masking/Aadhar_Rotate_images/rotate_masked_image_{counts}_angle_{angle}.jpg"
#         cv2.imwrite(final_masked_image_path, img2)

#         # Check if Aadhar number is found and break the loop
#         if check_addhar_status:
#             print(f"Aadhar number found and masked at angle {angle}. Exiting loop.")
#             break  # Exit the loop when an Aadhar number is found and masked

#     return final_masked_image_path, possible_UIDs, check_addhar_status, return_image_number

# def image_to_base64(image_path):
#     # Open the image file
#     with Image.open(image_path) as img:
#         # Create a BytesIO object to hold the image data
#         buffered = BytesIO()
#         # Save the image data to the BytesIO object in the desired format
#         img.save(buffered, format="PNG")  # You can change the format if needed
#         # Get the Base64 encoded string
#         img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
#     return img_str

# def addhar_mask(input_path, SR=False, SR_Ratio=[1, 1]):
#     counts = 0

#     masked_img, possible_UIDs ,status_check , image_count = Extract_and_Mask_UIDs(input_path,counts, SR, SR_Ratio)
    
#     if len(possible_UIDs) == 0:
#         masked_img, possible_UIDs , status_check , image_count= Extract_Law_Quality_Mask_UIDS(input_path , counts)
    

#     if len(possible_UIDs) != 0:
        
#         base64_string = image_to_base64(masked_img)
        
#         return {"response": "200",
#                 "Image_path":masked_img,
#                 "base64_string":"data:image/png;base64,"+base64_string}
    
#     else:
 
#             return { "message": "Error",
#                     "response": "400",
#                     "responseValue": "Please upload a clear and legible image of the entire document in JPEG, PNG format."}
    


import cv2
import pytesseract
import numpy as np
from PIL import Image
import re , os
import base64
from io import BytesIO
import shutil , time
from werkzeug.utils import secure_filename


pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' 
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/'


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

    print(Result)

    matches = [match.span() for match in re.finditer(r'\d{12}', Result)]
    for match in matches:
        UID = int(Result[match[0]:match[1]])

        if compute_checksum(UID) == 0 and UID % 10000 != 1947:
            possible_UIDs.append([UID, match[0]])

    possible_UIDs = np.array(possible_UIDs)
    
    return possible_UIDs



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


def Simple_way_Quality_Mask(image_path, SR=False, sr_image_path=None, SR_Ratio=[1, 1]):
    masked_image_pil = Image.open(image_path)
    masked_image_cv = cv2.cvtColor(np.array(masked_image_pil), cv2.COLOR_RGB2BGR)


    bounding_boxes = pytesseract.image_to_boxes(masked_image_pil ,config='-c tessedit_create_boxfile=1').split(" 0\n")

    possible_UIDs = Regex_Search(bounding_boxes)


    for uid, start_index in possible_UIDs:
        for i in range(8):  # Mask only the first 8 characters
            char_box = bounding_boxes[start_index + i].split()

            x1 = int(char_box[1])
            y1 = int(char_box[2])
            x2 = int(char_box[3])
            y2 = int(char_box[4])

            cv2.rectangle(masked_image_cv, (x1, masked_image_cv.shape[0] - y1), (x2, masked_image_cv.shape[0] - y2), (255, 255, 255), -1)

    masked_image_path = 'Simple_way_masked.jpg'
    cv2.imwrite(masked_image_path, masked_image_cv)

    return masked_image_path, possible_UIDs



def is_image_dark(image, threshold=50):
    """
    Check if the image is dark based on a threshold.
    Convert the image to grayscale and calculate the mean brightness.
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray_image)
    return mean_brightness < threshold


def is_image_blurry(image, threshold=100):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Calculate the Laplacian of the image and its variance
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    return variance < threshold

def map_coordinates_back_to_original(coords, resized_shape, original_shape, angle):
    """ Maps bounding box coordinates from the resized/rotated image back to the original image. """
    x1, y1, x2, y2 = coords
    scale_x = original_shape[1] / resized_shape[1]
    scale_y = original_shape[0] / resized_shape[0]
    
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


def Extract_Law_Quality_Mask_UIDS(image_path, counts):
    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    language_codes = ['eng']
    languages = '+'.join(language_codes)
    custom_config = f'--oem 3 --psm 6 -l {languages}'

    # Decode image from bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
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
        bounding_boxes = pytesseract.image_to_boxes(img2,lang='eng',config='-c tessedit_create_boxfile=1').split(" 0\n")
        possible_UIDs = Regex_Search(bounding_boxes)

        # If no UIDs found, retry without custom config
        if len(possible_UIDs) == 0:
            bounding_boxes = pytesseract.image_to_boxes(img2,config='-c tessedit_create_boxfile=1').split(" 0\n")
            possible_UIDs = Regex_Search(bounding_boxes)

        # Mask possible UIDs on the original image using the transformed coordinates
        for uid, start_index in possible_UIDs:
            for i in range(8):  # Mask only the first 8 characters
                char_box = bounding_boxes[start_index + i].split()

                if char_box[1] != "0":
                    check_addhar_status = True
                    return_image_number = str(counts)

                x1 = int(char_box[1])
                y1 = int(char_box[2])
                x2 = int(char_box[3])
                y2 = int(char_box[4])

                # Map the bounding box back to the original image using rotation
                orig_x1, orig_y1, orig_x2, orig_y2 = map_coordinates_back_to_original(
                    (x1, y1, x2, y2), img2.shape, rotated_image.shape, angle
                )

                # Apply the mask on the original image (not the rotated image)
                cv2.rectangle(original_img, (orig_x1, original_img.shape[0] - orig_y1), (orig_x2, original_img.shape[0] - orig_y2), (255, 255, 255), -1)

        # Save the masked original image for the current rotation angle
        final_masked_image_path = f"./apps/static/Aadhaar_Masking/Aadhar_Rotate_images/rotate_masked_image_{counts}_angle_{angle}.jpg"
        cv2.imwrite(final_masked_image_path, original_img)

        # Check if Aadhar number is found and break the loop
        if check_addhar_status:
            print(f"Aadhar number found and masked at angle {angle}. Exiting loop.")
            break  # Exit the loop when an Aadhar number is found and masked

    return final_masked_image_path, possible_UIDs, check_addhar_status, return_image_number


def Extract_and_Mask_UIDs(image_path, counts, SR=False, sr_image_path=None, SR_Ratio=[1, 1]):
    # Load and preprocess the original image (unmodified)
    original_image_pil = Image.open(image_path)
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
        bounding_boxes = pytesseract.image_to_boxes(scaled_image_pil, config='-c tessedit_create_boxfile=1').split(" 0\n")
    
        # Step 4: Find possible UIDs using regex
        possible_UIDs = Regex_Search(bounding_boxes)
        
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

        # Save the final masked image for the current rotation angle
        final_masked_image_path = f"./apps/static/Aadhaar_Masking/Aadhar_Rotate_images/original_masked_image_{counts}_angle_{angle}.jpg"
        cv2.imwrite(final_masked_image_path, original_image_cv)

        # Check if Aadhar number is found and exit if true
        if check_aadhar_status:
            print(f"Aadhar number found and masked at angle {angle}. Exiting loop.")
            break  # Exit the loop if an Aadhar number is found and masked
    
    return final_masked_image_path, possible_UIDs, check_aadhar_status, return_image_number


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

# Automatic brightness and contrast optimization with optional histogram clipping
def automatic_brightness_and_contrast(image, clip_hist_percent=25):
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

    '''
    # Calculate new histogram with desired range and show histogram 
    new_hist = cv2.calcHist([gray],[0],None,[256],[minimum_gray,maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0,256])
    plt.show()
    '''

    auto_result = convertScale(image, alpha=alpha, beta=beta)
    return (auto_result, alpha, beta)


def addhar_mask(input_path, SR=False, SR_Ratio=[1, 1]):
    counts = 0
    
    image = cv2.imread(input_path)


    # Normal Image 

    masked_img, possible_UIDs = Simple_way_Quality_Mask(input_path)

    # 4 Angle Wise Images
    if len(possible_UIDs) == 0:
        print("Without Lan")

        masked_img, possible_UIDs ,status_check , image_count = Extract_and_Mask_UIDs(input_path,counts, SR, SR_Ratio)
    
    # 4 Angle Wise Images English Lang
    if len(possible_UIDs) == 0:
        print("With Lan")
        masked_img, possible_UIDs , status_check , image_count= Extract_Law_Quality_Mask_UIDS(input_path , counts)
    
    if len(possible_UIDs) == 0:
        image = cv2.imread(input_path)

        # Contrast and brightness control
        alpha = 1.95 # Contrast control (1.0-3.0)
        beta = 0 # Brightness control (0-100)

        # Apply contrast and brightness
        manual_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

        # Save the images
        # cv2.imwrite('original_image.jpg', image)
        cv2.imwrite('manual_result_image.jpg', manual_result)

        masked_img, possible_UIDs , status_check , image_count= Extract_Law_Quality_Mask_UIDS('manual_result_image.jpg' , counts)


    if len(possible_UIDs) == 0:
        auto_result, alpha, beta = automatic_brightness_and_contrast(image)
        cv2.imwrite('auto_result.jpg', auto_result)
        image = cv2.imread('auto_result.jpg')

        # Contrast and brightness control
        alpha = 1.95 # Contrast control (1.0-3.0)
        beta = 0 # Brightness control (0-100)

        # Apply contrast and brightness
        manual_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

        # Save the images
        # cv2.imwrite('original_image.jpg', image)
        cv2.imwrite('manual_result_image.jpg', manual_result)

        masked_img, possible_UIDs , status_check , image_count= Extract_Law_Quality_Mask_UIDS('manual_result_image.jpg' , counts)
    
    

    # Image Rotate
    if len(possible_UIDs) == 0:
        print("Image Rotate")
        image = cv2.imread(input_path)

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
        
        
    
        # Save the rotated image if needed
        cv2.imwrite('rotated_image.jpg', rotated)

        # masked_img, possible_UIDs = Extract_Law_Quality_Mask_UIDS('rotated_image.jpg' )
        masked_img, possible_UIDs , status_check , image_count= Extract_Law_Quality_Mask_UIDS('rotated_image.jpg' , counts)


    # if len(possible_UIDs) == 0:

    if len(possible_UIDs) != 0:
        # print(masked_img)
        
        base64_string = image_to_base64(masked_img)
        
        return {"response": "200",
                "Image_path":masked_img,
                "base64_string":"data:image/png;base64,"+base64_string}
    
    else:
        # print("noooo")
        return { "message": "Error",
                "response": "400",
                "responseValue": "Please upload a clear and legible image of the entire document in JPEG, PNG format."}
