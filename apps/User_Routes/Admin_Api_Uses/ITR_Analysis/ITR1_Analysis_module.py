
import re
import pdfplumber
import pandas as pd
from datetime import datetime
import tabula , json , math
import numpy as np

from collections import defaultdict
from datetime import datetime


# page count
def count_page_numbers(pdf_file):
    page_numbers = []
    pdf_read = pdfplumber.open(pdf_file)
    for page in pdf_read.pages:
        page_numbers.append(page.page_number)
    
        # break
    
    return  page_numbers


# ITR Other Format Basic Info
def find_keyword_details(keyword,get_raw_table):
    for row in get_raw_table:
        for col, value in enumerate(row):
            if isinstance(value, str) and keyword in value:
                # Find the index of the keyword and extract the corresponding value from the next row
                index = col
                # Ensure we don't go out of bounds
                if len(get_raw_table) > get_raw_table.index(row) + 2:
                    next_row = get_raw_table[get_raw_table.index(row) + 2]
                    if index < len(next_row):
                        return next_row[index]
    return None

# get rae table from using of modules
def get_raw_table_from_tabula(page_numbers,pdf_file):
    extracted_data = []
    for xx in page_numbers:
        tables = tabula.read_pdf(pdf_file,pages=xx,multiple_tables=True)

        for i, table in enumerate(tables):
            # print(table.values.tolist())
            table_as_list = table.values.tolist()
            extracted_data.extend([table.columns.values.tolist()])
            extracted_data.extend(table_as_list)


    return extracted_data

# Extract the relevant information
def extract_basic_relevant_info(data):
    result = {
        'First Name': None,
        'Middle Name': None,
        'Last Name': None,
        'PAN': None,
    }

    first_name = None
    middle_name = None
    last_name = None
    pan_number = None
    ITR_Type = None

    basic_info = []

    for row in data:
        if 'ITR-3' in row:
            ITR_Type = "ITR-3"
        if 'ITR-1' in row:
            ITR_Type = "ITR-1"
        if 'First Name' in row:
            result['First Name'] = row[row.index('First Name') + 1]
        if 'Middle Name' in row:
            result['Middle Name'] = row[row.index('Middle Name') + 1]
        if 'Last Name' in row:
            result['Last Name'] = row[row.index('Last Name') + 1]
        if 'PAN' in row:
            result['PAN'] = row[row.index('PAN') + 1]

    def clean_text(text):
        if 'eligible for Aadhaar No.)' in text:
            return text.split('eligible for Aadhaar No.)')[0].strip()
        return text

    if pd.notna(result["First Name"]) and \
        result["First Name"] != "Last Name":
        first_name = clean_text(result["First Name"].replace("\r", ""))
    else:
        first_name_basic = find_keyword_details('First Name', data)
        if pd.notna(first_name_basic) and "Date" not in first_name_basic:
            first_name = clean_text(first_name_basic.replace("\r", ""))

    if pd.notna(result["Middle Name"]) and \
        result["Middle Name"] != "Last Name":
        middle_name = clean_text(result["Middle Name"].replace("\r", ""))
    else:
        middle_name_basic = find_keyword_details('Middle Name', data)
        if pd.notna(middle_name_basic) and 'Status' not in middle_name_basic:
            middle_name = clean_text(middle_name_basic.replace("\r", ""))

    if pd.notna(result["Last Name"]) and \
        result["Last Name"] != "Last Name":
        last_name = clean_text(result["Last Name"].replace("\r", ""))
    else:
        last_name_basic = find_keyword_details('Last Name', data)
        if pd.notna(last_name_basic) and 'ADDRESS' not in last_name_basic:
            last_name = clean_text(last_name_basic.replace("\r", ""))

    if pd.notna(result["PAN"]) and \
        result["PAN"] != "PAN":
        pan_number = clean_text(result["PAN"].replace("\r", ""))
    else:
        pan_number_basic = find_keyword_details('PAN', data)
        if pd.notna(pan_number_basic):
            pan_number = clean_text(pan_number_basic.replace("\r", ""))

    basic_info.append({
        "ITR Type": ITR_Type,
        "Acknowledgement Number": None,
        "Assessment Year": None,
        "First name": first_name,
        "Middle name": middle_name,
        "Last name": last_name,
        "PAN": pan_number,
        "CIN": None,
        "Document Type": "IT Return",
    })

    return basic_info


