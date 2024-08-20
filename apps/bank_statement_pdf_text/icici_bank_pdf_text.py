import re
import pdfplumber
import pandas as pd
from datetime import datetime
import tabula , json
import numpy as np
from collections import defaultdict
from datetime import datetime

# page count
def count_page_numbers(pdf_file):
    page_numbers = []
    pdf_read = pdfplumber.open(pdf_file)
    for page in pdf_read.pages:
        page_numbers.append(page.page_number)
    
    return  page_numbers


def read_text_from_First_page(page_numbers,pdf_file):
    # print(page_numbers)
    # for page_no in page_numbers:
        # print(page_no)
    pdf_read = pdfplumber.open(pdf_file)
    page = pdf_read.pages[0]
    pdf_to_String = page.extract_text()
    
    basic_Details = []


    account_number = re.search(r'Account Number\s*(\d+)|A/C No:\s*(\d+)', pdf_to_String)
    account_number = account_number.group(1) if account_number else None

    # Extract account name
    account_name = re.search(r'Name:\s*(.*?)(?:Branch|Address|A/C No|Account Number.*?-\s*(.*))', pdf_to_String, re.DOTALL)
    account_name = account_name.group(1).strip() if account_name else None

    # Extract account type
    account_type = re.search(r'A/C Type:\s*(\w+)', pdf_to_String)
    account_type = account_type.group(1) if account_type else None

    ifsc_code = re.search(r'IFSC Code:\s*([A-Z0-9]+)', pdf_to_String)
    ifsc_code = ifsc_code.group(1) if ifsc_code else None

    basic_Details.append({
        "account_number":account_number,
        "account_name":account_name,
        "account_type":account_type,
        "ifsc_code":ifsc_code,
    })


    return basic_Details


# get rae table from using of modules
def get_raw_table_from_tabula(page_numbers,pdf_file):
    extracted_data = []
    for xx in page_numbers:
        tables = tabula.read_pdf(pdf_file,pages=xx)
    # print(tables)
        for i, table in enumerate(tables):
            # print(table)
            table_as_list = table.values.tolist()
            extracted_data.extend([table.columns.values.tolist()])
            extracted_data.extend(table_as_list)


    return extracted_data


# Raw are concate All transction
def combine_rows(data):
    combined = []
    current_row = None
    
    for row in data:
        if pd.isna(row[0]):
            # If first element is NaN, it's a continuation row
            if current_row:
                current_row = [str(a) if pd.notna(a) else "" for a in current_row]
                current_row = [str(a) + (str(b) if pd.notna(b) else "") for a, b in zip(current_row, row)]
            continue
        else:
            # If first element is not NaN, finalize current row if it exists
            if current_row:
                combined.append([str(a) if pd.notna(a) else "" for a in current_row])
            current_row = row

    # Append the last row
    if current_row:
        combined.append([str(a) if pd.notna(a) else "" for a in current_row])
    
    return combined


# remove empty list from list
def is_unnamed_list(row):
    return all(isinstance(x, str) and x.startswith('Unnamed:') for x in row)

# transaction Mode
def transaction_mode_get(transaction_data):
    transaction_mode = "Other"
    if 'UPI' in transaction_data or 'Gpay' in transaction_data \
          or 'GOOGLE' in transaction_data or 'Phonepe' in transaction_data or \
              'VSI' in transaction_data or 'VIN' in transaction_data or "PAYTM" in transaction_data:
        transaction_mode = "UPI"
    if 'IMPS' in transaction_data:
        transaction_mode = "IMPS"
    if 'RTGS' in transaction_data:
        transaction_mode = "RTGS"
    if 'NEFT' in transaction_data:
        transaction_mode = "NEFT"
    if 'BIL' in transaction_data:
        transaction_mode = "Payment Gateway"
    if 'INFT' in transaction_data:
        transaction_mode = "Internal Fund Transfer"
    if 'CLG' in transaction_data or 'Cheque' in transaction_data or 'Chq' in transaction_data or 'CHQ' in transaction_data:
        transaction_mode = "Cheque"
    if 'CASH' in transaction_data:
        transaction_mode = "CASH"
    if 'ACH' in transaction_data:
        transaction_mode = "ACH"
    if 'POS' in transaction_data:
        transaction_mode = "POS"
    if 'IB' in transaction_data or 'TPT' in transaction_data:
        transaction_mode = "Internet Banking"
    if 'ATW' in transaction_data:
        transaction_mode = "ATM withdrawal"
    if  'NWD' in transaction_data:
        transaction_mode = "CARD Transaction"
    if 'DEBIT CARD' in transaction_data or 'EAW' in transaction_data or 'ATM' in transaction_data:
        transaction_mode = "ATM"
    if  'EMI' in transaction_data:
        transaction_mode = "Loan"

    return transaction_mode



