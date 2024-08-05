import re
import requests
import pdfplumber
import pandas as pd
from datetime import datetime


def extract_mr(text):
    match = re.search(r"MR\.\s([A-Z]+[A-Z\s]*)|MRS\.\s([A-Z]+[A-Z\s]*)|MS\.\s([A-Z]+[A-Z\s]*)|MISS\.\s([A-Z]+[A-Z\s]*)", text)
    return match.group(1) if match else None

def extract_currency(text):
    match = re.search(r"Currency\s:\s([A-Z]+)", text)
    return match.group(1) if match else None

def extract_email(text):
    match = re.search(r"Email\s:\s([\w\.\-]+@[\w\.\-]+)", text)
    return match.group(1) if match else None

def extract_account_no(text):
    match = re.search(r"AccountNo\s:\s(\d+)", text)
    return match.group(1) if match else None

def extract_rtgs_ifsc(text):
    match = re.search(r"RTGS/NEFTIFSC:\s([\w\d]+)", text)
    return match.group(1) if match else None

def extract_micr(text):
    match = re.search(r"MICR:([\d]+)", text)
    return match.group(1) if match else None

def extract_account_status(text):
    match = re.search(r"AccountStatus\s:\s(\w+)", text)
    return match.group(1) if match else None

def extract_phoneno(text):
    match = re.search(r"Phoneno\.\s:\s(\d+)", text)
    return match.group(1) if match else None

def extract_from_date(text):
    match = re.search(r"From\s:\s(\d{2}/\d{2}/\d{4})", text)
    return match.group(1) if match else None

def extract_to_date(text):
    match = re.search(r"To\s:\s(\d{2}/\d{2}/\d{4})", text)
    return match.group(1) if match else None


def extract_transction_details(text):
    # pattern = re.compile(r'''
    # (?P<date>\d{2}/\d{2}/\d{2})\s+                # Date
    # (?P<narration>[\w\W]+?)\s+                   # Narration
    # (?P<ref_no>\d{16,19})\s+                     # Chq./Ref.No.
    # (?P<value_date>\d{2}/\d{2}/\d{2})\s+        # Value Date
    # (?P<withdrawal_amt>[\d,]+\.\d{2})\s+         # Withdrawal Amount
    # (?P<closing_balance>[\d,]+\.\d{2})          # Closing Balance
    # ''', re.VERBOSE)

    # # Find all matches in the data
    # matches = pattern.finditer(text)


    # list_data = []

    # # Process and print matches
    # for match in matches:
    #     date = match.group('date')
    #     narration = match.group('narration').strip()
    #     ref_no = match.group('ref_no')
    #     value_date = match.group('value_date')
    #     amount = match.group('withdrawal_amt')
    #     closing_balance = match.group('closing_balance')

    #     list_data.append({
    #         "Date" :date,
    #         "Narration" :narration,
    #         "Chq_Ref_No" :ref_no,
    #         "value_date" :value_date,
    #         "amount" :amount,
    #         "closing_balance" :closing_balance,
    #     })

    # # Process the list
    # for i in range(1, len(list_data)):
    #     previous_balance = float(list_data[i - 1]['closing_balance'].replace(',', ''))
    #     current_balance = float(list_data[i]['closing_balance'].replace(',', ''))
    #     amount = float(list_data[i]['amount'].replace(',', ''))
        
    #     # Determine if it's a deposit or withdrawal
    #     if current_balance - previous_balance == amount:
    #         list_data[i]['type'] = 'Deposit'
    #     elif previous_balance - current_balance == amount:
    #         list_data[i]['type'] = 'Withdrawal'
    #     else:
    #         list_data[i]['type'] = 'Unknown'

    date_pattern = re.compile(r'^(\d{2}/\d{2}/\d{2})')

    pattern = re.compile(
        r"""
        (?P<date>\d{2}/\d{2}/\d{2})\s+              # Date
        (?P<narration>[\w\W]+?)\s+                  # Narration
        (?P<ref_no>\d{16,19})\s+                    # Reference Number
        (?P<value_date>\d{2}/\d{2}/\d{2})\s+        # Value Date
        (?P<withdrawal_amt>[\d,]+\.\d{2})\s+        # Withdrawal Amount
        (?P<closing_balance>[\d,]+\.\d{2})          # Closing Balance
        """,
        re.VERBOSE,
    )

    # Split the text into lines
    lines = text.strip().split('\n')
    list_data = []
    i = 0
    # print(text)
    # print(lines)
    while i < len(lines):
        match = pattern.match(lines[i])
        if match:
            date = match.group('date')
            narration = [match.group('narration')]
            ref_no = match.group('ref_no')
            value_date = match.group('value_date')
            withdrawal_amt = match.group('withdrawal_amt')
            closing_balance = match.group('closing_balance')

            i += 1

            # Collect subsequent lines for the narration if they don't start with a new date
            while i < len(lines) and not date_pattern.match(lines[i]):
                narration.append(lines[i].strip())
                i += 1

            list_data.append({
                "Date" :date,
                "Narration" :' '.join(narration),
                "Chq_Ref_No" :ref_no,
                "value_date" :value_date,
                "amount" :withdrawal_amt,
                "closing_balance" :closing_balance,
            })


        else:
            i += 1

    for i in range(1, len(list_data)):
        previous_balance = float(list_data[i - 1]['closing_balance'].replace(',', ''))
        current_balance = float(list_data[i]['closing_balance'].replace(',', ''))
        amount = float(list_data[i]['amount'].replace(',', ''))
        
        # Determine if it's a deposit or withdrawal
        if current_balance - previous_balance == amount:
            list_data[i]['type'] = 'Deposit'
        elif previous_balance - current_balance == amount:
            list_data[i]['type'] = 'Withdrawal'
        else:
            list_data[i]['type'] = 'Unknown'
        
    return list_data