def ITR1_all_info_get(nested_list):

    # Gross Salary (ia + ib + ic + id + ie)
    gross_salary_ia_ib_ic_id_ie = 0
    less_allowances = 0
    less_income = 0
    net_salary = 0
    deductions_us_16 = 0
    a_standard_deduction = 0
    b_entertainment_allowance = 0
    c_professional_tax = 0
    income_chargeable = 0

    # B2
    vii_income_chargeable = 0

    # B3
    income_from_other = 0

    # B4
    gross_total_income = 0

    for sublist in nested_list:
        for y in sublist:
            if pd.notna(y):
                # print(y)
                if isinstance(y, str) and "Gross Salary" in y: 
                    gross_salary_ia_ib_ic_id_ie = next(
                                        (item if isinstance(item, (int, float)) and not math.isnan(item) else match.group()
                                        for item in sublist
                                        if (isinstance(item, (int, float)) and not math.isnan(item)) or
                                            (isinstance(item, str) and (match := re.search(r'\b[\d,]+\b', item)))),0)

                if isinstance(y, str) and "Less allowances" in y:
                    for x_less_allow in sublist:
                        if pd.notna(x_less_allow):
                            if "ii" == x_less_allow:
                                less_allowances =  next(
                                        (item if isinstance(item, (int, float)) and not math.isnan(item) else match.group()
                                        for item in sublist
                                        if (isinstance(item, (int, float)) and not math.isnan(item)) or
                                            (isinstance(item, str) and (match := re.search(r'\b[\d,]+\b', item)))),0)


                if isinstance(y, str) and "Less : Income claimed" in y:
                    for x_less_income in sublist:
                        if pd.notna(x_less_income):
                            if "iia" == x_less_income:
                                less_income =  next(
                                        (item if isinstance(item, (int, float)) and not math.isnan(item) else match.group()
                                        for item in sublist
                                        if (isinstance(item, (int, float)) and not math.isnan(item)) or
                                            (isinstance(item, str) and (match := re.search(r'\b[\d,]+\b', item)))),0)

                
                if isinstance(y, str) and "Net Salary" in y:
                    for x_net_salary in sublist:
                        if pd.notna(x_net_salary):
                            if "iii" == x_net_salary:
                                net_salary =  next(
                                        (item if isinstance(item, (int, float)) and not math.isnan(item) else match.group()
                                        for item in sublist
                                        if (isinstance(item, (int, float)) and not math.isnan(item)) or
                                            (isinstance(item, str) and (match := re.search(r'\b[\d,]+\b', item)))),0)

                
                if isinstance(y, str) and "Deductions u/s 16" in y:
                    for x_deductions_us_16 in sublist:
                        if pd.notna(x_deductions_us_16):
                            if "iv" == x_deductions_us_16:
                                data = [float(item.replace(',', '')) for item in sublist if isinstance(item, str) and item.replace(',', '').replace('.', '').isdigit()]
                                amount = data[0] if data else None
                                deductions_us_16 =  amount


                if isinstance(y, str) and "Standard deduction" in y:
                    for x_a_standard_deduction in sublist:
                        if pd.notna(x_a_standard_deduction):
                            if "iva" == x_a_standard_deduction:
                                data = [float(item.replace(',', '')) for item in sublist if isinstance(item, str) and item.replace(',', '').replace('.', '').isdigit()]
                                amount = data[0] if data else None
                                a_standard_deduction =  amount

                
                if isinstance(y, str) and "Entertainment allowance" in y:
                    for x_b_entertainment_allowance in sublist:
                        if pd.notna(x_b_entertainment_allowance):
                            if "ivb" == x_b_entertainment_allowance:
                                data = [float(item.replace(',', '')) for item in sublist if isinstance(item, str) and item.replace(',', '').replace('.', '').isdigit()]
                                amount = data[0] if data else None
                                b_entertainment_allowance =  amount

                
                if isinstance(y, str) and "Income chargeable" in y:
                    for x_income_chargeable in sublist:
                        if pd.notna(x_income_chargeable):
                            if "B1" == x_income_chargeable:
                                income_chargeable =  next(
                                        (item if isinstance(item, (int, float)) and not math.isnan(item) else match.group()
                                        for item in sublist
                                        if (isinstance(item, (int, float)) and not math.isnan(item)) or
                                            (isinstance(item, str) and (match := re.search(r'\b[\d,]+\b', item)))),0)
                                
                if isinstance(y, str) and "Income chargeable" in y:
                    for x_vii_income_chargeable in sublist:
                        if pd.notna(x_vii_income_chargeable):
                            if "B2" == x_vii_income_chargeable:
                                data = [float(item.replace(',', '')) for item in sublist if isinstance(item, str) and item.replace(',', '').replace('.', '').isdigit()]
                                amount = data[0] if data else None
                                vii_income_chargeable =  amount


                if isinstance(y, str) and "Income from Other" in y:
                    income_from_other =  next(
                                        (item if isinstance(item, (int, float)) and not math.isnan(item) else match.group()
                                        for item in sublist
                                        if (isinstance(item, (int, float)) and not math.isnan(item)) or
                                            (isinstance(item, str) and (match := re.search(r'\b[\d,]+\b', item)))),0)
                
                if isinstance(y, str) and "Gross Total Income" in y:
                    for x_gross_total_income in sublist:
                        if pd.notna(x_gross_total_income):
                            if "B4" == x_gross_total_income:
                                data = [float(item.replace(',', '')) for item in sublist if isinstance(item, str) and item.replace(',', '').replace('.', '').isdigit()]
                                amount = data[0] if data else None

                                gross_total_income =  amount
    Extracted_details  = {}

    # GROSS TOTAL INCOME
    Extracted_details["Gross Salary"] = gross_salary_ia_ib_ic_id_ie
    Extracted_details["Less allowances"] = less_allowances
    Extracted_details["Less Income claimed"] = less_income
    Extracted_details["Net Salary"] = net_salary
    Extracted_details["Deductions US 16"] = deductions_us_16 
    Extracted_details["Standard deduction"] = a_standard_deduction
    Extracted_details["Entertainment allowance"] = b_entertainment_allowance
    Extracted_details["Professional tax"] = c_professional_tax
    Extracted_details["Income chargeable Salaries"] = income_chargeable
    Extracted_details["Income chargeable House Property"] = vii_income_chargeable
    Extracted_details["Income from Other Sources"] = income_from_other
    Extracted_details["Gross Total Income"] = gross_total_income

    return Extracted_details

    # print("B1 i .Gross Salary (ia + ib + ic + id + ie) = " , gross_salary_ia_ib_ic_id_ie)
    # print("ii. Less allowances = " , less_allowances)
    # print("iia. Less : Income claimed for relief from taxation u/s 89A = " , less_income)
    # print("iii. Net Salary = " , net_salary)
    # print("iv. Deductions u/s 16 (iva + ivb + ivc) = " , deductions_us_16)
    # print("iv. a . Standard deduction u/s 16(ia) = " , a_standard_deduction)
    # print("iv. b . Entertainment allowance u/s 16(ii) = " , b_entertainment_allowance)
    # print("iv. c . Professional tax = " , c_professional_tax)
    # print("v. Income chargeable under the head 'Salaries' (iii - iv) = " , income_chargeable)

    # print("B2 vii. Income chargeable under the head 'House Property' = ",vii_income_chargeable)

    # print("B3 Income from Other Sources = ",income_from_other)

    # print("B4 Gross Total Income (B1+B2+B3)  = ",gross_total_income)


def itr1_read_main(pdf_file):
    try:
        # count page number
        page_number = count_page_numbers(pdf_file)


        # get raw table
        get_raw_table = get_raw_table_from_tabula(page_number,pdf_file)

        # print(get_raw_table)

        # Get Basic Info ITR
        extracted_basic_info = extract_basic_relevant_info(get_raw_table)
        
        if extracted_basic_info[0]["ITR Type"] == "ITR-1":
            table_details =  ITR1_all_info_get(get_raw_table)
            
            return_responce = {}
            return_responce["metadata"] = extracted_basic_info
            return_responce["table"] = table_details
            # return_responce.append({"metadata":extracted_basic_info},
            #                 {"table": table_details})            
            return return_responce
    except:
        return_responce = "Please Upload Valid ITR Formate"

        return return_responce


