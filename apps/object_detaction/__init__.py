from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file
import os , base64
import torch
import cv2
from pathlib import Path
from collections import Counter
import time , io
from werkzeug.utils import secure_filename
from PIL import Image


# Blueprint
object_detaction_bp = Blueprint("object_detaction_bp",
                        __name__,
                        url_prefix="/")

model = torch.hub.load('./apps/yolov5','custom', path='./apps/yolov5/yolov5s.pt', source='local')

@object_detaction_bp.route("/api/v1/image/objectDetactionImage",methods=['POST'])
def object_detaction_main():


    data = request.get_json()

        # file_name =  request.files.get('image')

    if not data or 'image' not in data:
            return jsonify({"response": "999",
                    "message": "Error",
                    "responseValue": "image cannot be null or empty."
                }), 400
    
    if data['image'] != "":
            try:
                base64_string = data['image'].split(',')[1]
            except:
                base64_string = data['image']

            # print(base64_string.split(',')[1])

            # Base64 Convert To Image
            if base64_string.startswith('data:image/jpeg;base64,'):
                base64_string = base64_string.replace('data:image/jpeg;base64,', '')

            # Decode the base64 string into bytes
            image_bytes = base64.b64decode(base64_string)

            # Convert bytes data to PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Save the image to a file (example: 'output.jpg')
            filename_img = str(time.time()).replace(".", "")
            # print(filename_img+".png")
            static_file_name = filename_img+".png"

            image.save(os.path.join('apps/static/object_Detaction', secure_filename(static_file_name)))
            
            image_path = "apps/static/object_Detaction/" +static_file_name

            # Response Store List
            responce_list = []

            # Yolo Model Work Start
            imgss = cv2.imread(image_path)
            if imgss is None:
                return "Failed to load image", 400

            results = model(imgss)
            # results.show()

            output_path = './static/obj_dect_output/test.jpg'
            results.save(output_path)

            # time.sleep(2)
            img_rgb = cv2.cvtColor(imgss, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)

            # Create a BytesIO object to save the image in-memory
            buffered = io.BytesIO()
            pil_img.save(buffered, format="JPEG")

            # Encode image to Base64
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            responce_list.append({"image":img_base64})


            object_list = []
            # with open("image_base64.txt", "w") as text_file:
            #     text_file.write(img_base64)

            item_counts = Counter(results.pandas().xyxy[0]['name'].tolist())
            for x,y in zip(item_counts.keys(), item_counts.values()):
                object_list.append({"object_name":y,"object_count":x})
                # print(x,y)

            responce_list.append({"object_list":object_list})



            return jsonify({"response": "000",
                                    "message": "Success",
                                    "responseValue": responce_list}),200
    else:
            return jsonify({"response": "999",
                        "message": "Error",
                        "responseValue": "image cannot be null or empty."
                    }), 400