# Opning Balance & Closing Balance
def extract_balances(data):
    # Regular expression to match the balances
    pattern = r'(\d{1,3}(?:,\d{3})*\.\d{2})\s+\d+\s+\d+\s+(\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d{1,3}(?:,\d{3})*\.\d{2})'
    matches = re.search(pattern, data)
    
    if matches:
        opening_balance = matches.group(1)
        closing_balance = matches.group(3)
        return opening_balance, closing_balance
    else:
        return None, None


def hdfc_bank_statment_main(url):
    
    ifsc_code = ""
    account_number = ""
    nick_name = ""
    main_name = ""
    status = ""
    email = ""
    branch_name = ""
    open_date = ""
    account_type = ""
    address1 = ""
    address2 = ""
    contact_number = ""
    micr = ""
    start_date = ""
    end_Date = ""
    transction_final_list = []


    # Summary - Scorecard
    summary_scorecard = [{
                    "Item": "Monthly Average Surplus",
                    "Details": "NA",
                    "Verification": "NA"
                },
                {   "Item": "Account Type",
                    "Details": "NA",
                    "Verification": "NA"},
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
                },                {
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
    bureau_ratings_Summary = []

    # Bureau Ratings - Telephone
    bureau_ratings_telephone = []

    # Bureau Ratings - Address
    bureau_ratings_address = []

    # Bureau Ratings - Emails
    bureau_ratings_emails =[]
    
    pdf_read = pdfplumber.open(url)


    # Page Number Get From PDF
    page_numbers = []
        
    for page in pdf_read.pages:
        page_numbers.append(page.page_number - 1)

    for page_no in page_numbers:
            page = pdf_read.pages[page_no]

         
            

    # PDF NUmber Wise Get string
    for page_no in page_numbers:
        # print(page_no)
        page = pdf_read.pages[page_no]
        # print(page)
        pdf_to_String = page.extract_text()

        # print(pdf_to_String)


        # Getting Details From String
        
        opening_balance, closing_balance = extract_balances(pdf_to_String)
        # print(opening_balance , closing_balance)
        if opening_balance != None:
            summary_scorecard.append({
                    "Item": "Opening Balance",
                    "Details": opening_balance,
                    "Verification": "NA"
                })
            
        if closing_balance != None:
             summary_scorecard.append({
                    "Item": "Closing Balance",
                    "Details": closing_balance,
                    "Verification": "NA"
                })

        if main_name == "":
            main_name = extract_mr(pdf_to_String)
            if main_name != None:
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

        if email == "":
            email = extract_email(pdf_to_String)
            if email != None:
                bureau_ratings_emails.append(email)

        if account_number == "":
            account_number = extract_account_no(pdf_to_String)
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

        if ifsc_code == "":
            ifsc_code =  extract_rtgs_ifsc(pdf_to_String)
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

        if micr == "":
            micr = extract_micr(pdf_to_String)
            if micr != None:
                summary_scorecard.append({
                        "Item": "MICR Code",
                        "Details": micr,
                        "Verification": "NA"
                    })
            else:
                summary_scorecard.append({
                        "Item": "MICR Code",
                        "Details": "NA",
                        "Verification": "NA"
                    })

        if status == "":
            status = extract_account_status(pdf_to_String)
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

        if contact_number == "":
            contact_number = extract_phoneno(pdf_to_String)
            if contact_number != None:
                bureau_ratings_telephone.append({contact_number})
        
        if start_date == "":
            start_date = extract_from_date(pdf_to_String)
            if start_date != None:
                summary_scorecard.append({
                    "Item": "Start Date",
                    "Details": start_date,
                    "Verification": "NA"})
            else:
                summary_scorecard.append({
                    "Item": "Start Date",
                    "Details": "NA",
                    "Verification": "NA"})


        if end_Date == "":
            end_Date = extract_to_date(pdf_to_String)
            if end_Date != None:
                summary_scorecard.append({
                    "Item": "End Date",
                    "Details": end_Date,
                    "Verification": "NA"})
            else:
                 summary_scorecard.append({
                    "Item": "End Date",
                    "Details": "NA",
                    "Verification": "NA"})

        
        transction_details = extract_transction_details(pdf_to_String)
        if transction_details != []:
            for x in transction_details:
                narration = ""
                if "*Closing" in x['Narration']:
                    narration = x['Narration'].split("*Closing")[0].replace(" ","")
                else:
                    narration = x['Narration'].replace(" ","")
                
                types = ""
                try:
                    types = x['type']
                except:
                    types = "Unknown"

                transction_final_list.append({
                    "Date":x['Date'],
                    "Narration":narration,
                    "Chq_Ref_No":x['Chq_Ref_No'],
                    "value_date":x['value_date'],
                    "amount":x['amount'],
                    "closing_balance":x['closing_balance'],
                    "type":types,
                })


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
    formate_json["All Transactions"] = transction_final_list
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
    formate_json["Bureau Ratings - Address"]= bureau_ratings_address
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
    formate_json["Bureau Ratings - Emails"]= bureau_ratings_emails

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
    
    if transction_final_list != []:
        for yy in transction_final_list[:10]:
            if yy['type'] == 'Deposit':
                top10_transactions_credit.append({
                    "Date" : yy["Date"],
                    "Transaction_Details" : yy["Narration"],
                    "Chq_Ref_No" : yy["Chq_Ref_No"],
                    "Amount" : yy["amount"],
                    "value_date" : yy["value_date"],
                    "Total_Balance" : yy["closing_balance"],
                })
            elif yy['type'] == 'Withdrawal':
                top10_transactions_debit.append({
                    "Date" : yy["Date"],
                    "Transaction_Details" : yy["Narration"],
                    "Chq_Ref_No" : yy["Chq_Ref_No"],
                    "Amount" : yy["amount"],
                    "value_date" : yy["value_date"],
                    "Total_Balance" : yy["closing_balance"],
                })
    
    formate_json["Top Transactions - Top 10 Credit Transaction"] = top10_transactions_credit
    formate_json["Top Transactions - Top 10 Debit Transaction"] = top10_transactions_debit
    formate_json["Top Transactions - Top 10 Monthly Transaction"] = transction_final_list[:10]

    return formate_json
    # import json  

    # save_file = open("savedata.json", "w")  
    # json.dump(formate_json, save_file, indent = 6)  
    # save_file.close()
    # print(formate_json)
    
# hdfc_bank_statment_main("./Bank Statement Analysis/HDFC Anup Dubey.pdf")