# transaction date formate
def transac_date_formate(str_date):
    date_formats = [
        "%d/%m/%Y", # e.g., 6/4/2018
        "%d/%b/%Y",   # e.g., 02/Apr/2022
        "%d/%m/%Y",   # e.g., 03/04/2018
        "%d-%b-%Y",   # e.g., 02-Apr-2022
        "%d-%m-%Y",   # e.g., 03-04-2018
        "%d/%m/%Y", # 03/04/2018
        "%Y-%m-%d",   # e.g., 2022-04-02
        "%Y/%m/%d",   # e.g., 2022/04/02
        # "%d.%m.%Y",   # e.g., 13.07.2022
        "%d/%b/%Y.%f" # e.g., 13/Jul/2022.1 (with extra fractional seconds)
    ] 

    # try:
    for fmt in date_formats:
        try:
            # Attempt to parse the date
            date_obj = datetime.strptime(str_date.split('.')[0], fmt)
            return date_obj.strftime("%d-%m-%Y")
        except ValueError:
            continue
    
    raise ValueError(f"Date '{str_date}' is not in a recognized format.")


# Top Transactions - Top 10 Monthly Transaction
def top_10_month_transctions_fun(transction_details_list):
    # Top 10 Month Wise transctions

    if transction_details_list != []:
        top_10_trans_df = pd.DataFrame(transction_details_list)

        # Convert Amount to numeric
        top_10_trans_df['Amount'] = top_10_trans_df['Amount'].replace('[\$,]', '', regex=True).astype(float)

        # Convert Date to datetime
        top_10_trans_df['Date'] = pd.to_datetime(top_10_trans_df['Date'], format='%d-%m-%Y')

        # Extract month and year
        top_10_trans_df['Year'] = top_10_trans_df['Date'].dt.year
        top_10_trans_df['Month'] = top_10_trans_df['Date'].dt.month

        # Group by Year and Month and get top 10 transactions by Amount
        top_transactions = (top_10_trans_df.groupby(['Year', 'Month'])
                            .apply(lambda x: x.nlargest(10, 'Amount'))
                            .reset_index(drop=True))

        top_transactions['Date'] = top_transactions['Date'].dt.strftime('%d-%m-%Y')

        # Convert the result to JSON
        transct_top_10_json = top_transactions.to_dict(orient='records')

        return transct_top_10_json
    else:
        empty_json = {}
        return  empty_json


