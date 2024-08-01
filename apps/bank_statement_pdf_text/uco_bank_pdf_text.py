import re

import requests
import pdfplumber
import pandas as pd
from datetime import datetime




# Get Basic details UCO Bank Statement

# IFSC Code
def extract_ifsc(text):
    match = re.search(r'IFSC:\s*([\w]+)', text)
    return match.group(1) if match else None

# Bank Account Number
def extract_number(text):
    match = re.search(r'Number:\s*([\d]+)', text)
    return match.group(1) if match else None

# NickName
def extract_nickname(text):
    match = re.search(r'Nickname:\s*([A-Za-z\s]+)', text)
    return match.group(1).strip() if match else None

# Name 
def extract_name(text):
    match = re.search(r'Name:\s*([A-Za-z\s]+)', text)
    return match.group(1).strip() if match else None

# Status 
def extract_status(text):
    match = re.search(r'Status:\s*([\w]+)', text)
    return match.group(1) if match else None

# Currency
def extract_currency(text):
    match = re.search(r'Currency:\s*([\w]+)', text)
    return match.group(1) if match else None

# Branch Name
def extract_branch(text):
    match = re.search(r'Branch:\s*([\w\s]+)\s*Drawing Power:', text, re.DOTALL)
    if match:
        branch_name = match.group(1).strip()
        additional_info_match = re.search(r'Drawing Power:.*?\n([\w\s]+)', text, re.DOTALL)
        if additional_info_match:
            branch_name += " " + additional_info_match.group(1).strip().replace('\n', ' ')
        return branch_name
    return None

# OPen Date
def extract_open_date(text):
    match = re.search(r'Open Date:\s*([\d/]+)', text)
    return match.group(1) if match else None

# Account Type
def extract_account_type(text):
    match = re.search(r'Type:\s*([\w\s]+)', text)
    return match.group(1).strip() if match else None

# Address1
def extract_address_line_1(text):
    match = re.search(r'Address Line 1:\s*([^\n]+)', text)
    return match.group(1).strip() if match else None

# Address2
def extract_address_line_2(text):
    match = re.search(r'Address Line 2:\s*([^\n]+)', text)
    return match.group(1).strip() if match else None

# Contact Number
def extract_contact_number(text):
    match = re.search(r'Contact Number:\s*([\+\d]+)', text)
    return match.group(1).strip() if match else None


def parse_transactions(transactions):
    transaction_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}) ([+-]?[,\d]+\.\d{2}) (Dr\.|Cr\.) ([,\d]+\.\d{2})")
    lists = []
    i = 0
    while i < len(transactions):
        if transaction_pattern.match(transactions[i]):
            date, amount, type_, total_balance = transaction_pattern.match(transactions[i]).groups()
            details = []
            i += 1
            while i < len(transactions) and not transaction_pattern.match(transactions[i]):
                details.append(transactions[i])
                i += 1

            lists.append({'Date' : date,
                            'Amount' : amount,
                            'type' : type_,
                            'Total_Balance' : total_balance,
                            'Transaction_Details' : ' '.join(details)
                            })
            # print(f"Date: {date}")
            # print(f"Amount: {amount}")
            # print(f"Type: {type_}")
            # print(f"Total Balance: {total_balance}")
            # print(f"Transaction Details: {' '.join(details)}")
            # print('---')
        else:
            i += 1

    return lists

# Transcation Details
def extract_transaction_details(text):

    lines = text.strip().split('\n')

    transactions = parse_transactions(lines)

    # pattern = re.compile(
    # r'(\d{2}/\d{2}/\d{4})\s(-?[\d.,]+)\s(Dr\.|Cr\.)\s([\d.,]+)\n'
    # r'(MPAY.*\n.*\n.*)', re.MULTILINE)
    
    # transactions =[]

    # # Iterate over matches
    # for match in pattern.finditer(text):
    #     date = match.group(1).strip()
    #     amount = match.group(2).strip()
    #     txn_type = match.group(3).strip()
    #     total_balance = match.group(4).strip()
    #     txn_details = match.group(5).strip().replace('\n', ' ')
    #     print(date )
    #     transactions.append({'Date' : date,
    #                         'Amount' : amount,
    #                         'type' : txn_type,
    #                         'Total_Balance' : total_balance,
    #                         'Transaction_Details' : txn_details.replace(" ","")
    #                         })
        # transactions.append({'Amount' : amount})
        # transactions.append({'type' : txn_type})
        # transactions.append({'Total_Balance' : total_balance})
        # transactions.append({'Transaction_Details' : txn_details.replace(" ","")})

    
    return transactions





