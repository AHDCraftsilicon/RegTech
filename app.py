from apps import crete_app , socketios

app = crete_app()


if __name__ == "__main__":
    socketios.run(app, debug=True,port=8000)





# if data["doc_type"] == "Aadhaarcard":
#             ocr_image = data['image']

#             img_decoded = base64.b64decode(ocr_image)
#             qr_Code_scan_response = aadhaar_Qr_scan(img_decoded)
#             api_status = "Aadhaar_OCR"

#             if len(qr_Code_scan_response) != 0:
#                 store_response = {"status_code": 200,
#                             "status": "Success",
#                             "response": qr_Code_scan_response}
#             else:
#                 inseted_objid = ML_kit_value_storage_db.insert_one({"status":"loading.......","json_data":""}).inserted_id
#                 OCR_all_api_bp.socketios.emit('image_updates', {'image_url': 
#                                                                 {"image": ocr_image,
#                                                                  "objid":str(inseted_objid)}},
#                                                                  )
#                 OCR_all_api_bp.socketios.sleep(10)

                

#                 check_db_log = ML_kit_value_storage_db.find_one({"_id":ObjectId(inseted_objid)})
#                 if check_db_log != None:

#                     if check_db_log['json_data'] != "":
#                         print("Document found:", check_db_log['json_data'])
#                         store_response =  check_db_log['json_data'] 
#                     else:
#                         print("Document not found. Retrying...")

              
#                 return store_response

