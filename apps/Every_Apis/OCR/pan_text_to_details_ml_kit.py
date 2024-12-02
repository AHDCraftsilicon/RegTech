import re


def extract_pan_number(pan_string):
    pan_pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    pan_number = re.search(pan_pattern, pan_string)
    
    pan_numbers = ""
    if pan_number:
        pan_numbers = pan_number.group()
    
    return pan_numbers


def extract_date_of_birth(pan_string):
    dob_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    dob_match = re.search(dob_pattern, pan_string)

    dob_date = ""
    if dob_match:
        dob_date =  dob_match.group(0)

    return dob_date


def extract_father_name(pan_string,pan_number):
    father_pattern = r"Father's Name\n([A-Z ]+)\n([A-Z]+)"
    fathers_name = ""
    match = re.search(father_pattern, pan_string)
    if match:
        fathers_name = f"{match.group(1)} {match.group(2)}"
    
    if fathers_name == "":
        pattern = r"Father's Name\s*([\w\s]+!)\s*([\w\s]+)"

        # Search for the pattern in the text
        match = re.search(pattern, pan_string)

        if match:
            fathers_name = match.group(1).strip() + " " + match.group(2).strip()

    if fathers_name == "":
        escaped_pan = re.escape(pan_number)
        # name_pattern = r'{}\s+([A-Za-z\s]+)'.format(escaped_pan)
        name_pattern = r'{}\n(?:[A-Z\s]+\n)([A-Z\s]+)'.format(escaped_pan)
        match = re.search(name_pattern, pan_string)

        # Check if a match was found and print it
        if match:
            fathers_name = match.group(1).strip()


    try:
        if fathers_name == "":
            lines = pan_string.split('\n')
            date_of_birth = extract_date_of_birth(pan_string)
            for i in range(len(lines)):
                if "Fathe" in lines[i]:
                    if i >= 1:
                        fathers_name = lines[i + 1]
    except:
        pass

    try:
        if fathers_name == "":
            lines = pan_string.split('\n')
            for i in range(len(lines)):
                if date_of_birth in lines[i]:
                    if i >= 1:
                        fathers_name = lines[i - 1]
    except:
        pass

    if fathers_name == "":
        father_name_pattern = r"Fathar's Name\s*([A-Za-z\s]+)"
        match = re.search(father_name_pattern, pan_string, re.IGNORECASE)
        if match:
            fathers_name = match.group(1).strip()
            # print("Father's Name:", father_name)

    if ":" in fathers_name:
        father_name_pattern = r"Fathar's Name\s*([A-Za-z\s]+)"
        match = re.search(father_name_pattern, pan_string, re.IGNORECASE)
        if match:
            fathers_name = match.group(1).strip()

    if fathers_name != "":
        fathers_name = re.sub(r"\b\w\b$", "", fathers_name).strip()


    return fathers_name



def extract_holder_name(pan_string,pan_number):
    # Split the string into lines
    holder_name = ""
    lines = pan_string.split('\n')
    # Iterate through the lines to find the keyword
    for i in range(len(lines)):
        if "Father's Name" in lines[i]:
            if i >= 1:
                holder_name = lines[i - 1]


    if "Father's Name" in pan_string:
    
        if holder_name == "":
            lines = pan_string.split('\n')
            # Iterate through the lines to find the keyword
            for i in range(len(lines)):
                if "Father's Name" in lines[i]:
                    if i >= 1:
                        holder_name = lines[i - 1]

    

    try:
        if holder_name == "":
            date_of_birth = extract_date_of_birth(pan_string)
            for i in range(len(lines)):
                if date_of_birth in lines[i]:
                    if i >= 2:
                        holder_name = lines[i - 2]
    except:
        pass

    if holder_name == "" :
        escaped_pan = re.escape(pan_number)
        # name_pattern = r'{}\s+([A-Za-z\s]+)'.format(escaped_pan)
        name_pattern = r'{}(?:\n|\s)([A-Z\s]+)'.format(escaped_pan)
        match = re.search(name_pattern, pan_string)

        if match:
            holder_name = match.group(1).strip()

    if holder_name == pan_number:
        print("-----------")
        name_pattern = r"Name\s+([A-Z\s]+)\n"

        # Search for the name in the text
        name_match = re.search(name_pattern, pan_string)

        if name_match:
            name = name_match.group(1).strip()
            holder_name = name

    return holder_name




def pan_details(pan_string):

    pan_strings = pan_string.replace("Fa ther's Name","Father's Name").replace("Permanent Account Number Card","")

    # print(pan_strings)
    
    pan_number = extract_pan_number(pan_strings)
    dob_date = extract_date_of_birth(pan_strings)
    father_name = extract_father_name(pan_strings,pan_number)
    holder_name = extract_holder_name(pan_strings,pan_number)

    # print("Pan Number = ", pan_number)
    # print("DOB = ", dob_date)
    # print("Father Name = ", father_name)
    # print("Name = ", holder_name)

    details_list = []

    if pan_number == "" and dob_date == "" and father_name == "" and holder_name == "":
        return { "status_code": 400,
            "status": "Error",
            "response": "No Data Found!"}
    else:
        details_list.append({
        "PAN_no" : pan_number,
        "DOB" : dob_date,
        "Father_name" : father_name,
        "Name" : holder_name,
            })

        return {"status_code": 200,
                "status": "Success",
                "response":details_list}