def uco_bank_statmenr_main(url):
    # url = "15799_BANK_STMT_1 1 (2).pdf"
    pdf_read = pdfplumber.open(url)


    page_numbers = []
        
    # Iterate through each page
    for page in pdf_read.pages:
        page_numbers.append(page.page_number - 1)

    ifsc_code = ""
    account_number = ""
    nick_name = ""
    main_name = ""
    status = ""
    # currency = ""
    branch_name = ""
    open_date = ""
    account_type = ""
    address1 = ""
    address2 = ""
    contact_number = ""
    transction_list = []

    # details_list = []


    # Summary - Scorecard
    summary_scorecard = [{
                    "Item": "Monthly Average Surplus",
                    "Details": "NA",
                    "Verification": "NA"
                },
                {
                    "Item": "EMI Detected",
                    "Details": False,
                    "Verification": "NA"
                },
                {
                    "Item": "Cheque Bounce",
                    "Details": "NA",
                    "Verification": "NA"
                },
                {
                    "Item": "Bank",
                    "Details": "UCO BANK",
                    "Verification": "NA"
                },
                {
                    "Item": "Opening Balance",
                    "Details": "NA",
                    "Verification": "NA"
                },
                {
                    "Item": "Closing Balance",
                    "Details": "NA",
                    "Verification": "NA"
                },
                {
                "Item": "MICR Code",
                "Details": "NA",
                "Verification": "NA"
                },
                {
                    "Item": "Monthly Average Balance",
                    "Details": None,
                    "Verification": "NA"
                },]

    # Bureau Ratings - Summary
    bureau_ratings_Summary = [{
                    "Item": "Credit Score",
                    "Detail": None
                },
                {
                    "Item": "Status",
                    "Detail": None
                },
                {
                    "Item": "Total accounts",
                    "Detail": None
                },
            
                {
                    "Item": "Active Loan Accounts",
                    "Detail": None
                },
                {
                    "Item": "Active CC Accounts",
                    "Detail": None
                },
                {
                    "Item": "Overdue Accounts",
                    "Detail": None
                },
                {
                    "Item": "Delayed Payments",
                    "Detail": None
                },
                {
                    "Item": "Max Payment Delay Inactive",
                    "Detail": None
                },
                {
                    "Item": "Source",
                    "Detail": None
                }]

    # Bureau Ratings - Telephone
    bureau_ratings_telephone = []

    # Bureau Ratings - Address
    bureau_ratings_address = []

    # All Transactions
    all_transactions = []

    for page_no in page_numbers:
        # print(page_no)
        page = pdf_read.pages[page_no]
        pdf_to_String = page.extract_text()

        # Geting All Details
        

        if ifsc_code == "":
            ifsc_code = extract_ifsc(pdf_to_String)
            if ifsc_code != None:
                summary_scorecard.append({
                        "Item": "IFSC Code",
                        "Details": ifsc_code,
                        "Verification": "NA"
                    })
            else:
                summary_scorecard.append({
                        "Item": "IFSC Code",
                        "Details": "NA",
                        "Verification": "NA"
                    })
        
        if account_number == "":
            account_number = extract_number(pdf_to_String)
            if account_number != None:
                summary_scorecard.append({
                    "Item": "Account Number",
                    "Details": account_number,
                    "Verification": "NA"      
                    })
            else:
                summary_scorecard.append({
                    "Item": "Account Number",
                    "Details": "NA",
                    "Verification": "NA"      
                    })
        


        if main_name == "":
            main_name = extract_name(pdf_to_String)
            # print("NAME = ", main_name.replace("Status","").strip())

            if main_name != None:
                if "Status" in main_name:
                    summary_scorecard.append({
                        "Item": "Customer Name",
                        "Details": main_name.replace("Status","").strip(),
                        "Verification": "NA"
                    })
                else:
                    summary_scorecard.append({
                        "Item": "Customer Name",
                        "Details": main_name,
                        "Verification": "NA"
                    })
            else:
                summary_scorecard.append({
                        "Item": "Customer Name",
                        "Details": "NA",
                        "Verification": "NA"
                    })
                

        if status == "":
            status = extract_status(pdf_to_String)
          
        
            if status != None:
                bureau_ratings_Summary.append(
                    {
                        "Item": "Active Accounts",
                        "Detail": status
                    })
            else:
                bureau_ratings_Summary.append(
                    {
                        "Item": "Active Accounts",
                        "Detail": "NA"
                    })

     

        if account_type == "":
            account_type = extract_account_type(pdf_to_String)

            if account_type != None:
                if "Currency" in account_type:
                    summary_scorecard.append({
                    "Item": "Account Type",
                    "Details": account_type.split("Currency")[0].strip(),
                    "Verification": "NA"
                    })
                else:
                    # print("ACCOUNT TYPE = ", account_type)
                    summary_scorecard.append({
                        "Item": "Account Type",
                        "Details": account_type,
                        "Verification": "NA"
                    })
            else:
                summary_scorecard.append({
                        "Item": "Account Type",
                        "Details": "NA",
                        "Verification": "NA"
                    })


        if address1 == "":
            address1 = extract_address_line_1(pdf_to_String)
            if address1 != None:
                bureau_ratings_address.append({
                    "ADDRESS1" : address1
                    })
                                

        if address2 == "":
            address2 = extract_address_line_2(pdf_to_String)
            if address2 != None:
                bureau_ratings_address.append({
                    "ADDRESS2" : address2
                    })

        if contact_number == "":
            contact_number = extract_contact_number(pdf_to_String)
            if contact_number != None:
                bureau_ratings_telephone.append({contact_number})
        
        
        transction_Details = extract_transaction_details(pdf_to_String)
        for x in transction_Details:
            all_transactions.append(x)


    if all_transactions != []:
        if all_transactions[0] != {}:
            summary_scorecard.append({
                "Item": "Start Date",
                "Details": all_transactions[0]['Date'],
                "Verification": "NA"})

        if all_transactions[0] != {}:
            summary_scorecard.append({
                "Item": "End Date",
                "Details": all_transactions[-1]['Date'],
                "Verification": "NA"})
            
    else:
        summary_scorecard.append({
                "Item": "Start Date",
                "Details": "NA",
                "Verification": "NA"})
         
        summary_scorecard.append({
                "Item": "End Date",
                "Details": "NA",
                "Verification": "NA"})



    # Formated Json

    formate_json = {}

    formate_json["Summary - Scorecard"] = summary_scorecard
    formate_json["Summary - Document Authenticity Check"] = [{
                "Tag": "Fingerprint Check",
                "Status": "Yes"
            },{
                "Tag": "Balance Recon",
                "Status": "NA"
            }]

    formate_json["Summary - Fixed Income / Obligation"] = [{ "Salary": "Not Identified",
            "Probable Salary": "Not Identified",
            "EMI/Loan": "NA"}]

    formate_json["Fraud Check Triggers - Fraud Checks"] = [ {
                "Possible Fraud Indicators": "Balance Reconciliation",
                "Identified?": False
            },
            {
                "Possible Fraud Indicators": "Equal Debit Credit",
                "Identified?": "NA"
            },
            {
                "Possible Fraud Indicators": "Suspected Income Infusion",
                "Identified?": False
            },
            {
                "Possible Fraud Indicators": "Negative EOD Balance",
                "Identified?": "NA"
            },
            {
                "Possible Fraud Indicators": "Transactions on Bank Holidays",
                "Identified?": "NA"
            },
            {
                "Possible Fraud Indicators": "Suspicious RTGS Transactions",
                "Identified?": "NA"
            },
            {
                "Possible Fraud Indicators": "Suspicious Tax Payments",
                "Identified?": "NA"
            },
            {
                "Possible Fraud Indicators": "Irregular Credit Card Payments",
                "Identified?": "NA"
            },
            {
                "Possible Fraud Indicators": "Irregular Salary Credits",
                "Identified?": "NA"
            },
            {
                "Possible Fraud Indicators": "Unchanged Salary Credit Amount",
                "Identified?": "NA"
            },
            {
                "Possible Fraud Indicators": "Irregular Transfers to Parties",
                "Identified?": False
            },
            {
                "Possible Fraud Indicators": "Data Duplicity",
                "Identified?": "NA"
            },
            {
                "Possible Fraud Indicators": "Irregularr Interest Charges",
                "Identified?": "NA"
            }]


    formate_json["Fraud Check Triggers - Fraud Check Details"] = []

    formate_json["Emi Details"] = None
    formate_json["Month Wise Details"] = []
    formate_json["EOD"] = {}
    formate_json["All Transactions"] = all_transactions
    formate_json["Credit Card Info - Credit Card Details"] = [{
                "Card Number": "",
                "Statement Date": "",
                "Start Date": "",
                "End Date": "",
                "Payment Due": "",
                "Minimum Due": "",
                "Due Date": "",
                "Payment": "",
                "Payment in Statement": "",
                "Payment Date": "",
                "Payments Percentage": None
            },
            {
                "Card Number": "",
                "Statement Date": "",
                "Start Date": "",
                "End Date": "",
                "Payment Due": "",
                "Minimum Due": "",
                "Due Date": "",
                "Payment": "",
                "Payment in Statement": "",
                "Payment Date": "",
                "Payments Percentage": None
            }]

    formate_json["Credit Card Info - Credit Cards"] = None
    formate_json["Return Transactions"] = []
    formate_json["Recurring Debits"] = []
    formate_json["Recurring Credits"] = []

    formate_json["Scoring Details"] = [{
                "Description": "Monthly Average Inflow",
                "Value": "NA"
            },
            {
                "Description": "Monthly Average Outflow",
                "Value": "NA"
            },
            {
                "Description": "Average Credit Transactions",
                "Value": "NA"
            },
            {
                "Description": "Average Debit Transactions",
                "Value": "NA"
            },
            {
                "Description": "Total Credit Amount",
                "Value": "NA"
            },
            {
                "Description": "Total Debit Amount",
                "Value": "NA"
            },
            {
                "Description": "Total Count of Credit Transactions",
                "Value": "NA"
            },
            {
                "Description": "Total Count of Debit Transactions",
                "Value": "NA"
            },
            {
                "Description": "Monthly Average Surplus",
                "Value": "NA"
            },
            {
                "Description": "Fixed Obligation To Income Ratio",
                "Value": "NA"
            },
            {
                "Description": "Maximum Balance",
                "Value": "NA"
            },
            {
                "Description": "Minimum Balance",
                "Value": "NA"
            },
            {
                "Description": "Maximum Credit",
                "Value": "NA"
            },
            {
                "Description": "Minimum Credit",
                "Value": "NA"
            },
            {
                "Description": "Maximum Debit",
                "Value": "NA"
            },
            {
                "Description": "Minimum Debit",
                "Value": "NA"
            },
            {
                "Description": "Month end balance in last 90 days",
                "Value": "NA"
            },
            {
                "Description": "Month end balance in last 180 days",
                "Value": "NA"
            },
            {
                "Description": "Number of Cash withdrawal in last 3 months",
                "Value": "NA"
            },
            {
                "Description": "Number of Cash withdrawal in last 6 months",
                "Value": "NA"
            },
            {
                "Description": "Count of interest credited in last 3 months",
                "Value": "NA"
            },
            {
                "Description": "Amount of interest credited in last 3 months",
                "Value": "NA"
            },
            {
                "Description": "Count of interest credited in last 6 months",
                "Value": "NA"
            },
            {
                "Description": "Amount of interest credited in last 6 months",
                "Value": "NA"
            },
            {
                "Description": "Count of Cheque Bounce in last 3 months",
                "Value": "NA"
            },
            {
                "Description": "Amount of Cheque Bounce in last 3 months",
                "Value": "NA"
            },
            {
                "Description": "Count of Cheque Bounce in last 6 months",
                "Value": "NA"
            },
            {
                "Description": "Amount of Cheque Bounce in last 6 months",
                "Value": "NA"
            },
            {
                "Description": "Velocity \u2013 (Sum of debits and credits) /AMB in the last 3 months",
                "Value": "NA"
            },
            {
                "Description": "Velocity \u2013 (Sum of debits and credits) /AMB in the last 6 months",
                "Value": "NA"
            }]

    formate_json["Summary - Bureau Rating"] = [{
                "Item": "Total EMIs",
                "Bureau Ratings": "NA",
                "Bank Statement": "NA",
                "Reconciled": "NA"
            },
            {
                "Item": "EMI Value",
                "Bureau Ratings": "NA",
                "Bank Statement": "NA",
                "Reconciled": "NA"
            }]

    formate_json["Summary - Credit Card"] = [{
                "Item": "Payment Made",
                "Credit Data": "NA",
                "Bank Statement": "NA",
                "Reconciled": "NA"
            },
            {
                "Item": "Payment Amount",
                "Credit Data": "NA",
                "Bank Statement": "NA",
                "Reconciled": "NA"
            },
            {
                "Item": "Payment Due",
                "Credit Data": "NA",
                "Bank Statement": "NA",
                "Reconciled": "NA"
            }]

    formate_json["Summary - Salary Details"] = [{
                "Item": "Total Salary Transaction",
                "Salary Slip": "NA",
                "Bank Statement": "NA",
                "Reconciled": "NA"
            },
            {
                "Item": "Total Salary Credit",
                "Salary Slip": "NA",
                "Bank Statement": "NA",
                "Reconciled": "NA"
            }]


    formate_json["Summary - Cheque Bounce Charges"] = [ {
                "Type": "Amount of Cheque Bounce",
                "Value": "NA"
            },
            {
                "Type": "Count of Cheque Bounce",
                "Value": "NA"
            }]

    formate_json["Salary Slip Info"] = []
    formate_json["Bureau Ratings - Telephone"]= []
    formate_json["Bureau Ratings - Address"]= []
    formate_json["Bureau Ratings - Loans"]= []
    formate_json["Bureau Ratings - Enquiry"] = {
        "Member": None,
        "Enquiry Date": None,
        "Enquiry Purpose": None,
        "Enquiry Amount": None
    }
    formate_json["Bureau Ratings - Consumer Information"] = [
        {
            "Item": "Date of Birth",
            "Detail": None
        },
        {
            "Item": "Gender",
            "Detail": None
        }
    ],
    formate_json["Bureau Ratings - Identification Type"]= []
    formate_json["Bureau Ratings - Emails"]= []

    formate_json["Bureau Ratings - Summary"] = [
            {
                "Item": "Credit Score",
                "Detail": None
            },
            {
                "Item": "Status",
                "Detail": None
            },
            {
                "Item": "Total accounts",
                "Detail": None
            },
            {
                "Item": "Active Accounts",
                "Detail": bureau_ratings_Summary
            },
            {
                "Item": "Active Loan Accounts",
                "Detail": None
            },
            {
                "Item": "Active CC Accounts",
                "Detail": None
            },
            {
                "Item": "Overdue Accounts",
                "Detail": None
            },
            {
                "Item": "Delayed Payments",
                "Detail": None
            },
            {
                "Item": "Max Payment Delay Inactive",
                "Detail": None
            },
            {
                "Item": "Source",
                "Detail": None
            }
        ]


    formate_json["Salary Slip Info - Summary"] = [
            {
                "Item": "Employee Name",
                "Details": None,
                "Verification": ""
            },
            {
                "Item": "PAN Number",
                "Details": None,
                "Verification": ""
            },
            {
                "Item": "UAN Number",
                "Details": None,
                "Verification": ""
            },
            {
                "Item": "A/C Number",
                "Details": None,
                "Verification": ""
            },
            {
                "Item": "Bank Name",
                "Details": None,
                "Verification": ""
            },
            {
                "Item": "Name of Employer",
                "Details": None,
                "Verification": ""
            }
        ],

    formate_json["Salary Slip Info - Details"] = []
    formate_json["Associated Party Transactions"] = []


    top10_transactions_credit = []
    top10_transactions_debit = []
    for yy in all_transactions[:10]:
        # print(yy)
        if yy['type'] == 'Cr.':
            top10_transactions_credit.append({
                "Date" : yy["Date"],
                "Amount" : yy["Amount"],
                "type" : yy["type"],
                "Total_Balance" : yy["Total_Balance"],
                "Transaction_Details" : yy["Transaction_Details"],
            })
        elif yy['type'] == 'Dr.':
            top10_transactions_debit.append({
                "Date" : yy["Date"],
                "Amount" : yy["Amount"],
                "type" : yy["type"],
                "Total_Balance" : yy["Total_Balance"],
                "Transaction_Details" : yy["Transaction_Details"],
            })

            


    formate_json["Top Transactions - Top 10 Credit Transaction"] = top10_transactions_credit
    formate_json["Top Transactions - Top 10 Debit Transaction"] = top10_transactions_debit
    formate_json["Top Transactions - Top 10 Monthly Transaction"] = all_transactions[:10]


    return formate_json



# print(uco_bank_statmenr_main("15799_BANK_STMT_1 1 (2).pdf"))

# import json  

# save_file = open("savedata.json", "w")  
# json.dump(formate_json, save_file, indent = 6)  
# save_file.close()  

# with open("bank_list.txt", "w") as text_file:
#     text_file.write(formate_json)

# print(formate_json)


    # print("----- \n",pdf_to_String)
    # break