# Top 10 Credit & Debit
def top_credit_debit_transctions_fun(transction_details_list):

    if transction_details_list != []:
        transactions_by_month = defaultdict(lambda: {'CREDIT': [], 'DEBIT': []})

        for entry in transction_details_list:
            date_str = entry['Date']
            transaction_type = entry['Credit/Debit']
            amount_str = entry['Amount']
            description = entry['Description']
            reference = entry['Reference']
            
            # Parse date and amount
            date_obj = datetime.strptime(date_str, '%d-%m-%Y')
            amount = float(amount_str)
            
            # Store transactions
            month_key = date_obj.strftime('%Y-%m')
            transactions_by_month[month_key][transaction_type].append({
                'Amount': amount,
                'Description': description,
                'Reference': reference
            })

        # Find top credited and debited transactions per month
        top_transactions_credited = {}
        top_transactions_debited = {}

        for month, transactions in transactions_by_month.items():
            top_credited = max(transactions['CREDIT'], key=lambda x: x['Amount'], default={'Amount': 0, 'Description': '', 'Reference': ''})
            top_debited = max(transactions['DEBIT'], key=lambda x: x['Amount'], default={'Amount': 0, 'Description': '', 'Reference': ''})
            top_transactions_credited[month] = {
                'Top Credited': {
                    'Amount': top_credited['Amount'],
                    'Description': top_credited['Description'],
                    'Reference': top_credited['Reference']
                },
                
            }

            top_transactions_debited[month] = {
            'Top Debited': {
                    'Amount': top_debited['Amount'],
                    'Description': top_debited['Description'],
                    'Reference': top_debited['Reference']
                }}
            
        return top_transactions_credited , top_transactions_debited

    else:
        empty_json = {}
        return  empty_json , empty_json


# max min , credit , debit , balance
def max_min_Credit_debit_balance_fun(transction_details_list):

    if transction_details_list != []:
        min_balance = float('inf')
        max_balance = float('-inf')
        min_credit = float('inf')
        max_credit = float('-inf')
        min_debit = float('inf')
        max_debit = float('-inf')

        # Initialize start and end dates
        start_date = None
        end_date = None

        # Date format used in the data
        date_format = "%d-%m-%Y"

        summary_list = []
        # Process each transaction
        for transaction in transction_details_list:
            balance = transaction["Balance"]
            amount = transaction["Amount"]
            date = datetime.strptime(transaction["Date"], date_format)
            
            # Update balance statistics
            if balance < min_balance:
                min_balance = balance
            if balance > max_balance:
                max_balance = balance
            
            # Update credit and debit statistics
            if amount > 0:
                if transaction["Credit/Debit"] == "CREDIT":
                    if amount < min_credit:
                        min_credit = amount
                    if amount > max_credit:
                        max_credit = amount
                elif transaction["Credit/Debit"] == "DEBIT":
                    if amount < min_debit:
                        min_debit = amount
                    if amount > max_debit:
                        max_debit = amount
            
            # Update start and end dates
            if start_date is None or date < start_date:
                start_date = date
            if end_date is None or date > end_date:
                end_date = date

        # Output results
        summary_list.append({"min_balance":min_balance,
                            "max_balance":max_balance,
                            "min_credit":min_credit,
                            "max_credit":max_credit,
                            "min_debit":min_debit,
                            "max_debit":max_debit,
                            "end_date":end_date.strftime('%d-%m-%Y'),
                            "start_date":start_date.strftime('%d-%m-%Y'), 
                            })

        return summary_list
    else:
        empty_json = []
        return  empty_json

def icic_bank_statement_main(pdf_file):
    # count page number
    page_number = count_page_numbers(pdf_file)

    read_raw_text = read_text_from_First_page(page_number,pdf_file)
    # print(read_raw_text)

    # get raw table
    get_raw_table = get_raw_table_from_tabula(page_number,pdf_file)
    
    # Remove some space and characters
    all_transc_data = [row for row in get_raw_table if not (all(isinstance(x, float) and np.isnan(x) for x in row) or is_unnamed_list(row))]

    # multiple columns are combine
    multi_columns_table = combine_rows(all_transc_data)

    # Remove elements containing 'Unnamed: '
    cleaned_data = [
        [item.replace('\r', '').replace('Unnamed: 0', '').replace('Unnamed: 1', '').replace('Unnamed: 2', '') for item in sublist]
        for sublist in multi_columns_table
    ]


    temp_Data_store = pd.DataFrame(cleaned_data)
    temp_Data_store = temp_Data_store.drop([col for col in temp_Data_store.columns if 'Unnamed' in str(col)], axis=1)
    temp_Data_store = temp_Data_store.drop([col for col in temp_Data_store.columns if 'Unnamed: 1' in str(col)], axis=1)
    temp_Data_store = temp_Data_store.drop([col for col in temp_Data_store.columns if 'Unnamed: 2' in str(col)], axis=1)
    temp_Data_store.columns = temp_Data_store.columns.astype(str)
    temp_Data_store.columns = temp_Data_store.columns.str.replace('\r', ' ', regex=False)
    temp_Data_store.columns = temp_Data_store.columns.str.replace('_x000D_', ' ', regex=False)

    with pd.ExcelWriter('temp_Data_store.xlsx', engine='xlsxwriter') as writer:
        temp_Data_store.to_excel(writer, sheet_name='All Transctions', index=True,header=False)


    # Read excel file 
    all_transctions_df = pd.read_excel('temp_Data_store.xlsx')
    all_transctions_df = all_transctions_df.fillna("")

    headers = list(all_transctions_df.columns)
    cleaned_columns = [col.replace('_x000D_', ' ') if isinstance(col, str) else col for col in headers]



    tran_pattern = re.compile(r'Remarks|Description|PARTICULARS')
    with_pattern = re.compile(r'Withdrawal|Withd')
    depo_pattern = re.compile(r'Deposit|Depos')
    balance_pattern = re.compile(r'Balance|Balan')
    value_date_pattern = re.compile(r'Value Date|Value|ValueDate')
    trans_date_pattern = re.compile(r'Transaction Date|TransactionDate')
    trans_id_pattern = re.compile(r'Tran Id|TranId')

    try:
        tra_field = [i for i, item in enumerate(cleaned_columns) if isinstance(item, str) and tran_pattern.search(item)][0]
    except:
        tra_field = ""

    try:
        with_field = [i for i, item in enumerate(cleaned_columns) if isinstance(item, str) and with_pattern.search(item)][0]
    except:
        with_field = ""

    try:
        depo_field = [i for i, item in enumerate(cleaned_columns) if isinstance(item, str) and depo_pattern.search(item)][0]
    except:
        depo_field = ""

    try:
        balance_field = [i for i, item in enumerate(cleaned_columns) if isinstance(item, str) and balance_pattern.search(item)][0]
    except:
        balance_field = ""

    try:
        transc_date_field = [i for i, item in enumerate(cleaned_columns) if isinstance(item, str) and trans_date_pattern.search(item)][0]
    except:
        transc_date_field = ""

    try:
        transc_id_field = [i for i, item in enumerate(cleaned_columns) if isinstance(item, str) and trans_id_pattern.search(item)][0]
    except:
        transc_id_field = ""

    transction_details_list = []
    


    total_credit_amount = 0
    total_debit_amount = 0

    total_Count_credit_transc = 0
    total_Count_debit_transc = 0
    # All Transctions get
    for index, row in all_transctions_df.iterrows():
            # print(row)
     
        if tra_field != "":
            transaction_modes = transaction_mode_get(row[all_transctions_df.columns[tra_field]].replace("_x000D_","").strip())
            
            if row[all_transctions_df.columns[depo_field]] != "" and \
                row[all_transctions_df.columns[depo_field]] != 0.00 and \
                    row[all_transctions_df.columns[depo_field]] != float('nan'):
                
                date = ""
                description = ""
                amount = 0
                total_balance = 0
                reference = ""

                if transc_date_field != "":
                    modify_Date = transac_date_formate(str(row[all_transctions_df.columns[transc_date_field]]))
                    if modify_Date != "":
                        date = modify_Date

                if tra_field != "":
                    description = row[all_transctions_df.columns[tra_field]].strip()


                if with_field != "":
                    with_value = row[all_transctions_df.columns[with_field]]

                    amount = str(with_value)

                if balance_field != "":
                    balance_value = row[all_transctions_df.columns[balance_field]]
                    balance_value = str(balance_value)
                    balance_value = balance_value.replace(',', '')  # Remove commas
                    balance_value = float(balance_value)           # Convert to float
                    balance_value = int(balance_value)     
                    total_balance = float(balance_value)

                if depo_field != "":
                    with_value = row[all_transctions_df.columns[depo_field]]

                    amount = str(with_value)
                    amount_str_cleaned = amount.replace(',', '')  # Remove commas
                    amount_float = float(amount_str_cleaned)           # Convert to float
                    amount_int = int(amount_float)                     # Convert to int
             

                if transc_id_field != "":
                    reference = row[all_transctions_df.columns[transc_id_field]]
                
                # Total of Credit Amount
                

                total_credit_amount += int(amount_int)

                # Count Total of Credit Transctions 
                total_Count_credit_transc += 1

                transction_details_list.append({
                                        "Date":date,
                                        "Credit/Debit":"CREDIT",
                                        "Description" :description,
                                        "Amount" :amount_int,
                                        "Mode":transaction_modes,
                                        "Balance":total_balance,
                                        "Reference":reference,
                                    })


            if row[all_transctions_df.columns[with_field]] != "" and \
                row[all_transctions_df.columns[with_field]] != 0.00 and \
                    row[all_transctions_df.columns[with_field]] != float('nan'):
                
                date = ""
                description = ""
                amount = 0
                total_balance = 0
                reference = ""

                if transc_date_field != "":
                    modify_Date = transac_date_formate(str(row[all_transctions_df.columns[transc_date_field]]))
                    if modify_Date != "":
                        date = modify_Date

                if tra_field != "":
                    description = row[all_transctions_df.columns[tra_field]].strip()


                if with_field != "":
                    with_value = row[all_transctions_df.columns[with_field]]

                    amount = str(with_value)
                    amount_str_cleaned = amount.replace(',', '')  # Remove commas
                    amount_float = float(amount_str_cleaned)           # Convert to float
                    amount_int = int(amount_float)   
                    

                if balance_field != "":
                    balance_value = row[all_transctions_df.columns[balance_field]]
                    balance_value = str(balance_value)
                    balance_value = balance_value.replace(',', '')  # Remove commas
                    balance_value = float(balance_value)           # Convert to float
                    balance_value = int(balance_value)     
                    total_balance = float(balance_value)
                  
                if transc_id_field != "":
                    reference = row[all_transctions_df.columns[transc_id_field]]
                

                # Total of debit Amount
                total_debit_amount += int(amount_int)

                # Count Total of debit Transctions 
                total_Count_debit_transc += 1

                transction_details_list.append({
                                    "Date":date,
                                    "Credit/Debit":"DEBIT",
                                    "Description" :description,
                                    "Amount" :amount_int,
                                    "Mode":transaction_modes,
                                    "Balance":total_balance,
                                    "Reference":reference,
                                })
    

  
        # Top Transactions - Top 10 Monthly Transaction
    month_top_10_transc =  top_10_month_transctions_fun(transction_details_list)


    # Top 10 Credit & Debit
    top_transactions_credited , top_transactions_debited= top_credit_debit_transctions_fun(transction_details_list)
    # print(top_transactions_credited)
    # print(top_transactions_debited)


    # print(total_credit_amount , "total_credit_amount")
    # print(total_debit_amount , "total_debit_amount")
    # print(total_Count_credit_transc , "total_Count_credit_transc")
    # print(total_Count_debit_transc , "total_Count_debit_transc")


    summary_list = max_min_Credit_debit_balance_fun(transction_details_list)


    max_balance = 0
    min_balance = 0
    min_credit = 0
    max_credit = 0
    min_debit = 0
    max_debit = 0


    if summary_list != []:
        max_balance = summary_list[0]["max_balance"]

    if summary_list != []:
        min_balance = summary_list[0]["min_balance"]
    
    if summary_list != []:
        min_credit = summary_list[0]["min_credit"]
    
    if summary_list != []:
        max_credit = summary_list[0]["max_credit"]
    
    if summary_list != []:
        min_debit = summary_list[0]["min_debit"]

    if summary_list != []:
        max_debit = summary_list[0]["max_debit"]


    # Store Data in json format
    formate_json = {}

    # All Transactions
    formate_json["All Transactions"] = transction_details_list
    formate_json["Associated Party Transactions"] = []
    formate_json["Bureau Ratings - Address"]= []
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
    formate_json["Bureau Ratings - Emails"]= []
    formate_json["Bureau Ratings - Enquiry"] = {
        "Member": None,
        "Enquiry Date": None,
        "Enquiry Purpose": None,
        "Enquiry Amount": None
    }
    formate_json["Bureau Ratings - Identification Type"]= []
    formate_json["Bureau Ratings - Loans"]= []
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
            }
        ]
    formate_json["Bureau Ratings - Telephone"]= []
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
            }]
    formate_json["Credit Card Info - Credit Cards"] = None
    formate_json["EOD"] = {}
    formate_json["Emi Details"] = None
    formate_json["Fraud Check Triggers - Fraud Check Details"] = []
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
    formate_json["Month Wise Details"] = []
    formate_json["Recurring Credits"] = []
    formate_json["Recurring Debits"] = []
    formate_json["Return Transactions"] = []
    formate_json["Salary Slip Info"] = []
    formate_json["Salary Slip Info - Details"] = []
    formate_json["Salary Slip Info - Summary"] = []
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
                "Value": total_credit_amount / total_Count_credit_transc
            },
            {
                "Description": "Average Debit Transactions",
                "Value": total_debit_amount / total_Count_debit_transc
            },
            {
                "Description": "Total Credit Amount",
                "Value": total_credit_amount
            },
            {
                "Description": "Total Debit Amount",
                "Value": total_debit_amount
            },
            {
                "Description": "Total Count of Credit Transactions",
                "Value": total_Count_credit_transc
            },
            {
                "Description": "Total Count of Debit Transactions",
                "Value": total_Count_debit_transc
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
                "Value": max_balance
            },
            {
                "Description": "Minimum Balance",
                "Value": min_balance
            },
            {
                "Description": "Maximum Credit",
                "Value": max_credit
            },
            {
                "Description": "Minimum Credit",
                "Value": min_credit
            },
            {
                "Description": "Maximum Debit",
                "Value": max_debit
            },
            {
                "Description": "Minimum Debit",
                "Value": min_debit
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
    formate_json["Summary - Cheque Bounce Charges"] = [ {
                "Type": "Amount of Cheque Bounce",
                "Value": "NA"
            },
            {
                "Type": "Count of Cheque Bounce",
                "Value": "NA"
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
    formate_json["Summary - Scorecard"] = [{
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
                    "Details": "ICICI BANK",
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
                },
                {
                    "Item": "IFSC Code",
                    "Details": read_raw_text[0]["ifsc_code"],
                    "Verification": "NA"
                },
                {
                    "Item": "Account Number",
                    "Details": read_raw_text[0]["account_number"],
                    "Verification": "NA"      
                },
                {
                    "Item": "Customer Name",
                    "Details": read_raw_text[0]["account_name"],
                    "Verification": "NA"
                },
                {
                    "Item": "Account Type",
                    "Details": read_raw_text[0]["account_type"],
                    "Verification": "NA"
                },
                {"Item": "Start Date",
                    "Details": summary_list[0]["start_date"],
                    "Verification": "NA"
                },
                {
                    "Item": "End Date",
                    "Details": summary_list[0]["end_date"],
                    "Verification": "NA"
                },
                
                ]
    formate_json["Top Transactions - Top 10 Credit Transaction"] = [top_transactions_credited]
    formate_json["Top Transactions - Top 10 Debit Transaction"] = [top_transactions_debited]
    formate_json["Top Transactions - Top 10 Monthly Transaction"] = [month_top_10_transc]


    return formate_json


# icic_bank_statement_main("./Bank Statement Analysis/ICICI - Salaried.pdf")

     